#!/usr/bin/env python3
"""
SkyPost - Email Backend Microservice
Main application entry point
"""

try:
    import uvloop
    UVLOOP_AVAILABLE = True
except ImportError:
    UVLOOP_AVAILABLE = False
    print("⚠️  uvloop not available, using default event loop")

from sanic import Sanic
from sanic.response import json
from sanic_cors import CORS

from config.settings import config
from app.utils.database import init_db, close_db
from app.routes import auth, mail, websocket

def create_app() -> Sanic:
    """Create and configure the Sanic application."""
    
    # Create Sanic app
    app = Sanic(config.APP_NAME)
    
    # Configure CORS
    CORS(app, origins=config.CORS_ORIGINS)
    
    # Register blueprints
    app.blueprint(auth.bp)
    app.blueprint(mail.bp)
    app.blueprint(websocket.bp)
    
    # Database event handlers
    @app.before_server_start
    async def setup_db(app, loop):
        """Initialize database connection before server starts."""
        try:
            await init_db()
            print("✅ Database connection initialized")
        except Exception as e:
            print(f"⚠️  Database connection failed: {str(e)}")
            print("🚀 Starting server without database (some features will be disabled)")
    
    @app.after_server_stop
    async def close_db_connection(app, loop):
        """Close database connection after server stops."""
        try:
            await close_db()
            print("✅ Database connection closed")
        except Exception as e:
            print(f"⚠️  Database close failed: {str(e)}")
    
    # Health check endpoint
    @app.get("/health")
    async def health_check(request):
        """Health check endpoint."""
        return json({"status": "healthy", "service": config.APP_NAME})
    
    # Global error handler
    @app.exception(Exception)
    async def handle_exception(request, exception):
        """Global exception handler."""
        if config.APP_DEBUG:
            print(f"❌ Error: {str(exception)}")
        
        return json({
            "error": "Internal server error",
            "message": str(exception) if config.APP_DEBUG else "Something went wrong"
        }, status=500)
    
    return app

def main():
    """Main application entry point."""
    # Set uvloop as the event loop policy if available
    if UVLOOP_AVAILABLE:
        import asyncio
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    
    app = create_app()
    
    print(f"🚀 Starting {config.APP_NAME} server...")
    print(f"📍 Server will be available at http://{config.APP_HOST}:{config.APP_PORT}")
    print(f"🔧 Debug mode: {config.APP_DEBUG}")
    
    # Run the application with single process in debug mode
    app.run(
        host=config.APP_HOST,
        port=config.APP_PORT,
        debug=config.APP_DEBUG,
        access_log=config.APP_DEBUG,
        single_process=True  # Fix for development mode
    )

if __name__ == "__main__":
    main()
