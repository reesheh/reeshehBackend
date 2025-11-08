from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)