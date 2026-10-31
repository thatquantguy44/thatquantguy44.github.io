"""Frozen, deliberately bounded public-packet workflow; standard library only.

Supported grammar: sentence-delimited ``field_id: decimal [unit]`` records;
explicit ``label = arithmetic`` instructions using those fields; and one-hop
``1 UNIT = decimal UNIT`` currency conversion when conversion is requested.
Only explicitly stated final-over-draft or correction-over-original precedence
is recognized. Unsupported scope, prose synthesis, and arithmetic abstain.

This module has no filesystem, evaluator, provider, or network access. It never
branches on task IDs, answer IDs, known fixture values, or source IDs.
"""

import ast
import math
import re
from decimal import Decimal, InvalidOperation, localcontext


VERSION = "0.1.0"
NUMBER = r"[-+]?(?:\d+(?:\.\d*)?|\.\d+)"
RECORD = re.compile(
    rf"(?:^|[.;\n])\s*([a-z][a-z0-9_]*)\s*:\s*({NUMBER})\s*\[([a-z_]+)\]",
    re.I,
)
FX = re.compile(rf"\b1\s+([A-Z]{{3}})\s*=\s*({NUMBER})\s+([A-Z]{{3}})\b")
ALIASES = {"cost of goods sold": "cogs"}


class Unsupported(ValueError):
    """The frozen grammar cannot justify this answer."""


def _normalise(value):
    return re.sub(r"[^a-z0-9]", "", value.lower())


def _citations(sources):
    # Whole-source quotes preserve every input/rule span without reconstructing
    # or paraphrasing evidence. A human must still review their relevance.
    seen = set()
    result = []
    for source in sources:
        sid = source["source_id"]
        if sid not in seen:
            result.append({"source_id": sid, "quote": source["text"]})
            seen.add(sid)
    return result


def _json_number(value):
    if not value.is_finite():
        raise Unsupported("Non-finite arithmetic result")
    if abs(value) > Decimal("1e100"):
        raise Unsupported("Arithmetic magnitude exceeds frozen limit")
    if value == value.to_integral_value():
        return int(value)
    result = float(value)
    if not math.isfinite(result):
        raise Unsupported("Non-finite JSON conversion")
    return result


def _precedence(instructions, text):
    """Authority is applied only when a public instruction states the rule."""
    lower = text.lower()
    if re.search(r"final signed [a-z ]+ override drafts", instructions, re.I):
        if "final signed" in lower and "not final" not in lower:
            return 2
        if "draft" in lower:
            return 0
        raise Unsupported("Unknown authority under final-over-draft rule")
    if re.search(r"correction supersedes (?:the )?original", instructions, re.I):
        if "correction" in lower and "signed" in lower:
            return 2
        if "original" in lower:
            return 0
        raise Unsupported("Unknown authority under correction-over-original rule")
    return 1


def _select(field, records, task):
    available = [r for r in records if r[0] == field]
    if not available:
        raise Unsupported(f"No parseable record for {field}")
    ranked = [(_precedence(task["instructions"], r[3]["text"]), r) for r in available]
    best = max(rank for rank, _ in ranked)
    candidates = [record for rank, record in ranked if rank == best]
    if len({(r[1], r[2]) for r in candidates}) != 1:
        raise Unsupported(f"Conflicting authoritative records for {field}")
    # Same-value duplicates do not license omitting their provenance.
    return candidates[0][1], candidates[0][2], [r[3] for r in candidates]


def _rules(task):
    return [s for s in task["sources"] if not RECORD.search(s["text"])
            and re.search(r"\b(?:rule|supersed\w*|precedence)\b", s["text"], re.I)]


def _formulas(instructions):
    result = []
    # A decimal point followed by a digit is part of a numeric literal.
    for sentence in re.split(r"\.(?!\d)|[;\n]", instructions):
        if "=" not in sentence:
            continue
        label, expression = sentence.split("=", 1)
        for phrase, field in ALIASES.items():
            expression = re.sub(rf"\b{phrase}\b", field, expression, flags=re.I)
        result.append((_normalise(label), expression.strip()))
    return result


