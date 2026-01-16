from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router
from core.model_loader import get_model
from data.grid_loader import get_grid_loader

# Create FastAPI app
app = FastAPI(
    title="Seoul Dimming Recommendation API",
    description="API for street lighting dimming recommendations based on ML models",
    version="1.0.0"
)

# Configure CORS to allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite dev server default
        "http://localhost:3000",  # Alternative port
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(router)


@app.on_event("startup")
async def startup_event():
    """Load model and data on startup."""
    print("=" * 50)
    print("Starting Seoul Dimming Recommendation API...")
    print("=" * 50)
    
    # Pre-load model
    try:
        model = get_model()
        print(f"✓ Model loaded successfully")
    except Exception as e:
        print(f"✗ Error loading model: {e}")
        raise
    
    # Pre-load grid data
    try:
        grid_loader = get_grid_loader()
        grid_loader.load_data()
        print(f"✓ Grid data loaded successfully")
    except Exception as e:
        print(f"✗ Error loading grid data: {e}")
        raise
    
    print("=" * 50)
    print("API is ready!")
    print("API Docs: http://localhost:8000/docs")
    print("=" * 50)


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    print("Shutting down API...")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
