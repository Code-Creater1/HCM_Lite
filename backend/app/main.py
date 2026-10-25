from contextlib import asynccontextmanager
import os, uuid
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.db.init_db import init_db
from app.db.session import SessionLocal
from app.api import auth, setup, users, employees, org, attendance, leave


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


def create_app() -> FastAPI:
    app = FastAPI(title="HCM Lite", version="0.4.0", lifespan=lifespan)

    @app.middleware("http")
    async def request_id(request: Request, call_next):
        rid = request.headers.get("x-request-id") or uuid.uuid4().hex[:12]
        request.state.request_id = rid
        resp = await call_next(request)
        resp.headers["x-request-id"] = rid
        return resp

    origins = os.getenv(
        "ALLOWED_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000",
    ).split(",")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[o.strip() for o in origins],
        allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
    )

    @app.exception_handler(Exception)
    async def generic_error(request: Request, exc: Exception):
        return JSONResponse(
            status_code=500,
            content={"error": "internal", "detail": str(exc),
                     "path": request.url.path,
                     "request_id": getattr(request.state, "request_id", None)},
        )

    for r in (setup, auth, users, employees, org, attendance, leave):
        app.include_router(r.router, prefix="/api")

    @app.get("/")
    def root():
        return {"app": "HCM Lite API", "version": app.version,
                "docs": "/docs", "health": "/api/health", "api_base": "/api"}

    @app.get("/api/health")
    def health():
        db = SessionLocal()
        try:
            db.execute(text("SELECT 1"))
            return {"status": "ok", "db": "ok", "version": app.version}
        except Exception as e:
            return {"status": "degraded", "db": str(e)}
        finally:
            db.close()

    return app


app = create_app()