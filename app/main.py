from fastapi import FastAPI
import os
import redis

app = FastAPI()

# Read environment variables set by Docker Compose
REDIS_HOST = os.getenv("REDIS_HOST", "cache")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

# Connect to Redis
r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

@app.get("/")
def read_root():
    try:
        # Increment visit counter in Redis
        visits = r.incr("visit_counter")
    except Exception as e:
        visits = f"Cache offline: {str(e)}"
    
    return {
        "status": "online",
        "message": "Orchestrated with Docker Compose!",
        "visit_count": visits
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}