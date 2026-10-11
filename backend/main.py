from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers.auth import router as auth_router, users_router
from routers.employee import router as employee_router
from routers.leave import router as leave_router
from routers.dashboard import router as dashboard_router

app = FastAPI(title="NovaPay ERP Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(employee_router, prefix="/api/employees", tags=["employees"])
app.include_router(leave_router, prefix="/api/leaves", tags=["leaves"])
app.include_router(dashboard_router)


@app.get("/health")
def health_check():
    return {"status": "ok"}