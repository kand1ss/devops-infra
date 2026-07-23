#!/usr/bin/env python3
"""
audit_exporter.py — парсит ausearch output, ведёт накопительный (monotonic)
counter по ключам, пишет в node_exporter textfile collector directory.
Запускать через systemd timer каждые 30-60s.

Важно: metric объявлена как TYPE counter, поэтому значение должно только расти.
Состояние между запусками (последний обработанный timestamp + накопленные
суммы) хранится в STATE_FILE — без него метрика "спадала" бы между прогонами
и ломала бы increase()/rate() в PromQL.
"""

import json
import re
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path

TEXTFILE_DIR = Path("/var/lib/node_exporter/textfile_collector")
OUTPUT_FILE = TEXTFILE_DIR / "audit_events.prom"
STATE_FILE = TEXTFILE_DIR / ".audit_events.state.json"

WATCHED_KEYS = ["identity_change", "sudoers_change", "shadow_change", "root_exec"]

# Первый прогон — берём небольшое окно назад, чтобы не пропустить события,
# случившиеся между установкой и первым запуском таймера.
INITIAL_LOOKBACK_MINUTES = 5

AUSEARCH_TS_FORMAT = "%m/%d/%Y %H:%M:%S"


def _load_state() -> dict:
    if not STATE_FILE.exists():
        return {"last_ts": None, "totals": {key: 0 for key in WATCHED_KEYS}}
    try:
        state = json.loads(STATE_FILE.read_text())
    except (json.JSONDecodeError, OSError) as e:
        print(f"Corrupt state file, resetting: {e}", file=sys.stderr)
        return {"last_ts": None, "totals": {key: 0 for key in WATCHED_KEYS}}

    # На случай если WATCHED_KEYS расширили после того, как state уже существовал.
    totals = state.get("totals", {})
    for key in WATCHED_KEYS:
        totals.setdefault(key, 0)
    state["totals"] = totals
    return state


def _save_state(state: dict) -> None:
    tmp_state = STATE_FILE.with_suffix(".json.tmp")
    tmp_state.write_text(json.dumps(state))
    tmp_state.rename(STATE_FILE)


def get_new_events(last_ts: str | None) -> dict[str, int]:
    """
    Считает СОБЫТИЯ, произошедшие СТРОГО ПОСЛЕ last_ts, по каждому ключу.
    Возвращает дельту (не накопленную сумму) — накопление делает вызывающий код.
    """
    now = datetime.now()
    if last_ts is None:
        since_dt = now - timedelta(minutes=INITIAL_LOOKBACK_MINUTES)
    else:
        # +1 секунда, чтобы не задвоить событие, попавшее ровно на границу
        # предыдущего запроса (ausearch -ts инклюзивен по секунде).
        since_dt = datetime.strptime(last_ts, AUSEARCH_TS_FORMAT) + timedelta(seconds=1)

    since = since_dt.strftime(AUSEARCH_TS_FORMAT)
    deltas = {key: 0 for key in WATCHED_KEYS}

    for key in WATCHED_KEYS:
        try:
            result = subprocess.run(
                ["ausearch", "-k", key, "-ts", since],
                capture_output=True,
                text=True,
                timeout=10,
            )
            # ausearch возвращает 1, когда событий не найдено — это не ошибка.
            if result.returncode not in (0, 1):
                print(
                    f"ausearch failed for key={key}: {result.stderr}", file=sys.stderr
                )
                continue
            deltas[key] = len(re.findall(r"^type=SYSCALL", result.stdout, re.MULTILINE))
        except subprocess.TimeoutExpired:
            print(f"ausearch timeout for key={key}", file=sys.stderr)
        except FileNotFoundError:
            print("ausearch not found — audit package not installed?", file=sys.stderr)
            sys.exit(1)

    return deltas


def write_metrics(totals: dict[str, int]) -> None:
    """Атомарная запись — во избежание partial read со стороны node_exporter."""
    TEXTFILE_DIR.mkdir(parents=True, exist_ok=True)
    tmp_file = OUTPUT_FILE.with_suffix(".prom.tmp")

    lines = [
        "# HELP audit_events_total Cumulative count of auditd events by rule key",
        "# TYPE audit_events_total counter",
    ]
    for key, count in totals.items():
        lines.append(f'audit_events_total{{key="{key}"}} {count}')

    tmp_file.write_text("\n".join(lines) + "\n")
    tmp_file.rename(OUTPUT_FILE)


def main() -> None:
    state = _load_state()
    now_ts = datetime.now().strftime(AUSEARCH_TS_FORMAT)

    deltas = get_new_events(state["last_ts"])
    for key, delta in deltas.items():
        state["totals"][key] += delta

    state["last_ts"] = now_ts
    _save_state(state)
    write_metrics(state["totals"])


if __name__ == "__main__":
    main()
