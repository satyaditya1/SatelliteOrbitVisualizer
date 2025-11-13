# utils/propagate.py
import numpy as np
import math
from typing import Tuple, List
from .anomalies import newtonm

MU = 398600.4418  # km^3/s^2

def mean_motion_revday_to_rad_s(mean_motion_rev_per_day: float) -> float:
    return mean_motion_rev_per_day * 2.0 * math.pi / 86400.0

def kepler_to_eci(a_km: float, e: float, inc_deg: float, raan_deg: float, argp_deg: float, nu_rad: float) -> Tuple[float, float, float]:
    """
    Convert orbital elements and true anomaly (nu in radians) to ECI position (km).
    Perifocal position: [r cos nu, r sin nu, 0]
    Rotate by Rz(raan) * Rx(inc) * Rz(argp)
    """
    inc = math.radians(inc_deg)
    raan = math.radians(raan_deg)
    argp = math.radians(argp_deg)
    r = a_km * (1 - e*math.cos(newtonm(e, 0)[0]))  # not used here; we'll compute r from nu
    # compute radius using standard formula
    p = a_km * (1 - e*e)
    r_km = p / (1.0 + e * math.cos(nu_rad))
    # perifocal coords
    x_pf = r_km * math.cos(nu_rad)
    y_pf = r_km * math.sin(nu_rad)
    z_pf = 0.0
    # rotation matrices
    # R = Rz(raan) * Rx(inc) * Rz(argp)
    cos_raan = math.cos(raan); sin_raan = math.sin(raan)
    cos_inc = math.cos(inc); sin_inc = math.sin(inc)
    cos_argp = math.cos(argp); sin_argp = math.sin(argp)
    # Combined rotation matrix elements
    R11 = cos_raan * cos_argp - sin_raan * sin_argp * cos_inc
    R12 = -cos_raan * sin_argp - sin_raan * cos_argp * cos_inc
    R13 = sin_raan * sin_inc
    R21 = sin_raan * cos_argp + cos_raan * sin_argp * cos_inc
    R22 = -sin_raan * sin_argp + cos_raan * cos_argp * cos_inc
    R23 = -cos_raan * sin_inc
    R31 = sin_argp * sin_inc
    R32 = cos_argp * sin_inc
    R33 = cos_inc
    # ECI coords
    x = R11 * x_pf + R12 * y_pf + R13 * z_pf
    y = R21 * x_pf + R22 * y_pf + R23 * z_pf
    z = R31 * x_pf + R32 * y_pf + R33 * z_pf
    return x, y, z

def propagate_kepler(a_km: float, e: float, inc_deg: float, raan_deg: float, argp_deg: float,
                     mean_anom_deg: float, mean_motion_rev_per_day: float,
                     times_seconds_from_epoch: List[float]) -> Tuple[List[float], List[float], List[float]]:
    """
    Propagate orbit at given times (seconds from epoch) using simple Keplerian motion.
    Returns lists of x,y,z coordinates (km).
    """
    n_rad_s = mean_motion_revday_to_rad_s(mean_motion_rev_per_day)
    # initial mean anomaly (radians)
    M0 = math.radians(mean_anom_deg)
    xs, ys, zs = [], [], []
    for dt in times_seconds_from_epoch:
        M = (M0 + n_rad_s * dt) % (2.0 * math.pi)
        E, nu = newtonm(e, M)
        x, y, z = kepler_to_eci(a_km, e, inc_deg, raan_deg, argp_deg, nu)
        xs.append(x); ys.append(y); zs.append(z)
    return xs, ys, zs
