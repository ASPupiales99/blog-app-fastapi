from dotenv import load_dotenv
from fastapi import FastAPI

from app.auth.router import router as auth_router
from app.core.db import Base, engine
from app.router.post import router as post_router

load_dotenv()


# dev


def create_app() -> FastAPI:
    app = FastAPI(title="Mini Blog")
    Base.metadata.create_all(bind=engine)

    app.include_router(auth_router, prefix="/api/v1")
    app.include_router(post_router)

    return app


app = create_app()
