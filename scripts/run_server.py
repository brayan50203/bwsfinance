"""Production server runner for BWS Finance using Waitress.
Ensures database exists, seeds defaults, starts scheduler, then serves Flask app.
"""
from waitress import serve
import os
import sys
from pathlib import Path

# Allow importing app.py
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from app import app, init_db, seed_default_data  # noqa: E402

START_HOST = os.getenv('FLASK_HOST', '0.0.0.0')
START_PORT = int(os.getenv('FLASK_PORT', '5000'))


def run():
    db_path = BASE_DIR / app.config['DATABASE']
    if not db_path.exists():
        print('[INIT] Database not found. Creating and seeding...')
        init_db()
        seed_default_data()
    else:
        print('[INIT] Database exists:', db_path)

    # Ensure scheduler starts (import inside function to avoid circular refs at import time)
    try:
        from scheduler import start_scheduler
        start_scheduler()
        print('[SCHEDULER] Started successfully.')
    except Exception as e:
        print(f'[SCHEDULER] Failed to start: {e}')

    print('[WAITRESS] Serving BWS Finance...')
    print(f'[WAITRESS] Listening on http://{START_HOST}:{START_PORT}')
    # Thread pool size can be tuned later if needed
    serve(app, host=START_HOST, port=START_PORT, threads=8)


if __name__ == '__main__':
    run()
