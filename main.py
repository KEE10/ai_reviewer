from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from config import settings
from shared.database import init_db, close_db
from shared.events import subscribe, PR_CREATED, PR_REVIEWED
from shared.clients import init_clients, close_clients

from domain.pull_requests.route import router as pr_router
from domain.reviews.route import router as rev_router
from domain.pull_requests.events import handle_pr_reviewed
from domain.reviews.events import handle_pr_created


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    await subscribe(PR_CREATED, handle_pr_created)
    await subscribe(PR_REVIEWED, handle_pr_reviewed)
    await init_clients()
    yield
    await close_clients()
    await close_db()


app = FastAPI(title=settings.app_name, debug=settings.debug, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_credentials,
    allow_methods=settings.cors_methods,
    allow_headers=settings.cors_headers,
)

# Routers - to be added later
app.include_router(pr_router, tags=["Webhook"])
app.include_router(rev_router, tags=["Review"])


@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "environment": settings.environment,
        "app": settings.app_name,
    }
