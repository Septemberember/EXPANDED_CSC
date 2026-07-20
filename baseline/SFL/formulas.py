"""Classic SFL suspiciousness formulas."""

from __future__ import annotations

import math
from typing import Callable

import numpy as np

from .spectrum import ProgramSpectrum

# Type alias for a per-formula scoring function.
# Takes the spectrum and returns a 1D numpy array of scores (one per entity).
FormulaFunc = Callable[[ProgramSpectrum], np.ndarray]


def _compute_counts(spectrum: ProgramSpectrum) -> tuple[np.ndarray, np.ndarray,
                                                          np.ndarray, np.ndarray]:
    """Compute the four SFL statistics for all entities.

    Returns:
        a_ef: shape (|entities|,) — executed AND failed
        a_ep: shape (|entities|,) — executed AND passed
        a_nf: shape (|entities|,) — NOT executed AND failed
        a_np: shape (|entities|,) — NOT executed AND passed
    """
    total_failed = spectrum.total_failed
    total_passed = spectrum.total_passed

    coverage = spectrum.coverage  # (|entities|, |tests|), bool
    results = spectrum.results    # (|tests|,), bool

    a_ef = np.sum(coverage & results[None, :], axis=1).astype(np.float64)
    a_ep = np.sum(coverage & ~results[None, :], axis=1).astype(np.float64)
    a_nf = total_failed - a_ef
    a_np = total_passed - a_ep

    return a_ef, a_ep, a_nf, a_np


def formula_ochiai(spectrum: ProgramSpectrum) -> np.ndarray:
    """Ochiai suspiciousness.

    score = a_ef / sqrt(total_failed * (a_ef + a_ep))

    Reference: Abreu, Zoeteweij, van Gemund (2007).
    """
    a_ef, a_ep, _, _ = _compute_counts(spectrum)
    total_exec = a_ef + a_ep
    denom = np.sqrt(spectrum.total_failed * total_exec)
    mask = denom > 0
    scores = np.zeros_like(a_ef)
    scores[mask] = a_ef[mask] / denom[mask]
    return scores


def formula_tarantula(spectrum: ProgramSpectrum) -> np.ndarray:
    """Tarantula suspiciousness.

    score = (a_ef / total_failed) / (a_ef/total_failed + a_ep/total_passed)

    Reference: Jones, Harrold (2005).
    """
    a_ef, a_ep, _, _ = _compute_counts(spectrum)
    total_f = spectrum.total_failed
    total_p = spectrum.total_passed

    fail_frac = np.zeros_like(a_ef)
    pass_frac = np.zeros_like(a_ep)

    if total_f > 0:
        fail_frac = a_ef / total_f
    if total_p > 0:
        pass_frac = a_ep / total_p

    denom = fail_frac + pass_frac
    mask = denom > 0
    scores = np.zeros_like(a_ef)
    scores[mask] = fail_frac[mask] / denom[mask]
    return scores


def formula_dstar(spectrum: ProgramSpectrum, exponent: float = 2.0) -> np.ndarray:
    """DStar (D*) suspiciousness.

    score = a_ef^e / (a_ep + a_nf)

    When a_ep + a_nf == 0 **and** a_ef > 0, the entity is executed by
    all failing tests and by no passing or non-executing-failing tests
    — extremely suspicious.  We assign a large sentinel value (1e6)
    rather than 0 so these entities dominate the ranking.

    Reference: Wong, Debroy, Gao, Li (2014). Default exponent e=2.
    """
    a_ef, a_ep, a_nf, _ = _compute_counts(spectrum)
    denom = a_ep + a_nf
    scores = np.zeros_like(a_ef)

    safe = denom > 0
    scores[safe] = np.power(a_ef[safe], exponent) / denom[safe]
    # a_ef > 0 with zero denominator → sentinel
    sentinel = (denom == 0) & (a_ef > 0)
    scores[sentinel] = 1e6
    return scores


def formula_barinel(spectrum: ProgramSpectrum) -> np.ndarray:
    """Barinel suspiciousness.

    score = 1 - a_ep / (a_ep + a_ef)

    Reference: Abreu, Zoeteweij, van Gemund (2009).
    """
    a_ef, a_ep, _, _ = _compute_counts(spectrum)
    total_exec = a_ef + a_ep
    mask = total_exec > 0
    scores = np.zeros_like(a_ef)
    scores[mask] = 1.0 - a_ep[mask] / total_exec[mask]
    return scores


def formula_op2(spectrum: ProgramSpectrum) -> np.ndarray:
    """Op2 suspiciousness.

    score = a_ef - a_ep / (total_passed + 1)

    Reference: Naish, Lee, Ramamohanarao (2011).
    """
    a_ef, a_ep, _, _ = _compute_counts(spectrum)
    total_p = spectrum.total_passed
    return a_ef - a_ep / (total_p + 1)


FORMULA_FUNCTIONS: dict[str, FormulaFunc] = {
    "ochiai": formula_ochiai,
    "tarantula": formula_tarantula,
    "dstar": formula_dstar,
    "barinel": formula_barinel,
    "op2": formula_op2,
}

FORMULA_NAMES: list[str] = list(FORMULA_FUNCTIONS.keys())


def compute_suspiciousness(spectrum: ProgramSpectrum,
                           formulas: list[str] | None = None) -> dict[str, np.ndarray]:
    """Compute suspiciousness scores for all (or selected) formulas.

    Args:
        spectrum: The program spectrum.
        formulas: Formula names to compute. Defaults to all.

    Returns:
        Mapping from formula name to 1D numpy array of scores (one per entity).
    """
    names = formulas or FORMULA_NAMES
    results: dict[str, np.ndarray] = {}
    for name in names:
        func = FORMULA_FUNCTIONS[name]
        results[name] = func(spectrum)
    return results
