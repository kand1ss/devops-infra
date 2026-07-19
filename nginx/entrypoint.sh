#!/bin/sh
set -eu

DOMAIN="${DOMAIN:?DOMAIN env var is required}"
CERT_PATH="/etc/letsencrypt/live/${DOMAIN}/fullchain.pem"
CONF_DIR="/etc/nginx/conf.d"
CONF_FILE="${CONF_DIR}/default.conf"

mkdir -p "$CONF_DIR"

render_conf() {
  template="$1"
  DOMAIN="$DOMAIN" envsubst '${DOMAIN}' <"$template" >"$CONF_FILE"
}

if [ -f "$CERT_PATH" ]; then
  render_conf /etc/nginx/templates/nginx.ssl.conf.template
else
  render_conf /etc/nginx/templates/nginx.bootstrap.conf.template
fi

(
  while [ ! -f "$CERT_PATH" ]; do
    sleep 5
  done
  echo "[entrypoint] Certificate found, switching to SSL config"
  render_conf /etc/nginx/templates/nginx.ssl.conf.template
  nginx -s reload
) &

exec nginx -g 'daemon off;'
