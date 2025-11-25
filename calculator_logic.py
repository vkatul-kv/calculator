import ast
import operator as op

# Allowed operators for safe evaluation
ALLOWED_OPERATORS = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
    ast.USub: op.neg,
    ast.UAdd: op.pos,
    ast.Pow: op.pow,
    ast.Mod: op.mod,
}

def _eval_ast(node):
    """Recursively evaluate a limited safe AST (numbers and basic ops)."""
    if isinstance(node, ast.Constant):  # Python 3.8+ (Num removed in 3.14)
        if isinstance(node.value, (int, float)):
            return node.value
        raise ValueError("Unsupported constant")
    if isinstance(node, ast.UnaryOp) and type(node.op) in ALLOWED_OPERATORS:
        return ALLOWED_OPERATORS[type(node.op)](_eval_ast(node.operand))
    if isinstance(node, ast.BinOp) and type(node.op) in ALLOWED_OPERATORS:
        left = _eval_ast(node.left)
        right = _eval_ast(node.right)
        return ALLOWED_OPERATORS[type(node.op)](left, right)
    raise ValueError("Unsupported expression")

def safe_eval(expr: str):
    """Safely evaluate arithmetic expressions containing numbers and +-*/% and **."""
    parsed = ast.parse(expr, mode="eval")
    return _eval_ast(parsed.body)

class Calculator:
    def __init__(self):
        self.expression = ""
        self.history = []
        self.just_evaluated = False   # NEW FLAG

    def _last_is_operator(self):
        return bool(self.expression) and self.expression[-1] in "+-*/%"

    def add(self, value: str) -> str:
        v = str(value)

        # if last action was evaluate and user presses a digit, start fresh
        if self.just_evaluated and v.isdigit():
            self.expression = v
            self.just_evaluated = False
            return self.expression

        # if last action was evaluate and user presses an operator, continue chaining
        if self.just_evaluated and v in "+-*/%":
            self.just_evaluated = False
            self.expression += v
            return self.expression

        self.just_evaluated = False

        if v.isdigit():
            self.expression += v
            return self.expression

        if v == ".":
            if not self.expression or self.expression[-1] in "+-*/%":
                self.expression += "0."
                return self.expression
            last_op_index = -1
            for i in range(len(self.expression) - 1, -1, -1):
                if self.expression[i] in "+-*/%":
                    last_op_index = i
                    break
            last_number = self.expression[last_op_index + 1:]
            if "." not in last_number:
                self.expression += "."
            return self.expression

        if v in "+-*/%":
            if not self.expression:
                if v == "-":  # allow unary minus at start
                    self.expression = "-"
                return self.expression
            if self._last_is_operator():
                self.expression = self.expression[:-1] + v
            else:
                self.expression += v
            return self.expression

        return self.expression

    def backspace(self) -> str:
        if self.expression:
            self.expression = self.expression[:-1]
        return self.expression

    def clear(self) -> str:
        self.expression = ""
        self.just_evaluated = False
        return self.expression

    def _sanitize_expression(self, expr: str) -> str:
        """Remove trailing operators or dots to avoid SyntaxError."""
        while expr and (expr[-1] in "+-*/%." or expr.endswith("..")):
            expr = expr[:-1]
        return expr

    def evaluate(self) -> str:
        if not self.expression:
            return ""
        expr = self._sanitize_expression(self.expression)
        if not expr:
            self.expression = ""
            self.just_evaluated = False
            return "Error"
        try:
            result = safe_eval(expr)
            if isinstance(result, float) and result.is_integer():
                result = int(result)
            result_str = str(result)
            self.history.insert(0, (expr, result_str))
            self.expression = result_str
            self.just_evaluated = True   # mark that we just evaluated
            return result_str
        except ZeroDivisionError:
            self.expression = ""
            self.just_evaluated = False
            return "Error (division by zero)"
        except Exception:
            self.expression = ""
            self.just_evaluated = False
            return "Error"

    def get_history(self):
        return list(self.history)

    def clear_history(self):
        self.history = []
