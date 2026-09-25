"""
CLI Runner for Job Discovery
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from packages.domain.database import SessionLocal, init_db
from apps.api.routers.connectors import trigger_discovery

if __name__ == "__main__":
    platform = sys.argv[1] if len(sys.argv) > 1 else "mock"
    print(f"Running discovery for connector: {platform}")
    init_db()
    db = SessionLocal()
    try:
        res = trigger_discovery(platform=platform, db=db)
        print(f"Discovery Result: {res}")
    finally:
        db.close()
