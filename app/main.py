from fastapi import FastAPI

from app.api.v1.routes.auth import router as auth_router
from app.api.v1.routes.login import router as login_router
from app.api.v1.routes.wallet import router as wallet_router
from app.api.v1.routes.monnify import router as monnify_router
from app.api.v1.routes.changenow import router as changenow_router
from app.api.v1.routes.bigisub import router as bigisub_router
from app.api.v1.routes.admin_changenow import router as admin_changenow_router
from app.api.v1.routes.admin import router as admin_router
from app.api.v1.routes.admin_monnify import router as admin_monnify_router
from app.core.config import settings


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.APP_VERSION,
    description="Alpha Galaxy Fintech API",
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
# Admin Monnify
# =========================================================

app.include_router(
    admin_monnify_router,
    prefix="/api/v1",
)
app.include_router(
    admin_changenow_router,
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