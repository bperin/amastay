# app.py
import asyncio
import uvicorn
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from services.bedrock_service import BedrockService
from models.property_model import Property

from controllers.auth_controller import router as auth_router

# from controllers.property_controller import router as property_router  # Commented out to prevent conflicts
from controllers.webhook_controller import router as webhook_router
from controllers.health_controller import router as health_router
from controllers.model_controller import router as model_router
from controllers.booking_controller import router as booking_router
from controllers.guest_controller import router as guest_router
from controllers.manager_controller import router as manager_router
from controllers.user_controller import router as user_router
from controllers.team_controller import router as team_router
from controllers.admin.admin_controller import router as admin_router
from controllers.property_information_controller import router as property_information_router
from controllers.property_controller import router as property_router

# Create FastAPI app
app = FastAPI(title="Amastay API", description="Amastay API", version="0.3", docs_url="/swagger")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="Amastay API",
        version="0.1",
        summary="Property Management System API",
        description="API for managing properties, bookings, and guests",
        routes=app.routes,
    )

    # Add custom branding
    openapi_schema["info"]["x-logo"] = {"url": "https://amastay.ai/assets/logo.png"}  # Replace with your logo URL

    # Add security schemes
    openapi_schema["components"]["securitySchemes"] = {
        "bearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }

    # Apply security globally
    openapi_schema["security"] = [{"bearerAuth": []}]

    app.openapi_schema = openapi_schema
    return app.openapi_schema


@app.on_event("startup")
async def startup_event():
    setup_logging()

    try:
        # If BedrockService.initialize() is asynchronous, await it
        if asyncio.iscoroutinefunction(BedrockService.initialize):
            await BedrockService.initialize()
        else:
            BedrockService.initialize()
        logging.info("Bedrock service initialized successfully")
    except Exception as e:
        logging.error(f"Failed to initialize Bedrock service: {str(e)}")
        raise

    # Include routers
    app.include_router(auth_router, prefix="/api/v1/auth")
    app.include_router(property_router, prefix="/api/v1/properties")
    app.include_router(booking_router, prefix="/api/v1/bookings")
    app.include_router(guest_router, prefix="/api/v1/guests")
    app.include_router(health_router, prefix="/api/v1/health")
    app.include_router(webhook_router, prefix="/api/v1/webhooks")
    app.include_router(model_router, prefix="/api/v1/model")
    app.include_router(manager_router, prefix="/api/v1/managers")
    app.include_router(user_router, prefix="/api/v1/users")
    app.include_router(team_router, prefix="/api/v1/teams")
    app.include_router(admin_router, prefix="/api/v1/admin")
    app.include_router(property_information_router, prefix="/api/v1/property_information")

    # Override the default OpenAPI schema
    app.openapi = custom_openapi


@app.on_event("shutdown")
async def shutdown_event():
    """Close database connection on shutdown"""
    print("Shutting down...")


def setup_logging():
    """Configure logging with file and console handlers"""
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s",
    )
    file_handler = logging.FileHandler("app.log")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s"))
    logging.getLogger().addHandler(file_handler)


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=5001, reload=True, workers=2)
