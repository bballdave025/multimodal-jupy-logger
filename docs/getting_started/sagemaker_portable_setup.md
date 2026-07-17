# MMJL SageMaker Setup Instructions

This is the recommended drop-in setup for using Multimodal Jupy Logger
(MMJL) with existing AWS SageMaker course notebooks.

The setup keeps MMJL separate from the course workspace:

```text
~
├── multimodal-jupy-logger/
│   ├── requirements.txt
│   ├── requirements-ml.txt
│   ├── requirements-experimental-pdf.txt
│   ├── requirements-all-experimental.txt
│   └── src/
│       └── multimodal_jupy_logger/
│           ├── __init__.py
│           ├── environment_checks.py
│           ├── logger.py
│           ├── magics.py
│           ├── metadata.py
│           ├── jupy_pdf_utils.py
│           ├── mmjl_cli.py
│           └── utils/
│               ├── __init__.py
│               └── path_display.py
│
└── mlu-wjupy-lab/
    ├── some_course_notebook.ipynb
    └── jupy_log_<notebook_slug>/
```

The course notebook keeps its provisioned kernel. MMJL is added through
`sys.path`; the course environment does not need to be reconstructed.

## 1. Create the source tree

```bash
mkdir -p \
  ~/multimodal-jupy-logger/src/multimodal_jupy_logger/utils
```

Create and populate the transferred source files under that directory.

## 2. Open the actual course notebook

Keep the kernel already provisioned for the course unless there is a specific
reason to replace it.

MMJL is an addition to the course environment. The selected kernel must still
contain everything the lesson notebook needs.

## 3. Setup cell: locate MMJL and check the environment

For SageMaker, keep:

```python
USE_EXPLICIT_MMJL_SRC = False
```

For a Windows development checkout, set it to `True` and edit
`EXPLICIT_MMJL_SRC`.

```python
from pathlib import Path
import importlib
import sys

USE_EXPLICIT_MMJL_SRC = False

EXPLICIT_MMJL_SRC = Path(
    r"D:\David\my_repos_dwb\multimodal-jupy-logger\src"
)

starting_dir = Path.cwd().resolve()
candidate_src_paths = []

if USE_EXPLICIT_MMJL_SRC:
    candidate_src_paths.append(
        EXPLICIT_MMJL_SRC.expanduser().resolve()
    )
else:
    for candidate in [starting_dir, *starting_dir.parents]:
        candidate_src_paths.append(candidate / "src")
    ##endof:  for candidate in [...]

    candidate_src_paths.append(
        Path.home() / "multimodal-jupy-logger" / "src"
    )
##endof:  if USE_EXPLICIT_MMJL_SRC

mmjl_src = None

for candidate_src in candidate_src_paths:
    package_dir = (
        candidate_src
        / "multimodal_jupy_logger"
    )

    if package_dir.is_dir():
        mmjl_src = candidate_src
        break
    ##endof:  if package_dir.is_dir()
##endof:  for candidate_src in candidate_src_paths

if mmjl_src is None:
    checked_paths = "\n".join(
        f"  - {candidate}"
        for candidate in candidate_src_paths
    )

    raise RuntimeError(
        "Could not find MMJL source.\n"
        "Checked:\n"
        f"{checked_paths}"
    )
##endof:  if mmjl_src is None

if str(mmjl_src) not in sys.path:
    sys.path.insert(0, str(mmjl_src))
##endof:  if str(mmjl_src) not in sys.path

importlib.invalidate_caches()

from multimodal_jupy_logger import (
    print_environment_check,
)

REQUIRED_PACKAGES = {
    "IPython": "ipython",
    "matplotlib": "matplotlib",
}

OPTIONAL_NOTEBOOK_TRANSFORMS = {
    "nbformat": "nbformat",
    "nbconvert": "nbconvert",
    "traitlets": "traitlets",
}

OPTIONAL_INVESTIGATION_PACKAGES = {
    "numpy": "numpy",
    "pandas": "pandas",
    "sklearn": "scikit-learn",
    "torch": "torch",
    "tensorflow": "tensorflow",
}

environment_report = print_environment_check(
    required_packages=REQUIRED_PACKAGES,
    investigation_packages={
        **OPTIONAL_NOTEBOOK_TRANSFORMS,
        **OPTIONAL_INVESTIGATION_PACKAGES,
    },
    show_import_paths=False,
)

required_missing = environment_report[
    "required_missing"
]

if required_missing:
    install_text = " ".join(required_missing)

    raise RuntimeError(
        "Required packages are missing.\n\n"
        "Install into the active notebook kernel with:\n\n"
        f"  %pip install {install_text}\n\n"
        "Then restart the kernel and rerun this cell."
    )
##endof:  if required_missing

print()
print("[PASS] Required notebook environment is ready.")
print("MMJL source mode:", (
    "explicit"
    if USE_EXPLICIT_MMJL_SRC
    else "portable discovery"
))
print("MMJL source:", mmjl_src)
```

