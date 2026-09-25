"""
OpenTelemetry and Observability Foundation for ApplyForge
"""
from typing import Optional
from packages.shared.logger import logger

_tracer = None

def init_telemetry(service_name: str = "applyforge-api") -> Optional[object]:
    """
    Initializes OpenTelemetry tracer provider if opentelemetry SDK is installed.
    """
    global _tracer
    try:
        from opentelemetry import trace
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.resources import Resource

        provider = TracerProvider(resource=Resource.create({"service.name": service_name}))
        trace.set_tracer_provider(provider)
        _tracer = trace.get_tracer(service_name)
        logger.info(f"OpenTelemetry initialized for {service_name}")
        return _tracer
    except ImportError:
        logger.info("OpenTelemetry SDK not installed; telemetry is running in no-op mode")
        return None

def get_tracer(service_name: str = "applyforge"):
    global _tracer
    if _tracer is None:
        _tracer = init_telemetry(service_name)
    return _tracer
