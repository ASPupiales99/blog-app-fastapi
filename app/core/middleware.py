import time
import uuid

from fastapi import FastAPI, Request, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

BLACK_LIST = {}


def register_middleware(app: FastAPI):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def add_process_time_header(request: Request, call_next):
        start_time = time.perf_counter()
        response = await call_next(request)
        process_time = time.perf_counter() - start_time
        response.headers["X-Process-Time"] = f"{process_time:.4f} s"
        return response

    @app.middleware("http")
    async def log_request(request: Request, call_next):
        print(f"**Request: {request.method} {request.url} **")
        response = await call_next(request)
        print(f"**Response: {response.status_code} **")
        return response

    @app.middleware("http")
    async def add_request_id_header(request: Request, call_next):
        request_id = str(uuid.uuid4())
        response = await call_next(request)
        response.headers["X-Request-Id"] = request_id
        return response

    @app.middleware("http")
    async def block_ip_middleware(request: Request, call_next):
        client_ip = request.client.host
        if client_ip in BLACK_LIST:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Access Denied")

        return await call_next(request)
