# Import the FastAPI class from the fastapi package.
# FastAPI is the framework we are using to build our backend API.
from fastapi import FastAPI

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

# Create an instance of the FastAPI application.
#
# Think of "app" as our actual LifeOS backend application.
app = FastAPI(
    title="LifeOS API",
    version="0.1.0",
    description="Personal intelligence and decision system",

)



# ---------------------------------------------------------
# API ROUTES
# ---------------------------------------------------------

# Register the user router.
#
# This means:
#
# /users
#     ↓
# user_router
#
app.include_router(
    user_router,
    prefix="/api/v1",
)

# Register the task router.
#
# This makes the Task endpoints available under:
#
# /api/v1/tasks
#
app.include_router(
    task_router,
    prefix="/api/v1",
)


app.include_router(
    goal_router, 
    prefix="/api/v1"
)

app.include_router(
    habit_router,
    prefix="/api/v1",
)

app.include_router(
    project_router,
    prefix="/api/v1",
)

app.include_router(
    activity_router,
    prefix="/api/v1",
)

app.include_router(
    analytics_router,
    prefix="/api/v1",
)


app.include_router(
    context.router, 
    prefix="/api/v1")


app.include_router(
    intelligence.router,
    prefix="/api/v1",
)

app.include_router(
    recommendation.router,
    prefix="/api/v1",
)

# ---------------------------------------------------------
# ROOT ENDPOINT
# ---------------------------------------------------------
#
# This endpoint runs when someone visits:
#
# http://127.0.0.1:8000/
#
# @app.get("/") means:
# "When someone sends a GET request to /, run this function."
@app.get("/")
def root():
    # Return a Python dictionary.
    #
    # FastAPI automatically converts this dictionary
    # into JSON when sending it to the client.
    return {
        "message": "Welcome to LifeOS",
        "version": "0.1.0",
        "status": "running",
    }


# ---------------------------------------------------------
# HEALTH CHECK ENDPOINT
# ---------------------------------------------------------
#
# This endpoint will be useful later when we deploy LifeOS.
#
# URL:
# http://127.0.0.1:8000/health
#
# Other services can use this endpoint to check whether
# our backend is running correctly.
@app.get("/health")
def health_check():
    """
    Simple endpoint used to verify that the API is running.
    """
    return {
        "status": "healthy"
    }