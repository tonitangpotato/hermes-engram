#!/usr/bin/env python3
"""Engram CLI wrapper for Hermes Agent — add, recall, consolidate, stats."""
import sys
import json
import os

DB_PATH = os.environ.get("ENGRAM_DB", os.path.expanduser("~/.hermes/engram.db"))

def main():
    from engram import Memory
    mem = Memory(DB_PATH)

    if len(sys.argv) < 2:
        print("Usage: engram_cli.py <command> [args]")
        print("Commands: add, recall, consolidate, stats, detail")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "add":
        content = sys.argv[2] if len(sys.argv) > 2 else None
        if not content:
            print("Error: content required")
            sys.exit(1)
        mem_type = sys.argv[3] if len(sys.argv) > 3 else "semantic"
        importance = float(sys.argv[4]) if len(sys.argv) > 4 else 0.5
        result = mem.add(content, type=mem_type, importance=importance)
        print(f"Stored memory: {result}")

    elif cmd == "recall":
        query = sys.argv[2] if len(sys.argv) > 2 else ""
        limit = int(sys.argv[3]) if len(sys.argv) > 3 else 5
        results = mem.recall(query, limit=limit)
        if not results:
            print("No memories found.")
        for r in results:
            score = r.get("score", 0)
            mtype = r.get("memory_type", "?")
            content = r.get("content", "")
            mid = r.get("id", "")[:8]
            print(f"[{mtype}] (score: {score:.2f}) {content[:200]}")

    elif cmd == "consolidate":
        mem.consolidate()
        print("Consolidation complete.")

    elif cmd == "stats":
        stats = mem.stats()
        print(json.dumps(stats, indent=2, default=str))

    elif cmd == "detail":
        mid = sys.argv[2] if len(sys.argv) > 2 else None
        if not mid:
            print("Error: memory_id required")
            sys.exit(1)
        # Direct DB access for detail
        import sqlite3
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        row = conn.execute("SELECT * FROM memories WHERE id = ?", [mid]).fetchone()
        if row:
            print(json.dumps(dict(row), indent=2, default=str))
        else:
            print(f"Memory {mid} not found")
        conn.close()

    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)

if __name__ == "__main__":
    main()
