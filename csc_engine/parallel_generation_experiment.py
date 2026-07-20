"""Compatibility wrapper for the isolated RQ2 experiment package.

The implementation moved to :mod:`csc_experiments.parallel_generation` so the
experiment tooling is separated from the CSC engine.  Existing imports keep
working through this module.
"""

from csc_experiments.parallel_generation import *  # noqa: F401,F403