This report includes:

- Python executable;
- Python version;
- active IPython/kernel implementation;
- working directory;
- home directory;
- platform;
- relevant package availability and versions.

Edit the package maps for the work at hand. For example, move `torch` into
`REQUIRED_PACKAGES` when a notebook must use PyTorch.

## 4. Setup cell: choose a notebook slug and log policy

The slug must be visible in the notebook. It determines the log directory.

```python
from datetime import datetime
from pathlib import Path
import re
import shutil
import time

NOTEBOOK_SLUG = "mlu_jupyter_magics_l01"

USE_TIMESTAMP_IF_SLUG_EMPTY = True

ALLOW_DESTRUCTIVE_LOG_RESET = False

MARK_LOG_AS_DISPOSABLE = False

DESTRUCTIVE_RESET_DELAY_SECONDS = 7

DISPOSABLE_LOG_SENTINEL = (
    ".mmjl_disposable_smoke_test"
)


def normalize_notebook_slug(slug):
    normalized = slug.strip().lower()

    normalized = re.sub(
        r"[^a-z0-9._-]+",
        "_",
        normalized,
    )

    return normalized.strip("._-")
##endof:  normalize_notebook_slug(...)


requested_slug = normalize_notebook_slug(
    NOTEBOOK_SLUG
)

if requested_slug:
    notebook_slug = requested_slug
else:
    if not USE_TIMESTAMP_IF_SLUG_EMPTY:
        raise RuntimeError(
            "NOTEBOOK_SLUG is empty.\n"
            "Choose a descriptive slug before registering MMJL."
        )
    ##endof:  if not USE_TIMESTAMP_IF_SLUG_EMPTY

    notebook_slug = datetime.now().strftime(
        "unnamed_%Y-%m-%dT%H%M%S"
    )

    print("=" * 72)
    print("[WARNING] NOTEBOOK_SLUG was not chosen.")
    print("Using generated timestamp slug:")
    print(f"  {notebook_slug}")
    print()
    print(
        "For a meaningful long-lived log, stop now and "
        "choose a descriptive NOTEBOOK_SLUG."
    )
    print("=" * 72)
##endof:  if requested_slug

log_root = (
    Path.cwd()
    / f"jupy_log_{notebook_slug}"
)

manifest_path = log_root / "manifest.tsv"

sentinel_path = (
    log_root
    / DISPOSABLE_LOG_SENTINEL
)

print()
print("=" * 72)
print("MMJL LOG DIRECTORY")
print("=" * 72)
print("Notebook slug:")
print(f"  {notebook_slug}")
print()
print("Log root:")
print(f"  {log_root.resolve()}")
print()

if manifest_path.exists():
    print("[NOTICE] Existing MMJL manifest detected:")
    print(f"  {manifest_path.resolve()}")
    print()
    print("MMJL will continue appending to this log.")
    print(
        "For a separate record, change NOTEBOOK_SLUG "
        "before registration."
    )
elif log_root.exists():
    print("[NOTICE] The target directory already exists,")
    print("but no MMJL manifest was found:")
    print(f"  {log_root.resolve()}")
    print()
    print(
        "Review the directory before registering MMJL."
    )
else:
    print("No existing log directory was found.")
    print("A new MMJL log will be initialized.")
##endof:  if manifest_path.exists()

if ALLOW_DESTRUCTIVE_LOG_RESET:
    if not MARK_LOG_AS_DISPOSABLE:
        raise RuntimeError(
            "Destructive reset is enabled, but "
            "MARK_LOG_AS_DISPOSABLE is False."
        )
    ##endof:  if not MARK_LOG_AS_DISPOSABLE

    if log_root.exists():
        if not sentinel_path.is_file():
            raise RuntimeError(
                "Destructive reset refused.\n\n"
                "The target directory does not contain the "
                "MMJL disposable-log sentinel:\n\n"
                f"  {sentinel_path}\n\n"
                "MMJL will not delete a directory that it "
                "cannot verify as a disposable smoke-test log."
            )
        ##endof:  if not sentinel_path.is_file()

        print()
        print("=" * 72)
        print("[DESTRUCTIVE RESET ARMED]")
        print()
        print("Verified disposable smoke-test directory:")
        print(f"  {log_root.resolve()}")
        print()
        print(
            "Interrupt the kernel during the countdown "
            "to prevent deletion."
        )
        print("=" * 72)

        for seconds_remaining in range(
            DESTRUCTIVE_RESET_DELAY_SECONDS,
            0,
            -1,
        ):
            print(
                "\r"
                "Continuing unless the kernel is interrupted "
                f"in {seconds_remaining} second(s)...",
                end="",
                flush=True,
            )

            time.sleep(1)
        ##endof:  for seconds_remaining in range(...)

        print()
        print()
        print("Deleting verified disposable log directory:")
        print(f"  {log_root.resolve()}")

        shutil.rmtree(log_root)

        print("[DONE] Disposable log directory deleted.")
    ##endof:  if log_root.exists()
else:
    print()
    print(
        "Destructive log reset: disabled "
        "(recommended for real notebooks)"
    )
##endof:  if ALLOW_DESTRUCTIVE_LOG_RESET
```

