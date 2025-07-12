# benchHUB/api.py
from fastapi import FastAPI, Depends, Request, HTTPException
from pydantic import BaseModel, field_validator
from sqlalchemy import create_engine, Column, Integer, String, Float, Text
from sqlalchemy.orm import sessionmaker, Session, declarative_base
import json
import os
import uvicorn
from datetime import datetime
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

# --- Test Configuration ---
IS_LOCAL_TEST = not os.environ.get("DATABASE_URL")
if IS_LOCAL_TEST:
    print("Running in local test mode with SQLite database.")
    DATABASE_URL = "sqlite:///./test.db"
else:
    DATABASE_URL = os.environ.get("DATABASE_URL")

# Rate Limiter Setup
limiter = Limiter(key_func=get_remote_address, default_limits=["100/hour"])

# Database setup
Base = declarative_base()
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if IS_LOCAL_TEST else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class BenchmarkResult(Base):
    __tablename__ = "results"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    system_info = Column(Text)
    cpu = Column(Text)
    memory = Column(Text)
    gpu = Column(Text)
    disk = Column(Text)
    ml = Column(Text)
    plot = Column(Text)
    reference_index = Column(Float)
    config_name = Column(Text, nullable=True)
    uuid = Column(String, unique=True, nullable=False)
    timestamp = Column(String, default=datetime.utcnow().isoformat)

# Create/update the table
Base.metadata.create_all(bind=engine)

# Pydantic models with validation
class BenchmarkPayload(BaseModel):
    system_info: dict
    cpu: dict
    memory: dict
    gpu: dict
    disk: dict
    ml: dict
    plot: dict
    reference_index: float
    config_name: str = "standard"
    uuid: str
    timestamp: str
    
    @field_validator('reference_index')
    @classmethod
    def validate_reference_index(cls, v):
        # Reject zero or negative scores to prevent fake submissions
        if v <= 0:
            raise ValueError('Reference index must be positive (> 0)')
        # Reject unrealistically high scores that could indicate manipulation
        if v > 10_000_000:
            raise ValueError('Reference index too high (> 10,000,000)')
        return v
    
    @field_validator('cpu', 'memory', 'gpu')
    @classmethod
    def validate_benchmark_data(cls, v, info):
        # Ensure benchmark dictionaries contain timing data
        if not isinstance(v, dict) or not v:
            raise ValueError(f'{info.field_name} benchmark data cannot be empty')
        
        # Check that values are realistic timing measurements (not negative, not too large)
        for key, timing in v.items():
            if not isinstance(timing, (int, float)):
                raise ValueError(f'{info.field_name}.{key} must be a number')
            if timing < 0:
                raise ValueError(f'{info.field_name}.{key} cannot be negative')
            if timing > 3600:  # 1 hour max for any single benchmark
                raise ValueError(f'{info.field_name}.{key} timing too large (> 1 hour)')
        
        return v

# FastAPI app
app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/api/submit")
@limiter.limit("10/hour")
def submit_result(request: Request, payload: BenchmarkPayload, db: Session = Depends(get_db)):
    # Server-side score verification to prevent manipulation
    try:
        from benchHUB.reference_index import calculate_reference_index, score_cpu, score_gpu, score_memory
        
        cpu_score = score_cpu(payload.cpu)
        gpu_score = score_gpu(payload.gpu)
        memory_score = score_memory(payload.memory)
        server_calculated_score = calculate_reference_index(cpu_score, gpu_score, memory_score)
        
        # Allow 5% tolerance for floating-point differences
        tolerance = 0.05
        if abs(payload.reference_index - server_calculated_score) / server_calculated_score > tolerance:
            raise HTTPException(
                status_code=422, 
                detail=f"Score mismatch: submitted {payload.reference_index:.0f}, calculated {server_calculated_score:.0f}"
            )
            
        # Use server-calculated score for data integrity
        verified_score = server_calculated_score
        
    except ImportError:
        # Fallback if reference_index module unavailable
        verified_score = payload.reference_index
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Score validation failed: {str(e)}")
    
    result = BenchmarkResult(
        system_info=json.dumps(payload.system_info),
        cpu=json.dumps(payload.cpu),
        memory=json.dumps(payload.memory),
        gpu=json.dumps(payload.gpu),
        disk=json.dumps(payload.disk),
        ml=json.dumps(payload.ml),
        plot=json.dumps(payload.plot),
        reference_index=verified_score,
        config_name=payload.config_name,
        uuid=payload.uuid,
        timestamp=payload.timestamp
    )
    db.add(result)
    db.commit()
    db.refresh(result)
    return {"message": "Result submitted successfully", "id": result.id}

@app.get("/api/leaderboard")
def get_leaderboard(db: Session = Depends(get_db)):
    results = db.query(BenchmarkResult).order_by(BenchmarkResult.reference_index.desc()).all()
    return results

if __name__ == "__main__":
    print("Starting Uvicorn server...")
    uvicorn.run(app, host="127.0.0.1", port=8000)
