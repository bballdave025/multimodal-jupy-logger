## Markdown cell

# MMJL portable smoke test

This notebook tests the drop-in `sys.path` setup, `register_jupy_logger(root=...)`,
quiet magic wrappers, pin-family behavior, relative manifest paths, relative
timeline links, validation, and HTML/Markdown export.

It is intended to run in:

- local JupyterLab
- VS Code notebooks
- AWS SageMaker Jupyter spaces

Expected source layouts:

- local repo: `./src/multimodal_jupy_logger`
- SageMaker/drop-in: `~/multimodal-jupy-logger/src`

## Code cell

```python
from pathlib import Path
import importlib
import os
import shutil
import sys

starting_dir = Path.cwd().resolve()

candidate_src_paths = []

for candidate in [starting_dir, *starting_dir.parents]:
    candidate_src_paths.append(candidate / "src")
##endof:  for candidate in [...]

candidate_src_paths.append(
    Path.home() / "multimodal-jupy-logger" / "src"
)

mmjl_src = None

for candidate_src in candidate_src_paths:
    if (candidate_src / "multimodal_jupy_logger").is_dir():
        mmjl_src = candidate_src
        break
    ##endof:  if (candidate_src / ...)
##endof:  for candidate_src in candidate_src_paths

if mmjl_src is None:
    raise RuntimeError(
        "Could not find MMJL source. Expected either a repo-local "
        "'src/multimodal_jupy_logger' or "
        "'~/multimodal-jupy-logger/src/multimodal_jupy_logger'."
    )
##endof:  if mmjl_src is None

if str(mmjl_src) not in sys.path:
    sys.path.insert(0, str(mmjl_src))
##endof:  if str(mmjl_src) not in sys.path

importlib.invalidate_caches()

print("starting_dir:", starting_dir)
print("mmjl_src:", mmjl_src)
print("python:", sys.executable)
```

## Code cell

```python
from pathlib import Path
import shutil

from multimodal_jupy_logger import (
    MultimodalJupyLogger,
    register_jupy_logger,
)

log_root = Path.cwd() / "jupy_log_smoke_test"

# Smoke test root is intentionally disposable.
if log_root.exists():
    shutil.rmtree(log_root)
##endof:  if log_root.exists()

register_jupy_logger(root=log_root)

print("MMJL log root:", log_root)
print("log root exists:", log_root.exists())
```

## Code cell

```python
%jupy_inspect
```

## Markdown cell

## Literal logging smoke test

Expected:

- no `WindowsPath(...)` display after the magic
- one `[DONE] Logged text: ...` status line
- a manifest row with a relative `artifacts/...` path

## Code cell

```python
%%jupy_log --label smoke-markdown-note --mime text/markdown
# Smoke Markdown note

This text was logged with `%%jupy_log`.

It should appear in the manifest and exported timelines.
```

## Markdown cell

## Pin family smoke tests

Expected:

- `--pin` logs input + stdout with an automatic label
- `--label NAME` with no pin option behaves like `--pin`
- `--pin-input` logs input only
- `--pin-output` logs output only

## Code cell

```python
%%jupy_capture --pin
pin_message = "pin captures input and output"
print(pin_message)
```

## Code cell

```python
%%jupy_capture --label named-pin-default
named_message = "label alone behaves like pin"
print(named_message)
```

## Code cell

```python
%%jupy_capture --label input-only-example --pin-input
quiet_value = sum([1, 2, 3, 4])
print("This output should show in Jupyter, but not be logged by --pin-input.")
```

## Code cell

```python
%%jupy_capture --label output-only-example --pin-output
output_only_value = 6 * 7
print("This output should be logged, but the input should not be logged.")
output_only_value
```

## Markdown cell

## Plot capture smoke test

Expected:

- stdout is logged
- Matplotlib display is logged as an image artifact
- timeline HTML/Markdown uses relative links to that image

## Code cell

```python
%%jupy_capture --label tiny-plot --pin
import matplotlib.pyplot as plt

xs = [0, 1, 2, 3, 4]
ys = [x * x for x in xs]

plt.figure(figsize=(5, 3))
plt.plot(xs, ys, marker="o")
plt.title("MMJL smoke test plot")
plt.xlabel("x")
plt.ylabel("x squared")
plt.grid(True)
plt.show()
```

## Markdown cell

## Exception capture smoke test

Expected:

- Jupyter shows an error
- MMJL logs the input and exception artifact
- continuing with later cells still works after manually running the next cell

Run this cell intentionally. The error is expected.

## Code cell

```python
%%jupy_capture --label expected-exception --pin
print("This cell intentionally raises an exception.")
raise ValueError("Expected MMJL smoke-test exception")
```

## Markdown cell

## Validate and export

Expected:

- `%jupy_validate` reports zero missing artifacts
- `%jupy_markdown` and `%jupy_html` create timeline files
- no `[]` or `WindowsPath(...)` appears as extra notebook output from the magic wrappers

## Code cell

```python
%jupy_inspect
%jupy_validate
%jupy_markdown
%jupy_html
```

## Code cell

```python
from pathlib import Path
import csv

manifest_path = log_root / "manifest.tsv"
timeline_md = log_root / "timelines" / "timeline.md"
timeline_html = log_root / "timelines" / "timeline.html"

print("manifest:", manifest_path)
print("timeline_md:", timeline_md)
print("timeline_html:", timeline_html)

assert manifest_path.exists()
assert timeline_md.exists()
assert timeline_html.exists()

rows = list(csv.DictReader(
    manifest_path.open("r", encoding="utf-8", newline=""),
    delimiter="\t",
))

print("manifest rows:", len(rows))

absolute_paths = [
    row["path"]
    for row in rows
    if Path(row["path"]).is_absolute()
]

print("absolute manifest paths:", absolute_paths)

assert not absolute_paths, "Manifest should use relative artifact paths."

md_text = timeline_md.read_text(encoding="utf-8")
html_text = timeline_html.read_text(encoding="utf-8")

assert "../artifacts/" in md_text or "../artifacts/" in html_text
assert str(log_root.resolve()) not in md_text
assert str(log_root.resolve()) not in html_text

print("[PASS] Portable relative-path smoke test passed.")
```

## Markdown cell

## Manual checks

After the test, inspect:

```text
jupy_log_smoke_test/
├── artifacts/
├── staging/
├── timelines/
│   ├── timeline.html
│   └── timeline.md
└── manifest.tsv
```

The manifest `path` column should contain paths like:

```text
artifacts/000001_..._smoke-markdown-note.md
```

The timeline files should link to artifacts with:

```text
../artifacts/...
```

