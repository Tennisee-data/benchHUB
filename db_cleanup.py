#!/usr/bin/env python3
"""
Simple database cleanup script for benchHUB
Handles score reset and database maintenance
"""

import sqlite3
import os
import sys

def get_database_path():
    """Get the database file path"""
    # Check for production database URL
    db_url = os.environ.get("DATABASE_URL")
    if db_url and not db_url.startswith("sqlite"):
        print("❌ This script only works with local SQLite databases")
        print("For production PostgreSQL, use the online admin tools")
        sys.exit(1)
    
    # Use local SQLite database
    return "leaderboard.db"

def show_stats():
    """Show current database statistics"""
    db_path = get_database_path()
    if not os.path.exists(db_path):
        print(f"❌ Database not found: {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("📈 Database Statistics:")
    print("-" * 40)
    
    # Total count
    cursor.execute("SELECT COUNT(*) FROM results")
    total = cursor.fetchone()[0]
    print(f"Total results: {total}")
    
    # By category
    cursor.execute("SELECT config_name, COUNT(*) FROM results GROUP BY config_name")
    categories = cursor.fetchall()
    
    print("\nBy configuration:")
    for name, count in categories:
        print(f"  {name or 'unknown'}: {count} results")
    
    # Score ranges
    print("\nScore ranges:")
    for name, _ in categories:
        cursor.execute("""
            SELECT MIN(reference_index), MAX(reference_index) 
            FROM results 
            WHERE config_name = ? AND reference_index > 0
        """, (name,))
        result = cursor.fetchone()
        if result[0] is not None:
            print(f"  {name or 'unknown'}: {result[0]:.1f} - {result[1]:.1f}")
    
    conn.close()

def clear_all():
    """Clear all benchmark results"""
    db_path = get_database_path()
    if not os.path.exists(db_path):
        print(f"❌ Database not found: {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM results")
    count = cursor.fetchone()[0]
    
    print(f"🗑️  Found {count} results to delete")
    
    if count > 0:
        confirm = input(f"Are you sure you want to delete all {count} results? (yes/no): ")
        if confirm.lower() == 'yes':
            cursor.execute("DELETE FROM results")
            conn.commit()
            print(f"✅ Deleted {count} results")
        else:
            print("❌ Operation cancelled")
    else:
        print("ℹ️  Database is already empty")
    
    conn.close()

def limit_per_category(limit=2000):
    """Keep only top N scores per category"""
    db_path = get_database_path()
    if not os.path.exists(db_path):
        print(f"❌ Database not found: {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print(f"📊 Limiting each category to top {limit} scores...")
    
    # Get categories
    cursor.execute("SELECT DISTINCT config_name FROM results")
    categories = [row[0] for row in cursor.fetchall()]
    
    total_deleted = 0
    
    for category in categories:
        print(f"Processing category: {category or 'unknown'}")
        
        # Count current results
        cursor.execute("SELECT COUNT(*) FROM results WHERE config_name = ?", (category,))
        current_count = cursor.fetchone()[0]
        
        if current_count <= limit:
            print(f"  ✅ {category or 'unknown'}: {current_count} results (within limit)")
            continue
        
        # Delete excess results (keep top N by reference_index)
        cursor.execute("""
            DELETE FROM results 
            WHERE config_name = ? 
            AND id NOT IN (
                SELECT id FROM results 
                WHERE config_name = ? 
                ORDER BY reference_index DESC 
                LIMIT ?
            )
        """, (category, category, limit))
        
        deleted = cursor.rowcount
        conn.commit()
        total_deleted += deleted
        print(f"  🗑️  {category or 'unknown'}: Deleted {deleted} results, kept top {limit}")
    
    print(f"✅ Total deleted: {total_deleted} results")
    conn.close()

def reset_schema():
    """Reset database schema (nuclear option)"""
    db_path = get_database_path()
    
    print("💥 NUCLEAR OPTION: Resetting entire database...")
    confirm = input("This will DELETE ALL DATA. Type 'RESET' to confirm: ")
    
    if confirm == 'RESET':
        if os.path.exists(db_path):
            os.remove(db_path)
        print(f"✅ Database {db_path} deleted")
        print("Run the API once to recreate the schema")
    else:
        print("❌ Operation cancelled")

def main():
    if len(sys.argv) < 2:
        print("Usage: python db_cleanup.py <action>")
        print("Actions: stats, clear, limit [N], reset")
        sys.exit(1)
    
    action = sys.argv[1]
    
    if action == 'stats':
        show_stats()
    elif action == 'clear':
        clear_all()
    elif action == 'limit':
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else 2000
        limit_per_category(limit)
    elif action == 'reset':
        reset_schema()
    else:
        print(f"❌ Unknown action: {action}")
        sys.exit(1)

if __name__ == "__main__":
    main()