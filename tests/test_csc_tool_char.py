from csc_tool import build_main_method, java_literal_for_type


def test_java_literal_for_char_from_solver_model():
    assert java_literal_for_type("Z", "char") == "'Z'"
    assert java_literal_for_type(0, "char") == "(char)0"
    assert java_literal_for_type("0", "char") == "(char)0"


def test_build_main_method_uses_char_variable_for_char_input():
    java_code = """
public class GetLowCaseLoop {
    public static char getLowCase(char c) {
        return c;
    }
}
"""

    main = build_main_method(java_code, "GetLowCaseLoop", {"c": "Z"})

    assert "char c = 'Z';" in main
    assert "char r = getLowCase(c);" in main
    assert "int c = Z;" not in main
    assert "getLowCase(Z)" not in main
