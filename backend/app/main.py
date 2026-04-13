import time

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from .api.routes.recommendations import router as recommendations_router
from .observability.metrics import metrics


def create_app() -> FastAPI:
    """
    Application factory for the Zomato-style restaurant recommendation backend.

    Phase 1: only high-level skeleton and health check are provided.
    Later phases will add data ingestion, recommendation routes, and LLM integration.
    """
    app = FastAPI(
        title="AI-Powered Restaurant Recommendation Service",
        description=(
            "Backend API for an AI-powered restaurant recommendation system inspired by Zomato. "
            "Combines structured restaurant data with an LLM for ranked, explained recommendations."
        ),
        version="0.1.0",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def metrics_middleware(request: Request, call_next):
        started = time.perf_counter()
        try:
            response = await call_next(request)
        except Exception:
            metrics.inc("http.5xx")
            raise
        elapsed_ms = (time.perf_counter() - started) * 1000
        metrics.observe_ms("http.request_latency_ms", elapsed_ms)
        metrics.inc(f"http.status.{response.status_code}")
        if response.status_code >= 500:
            metrics.inc("http.5xx")
        elif response.status_code >= 400:
            metrics.inc("http.4xx")
        return response

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        # Phase 8: centralized fallback for uncaught errors.
        print(f"[error] path={request.url.path} type={type(exc).__name__} msg={exc}")
        return JSONResponse(
            status_code=500,
            content={"error": {"code": "INTERNAL_ERROR", "message": "Unexpected server error occurred."}},
        )

    @app.get("/health", tags=["health"])
    async def health() -> dict:
        """Basic health check endpoint."""
        return {"status": "ok", "version": "0.1.0"}

    app.include_router(recommendations_router)

    return app


app = create_app()

