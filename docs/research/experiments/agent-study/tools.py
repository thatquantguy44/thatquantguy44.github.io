"""Shared, deterministic packet tools. Never opens files or executes source text."""

import ast
import re
from decimal import Decimal, DecimalException, localcontext


MAX_EXPRESSION_CHARS = 512
MAX_AST_NODES = 128
MAX_AST_DEPTH = 24
DECIMAL_PRECISION = 40
MAX_MAGNITUDE = Decimal("1e30")
MIN_MAGNITUDE = Decimal("1e-30")
_NUMBER = re.compile(r"(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[eE][+-]?[0-9]+)?\Z")


def tool_specs():
    """Return fresh JSON-compatible definitions shared by every model condition."""
    return [
        {"name": "read_source", "description": "Read one source from this public task only.",
         "parameters": {"type": "object", "properties": {"source_id": {"type": "string"}},
                        "required": ["source_id"], "additionalProperties": False}},
        {"name": "search_sources", "description": "Literal, case-sensitive line search in public sources; no regular expressions.",
         "parameters": {"type": "object", "properties": {"query": {"type": "string"},
                                                               "source_id": {"type": "string"}},
                        "required": ["query"], "additionalProperties": False}},
        {"name": "calculate", "description": "Decimal arithmetic with numeric literals, parentheses, +, -, *, and / only. Returns a decimal string; precision 40, nonzero magnitude 1e-30 through 1e30.",
         "parameters": {"type": "object", "properties": {"expression": {"type": "string"}},
                        "required": ["expression"], "additionalProperties": False}},
    ]


def _arguments(arguments, required, optional=()):
    if not isinstance(arguments, dict) or not set(required) <= set(arguments) or set(arguments) - set(required) - set(optional):
        raise ValueError("Invalid tool arguments")


def _text(value, name, limit):
    if not isinstance(value, str) or not value.strip() or len(value) > limit:
        raise ValueError(f"Invalid {name}")
    return value


def _sources(task):
    if not isinstance(task, dict) or not isinstance(task.get("sources"), list):
        raise ValueError("Invalid public source packet")
    sources = {}
    for source in task["sources"]:
        if not isinstance(source, dict):
            raise ValueError("Invalid public source")
        source_id = _text(source.get("source_id"), "source_id", 128)
        if source_id in sources or not isinstance(source.get("text"), str):
            raise ValueError("Duplicate source ID or invalid public source text")
        sources[source_id] = source["text"]
    return sources


def _bounded(value):
    if not value.is_finite() or abs(value) > MAX_MAGNITUDE or (value and abs(value) < MIN_MAGNITUDE):
        raise ValueError("Arithmetic magnitude outside supported range")
    return value


def _calculate(expression):
    expression = _text(expression, "expression", MAX_EXPRESSION_CHARS).strip()
    try:
        tree = ast.parse(expression, mode="eval")
        if sum(1 for _ in ast.walk(tree)) > MAX_AST_NODES:
            raise ValueError("Expression exceeds AST node limit")

        def visit(node, depth=0):
            if depth > MAX_AST_DEPTH:
                raise ValueError("Expression exceeds nesting limit")
            if isinstance(node, ast.Expression):
                return visit(node.body, depth + 1)
            if isinstance(node, ast.Constant) and type(node.value) in (int, float):
                raw = ast.get_source_segment(expression, node)
                if not raw or not _NUMBER.fullmatch(raw):
                    raise ValueError("Only decimal numeric literals are supported")
                return _bounded(Decimal(raw))
            if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
                value = visit(node.operand, depth + 1)
                return _bounded(value if isinstance(node.op, ast.UAdd) else -value)
            if isinstance(node, ast.BinOp) and isinstance(node.op, (ast.Add, ast.Sub, ast.Mult, ast.Div)):
                left, right = visit(node.left, depth + 1), visit(node.right, depth + 1)
                if isinstance(node.op, ast.Add):
                    value = left + right
                elif isinstance(node.op, ast.Sub):
                    value = left - right
                elif isinstance(node.op, ast.Mult):
                    value = left * right
                else:
                    value = left / right
                return _bounded(value)
            raise ValueError("Unsupported arithmetic syntax")

        with localcontext() as context:
            context.prec = DECIMAL_PRECISION
            value = visit(tree)
            result = format(value, "f")
            if "." in result:
                result = result.rstrip("0").rstrip(".")
            return "0" if not value else result
    except (SyntaxError, DecimalException, RecursionError, OverflowError) as exc:
        raise ValueError("Invalid or unsupported arithmetic expression") from exc


def execute_tool(task, name, arguments):
    """Execute against the supplied public packet; invalid requests raise ValueError."""
    if name == "calculate":
        _arguments(arguments, ("expression",))
        return {"result": _calculate(arguments["expression"])}
    if name == "read_source":
        _arguments(arguments, ("source_id",))
    elif name == "search_sources":
        _arguments(arguments, ("query",), ("source_id",))
        _text(arguments["query"], "query", 256)
    else:
        raise ValueError("Unknown tool name")
    sources = _sources(task)
    if "source_id" in arguments:
        source_id = _text(arguments["source_id"], "source_id", 128)
        if source_id not in sources:
            raise ValueError("Unknown public source ID")
        sources = {source_id: sources[source_id]}
    if name == "read_source":
        return {"source_id": source_id, "text": sources[source_id]}
    return {"matches": [{"source_id": source_id, "line_number": number, "text": line}
                        for source_id, text in sources.items()
                        for number, line in enumerate(text.splitlines(), 1)
                        if arguments["query"] in line]}
