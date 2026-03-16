import traceback
from backend.db.pg_session import SessionLocal
from backend.services.analytics.engine import AnalyticsEngine

def main():
    print("--- START DEBUG ---")
    db = SessionLocal()
    try:
        engine = AnalyticsEngine(db)
        print("1. Fetching INFLATION for HTI...")
        series = engine.get_time_series('INFLATION', 'HTI')
        if not series:
            print("Series empty!")
            return
            
        print(f"2. Series length: {len(series)}")
        print(f"Sample: {series[0]}")
        
        print("3. Calculating stats...")
        stats = engine.calculate_stats(series)
        print(f"Done. Stats: {stats}")
    except Exception as e:
        print("CRASH DETAILS:")
        traceback.print_exc()
    finally:
        db.close()
        print("--- END DEBUG ---")

if __name__ == "__main__":
    main()
