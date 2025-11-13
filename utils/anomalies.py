# utils/anomalies.py
import math
from typing import Tuple

def newtonm(ecc: float, m: float) -> Tuple[float, float]:
    """
    Newton-Raphson to solve Kepler's equation and return (E, nu) in radians.
    ecc: eccentricity
    m: mean anomaly in radians
    returns: (E (eccentric anomaly), nu (true anomaly)) in radians
    Implements the algorithm similar to Vallado's newtonm.
    """
    numiter = 100
    small = 1e-8
    # hyperbolic
    if ecc > 1.0 + small:
        # hyperbolic not expected for TLE; simple fallback
        E = m / (ecc - 1.0)
        # compute true anomaly roughly
        nu = 2.0 * math.atan(math.sqrt((ecc + 1.0) / (ecc - 1.0)) * math.tanh(E/2.0))
        return E, nu

    # elliptical / circular
    # Initial guess
    E = m if ecc < 0.8 else math.pi
    for _ in range(numiter):
        f = E - ecc * math.sin(E) - m
        fp = 1 - ecc * math.cos(E)
        dE = f / fp
        E = E - dE
        if abs(dE) < 1e-12:
            break

    # true anomaly
    sinv = math.sqrt(1.0 - ecc*ecc) * math.sin(E) / (1.0 - ecc * math.cos(E))
    cosv = (math.cos(E) - ecc) / (1.0 - ecc * math.cos(E))
    nu = math.atan2(sinv, cosv)
    return E, nu


def solve_true_anomaly(ecc: float, M_deg: float) -> float:
    """
    Convenience: take mean anomaly in degrees, return true anomaly in degrees.
    """
    M = math.radians(M_deg) % (2.0*math.pi)
    _, nu = newtonm(ecc, M)
    # normalize same as MATLAB (-180,180]
    deg = math.degrees(nu)
    deg_wrapped = ((deg + 180.0) % 360.0) - 180.0
    return deg_wrapped