def _evaluate(expression, records, task):
    """Interpret a restricted arithmetic AST; never eval/exec source text."""
    if len(expression) > 512:
        raise Unsupported("Formula too long")
    try:
        tree = ast.parse(expression, mode="eval")
    except SyntaxError as exc:
        raise Unsupported("Unparseable explicit formula") from exc
    if len(list(ast.walk(tree))) > 64:
        raise Unsupported("Formula too complex")
    evidence = []

    def combine(left, right, sign):
        result = dict(left)
        for unit, exponent in right.items():
            result[unit] = result.get(unit, 0) + sign * exponent
        return {unit: exponent for unit, exponent in result.items() if exponent}

    def visit(node):
        if isinstance(node, ast.Expression):
            return visit(node.body)
        if isinstance(node, ast.Name):
            value, unit, sources = _select(node.id.lower(), records, task)
            evidence.extend(sources)
            return value, {unit: 1}
        if isinstance(node, ast.Constant) and type(node.value) in (int, float):
            # Preserve source decimal spelling, rather than the AST's float.
            return Decimal(ast.get_source_segment(expression, node)), {}
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
            value, dimensions = visit(node.operand)
            return (-value if isinstance(node.op, ast.USub) else value), dimensions
        if isinstance(node, ast.BinOp):
            (left, left_dims), (right, right_dims) = visit(node.left), visit(node.right)
            if isinstance(node.op, ast.Add):
                if left_dims != right_dims:
                    raise Unsupported("Addition requires matching dimensions")
                return left + right, left_dims
            if isinstance(node.op, ast.Sub):
                if left_dims != right_dims:
                    raise Unsupported("Subtraction requires matching dimensions")
                return left - right, left_dims
            if isinstance(node.op, ast.Mult):
                return left * right, combine(left_dims, right_dims, 1)
            if isinstance(node.op, ast.Div) and right != 0:
                return left / right, combine(left_dims, right_dims, -1)
        raise Unsupported("Unsupported arithmetic node or division by zero")

    value, dimensions = visit(tree)
    if dimensions:
        raise Unsupported("Percent formula must have dimensionless result")
    return value, dimensions, evidence


def _answer_question(task, question, records):
    wanted = question["unit"]
    qtext = question["question"].lower()
    aid = _normalise(question["answer_id"])
    for label, expression in _formulas(task["instructions"]):
        # Label matching is generic, not a list of known answer IDs.
        if label == aid or label == aid + _normalise(wanted):
            value, input_unit, sources = _evaluate(expression, records, task)
            # This initial grammar admits dimensionless explicit percent ratios
            # only. Other dimensional arithmetic requires a protocol amendment.
            if wanted != "percent" or "/" not in expression or not re.search(r"\*\s*100\b", expression):
                raise Unsupported("Formula result-unit rule is unsupported")
            return value, sources

    fields = {r[0] for r in records}
    exact = [f for f in fields if _normalise(f) == aid]
    matched = exact or [f for f in fields if re.search(
        r"\b" + r"[ _]".join(map(re.escape, f.split("_"))) + r"\b", qtext)]
    if len(matched) != 1:
        raise Unsupported("Question does not identify one supported field")
    value, unit, evidence = _select(matched[0], records, task)
    if unit != wanted:
        if not re.search(r"\bconvert\w*\b", task["instructions"], re.I):
            raise Unsupported("Unit conversion was not explicitly requested")
        options = []
        for source in task["sources"]:
            for source_unit, rate, target_unit in FX.findall(source["text"]):
                if source_unit == unit and target_unit == wanted:
                    options.append((Decimal(rate), source))
        if len(options) != 1 or options[0][0] <= 0:
            raise Unsupported("Missing or ambiguous one-hop conversion")
        value *= options[0][0]
        evidence.append(options[0][1])
    return value, evidence + _rules(task)


def execute_with_report(task):
    """Return (schema-valid answer, per-question coverage diagnostics).

    An abstention is deliberately not classified as correct here. Only the
    separate evaluator knows whether an unsupported answer ought to be null.
    """
    records = []
    for source in task["sources"]:
        for field, value, unit in RECORD.findall(source["text"]):
            records.append((field.lower(), Decimal(value), unit, source))
    answers, report = {}, {}
    # As-of/entity/tier selection needs a grammar the baseline does not yet have.
    complex_scope = bool(re.search(r"\bas of\b|tier defaults|account overrides", task["instructions"], re.I))
    for question in task["questions"]:
        aid = question["answer_id"]
        try:
            if question["value_type"] not in ("number", "number_or_null"):
                raise Unsupported("Prose/boolean synthesis is unsupported")
            if complex_scope:
                raise Unsupported("Dated/entity/tier scope is unsupported")
            with localcontext() as context:
                context.prec = 40
                value, evidence = _answer_question(task, question, records)
                number = _json_number(value)
            answers[aid] = {"value": number, "unit": question["unit"], "citations": _citations(evidence)}
            report[aid] = {"supported": True, "reason": None}
        except (Unsupported, InvalidOperation, OverflowError) as exc:
            answers[aid] = {"value": None, "unit": "unknown", "citations": []}
            report[aid] = {"supported": False, "reason": str(exc)}
    return {"task_id": task["task_id"], "answers": answers}, report


def execute(task):
    """Return the public answer schema; no evaluator state is consulted."""
    return execute_with_report(task)[0]
