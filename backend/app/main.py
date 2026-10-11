from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import routers using absolute imports within the package
# from app.routers.auth import router as auth_router
from app.routers.user import router as user_router
from app.routers.employee import router as employee_router
from app.routers.leave import router as leave_router
from app.routers.expense import router as expense_router
from app.routers.dashboard import router as dashboard_router

app = FastAPI(title="NovaPay ERP Backend")

# CORS settings for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all routers
# auth routes handled by user_router
app.include_router(user_router, prefix="/api/users", tags=["users"])
app.include_router(employee_router, prefix="/api/employees", tags=["employees"])
app.include_router(leave_router, prefix="/api/leaves", tags=["leaves"])
app.include_router(expense_router, prefix="/api/expenses", tags=["expenses"])
app.include_router(dashboard_router, prefix="/api/dashboard", tags=["dashboard"])

@app.get("/health")
def health_check():
    return {"status": "ok"}
