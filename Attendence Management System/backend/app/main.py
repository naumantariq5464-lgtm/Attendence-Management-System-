"""
FastAPI Application Entry Point.

- CORS middleware for frontend communication
- Static file serving for frontend
- Router registration (auth, admin, teacher, student)
- Health check endpoint
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import os

from app.routers import auth, admin, teacher, student
from app.database import engine, Base

# Create all database tables (development convenience)
# In production, use Alembic migrations instead
try:
    Base.metadata.create_all(bind=engine)
except Exception as e:
    print(f"Warning: Could not create tables on startup: {e}")

# ── APP INSTANCE ──

app = FastAPI(
    title="Attendance Management System",
    description="A role-based REST API for managing attendance with Admin, Teacher, and Student roles.",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS MIDDLEWARE ──
# Allow frontend to communicate with the API from any origin during development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],                  # In production: restrict to your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── REGISTER ROUTERS ──

app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(teacher.router)
app.include_router(student.router)

# ── SERVE FRONTEND STATIC FILES ──
# Mount the frontend directory so the API server also serves HTML/CSS/JS

frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "..", "frontend")
if os.path.exists(frontend_path):
    app.mount("/static", StaticFiles(directory=frontend_path), name="static")


# ── ROOT ENDPOINT ──
@app.get("/", tags=["General"])
def root():
    return {"message": "AMS API is running", "docs": "/docs"}

    
# ── HEALTH CHECK ──

@app.get("/health", tags=["General"])
def health_check():
    """Health check endpoint — useful for deployment monitoring."""
    return {
        "status": "healthy",
        "service": "Attendance Management System API",
        "version": "2.0.0",
    }
