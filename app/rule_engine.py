import re
import ast
from dataclasses import dataclass, field
from app.diff_parser import ChangedLine


@dataclass
class Violation:
    rule: str
    severity: str
    filename: str
    line_number: int
    message: str


SECRET_PATTERNS: dict[str, str] = {
    "AWS Access Key": r"(?:A3T[A-Z0-9]|AKIA|AGPA|AIDA|AROA|AIPA|ANPA|ANVA|ASIA)[A-Z0-9]{16}",
    "Private Key Block": r"-----BEGIN (?:RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----",
    "GitHub Token": r"(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9_]{36,255}",
    "Stripe Secret Key": r"sk_live_[0-9a-zA-Z]{24,}",
    "Generic High-Entropy Secret": r"""(?i)(?:password|secret|api_key|apikey|token)\s*[=:]\s*["'][^\s"']{8,}["']""",
}


def scan_secrets(lines: list[ChangedLine]) -> list[Violation]:
    violations: list[Violation] = []
    for changed in lines:
        for rule_name, pattern in SECRET_PATTERNS.items():
            if re.search(pattern, changed.content):
                violations.append(Violation(
                    rule=rule_name,
                    severity="CRITICAL",
                    filename=changed.filename,
                    line_number=changed.line_number,
                    message=f"Potential {rule_name} detected in added code.",
                ))
    return violations


def check_python_syntax(lines: list[ChangedLine]) -> list[Violation]:
    files: dict[str, list[str]] = {}
    for changed in lines:
        if changed.filename.endswith(".py"):
            files.setdefault(changed.filename, []).append(changed.content)

    violations: list[Violation] = []
    for filename, code_lines in files.items():
        source = "\n".join(code_lines)
        try:
            ast.parse(source, filename=filename)
        except SyntaxError as exc:
            violations.append(Violation(
                rule="Python Syntax Error",
                severity="WARNING",
                filename=filename,
                line_number=exc.lineno or 1,
                message=f"SyntaxError: {exc.msg}",
            ))
    return violations


def run_all_rules(lines: list[ChangedLine]) -> list[Violation]:
    violations: list[Violation] = []
    violations.extend(scan_secrets(lines))
    violations.extend(check_python_syntax(lines))
    return violations
