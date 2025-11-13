# utils/tle_parser.py
import math
from typing import List, Tuple, Dict

def parse_tle(line1: str, line2: str) -> Dict:
    """
    Parse a single 2-line TLE pair (line1, line2) and return a dictionary
    of orbital parameters (numbers) similar to MATLAB tleread outputs.
    - Expects character positions per standard TLE format.
    """
    # sanitize
    l1 = line1.rstrip("\n")
    l2 = line2.rstrip("\n")

    satnum = l1[2:7].strip()

    # epoch
    epoch_year = int(l1[18:20])
    epoch_day = float(l1[20:32])

    if epoch_year < 57:
        epoch_year += 2000
    else:
        epoch_year += 1900

    # line2 fields by fixed columns (1-indexed spec -> convert to 0-index)
    inc = float(l2[8:16])                    # inclination (deg)
    raan = float(l2[17:25])                  # RAAN (deg)
    ecc = float("0." + l2[26:33].strip())    # eccentricity (no decimal in TLE)
    argp = float(l2[34:42])                  # argument of perigee (deg)
    mean_anom = float(l2[43:51])             # mean anomaly (deg)
    mean_motion = float(l2[52:63])           # revs per day

    # semi-major axis (km) from mean motion (revs/day)
    # n (rad/s) = mean_motion * 2*pi / 86400
    mu = 398600.4418
    n_rad_s = mean_motion * 2.0 * math.pi / 86400.0
    sma = (mu / (n_rad_s**2)) ** (1.0/3.0)

    # Build a TLE-like struct/dict for display
    tle_struct = {
        "satnum": satnum,
        "epoch_year": epoch_year,
        "epoch_day": epoch_day,
        "inclination": inc,
        "raan": raan,
        "eccentricity": ecc,
        "argp": argp,
        "mean_anom": mean_anom,
        "mean_motion_rev_per_day": mean_motion,
        "sma_km": sma
    }

    return tle_struct


def parse_tle_lines(text: str) -> List[Tuple[str, str, str]]:
    """
    Parse raw TLE text (may contain many TLEs).
    Returns list of (name, line1, line2). Name may be generated if not present.
    """
    lines = [ln.strip() for ln in text.splitlines() if ln.strip() != ""]
    sats = []
    i = 0
    while i < len(lines) - 1:
        # pattern: name + line1 + line2
        if (i + 2 < len(lines)) and lines[i+1].startswith("1 ") and lines[i+2].startswith("2 "):
            name = lines[i]
            l1 = lines[i+1]
            l2 = lines[i+2]
            i += 3
        # pattern: line1 + line2
        elif lines[i].startswith("1 ") and lines[i+1].startswith("2 "):
            name = f"SAT_{len(sats)+1}"
            l1 = lines[i]
            l2 = lines[i+1]
            i += 2
        else:
            i += 1
            continue
        sats.append((name, l1, l2))
    return sats


def parse_tle_file(path: str):
    with open(path, "r", encoding="utf-8") as f:
        txt = f.read()
    return parse_tle_lines(txt)
