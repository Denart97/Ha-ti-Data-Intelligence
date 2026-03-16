import traceback
from backend.db.pg_session import SessionLocal
from backend.services.analytics.engine import AnalyticsEngine

def test_engine():
    db = SessionLocal()
    try:
        engine = AnalyticsEngine(db)
        print("Testing get_time_series...")
        series = engine.get_time_series("INFLATION", "HTI")
        print(f"Series length: {len(series) if series else 0}")
        
        print("Testing calculate_stats...")
        stats = engine.calculate_stats(series)
        print("Stats ok")
    except Exception as e:
        print("--- ERROR CAUGHT ---")
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_engine()
