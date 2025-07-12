#!/usr/bin/env python3
"""
Production database management script for benchHUB
Works with both local SQLite (dev) and Render PostgreSQL (production)
"""

import os
import sys
import argparse
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from benchHUB.api import BenchmarkResult, Base

def get_database_connection():
    """Get database connection from environment or fallback to local"""
    DATABASE_URL = os.environ.get("DATABASE_URL")
    
    if DATABASE_URL:
        print(f"🔗 Using production database: {DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else 'Render PostgreSQL'}")
        # Handle connection args for different database types
        connect_args = {}
    else:
        print("🔗 Using local SQLite database (development)")
        DATABASE_URL = "sqlite:///./leaderboard.db"
        connect_args = {"check_same_thread": False}
    
    engine = create_engine(DATABASE_URL, connect_args=connect_args)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return engine, SessionLocal

def show_database_stats(engine, session_factory):
    """Show current database statistics"""
    print("📈 Database Statistics:")
    print("-" * 50)
    
    with session_factory() as session:
        try:
            # Total count
            total = session.query(BenchmarkResult).count()
            print(f"Total results: {total}")
            
            if total == 0:
                print("ℹ️  Database is empty")
                return
            
            # By category with score ranges
            categories = session.execute(text("""
                SELECT 
                    config_name,
                    COUNT(*) as count,
                    MIN(reference_index) as min_score,
                    MAX(reference_index) as max_score,
                    AVG(reference_index) as avg_score
                FROM results 
                WHERE reference_index > 0
                GROUP BY config_name
                ORDER BY config_name
            """)).fetchall()
            
            print("\nBy configuration:")
            for row in categories:
                config, count, min_score, max_score, avg_score = row
                print(f"  {config or 'unknown'}: {count} results")
                print(f"    Range: {min_score:.1f} - {max_score:.1f} (avg: {avg_score:.1f})")
            
            # Score distribution
            print("\nScore distribution:")
            score_ranges = session.execute(text("""
                SELECT 
                    CASE 
                        WHEN reference_index = 0 THEN 'Zero scores'
                        WHEN reference_index < 100 THEN '< 100'
                        WHEN reference_index < 500 THEN '100-500'
                        WHEN reference_index < 1000 THEN '500-1000'
                        WHEN reference_index < 10000 THEN '1K-10K'
                        ELSE '> 10K'
                    END as range,
                    COUNT(*) as count
                FROM results
                GROUP BY 
                    CASE 
                        WHEN reference_index = 0 THEN 'Zero scores'
                        WHEN reference_index < 100 THEN '< 100'
                        WHEN reference_index < 500 THEN '100-500'
                        WHEN reference_index < 1000 THEN '500-1000'
                        WHEN reference_index < 10000 THEN '1K-10K'
                        ELSE '> 10K'
                    END
                ORDER BY count DESC
            """)).fetchall()
            
            for range_name, count in score_ranges:
                print(f"  {range_name}: {count} results")
                
        except Exception as e:
            print(f"❌ Error querying database: {e}")

def clear_all_scores(engine, session_factory):
    """Clear all benchmark results"""
    print("🗑️  Clearing all benchmark results...")
    
    with session_factory() as session:
        try:
            count = session.query(BenchmarkResult).count()
            print(f"Found {count} results to delete")
            
            if count > 0:
                print("⚠️  WARNING: This will delete ALL benchmark results from the production database!")
                confirm = input(f"Type 'DELETE ALL' to confirm deletion of {count} results: ")
                if confirm == 'DELETE ALL':
                    session.query(BenchmarkResult).delete()
                    session.commit()
                    print(f"✅ Deleted {count} results")
                else:
                    print("❌ Operation cancelled")
            else:
                print("ℹ️  Database is already empty")
                
        except Exception as e:
            print(f"❌ Error clearing database: {e}")

