from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from supabase import create_client, Client
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="FastAPI", version="1.0.0")

# ⚠️ CRITICAL: Configure CORS to allow Next.js to call FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        os.getenv("NEXTJS_URL"), # FOR DEV
        os.getenv("NEXTJS_URL_PROD"), # FOR PROD
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🏥 Health check endpoint (test this first!)
@app.get("/")
async def root():
    return {
        "status": "ok",
        "message": "FastAPI is running!",
        "supabase_url": os.getenv("SUPABASE_URL", "not set"),
        "nextjs_url": os.getenv("NEXTJS_URL", "not set")
    }

# 🧪 Test endpoint (no auth needed yet)
@app.get("/api/test")
async def test():
    return {"message": "Test endpoint works!"}


# Create Supabase client
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("❌ Missing SUPABASE_URL or SUPABASE_SERVICE_KEY in .env")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.get("/")
async def root():
    return {
        "status": "ok",
        "message": "FastAPI is running!",
        "supabase_url": SUPABASE_URL
    }

# 🧪 Test Supabase connection
@app.get("/api/test-supabase")
async def test_supabase():
    try:
        # Try to query a simple table or just tests the connection
        # This will fail if credentials are wrong
        response = supabase.table("profiles").select("id", count="exact").limit(0).execute()
        
        return {
            "status": "ok",
            "message": "Supabase connection works!",
            "supabase_connected": True
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Supabase connection failed: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)