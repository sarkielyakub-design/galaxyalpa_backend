from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.routes.auth import router as auth_router
from app.api.v1.routes.login import router as login_router
from app.api.v1.routes.wallet import router as wallet_router
from app.api.v1.routes.monnify import router as monnify_router
from app.api.v1.routes.changenow import router as changenow_router
from app.api.v1.routes.bigisub import router as bigisub_router

from app.api.v1.routes.admin import router as admin_router
from app.api.v1.routes.admin_monnify import router as admin_monnify_router
from app.api.v1.routes.admin_changenow import router as admin_changenow_router
from app.api.v1.routes.admin_bigisub import router as admin_bigisub_router
from app.api.v1.routes.admin_audit import router as admin_audit_router

from app.core.config import settings


# =========================================================
# Application
# =========================================================

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.APP_VERSION,
    description="Alpha Galaxy Fintech API",
)


# =========================================================
# CORS
# =========================================================
#
# Local development:
#
# Next.js Admin:
#   http://localhost:3000
#
# FastAPI:
#   http://localhost:8000
#
# We allow both localhost and 127.0.0.1 because browsers
# treat them as different origins.
#

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================================================
# Authentication
# =========================================================

app.include_router(
    auth_router,
    prefix="/api/v1",
)

app.include_router(
    login_router,
    prefix="/api/v1",
)


# =========================================================
# Wallet
# =========================================================

app.include_router(
    wallet_router,
    prefix="/api/v1",
)


# =========================================================
# Monnify
# =========================================================

app.include_router(
    monnify_router,
    prefix="/api/v1",
)


# =========================================================
# ChangeNOW
# =========================================================

app.include_router(
    changenow_router,
    prefix="/api/v1",
)


# =========================================================
# Bigisub
# =========================================================

app.include_router(
    bigisub_router,
    prefix="/api/v1",
)


# =========================================================
# Admin
# =========================================================

app.include_router(
    admin_router,
    prefix="/api/v1",
)


# =========================================================
# Admin - Monnify
# =========================================================

app.include_router(
    admin_monnify_router,
    prefix="/api/v1",
)


# =========================================================
# Admin - ChangeNOW
# =========================================================

app.include_router(
    admin_changenow_router,
    prefix="/api/v1",
)


# =========================================================
# Admin - Bigisub
# =========================================================

app.include_router(
    admin_bigisub_router,
    prefix="/api/v1",
)


# =========================================================
# Admin - Audit
# =========================================================

app.include_router(
    admin_audit_router,
    prefix="/api/v1",
)


# =========================================================
# Root
# =========================================================

@app.get("/")
async def home():
    return {
        "project": settings.PROJECT_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
    }


# =========================================================
# Health
# =========================================================

@app.get("/health")
async def health():
    return {
        "status": "healthy",
    }