def clear_zero_scores(engine, session_factory):
    """Clear only zero/invalid scores"""
    print("🗑️  Clearing zero and invalid scores...")
    
    with session_factory() as session:
        try:
            count = session.query(BenchmarkResult).filter(
                BenchmarkResult.reference_index <= 0
            ).count()
            
            print(f"Found {count} zero/invalid scores to delete")
            
            if count > 0:
                confirm = input(f"Delete {count} zero/invalid scores? (yes/no): ")
                if confirm.lower() == 'yes':
                    session.query(BenchmarkResult).filter(
                        BenchmarkResult.reference_index <= 0
                    ).delete()
                    session.commit()
                    print(f"✅ Deleted {count} zero/invalid scores")
                else:
                    print("❌ Operation cancelled")
            else:
                print("ℹ️  No zero scores found")
                
        except Exception as e:
            print(f"❌ Error clearing zero scores: {e}")

def clear_high_scores(engine, session_factory, threshold=1000):
    """Clear scores above threshold (old scoring system)"""
    print(f"🗑️  Clearing scores above {threshold} (old scoring system)...")
    
    with session_factory() as session:
        try:
            count = session.query(BenchmarkResult).filter(
                BenchmarkResult.reference_index > threshold
            ).count()
            
            print(f"Found {count} high scores (>{threshold}) to delete")
            
            if count > 0:
                confirm = input(f"Delete {count} high scores from old scoring system? (yes/no): ")
                if confirm.lower() == 'yes':
                    session.query(BenchmarkResult).filter(
                        BenchmarkResult.reference_index > threshold
                    ).delete()
                    session.commit()
                    print(f"✅ Deleted {count} high scores")
                else:
                    print("❌ Operation cancelled")
            else:
                print(f"ℹ️  No scores above {threshold} found")
                
        except Exception as e:
            print(f"❌ Error clearing high scores: {e}")

def limit_scores_per_category(engine, session_factory, limit=2000):
    """Keep only top N scores per configuration"""
    print(f"📊 Limiting each category to top {limit} scores...")
    
    with session_factory() as session:
        try:
            # Get categories
            categories = session.execute(text(
                "SELECT DISTINCT config_name FROM results WHERE config_name IS NOT NULL"
            )).fetchall()
            
            total_deleted = 0
            
            for (category,) in categories:
                print(f"Processing category: {category}")
                
                # Count current results
                current_count = session.query(BenchmarkResult).filter(
                    BenchmarkResult.config_name == category
                ).count()
                
                if current_count <= limit:
                    print(f"  ✅ {category}: {current_count} results (within limit)")
                    continue
                
                # Get IDs to keep (top N by score)
                keep_ids = session.execute(text("""
                    SELECT id FROM results 
                    WHERE config_name = :category 
                    ORDER BY reference_index DESC 
                    LIMIT :limit
                """), {"category": category, "limit": limit}).fetchall()
                
                keep_ids = [row[0] for row in keep_ids]
                
                # Delete excess results
                deleted = session.execute(text("""
                    DELETE FROM results 
                    WHERE config_name = :category 
                    AND id NOT IN :keep_ids
                """), {"category": category, "keep_ids": tuple(keep_ids)})
                
                session.commit()
                deleted_count = deleted.rowcount
                total_deleted += deleted_count
                print(f"  🗑️  {category}: Deleted {deleted_count} results, kept top {limit}")
            
            print(f"✅ Total deleted: {total_deleted} results")
            
        except Exception as e:
            print(f"❌ Error limiting scores: {e}")

def main():
    parser = argparse.ArgumentParser(description="Manage benchHUB database")
    parser.add_argument('action', choices=[
        'stats', 'clear-all', 'clear-zero', 'clear-high', 'limit'
    ], help='Action to perform')
    parser.add_argument('--limit', type=int, default=2000,
                       help='Number of top scores to keep per category (default: 2000)')
    parser.add_argument('--threshold', type=int, default=1000,
                       help='Score threshold for clearing high scores (default: 1000)')
    
    args = parser.parse_args()
    
    try:
        engine, session_factory = get_database_connection()
        
        if args.action == 'stats':
            show_database_stats(engine, session_factory)
        elif args.action == 'clear-all':
            clear_all_scores(engine, session_factory)
        elif args.action == 'clear-zero':
            clear_zero_scores(engine, session_factory)
        elif args.action == 'clear-high':
            clear_high_scores(engine, session_factory, args.threshold)
        elif args.action == 'limit':
            limit_scores_per_category(engine, session_factory, args.limit)
            
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()