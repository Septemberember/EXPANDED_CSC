"""Program spectrum construction from instrumented trace files and TBFV results."""

from __future__ import annotations

import json
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

import numpy as np

# Import from CSC_EXPANDED project in both portable-kit and source-checkout
# layouts.
_ROOT = Path(__file__).resolve().parents[2]
_PROJECT_CANDIDATES = [
    _ROOT,
    _ROOT / "project" / "CSC_EXPANDED",
]
for _p in _PROJECT_CANDIDATES:
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from csc_engine.execution_trace import ExecutionEvent, parse_trace_jsonl  # noqa: E402


@dataclass
class ProgramSpectrum:
    """A program spectrum built from instrumented trace files and TBFV results.

    Attributes:
        entities: Ordered list of source line numbers (the "program entities").
        test_ids: Ordered list of test case identifiers.
        coverage: Boolean matrix of shape (|entities|, |tests|).
                  coverage[i, j] == True iff entity i was executed by test j.
        results: Boolean vector of shape (|tests|,).
                 results[j] == True iff test j failed.
        timings: Phase-level wall-clock timings in seconds.
        source_lines: Per-test set of executed lines, keyed by test_case_id.
    """

    entities: list[int]
    test_ids: list[str]
    coverage: np.ndarray
    results: np.ndarray
    timings: dict[str, float] = field(default_factory=dict)
    source_lines: dict[str, set[int]] = field(default_factory=dict)

    @property
    def n_entities(self) -> int:
        return len(self.entities)

    @property
    def n_tests(self) -> int:
        return len(self.test_ids)

    @property
    def total_failed(self) -> int:
        return int(np.sum(self.results))

    @property
    def total_passed(self) -> int:
        return self.n_tests - self.total_failed

    @property
    def coverage_ratio(self) -> float:
        if self.coverage.size == 0:
            return 0.0
        return float(np.sum(self.coverage)) / self.coverage.size


def build_spectrum(session_dir: str | Path,
                   tbfv_report_path: Optional[str | Path] = None) -> ProgramSpectrum:
    """Build a ProgramSpectrum from a CSC session directory.

    Args:
        session_dir: Path to the session directory, e.g.
                     csc_tmp/mut_loopselection_m4/LoopSelectionSortFive/
        tbfv_report_path: Optional explicit path to refined_tbfv_report.json.
                          If None, looked up under session_dir.

    Returns:
        A ProgramSpectrum ready for SFL formula computation.
    """
    t0 = time.perf_counter()
    session = Path(session_dir)

    # Phase 1a: Discover and read all trace files
    t1 = time.perf_counter()
    trace_files = discover_trace_files(session)
    source_lines: dict[str, set[int]] = {}
    for test_id, trace_path in sorted(trace_files.items()):
        lines = _extract_covered_lines(trace_path)
        if test_id in source_lines:
            source_lines[test_id] |= lines
        else:
            source_lines[test_id] = set(lines)
    t_discover = time.perf_counter() - t1

    # Phase 1b: Load TBFV pass/fail results
    t2 = time.perf_counter()
    tbfv = load_tbfv_results(session, tbfv_report_path)
    t_tbfv = time.perf_counter() - t2

    # Phase 1c: Build matrix — exclude tests whose TBFV result is all-skipped
    t3 = time.perf_counter()
    # Determine which tests to keep (have at least one pass or fail verdict)
    excluded_tests: set[str] = set()
    test_results: dict[str, bool] = {}
    for test_id in source_lines:
        result = _test_verdict(test_id, tbfv)
        if result is None:
            excluded_tests.add(test_id)
        else:
            test_results[test_id] = result

    all_test_ids = sorted(set(source_lines.keys()) - excluded_tests)
    all_lines = sorted(set().union(*(source_lines[t] for t in all_test_ids))) if all_test_ids else []

    entity_to_index = {line: idx for idx, line in enumerate(all_lines)}
    test_to_index = {tid: idx for idx, tid in enumerate(all_test_ids)}

    coverage = np.zeros((len(all_lines), len(all_test_ids)), dtype=bool)
    for test_id in all_test_ids:
        j = test_to_index[test_id]
        for line in source_lines[test_id]:
            i = entity_to_index[line]
            coverage[i, j] = True

    results = np.array(
        [test_results[tid] for tid in all_test_ids],
        dtype=bool,
    )
    t_build = time.perf_counter() - t3

    t_total = time.perf_counter() - t0

    return ProgramSpectrum(
        entities=all_lines,
        test_ids=all_test_ids,
        coverage=coverage,
        results=results,
        source_lines=source_lines,
        timings={
            "trace_discovery_s": round(t_discover, 4),
            "tbfv_load_s": round(t_tbfv, 4),
            "matrix_build_s": round(t_build, 4),
            "spectrum_total_s": round(t_total, 4),
        },
    )


def discover_trace_files(session_dir: Path) -> dict[str, str]:
    """Discover all trace.jsonl files under session_dir/traces/.

    Returns a mapping from test_case_id to trace file path. When multiple trace
    files exist for the same test_case_id (different rounds), the last one
    alphabetically by path is retained.
    """
    traces_dir = session_dir / "traces"
    if not traces_dir.is_dir():
        return {}

    mapping: dict[str, str] = {}
    for trace_path in sorted(traces_dir.rglob("trace.jsonl")):
        run_dir = trace_path.parent   # e.g. "bootstrap" or "b0"
        run_name = run_dir.name
        if run_name == "bootstrap":
            test_id = "bootstrap"
        elif run_dir.parent.name.startswith("round_"):
            round_str = run_dir.parent.name.replace("round_", "")
            if round_str.isdigit():
                test_id = f"tc_{int(round_str)}_{run_name}"
            else:
                test_id = f"tc_{run_name}"
        else:
            test_id = run_name
        mapping[test_id] = str(trace_path)
    return mapping


def load_tbfv_results(session_dir: Path,
                      report_path: Optional[str | Path] = None) -> dict[str, Any]:
    """Load the refined TBFV report from a session directory.

    Returns the full JSON report dict, or an empty dict if not found.
    """
    if report_path is not None:
        path = Path(report_path)
    else:
        path = session_dir / "refined_tbfv_report.json"
    if not path.is_file():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _extract_covered_lines(trace_path: str) -> set[int]:
    """Extract the set of source lines executed in a single trace file."""
    try:
        events = parse_trace_jsonl(trace_path)
    except Exception:
        return set()
    return {event.line for event in events if event.line > 0}


def _test_verdict(test_id: str, tbfv_report: dict[str, Any]) -> bool | None:
    """Return the TBFV verdict for a test case.

    Returns:
        True  — at least one FSF unit failed (definite failure).
        False — at least one FSF unit passed AND none failed (definite pass).
        None  — every FSF unit was skipped / unsupported / missing.
                Such tests carry no pass/fail signal and are excluded from the
                SFL spectrum.
    """
    results = tbfv_report.get("results", [])
    has_fail = False
    has_pass = False
    for entry in results:
        if entry.get("test_case_id") == test_id:
            status = entry.get("status", "")
            if status == "fail":
                has_fail = True
            elif status == "pass":
                has_pass = True
    if has_fail:
        return True
    if has_pass:
        return False
    return None
