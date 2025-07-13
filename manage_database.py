#!/usr/bin/env python3
"""
Database management script for benchHUB
Provides tools to clean, reset, and maintain the leaderboard database
"""

import argparse
import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from benchHUB.api import BenchmarkResult, Base

def get_database_connection():
    """Get database connection based on environment"""
    DATABASE_URL = os.environ.get("DATABASE_URL")
    if not DATABASE_URL:
        print("Warning: No DATABASE_URL found, using local SQLite")
        DATABASE_URL = "sqlite:///./leaderboard.db"
    
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return engine, SessionLocal

def clear_all_scores(engine, session_factory):
    """Clear all benchmark results from the database"""
    print("🗑️  Clearing all benchmark results...")
    
    with session_factory() as session:
        count = session.query(BenchmarkResult).count()
        print(f"Found {count} results to delete")
        
        if count > 0:
            confirm = input(f"Are you sure you want to delete all {count} results? (yes/no): ")
            if confirm.lower() == 'yes':
                session.query(BenchmarkResult).delete()
                session.commit()
                print(f"✅ Deleted {count} results")
            else:
                print("❌ Operation cancelled")
        else:
            print("ℹ️  Database is already empty")

def limit_scores_per_category(engine, session_factory, limit=2000):
    """Keep only the top N scores per configuration category"""
    print(f"📊 Limiting each category to top {limit} scores...")
    
    with session_factory() as session:
        # Get all config categories
        categories = session.query(BenchmarkResult.config_name).distinct().all()
        categories = [cat[0] for cat in categories if cat[0]]
        
        total_deleted = 0
        
        for category in categories:
            print(f"Processing category: {category}")
            
            # Count current results in this category
            current_count = session.query(BenchmarkResult).filter(
                BenchmarkResult.config_name == category
            ).count()
            
            if current_count <= limit:
                print(f"  ✅ {category}: {current_count} results (within limit)")
                continue
            
            # Get IDs of results to keep (top N by reference_index)
            keep_ids = session.query(BenchmarkResult.id).filter(
                BenchmarkResult.config_name == category
            ).order_by(BenchmarkResult.reference_index.desc()).limit(limit).subquery()
            
            # Delete results not in the keep list
            deleted = session.query(BenchmarkResult).filter(
                BenchmarkResult.config_name == category,
                ~BenchmarkResult.id.in_(keep_ids)
            ).delete(synchronize_session=False)
            
            session.commit()
            total_deleted += deleted
            print(f"  🗑️  {category}: Deleted {deleted} results, kept top {limit}")
        
        print(f"✅ Total deleted: {total_deleted} results")

def show_database_stats(engine, session_factory):
    """Show current database statistics"""
    print("📈 Database Statistics:")
    print("-" * 40)
    
    with session_factory() as session:
        # Total count
        total = session.query(BenchmarkResult).count()
        print(f"Total results: {total}")
        
        # By category
        categories = session.query(BenchmarkResult.config_name).distinct().all()
        categories = [cat[0] for cat in categories if cat[0]]
        
        print("\nBy configuration:")
        for category in categories:
            name = category or "unknown"
            count = session.query(BenchmarkResult).filter(
                BenchmarkResult.config_name == name
            ).count()
            print(f"  {name}: {count} results")
        
        # Score ranges
        print("\nScore ranges:")
        for category in categories:
            name = category or "unknown"
            results = session.query(BenchmarkResult).filter(
                BenchmarkResult.config_name == name,
                BenchmarkResult.reference_index > 0
            ).all()
            
            if results:
                scores = [r.reference_index for r in results]
                print(f"  {name}: {min(scores):.1f} - {max(scores):.1f}")

def reset_database_schema(engine):
    """Reset the entire database schema (nuclear option)"""
    print("💥 NUCLEAR OPTION: Resetting entire database schema...")
    
    confirm = input("This will DELETE ALL DATA and recreate tables. Type 'RESET' to confirm: ")
    if confirm == 'RESET':
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        print("✅ Database schema reset complete")
    else:
        print("❌ Operation cancelled")

def main():
    parser = argparse.ArgumentParser(description="Manage benchHUB database")
    parser.add_argument('action', choices=[
        'stats', 'clear', 'limit', 'reset'
    ], help='Action to perform')
    parser.add_argument('--limit', type=int, default=2000, 
                       help='Number of top scores to keep per category (default: 2000)')
    
    args = parser.parse_args()
    
    try:
        engine, session_factory = get_database_connection()
        
        if args.action == 'stats':
            show_database_stats(engine, session_factory)
        elif args.action == 'clear':
            clear_all_scores(engine, session_factory)
        elif args.action == 'limit':
            limit_scores_per_category(engine, session_factory, args.limit)
        elif args.action == 'reset':
            reset_database_schema(engine)
            
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()