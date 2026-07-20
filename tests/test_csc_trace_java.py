import os
import re
import subprocess
import textwrap
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from csc_engine import condition_results_from_trace, parse_trace_jsonl


def test_csc_trace_file_backend_and_short_circuit(tmp_path):
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    trace_src = os.path.join(
        project_root,
        "java_bridge",
        "src",
        "main",
        "java",
        "csc",
        "bridge",
        "CSCTrace.java",
    )
    classes_dir = tmp_path / "classes"
    classes_dir.mkdir()

    subprocess.run(
        ["javac", "-d", str(classes_dir), trace_src],
        check=True,
        capture_output=True,
        text=True,
    )

    smoke_src = tmp_path / "CSCTraceSmoke.java"
    smoke_src.write_text(
        textwrap.dedent(
            """
            import csc.bridge.CSCTrace;

            public class CSCTraceSmoke {
                static int calls = 0;

                static boolean skipped() {
                    calls++;
                    return false;
                }

                public static void main(String[] args) {
                    int x = CSCTrace.assignInt(3, "assign", "x", "2 + 3", 2 + 3);
                    boolean decision = CSCTrace.cond(4, "if", 1, "true", true)
                            || CSCTrace.cond(4, "if", 2, "skipped()", skipped());
                    int result = CSCTrace.retInt(5, "return_value", "x", x);
                    if (!decision || calls != 0 || result != 5) {
                        throw new RuntimeException("CSCTrace changed program semantics");
                    }
                }
            }
            """
        ),
        encoding="utf-8",
    )

    subprocess.run(
        ["javac", "-cp", str(classes_dir), "-d", str(classes_dir), str(smoke_src)],
        check=True,
        capture_output=True,
        text=True,
    )

    trace_path = tmp_path / "trace.jsonl"
    subprocess.run(
        [
            "java",
            f"-Dcsc.trace.file={trace_path}",
            "-cp",
            str(classes_dir),
            "CSCTraceSmoke",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    events = parse_trace_jsonl(trace_path)

    assert [event.type for event in events] == ["ASSIGN", "COND", "RETURN"]
    assert events[0].target == "x"
    assert events[0].rhs == "2 + 3"
    assert events[0].value == "5"
    assert events[1].expr == "true"
    assert events[1].value is True
    assert events[2].target == "return_value"
    assert all(event.expr != "skipped()" for event in events)


def test_instrumenter_wraps_conditions_without_breaking_short_circuit(tmp_path):
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    bridge_dir = os.path.join(project_root, "java_bridge")
    bridge_jar = os.path.join(
        bridge_dir,
        "target",
        "csc-bridge-0.1.0-jar-with-dependencies.jar",
    )
    bridge_classes = os.path.join(bridge_dir, "target", "classes")

    subprocess.run(
        ["mvn", "-q", "-f", os.path.join(bridge_dir, "pom.xml"), "package"],
        check=True,
        capture_output=True,
        text=True,
    )

    sample_src = tmp_path / "ShortCircuitSample.java"
    sample_src.write_text(
        textwrap.dedent(
            """
            public class ShortCircuitSample {
                static int calls = 0;

                static boolean skipped() {
                    calls++;
                    return false;
                }

                public static int run() {
                    if (true || skipped()) {
                        return calls;
                    }
                    return -1;
                }

                public static void main(String[] args) {
                    int result = run();
                    if (result != 0) {
                        throw new RuntimeException("short-circuit changed");
                    }
                }
            }
            """
        ),
        encoding="utf-8",
    )
    instrumented_src = tmp_path / "ShortCircuitSampleInstrumented.java"

    subprocess.run(
        ["java", "-jar", bridge_jar, str(sample_src), str(instrumented_src)],
        check=True,
        capture_output=True,
        text=True,
    )

    instrumented_code = instrumented_src.read_text(encoding="utf-8")
    assert "csc.bridge.CSCTrace.cond" in instrumented_code
    assert "true || csc.bridge.CSCTrace.cond" not in instrumented_code

    # The Java class is still named ShortCircuitSample, so compile from a file
    # with the matching name in a separate output directory.
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    runnable_src = run_dir / "ShortCircuitSample.java"
    runnable_src.write_text(instrumented_code, encoding="utf-8")

    subprocess.run(
        ["javac", "-cp", bridge_classes, "-d", str(run_dir), str(runnable_src)],
        check=True,
        capture_output=True,
        text=True,
    )

    trace_path = tmp_path / "instrumented-trace.jsonl"
    subprocess.run(
        [
            "java",
            f"-Dcsc.trace.file={trace_path}",
            "-cp",
            f"{run_dir}{os.pathsep}{bridge_classes}",
            "ShortCircuitSample",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    events = parse_trace_jsonl(trace_path)
    cond_events = [event for event in events if event.type == "COND"]
    assign_events = [event for event in events if event.type == "ASSIGN"]
    return_events = [event for event in events if event.type == "RETURN"]

    assert any(event.expr == "true" and event.value is True for event in cond_events)
    assert all(event.expr != "skipped()" for event in cond_events)
    assert any(event.target == "result" and event.rhs == "run()" for event in assign_events)
    assert any(event.target == "return_value" and event.rhs == "calls" for event in return_events)


def test_get_max_factor_records_atomic_conditions(tmp_path):
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    bridge_dir = os.path.join(project_root, "java_bridge")
    bridge_jar = os.path.join(
        bridge_dir,
        "target",
        "csc-bridge-0.1.0-jar-with-dependencies.jar",
    )
    bridge_classes = os.path.join(bridge_dir, "target", "classes")

    subprocess.run(
        ["mvn", "-q", "-f", os.path.join(bridge_dir, "pom.xml"), "package"],
        check=True,
        capture_output=True,
        text=True,
    )

    sample_src = tmp_path / "GetMaxFactor.java"
    sample_src.write_text(
        textwrap.dedent(
            """
            public class GetMaxFactor {
                public static int getMaxFactor(int n) {
                    if (n <= 1) {
                        return -1;
                    }
                    int i = n / 2;
                    while (i > 1) {
                        if (n % i == 0 && i != 500000) {
                            return i;
                        }
                        i = i - 1;
                    }
                    return 1;
                }

                public static void main(String[] args) {
                    getMaxFactor(Integer.parseInt(args[0]));
                }
            }
            """
        ),
        encoding="utf-8",
    )
    instrumented_src = tmp_path / "GetMaxFactorInstrumented.java"
    subprocess.run(
        ["java", "-jar", bridge_jar, str(sample_src), str(instrumented_src)],
        check=True,
        capture_output=True,
        text=True,
    )

    run_dir = tmp_path / "run"
    run_dir.mkdir()
    runnable_src = run_dir / "GetMaxFactor.java"
    runnable_src.write_text(instrumented_src.read_text(encoding="utf-8"), encoding="utf-8")
    subprocess.run(
        ["javac", "-cp", bridge_classes, "-d", str(run_dir), str(runnable_src)],
        check=True,
        capture_output=True,
        text=True,
    )

    def run_case(n):
        trace_path = tmp_path / f"trace-{n}.jsonl"
        subprocess.run(
            [
                "java",
                f"-Dcsc.trace.file={trace_path}",
                "-cp",
                f"{run_dir}{os.pathsep}{bridge_classes}",
                "GetMaxFactor",
                str(n),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        return [(event.expr, event.value) for event in parse_trace_jsonl(trace_path)
                if event.type == "COND"]

    assert run_case(6)[:4] == [
        ("n <= 1", False),
        ("i > 1", True),
        ("n % i == 0", True),
        ("i != 500000", True),
    ]
    assert run_case(5)[:4] == [
        ("n <= 1", False),
        ("i > 1", True),
        ("n % i == 0", False),
        ("i > 1", False),
    ]


def _build_bridge():
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    bridge_dir = os.path.join(project_root, "java_bridge")
    bridge_jar = os.path.join(
        bridge_dir,
        "target",
        "csc-bridge-0.1.0-jar-with-dependencies.jar",
    )
    bridge_classes = os.path.join(bridge_dir, "target", "classes")

    subprocess.run(
        ["mvn", "-q", "-f", os.path.join(bridge_dir, "pom.xml"), "package"],
        check=True,
        capture_output=True,
        text=True,
    )
    return bridge_jar, bridge_classes


def _instrument_compile_and_run(tmp_path, class_name, source_code, args):
    bridge_jar, bridge_classes = _build_bridge()
    source_path = tmp_path / f"{class_name}.java"
    source_path.write_text(textwrap.dedent(source_code), encoding="utf-8")
    instrumented_path = tmp_path / f"{class_name}Instrumented.java"

    subprocess.run(
        ["java", "-jar", bridge_jar, str(source_path), str(instrumented_path)],
        check=True,
        capture_output=True,
        text=True,
    )

    run_dir = tmp_path / "run"
    run_dir.mkdir()
    runnable_src = run_dir / f"{class_name}.java"
    instrumented_code = instrumented_path.read_text(encoding="utf-8")
    runnable_src.write_text(instrumented_code, encoding="utf-8")

    subprocess.run(
        ["javac", "-cp", bridge_classes, "-d", str(run_dir), str(runnable_src)],
        check=True,
        capture_output=True,
        text=True,
    )

    trace_path = tmp_path / "trace.jsonl"
    subprocess.run(
        [
            "java",
            f"-Dcsc.trace.file={trace_path}",
            "-cp",
            f"{run_dir}{os.pathsep}{bridge_classes}",
            class_name,
            *args,
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    return instrumented_code, parse_trace_jsonl(trace_path)


def _contains_standalone_var(expr, name):
    return re.search(rf"\b{re.escape(name)}\b", expr) is not None


def test_instrumenter_records_pre_instrumentation_source_lines(tmp_path):
    instrumented_code, events = _instrument_compile_and_run(
        tmp_path,
        "SourceLineSample",
        """public class SourceLineSample {
    public static int run(int x, int y) {
        int sum = x;
        if (y > 0) {
            sum = sum + 1;
        } else {
            sum = sum - 1;
        }
        return sum;
    }

    public static void main(String[] args) {
        int x = Integer.parseInt(args[0]);
        int y = Integer.parseInt(args[1]);
        run(x, y);
    }
}
""",
        ["1", "-1"],
    )

    assert 'CSCTrace.assignObject(3, "var_decl", "sum", "x", x)' in instrumented_code
    assert 'CSCTrace.cond(4, "if", 1, "y > 0", y > 0)' in instrumented_code
    assert 'CSCTrace.assignObject(7, "assign", "sum", "sum - 1", sum - 1)' in instrumented_code
    assert 'CSCTrace.retObject(9, "return_value", "sum", sum)' in instrumented_code

    observed = [
        (event.type, event.line, event.target or event.expr)
        for event in events
        if event.type in {"ASSIGN", "COND", "RETURN"}
    ]

    assert observed == [
        ("ASSIGN", 13, "x"),
        ("ASSIGN", 14, "y"),
        ("ASSIGN", 3, "sum"),
        ("COND", 4, "y > 0"),
        ("ASSIGN", 7, "sum"),
        ("RETURN", 9, "return_value"),
    ]


def test_instrumenter_records_simple_unary_and_compound_updates(tmp_path):
    instrumented_code, events = _instrument_compile_and_run(
        tmp_path,
        "TraceUpdateSample",
        """
        public class TraceUpdateSample {
            public static int run(int x) {
                int i = x;
                i++;
                i += 2;
                if (i > 3) {
                    x = x + 1;
                }

                int j = x;
                j--;
                j *= 3;
                if (j < 9) {
                    return j;
                }
                return -1;
            }

            public static void main(String[] args) {
                int arg = Integer.parseInt(args[0]);
                run(arg);
            }
        }
        """,
        ["1"],
    )

    assert "i = csc.bridge.CSCTrace.assignObject" in instrumented_code
    assert "j = csc.bridge.CSCTrace.assignObject" in instrumented_code

    assign_rhs = [event.rhs for event in events if event.type == "ASSIGN"]
    assert "i + 1" in assign_rhs
    assert "i + 2" in assign_rhs
    assert "j - 1" in assign_rhs
    assert "j * 3" in assign_rhs

    results = condition_results_from_trace(events)
    i_condition = next(result.condition for result in results
                       if result.condition.condition_string == "i > 3")
    j_condition = next(result.condition for result in results
                       if result.condition.condition_string == "j < 9")

    assert not _contains_standalone_var(i_condition.input_constraint, "i")
    assert "x" in i_condition.input_constraint
    assert not _contains_standalone_var(j_condition.input_constraint, "j")
    assert "x" in j_condition.input_constraint


def test_instrumenter_records_for_update_unary_assignments(tmp_path):
    _, events = _instrument_compile_and_run(
        tmp_path,
        "TraceForUpdateSample",
        """
        public class TraceForUpdateSample {
            public static int run(int x) {
                int i = x;
                for (; i < 3; i++) {
                }
                if (i >= 3) {
                    return i;
                }
                return -1;
            }

            public static void main(String[] args) {
                int arg = Integer.parseInt(args[0]);
                run(arg);
            }
        }
        """,
        ["1"],
    )

    update_events = [event for event in events
                     if event.type == "ASSIGN" and event.target == "i" and event.rhs == "i + 1"]
    assert len(update_events) == 2

    loop_conditions = [
        result.condition.input_constraint
        for result in condition_results_from_trace(events)
        if result.condition.condition_string == "i < 3"
    ]
    assert len(loop_conditions) == 3
    assert all(not _contains_standalone_var(condition, "i") for condition in loop_conditions)
    assert any("x" in condition and "+ 1" in condition for condition in loop_conditions)
