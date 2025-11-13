# utils/time_utils.py
from datetime import datetime, timezone, timedelta
from typing import List

def parse_epoch(year: int, day_of_year: float) -> datetime:
    """
    Convert TLE epoch (year, day_of_year) to timezone-aware UTC datetime.
    """
    # year already expanded to YYYY in parser
    base = datetime(year, 1, 1, tzinfo=timezone.utc)
    return base + timedelta(days=day_of_year - 1)

def build_time_array(start_dt: datetime, numdays: int, sample_seconds: int):
    """
    Build a list of datetimes from start_dt to start_dt + numdays at given interval.
    """
    total_seconds = int(numdays * 24 * 3600)
    steps = max(2, total_seconds // sample_seconds + 1)
    return [start_dt + timedelta(seconds=i*sample_seconds) for i in range(steps)]
