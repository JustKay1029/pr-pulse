from app.diff_parser import parse_diff, ChangedLine


SAMPLE_DIFF = """diff --git a/app/main.py b/app/main.py
index e69de29..d95f3ad 100644
--- a/app/main.py
+++ b/app/main.py
@@ -10,3 +10,4 @@
 def existing_function():
-    return False
+    return True
+    extra_line = 42
"""

MULTI_FILE_DIFF = """diff --git a/file1.py b/file1.py
--- a/file1.py
+++ b/file1.py
@@ -1,2 +1,3 @@
-old_code()
+new_code()
diff --git a/file2.txt b/file2.txt
--- a/file2.txt
+++ b/file2.txt
@@ -5,2 +5,3 @@
+hello world
"""


def test_t7_parse_single_file_diff():
    lines = parse_diff(SAMPLE_DIFF)
    assert len(lines) == 2
    assert lines[0].filename == "app/main.py"
    assert lines[0].line_number == 11
    assert lines[0].content == "    return True"
    assert lines[1].line_number == 12
    assert lines[1].content == "    extra_line = 42"


def test_t8_parse_multiple_files():
    lines = parse_diff(MULTI_FILE_DIFF)
    assert len(lines) == 2
    assert lines[0].filename == "file1.py"
    assert lines[0].content == "new_code()"
    assert lines[1].filename == "file2.txt"
    assert lines[1].content == "hello world"


def test_t9_parse_empty_diff():
    lines = parse_diff("")
    assert lines == []
