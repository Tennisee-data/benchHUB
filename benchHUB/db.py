#db.py
"""
db.py

A minimal example of how to store and retrieve benchmark results
in a SQLite database. Adjust as needed for your own environment.
"""

import sqlite3
import json
from datetime import datetime
from typing import Dict, Any, List, Optional


class BenchmarkDB:
    """
    A small class to manage SQLite database operations for benchmark results.
    You can store results, retrieve them, or drop the table if needed.
    """

    def __init__(self, db_path: str = "benchmark_results.db"):
        """
        :param db_path: Path to the SQLite database file.
        """
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """
        Create the 'benchmarks' table if it doesn't exist yet.
        The table stores each component of the benchmark results as a JSON blob,
        plus a timestamp and optional notes.
        """
        query = """
        CREATE TABLE IF NOT EXISTS benchmarks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            system_info TEXT NOT NULL,
            cpu TEXT,
            memory TEXT,
            gpu TEXT,
            disk TEXT,
            ml TEXT,
            plot TEXT,
            notes TEXT
        )
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(query)
            conn.commit()

    def store_results(
        self,
        results: Dict[str, Any],
        notes: str = ""
    ) -> int:
        """
        Store a set of benchmark results in the database.

        :param results: Dictionary containing keys like
                        ['system_info', 'cpu', 'memory', 'gpu', 'disk', 'ml', 'plot'].
        :param notes:   Optional notes about the run (machine name, environment, etc.).
        :return:        The ID of the newly inserted record.
        """

        # Ensure required field "system_info" is present
        if "system_info" not in results:
            raise ValueError("Results must contain 'system_info' key.")

        # Prepare data
        now_str = datetime.utcnow().isoformat()
        system_info_json = json.dumps(results["system_info"]) if "system_info" in results else ""
        cpu_json = json.dumps(results.get("cpu", {}))
        memory_json = json.dumps(results.get("memory", {}))
        gpu_json = json.dumps(results.get("gpu", {}))
        disk_json = json.dumps(results.get("disk", {}))
        ml_json = json.dumps(results.get("ml", {}))
        plot_json = json.dumps(results.get("plot", {}))

        query = """
        INSERT INTO benchmarks (
            timestamp,
            system_info,
            cpu,
            memory,
            gpu,
            disk,
            ml,
            plot,
            notes
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(query, [
                now_str,
                system_info_json,
                cpu_json,
                memory_json,
                gpu_json,
                disk_json,
                ml_json,
                plot_json,
                notes
            ])
            conn.commit()
            return cursor.lastrowid

    def fetch_results(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Retrieve results from the database. By default returns all rows, unless
        'limit' is specified.

        :param limit: Maximum number of rows to fetch.
        :return: A list of dictionaries, each representing one row in 'benchmarks'.
        """
        query = "SELECT * FROM benchmarks ORDER BY id DESC"
        if limit:
            query += f" LIMIT {limit}"

        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(query).fetchall()

        results = []
        for row in rows:
            # Convert JSON fields back to Python objects
            results.append({
                "id": row["id"],
                "timestamp": row["timestamp"],
                "system_info": json.loads(row["system_info"]),
                "cpu": json.loads(row["cpu"]) if row["cpu"] else None,
                "memory": json.loads(row["memory"]) if row["memory"] else None,
                "gpu": json.loads(row["gpu"]) if row["gpu"] else None,
                "disk": json.loads(row["disk"]) if row["disk"] else None,
                "ml": json.loads(row["ml"]) if row["ml"] else None,
                "plot": json.loads(row["plot"]) if row["plot"] else None,
                "notes": row["notes"]
            })
        return results

    def drop_table(self):
        """
        Drop the 'benchmarks' table. Use with caution!
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DROP TABLE IF EXISTS benchmarks")
            conn.commit()