Recommended real-notebook values:

```python
NOTEBOOK_SLUG = "descriptive_notebook_slug"
ALLOW_DESTRUCTIVE_LOG_RESET = False
MARK_LOG_AS_DISPOSABLE = False
```

Recommended smoke-test values:

```python
NOTEBOOK_SLUG = "portable_smoke_test"
ALLOW_DESTRUCTIVE_LOG_RESET = True
MARK_LOG_AS_DISPOSABLE = True
```

## 5. Setup cell: register MMJL

```python
from multimodal_jupy_logger import (
    register_jupy_logger,
)

register_jupy_logger(
    root=log_root,
)

if MARK_LOG_AS_DISPOSABLE:
    sentinel_path.write_text(
        (
            "This directory was created as a disposable "
            "MMJL smoke-test log.\n"
        ),
        encoding="utf-8",
    )

    print("[DONE] Disposable smoke-test sentinel written:")
    print(f"  {sentinel_path}")
##endof:  if MARK_LOG_AS_DISPOSABLE

print()
print("[DONE] MMJL registered.")
print("MMJL log root:")
print(f"  {log_root.resolve()}")
```

## 6. Record the environment report

The environment had to be checked before registration. Rerun the check once
under MMJL capture to create a compact, task-scoped environment record.

```python
%%jupy_capture --label environment-check --pin-output
environment_report = print_environment_check(
    required_packages=REQUIRED_PACKAGES,
    investigation_packages={
        **OPTIONAL_NOTEBOOK_TRANSFORMS,
        **OPTIONAL_INVESTIGATION_PACKAGES,
    },
    show_import_paths=False,
)
```

This is a focused alternative to filling the timeline with a complete
`pip freeze`.

## 7. Use MMJL

Quick note:

```python
%%jupy_log --mime text/markdown
### Question

Why does the dual basis appear naturally here?
```

Keep input and output:

```python
%%jupy_capture --label useful-example
print("Useful result")
```

Keep input only:

```python
%%jupy_capture --label setup-code --pin-input
value = 42
```

Keep output only:

```python
%%jupy_capture --label final-result --pin-output
value
```

Log an existing or high-resolution file:

```python
%jupy_file --label high-resolution-plot plot_300dpi.png
```

## 8. Finalize the session

```python
%jupy_save
%jupy_inspect
%jupy_validate
%jupy_markdown
%jupy_html
```

To stop using MMJL, stop adding MMJL magics to cells.

## 9. Zip and download the durable record

SageMaker course spaces may reset or discard the transferred MMJL source and
generated logs between visits.

Zip and download the complete notebook-specific log directory:

```bash
cd ~/mlu-wjupy-lab

zip -r \
  jupy_log_mlu_jupyter_magics_l01.zip \
  jupy_log_mlu_jupyter_magics_l01
```

Keep these together:

```text
jupy_log_<notebook_slug>/
├── artifacts/
├── staging/
├── timelines/
│   ├── timeline.html
│   └── timeline.md
└── manifest.tsv
```

Opening `timelines/timeline.html` after moving the complete log directory
should preserve linked artifacts through relative paths.

The goal is not to download the entire course environment. The log should be
sufficient for quick continuation and reconstruction.
