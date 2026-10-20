# Import the FastAPI class from the fastapi package.
# FastAPI is the framework we are using to build our backend API.
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import API routers.
from app.api.routes.user import router as user_router
from app.api.routes.task import router as task_router
from app.api.routes.goal import router as goal_router
from app.api.routes.habit import router as habit_router
from app.api.routes.project import router as project_router
from app.api.routes.activity import router as activity_router
from app.api.routes.analytics import router as analytics_router
from app.api.routes import context
from app.api.routes import recommendation
from app.api.routes import intelligence


# ---------------------------------------------------------
# CREATE FASTAPI APPLICATION
# ---------------------------------------------------------

app = FastAPI(
    title="LifeOS API",
    version="0.1.0",
    description="Personal intelligence and decision system",
)


# ---------------------------------------------------------
# CORS CONFIGURATION
# ---------------------------------------------------------
#
# Allows the local React frontend to communicate with
# the FastAPI backend during development.
#
# Frontend: http://localhost:5173
# Backend:  http://localhost:8001
#

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------
# API ROUTES
# ---------------------------------------------------------

# User routes.
app.include_router(
    user_router,
    prefix="/api/v1",
)

# Task routes.
app.include_router(
    task_router,
    prefix="/api/v1",
)

# Goal routes.
app.include_router(
    goal_router,
    prefix="/api/v1",
)

# Habit routes.
app.include_router(
    habit_router,
    prefix="/api/v1",
)

# Project routes.
app.include_router(
    project_router,
    prefix="/api/v1",
)

# Activity routes.
app.include_router(
    activity_router,
    prefix="/api/v1",
)

# Analytics routes.
app.include_router(
    analytics_router,
    prefix="/api/v1",
)

# Context routes.
app.include_router(
    context.router,
    prefix="/api/v1",
)

# Intelligence routes.
app.include_router(
    intelligence.router,
    prefix="/api/v1",
)

# Recommendation routes.
app.include_router(
    recommendation.router,
    prefix="/api/v1",
)


# ---------------------------------------------------------
# ROOT ENDPOINT
# ---------------------------------------------------------
#
# URL: http://localhost:8001/
#
# Returns a welcome message when someone visits the API root.
#

@app.get("/")
def root():
    return {
        "message": "Welcome to LifeOS",
        "version": "0.1.0",
        "status": "running",
    }


# ---------------------------------------------------------
# HEALTH CHECK ENDPOINT
# ---------------------------------------------------------
#
# URL: http://localhost:8001/health
#
# Checks whether the API is running correctly.
#

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
    }