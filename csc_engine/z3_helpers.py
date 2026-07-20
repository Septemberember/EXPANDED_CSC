"""
Z3 expression building and constraint solving helpers.

Converts Java-like boolean expressions into Z3 expressions, solves for
satisfying models, and adds value/range constraints to variable domains.
"""

import re
import ast
from z3 import *


def solver_check_z3(z3_expr, vars_types: dict = None) -> str:
    """Solve a Z3 expression and return a model string or 'OK' if UNSAT."""
    if vars_types is None:
        vars_types = {}
    try:
        solver = Solver()
        solver.set("timeout", 5000)
        solver.add(z3_expr)

        if solver.check() == sat:
            model = solver.model()
            model_str = "["
            for var_name, var_type in vars_types.items():
                if var_name == "return_value":
                    continue
                try:
                    if var_type in ["bool", "boolean"]:
                        z3_val = model.eval(Bool(var_name), model_completion=True)
                    elif var_type in ["int", "char"]:
                        z3_val = model.eval(BitVec(var_name, 32), model_completion=True)
                    elif var_type in ["float", "double"]:
                        z3_val = model.eval(Real(var_name), model_completion=True)
                    else:
                        continue

                    if var_type == "int":
                        var_value = str(z3_val.as_signed_long())
                    elif var_type == "char":
                        var_value = chr(z3_val.as_long() & 0x10FFFF)
                    elif var_type in ["bool", "boolean"]:
                        var_value = str(z3_val)
                    elif var_type in ["float", "double"]:
                        var_value = str(z3_val)
                    else:
                        var_value = str(z3_val)
                    model_str = model_str + f"{var_name}={var_value}, "
                except Exception:
                    model_str = model_str + f"{var_name}=ERROR, "
            model_str = model_str.rstrip(", ") + "]"
            return model_str
        else:
            return "OK"
    except Exception as e:
        print(f"solver_check_z3 error: {e}")
        raise


def parse_result(z3_result_str: str) -> dict:
    """Parse Z3 model string into dict of var_name -> value."""
    var_values_dict = {}
    z3_result_str = z3_result_str.strip("[").strip("]")
    if not z3_result_str:
        return var_values_dict
    var_values = z3_result_str.split(",")
    for var_value in var_values:
        tmp = var_value.split("=")
        if len(tmp) >= 2:
            var_values_dict[tmp[0].strip()] = tmp[1].strip()
    return var_values_dict


def replace_char_literals(expr):
    return re.sub(r"'(.)'", lambda m: str(ord(m.group(1))), expr)


def remove_float_suffix(expr):
    return re.sub(r'(\b-?\d+(?:\.\d+)?)[fF]\b', r'\1', expr)


def clean_empty_not(expr):
    expr = re.sub(r'!\s*\(\s*\)', 'True', expr)
    expr = re.sub(r'not\s*\(\s*\)', 'True', expr)
    return expr


def to_z3_val(val):
    if isinstance(val, int):
        return IntVal(val)
    if isinstance(val, float):
        return RealVal(val)
    return val


def remove_type_transfer_stmt_in_expr(expr: str) -> str:
    return expr.replace("(long)", "").replace("(int)", "").replace("(short)", "").replace("(byte)", "").replace("(char)", "")


