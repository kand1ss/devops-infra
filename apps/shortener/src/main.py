from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator
from routs import router

app = FastAPI(name="Shortener Service")
app.include_router(router)

instrumentator = Instrumentator(
    should_group_status_codes=False,
    should_ignore_untemplated=True,
    should_respect_env_var=True,
    should_instrument_requests_inprogress=True,
    excluded_handlers=[".*admin.*", "/metrics"],
    env_var_name="ENABLE_METRICS",
    inprogress_name="inprogress",
    inprogress_labels=True
)
_ = instrumentator.instrument(
    app,
    metric_namespace="shortener-service"
).expose(app)
