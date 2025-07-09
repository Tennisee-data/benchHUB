# benchHUB/api.py
from fastapi import FastAPI, Depends, Request
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Float, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import json
import os
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

# Rate Limiter Setup
limiter = Limiter(key_func=get_remote_address, default_limits=["100/hour"])

# Database setup
DATABASE_URL = os.environ.get("DATABASE_URL") # Render will provide this
Base = declarative_base()
engine = create_engine(DATABASE_URL)
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

# Base.metadata.drop_all(bind=engine) # REMOVE THIS FOR PRODUCTION
Base.metadata.create_all(bind=engine)

# Pydantic models
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
    result = BenchmarkResult(
        system_info=json.dumps(payload.system_info),
        cpu=json.dumps(payload.cpu),
        memory=json.dumps(payload.memory),
        gpu=json.dumps(payload.gpu),
        disk=json.dumps(payload.disk),
        ml=json.dumps(payload.ml),
        plot=json.dumps(payload.plot),
        reference_index=payload.reference_index,
        config_name=payload.config_name,
        uuid=payload.uuid
    )
    db.add(result)
    db.commit()
    db.refresh(result)
    return {"message": "Result submitted successfully", "id": result.id}

@app.get("/api/leaderboard")
def get_leaderboard(db: Session = Depends(get_db)):
    results = db.query(BenchmarkResult).order_by(BenchmarkResult.reference_index.desc()).all()
    return results