def java_expr_to_z3(expr_str, var_types: dict):
    """Convert a Java-like boolean expression to a Z3 expression."""
    expr_str = expr_str.strip()
    expr_str = expr_str.lstrip()
    expr_str = " ".join(expr_str.splitlines())
    expr_str = remove_type_transfer_stmt_in_expr(expr_str)

    z3_vars = {}
    for name, vtype in var_types.items():
        if vtype in ('boolean', 'bool'):
            z3_vars[name] = Bool(name)
        elif vtype == 'int':
            z3_vars[name] = BitVec(name, 32)
        elif vtype == 'char':
            z3_vars[name] = BitVec(name, 32)
        elif vtype in ('float', 'double'):
            z3_vars[name] = Real(name)
        elif vtype == "void":
            continue
        elif any(kw in vtype for kw in ["List", "Map", "Set", "String", "Integer",
                                         "Float", "Double", "Boolean", "Object"]):
            continue
        else:
            raise ValueError(f"illegal type: {vtype}")

    expr_str = replace_char_literals(expr_str)
    expr_str = remove_float_suffix(expr_str)
    expr_str = clean_empty_not(expr_str)
    expr_str = expr_str.replace("true", "True").replace("false", "False")
    expr_str = expr_str.replace("&&", " and ").replace("||", " or ").replace("!", " not ")
    expr_str = expr_str.replace("not =", "!=")
    expr_str = expr_str.strip()

    class Z3Transformer(ast.NodeTransformer):
        def visit_Name(self, node):
            if node.id in z3_vars:
                return z3_vars[node.id]
            elif node.id in {"char", "int", "boolean", "float", "double"}:
                return ""
            else:
                raise ValueError(f"unknown vars: {node.id}")

        def visit_Constant(self, node):
            if isinstance(node.value, bool):
                return node.value
            elif isinstance(node.value, int):
                return BitVecVal(node.value, 32)
            elif isinstance(node.value, float):
                return RealVal(node.value)
            elif isinstance(node.value, str):
                if len(node.value) == 1:
                    return BitVecVal(ord(node.value), 32)
                return node.value
            else:
                raise ValueError(f"unacceptable type: {node.value}")

        def visit_BoolOp(self, node):
            values = [self.visit(v) for v in node.values]
            if isinstance(node.op, ast.And):
                return And(*values)
            elif isinstance(node.op, ast.Or):
                return Or(*values)
            else:
                raise ValueError(f"unacceptable operation of bool: {type(node.op)}")

        def visit_UnaryOp(self, node):
            if isinstance(node.op, ast.Not):
                if isinstance(node.operand, ast.Tuple):
                    return BoolVal(True)
                return Not(self.visit(node.operand))
            if isinstance(node.op, ast.USub):
                return -self.visit(node.operand)
            else:
                raise ValueError(f"unacceptable operation of UnaryOp: {type(node.op)}")

        def visit_Compare(self, node):
            left = self.visit(node.left)
            right = self.visit(node.comparators[0])
            op = node.ops[0]

            left = to_z3_val(left)
            right = to_z3_val(right)

            if (is_int_value(left) and is_real(right)) or (is_real(left) and is_int_value(right)):
                left = ToReal(left)
                right = ToReal(right)

            if isinstance(left, BitVecRef) and is_real(right):
                left = BV2Int(left, is_signed=False)
            if isinstance(right, BitVecRef) and is_real(left):
                right = BV2Int(right, is_signed=False)

            if isinstance(left, BitVecRef) and isinstance(right, IntNumRef):
                left = BV2Int(left, is_signed=False)
            if isinstance(right, BitVecRef) and isinstance(left, IntNumRef):
                right = BV2Int(right, is_signed=False)

            if is_bv(left) and is_bv(right):
                if left.size() == 16 and right.size() == 32:
                    left = SignExt(16, left)
                if right.size() == 16 and left.size() == 32:
                    right = SignExt(16, right)

            if isinstance(op, ast.Eq):
                return left == right
            elif isinstance(op, ast.NotEq):
                return left != right
            elif isinstance(op, ast.Gt):
                return left > right
            elif isinstance(op, ast.GtE):
                return left >= right
            elif isinstance(op, ast.Lt):
                return left < right
            elif isinstance(op, ast.LtE):
                return left <= right
            else:
                raise ValueError(f"illegal operator: {type(op)}")

        def visit_BinOp(self, node):
            left = self.visit(node.left)
            right = self.visit(node.right)
            op = node.op

            if isinstance(op, ast.Add):
                return left + right
            elif isinstance(op, ast.Sub):
                return left - right
            elif isinstance(op, ast.Mult):
                return left * right
            elif isinstance(op, ast.Div):
                return left / right
            elif isinstance(op, ast.Mod):
                return SRem(left, right)
            elif isinstance(op, ast.Pow):
                if isinstance(left, BitVecRef) and isinstance(right, BitVecRef):
                    left1 = BV2Int(left, is_signed=True)
                    right1 = BV2Int(right, is_signed=True)
                return Int2BV(left1 ** right1, 32)
            elif isinstance(op, ast.BitAnd):
                if not (isinstance(left, BitVecRef) and isinstance(right, BitVecRef)):
                    left = Int2BV(left, 32) if is_int(left) else left
                    right = Int2BV(right, 32) if is_int(right) else right
                return left & right
            elif isinstance(op, ast.BitOr):
                if not (isinstance(left, BitVecRef) and isinstance(right, BitVecRef)):
                    left = Int2BV(left, 32) if is_int(left) else left
                    right = Int2BV(right, 32) if is_int(right) else right
                return left | right
            elif isinstance(op, ast.BitXor):
                if not (isinstance(left, BitVecRef) and isinstance(right, BitVecRef)):
                    left = Int2BV(left, 32) if is_int(left) else left
                    right = Int2BV(right, 32) if is_int(right) else right
                return left ^ right
            else:
                raise ValueError(f"illegal operator: {type(op)}")

    try:
        parsed = ast.parse(expr_str, mode="eval")
    except Exception as e:
        print(f"ast.parse error: {e}, expr_str={repr(expr_str)}")
        raise

    z3_expr = Z3Transformer().visit(parsed.body)
    return z3_expr


def add_value_constraints(logic_expr: str, var_types: dict) -> str:
    """Add global bounds to int (-32768..32767) and char (32..126) variables."""
    value_constraints_expr = ""
    for var, vtype in var_types.items():
        if var == "return_value":
            continue
        if vtype == 'int':
            value_constraints_expr += f" && ({var} >= -32768 && {var} <= 32767)"
        elif vtype == 'char':
            value_constraints_expr += f" && ({var} >= 32 && {var} <= 126)"
    value_constraints_expr = value_constraints_expr.strip().strip("&&").strip()
    if len(value_constraints_expr) > 0:
        logic_expr = f"({logic_expr})" + f" && ({value_constraints_expr})"
    return logic_expr


def add_bounded_range_constraints(logic_expr: str, var_types: dict,
                                   bound: int = 200) -> str:
    """Add closed finite-domain constraints for supported integer-valued inputs."""
    range_constraints_expr = ""
    for var, vtype in var_types.items():
        if var == "return_value":
            continue
        if vtype == 'int':
            range_constraints_expr += f" && ({var} >= -{bound} && {var} <= {bound})"
        elif vtype == 'char':
            char_upper = min(bound, 65535)
            range_constraints_expr += f" && ({var} >= 0 && {var} <= {char_upper})"
    range_constraints_expr = range_constraints_expr.strip().strip("&&").strip()
    if len(range_constraints_expr) > 0:
        logic_expr = f"({logic_expr})" + f" && ({range_constraints_expr})"
    return logic_expr
