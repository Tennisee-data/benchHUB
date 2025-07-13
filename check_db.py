import os
import psycopg2

# Get database URL
db_url = os.environ['DATABASE_URL']
print(f"Using database: {db_url[:50]}...")

try:
    # Connect directly with psycopg2
    conn = psycopg2.connect(db_url)
    cur = conn.cursor()

    # Check stats
    print("\n=== Database Stats ===")
    cur.execute("SELECT config_name, COUNT(*) FROM results GROUP BY config_name;")
    for row in cur.fetchall():
        print(f"{row[0]}: {row[1]} results")

    print("\n=== Score Ranges ===")
    cur.execute("SELECT config_name, MIN(reference_index), MAX(reference_index) FROM results GROUP BY config_name;")
    for row in cur.fetchall():
        print(f"{row[0]}: {row[1]:.1f} - {row[2]:.1f}")

    conn.close()
    print("\n✅ Database check complete")

except Exception as e:
    print(f"Error: {e}")