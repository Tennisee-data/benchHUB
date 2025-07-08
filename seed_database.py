import os
import json
import uuid
from sqlalchemy import create_engine, Column, Integer, String, Float, Text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv
import glob

# Load environment variables from .env file
load_dotenv()

# --- Database Setup ---
DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("No DATABASE_URL environment variable set. Please set it in your .env file.")

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

# Create table if it doesn't exist
Base.metadata.create_all(bind=engine)

# --- Reference Index Calculation ---
CPU_WEIGHT = 0.4
GPU_WEIGHT = 0.4
MEMORY_WEIGHT = 0.2

def calculate_reference_index(cpu_score, gpu_score, memory_score):
    return (
        CPU_WEIGHT * cpu_score +
        GPU_WEIGHT * gpu_score +
        MEMORY_WEIGHT * memory_score
    )

def score_cpu(cpu_results):
    return 1.0 / cpu_results.get('floating_point', 1.0)

def score_gpu(gpu_results):
    return 1.0 / gpu_results.get('tensor_operations', 1.0)

def score_memory(memory_results):
    return 1.0 / memory_results.get('allocation', 1.0)


def seed_data():
    db = SessionLocal()
    
    json_files = glob.glob('results/benchmark_*.json')[:3]
    
    if not json_files:
        print("No benchmark JSON files found in the 'results/' directory.")
        return

    print(f"Found {len(json_files)} files to process.")

    for file_path in json_files:
        with open(file_path, 'r') as f:
            data = json.load(f)
            
            record_uuid = str(uuid.uuid4())
            
            existing_record = db.query(BenchmarkResult).filter_by(uuid=record_uuid).first()
            if existing_record:
                print(f"Record with UUID {record_uuid} already exists. Skipping.")
                continue

            cpu_score = score_cpu(data.get('cpu', {}))
            gpu_score = score_gpu(data.get('gpu', {}))
            memory_score = score_memory(data.get('memory', {}))
            
            reference_index = calculate_reference_index(cpu_score, gpu_score, memory_score)

            result = BenchmarkResult(
                system_info=json.dumps(data.get('system_info', {})),
                cpu=json.dumps(data.get('cpu', {})),
                memory=json.dumps(data.get('memory', {})),
                gpu=json.dumps(data.get('gpu', {})),
                disk=json.dumps(data.get('disk', {})),
                ml=json.dumps(data.get('ml', {})),
                plot=json.dumps(data.get('plot', {})),
                reference_index=reference_index,
                config_name=data.get('config_name', 'standard'),
                uuid=record_uuid
            )
            db.add(result)
            print(f"Adding record with UUID {record_uuid} from {file_path}")

    try:
        db.commit()
        print("Successfully committed new records to the database.")
    except Exception as e:
        db.rollback()
        print(f"An error occurred: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()