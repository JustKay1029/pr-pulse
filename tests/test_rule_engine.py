from app.diff_parser import ChangedLine
from app.rule_engine import scan_secrets, check_python_syntax, run_all_rules


def test_t4_detect_aws_secret():
    lines = [
        ChangedLine(
            filename="config.py",
            line_number=14,
            content='AWS_KEY = "AKIAIOSFODNN7EXAMPLE"',
        )
    ]
    violations = scan_secrets(lines)
    rules_found = [v.rule for v in violations]
    assert "AWS Access Key" in rules_found
    assert any(v.severity == "CRITICAL" for v in violations)


def test_t5_detect_github_token():
    lines = [
        ChangedLine(
            filename="auth.py",
            line_number=20,
            content='TOKEN = "ghp_123456789012345678901234567890123456"',
        )
    ]
    violations = scan_secrets(lines)
    rules_found = [v.rule for v in violations]
    assert "GitHub Token" in rules_found
    assert any(v.severity == "CRITICAL" for v in violations)


def test_t6_detect_python_syntax_error():
    lines = [
        ChangedLine(filename="app/calc.py", line_number=1, content="def broken_function("),
    ]
    violations = check_python_syntax(lines)
    assert len(violations) == 1
    assert violations[0].rule == "Python Syntax Error"
    assert violations[0].severity == "WARNING"


def test_t10_clean_code_passes():
    lines = [
        ChangedLine(filename="app/good.py", line_number=1, content="def valid():"),
        ChangedLine(filename="app/good.py", line_number=2, content="    return 100"),
    ]
    violations = run_all_rules(lines)
    assert len(violations) == 0
