# MMJL First Smoke Test — Setup, Split Package, and Notebook Logging

**Date:** 2026-06-14  
**Project:** Multimodal Jupy Logger  
**Branch:** `initial-code-and-pdf-and-tee`  
**Purpose:** Record the setup and first successful smoke test of the split
MMJL package, command interface, and Jupyter magic workflow.

---

## 1. Goal of this test pass

The goal of this pass was not to finish the whole logger. The goal was to
confirm that the newly split package structure works well enough to support
basic notebook-driven logging.

The main questions were:

- Can the package be imported from the repo without a full build system?
- Can the command interface run?
- Can JupyterLab use the test kernel?
- Can the notebook register MMJL magics?
- Can `%%jupy_log` save a Markdown artifact?
- Can `%jupy_inspect` and `%jupy_validate` see the artifact?
- Can `%jupy_markdown` and `%jupy_html` produce timelines?

This was intentionally a lean-to test before larger PDF, animation, audio,
and notebook-capture work.

---

## 2. Package split completed

The early prototype was split into separate files:

```text
src/
  multimodal_jupy_logger/
    __init__.py
    metadata.py
    logger.py
    magics.py
    mmjl_cli.py
````

The design rule is:

```text
core methods do the work
magics call core methods
CLI calls core methods
tests call core methods
```

Current responsibilities:

```text
metadata.py
  timestamp and provenance/header helpers

logger.py
  core MultimodalJupyLogger engine
  MIME detection
  artifact logging
  manifest reading
  inspect/validate
  Markdown/HTML timeline export

magics.py
  thin Jupyter/IPython magic wrappers

mmjl_cli.py
  command interface usable from PowerShell/bash or Python imports

__init__.py
  public package interface
```

This keeps the notebook interface, command interface, and core engine from
becoming tangled.

---

## 3. Environment setup

A local virtual environment was created from the repo root.

```powershell
python -m venv .venv_test_mmjl
.\.venv_test_mmjl\Scripts\Activate.ps1

python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

A kernel was installed for JupyterLab:

```powershell
python -m ipykernel install --user `
  --name mmjl-test `
  --display-name "Python (MMJL Test)"
```

A frozen package list was also saved:

```powershell
pip freeze > reproducibility_windows_initial.txt
```

The venv Python was confirmed:

```powershell
python -c "import sys; print(sys.executable)"
```

Expected path shape:

```text
...\multimodal-jupy-logger\.venv_test_mmjl\Scripts\python.exe
```

---

## 4. Temporary import path setup

Because this project is still using a lean-to setup rather than an installed
package or `pyproject.toml`, the repo `src` directory was added to
`PYTHONPATH` for the current PowerShell session.

```powershell
$src_path = Join-Path (Get-Location) "src"
$path_sep = [System.IO.Path]::PathSeparator

if ($env:PYTHONPATH) {
  $env:PYTHONPATH = "$env:PYTHONPATH$path_sep$src_path"
} else {
  $env:PYTHONPATH = "$src_path"
}
```

Check:

```powershell
$env:PYTHONPATH
```

Expected path shape:

```text
C:\...\multimodal-jupy-logger\src
```

Note: on Windows, Python path entries use `;`. On Linux/macOS, they use `:`.
Using `[System.IO.Path]::PathSeparator` avoids hard-coding the separator.

---

## 5. Command interface checks

The package import was checked:

```powershell
python -c "from multimodal_jupy_logger import MultimodalJupyLogger; print(MultimodalJupyLogger)"
```

Expected output shape:

```text
<class 'multimodal_jupy_logger.logger.MultimodalJupyLogger'>
```

The command interface help was checked:

```powershell
python -m multimodal_jupy_logger.mmjl_cli --help
```

Available commands at this stage:

```text
html
markdown
log-file
inspect
validate
```

The first `inspect` and `validate` checks were run:

```powershell
python -m multimodal_jupy_logger.mmjl_cli inspect
python -m multimodal_jupy_logger.mmjl_cli validate
```

Expected early result:

```text
Rows: 0
Missing artifacts: 0
```

This confirms the command interface can create/read the default `jupy_log`
directory and manifest.

---

## 6. JupyterLab launch

JupyterLab was launched from the repo root with the venv active:

```powershell
jupyter lab
```

A blank notebook was created with this kernel:

```text
Python (MMJL Test)
```

The first notebook cell confirmed the repo root, `src` path, and active Python:

```python
import sys
from pathlib import Path

repo_root = Path.cwd()
src_path = repo_root / "src"

if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))
##endof:  if str(src_path) not in sys.path

print("repo_root:", repo_root)
print("src_path:", src_path)
print("python:", sys.executable)
```

Expected result:

```text
repo_root: C:\...\multimodal-jupy-logger
src_path: C:\...\multimodal-jupy-logger\src
python: C:\...\multimodal-jupy-logger\.venv_test_mmjl\Scripts\python.exe
```

---

## 7. Logger import and magic registration

The package was imported in the notebook:

```python
from multimodal_jupy_logger import (
    MultimodalJupyLogger,
    register_jupy_logger,
    jupy_logger_register,
)

logger = MultimodalJupyLogger(root="mmjl_test_log")
logger.inspect_manifest()
```

This confirmed a manually created logger instance worked.

Then the Jupyter magics were registered:

```python
register_jupy_logger()
```

Expected output:

```text
[DONE] Registered: %jupy_save, %jupy_file, %%jupy_log, %jupy_markdown,
%jupy_html, %jupy_inspect, %jupy_validate
```

Note: the manual `logger` instance above used `mmjl_test_log`, while the
registered magics currently use their own default root, `jupy_log`. That is
acceptable for the smoke test. Later work should add either:

```text
register_jupy_logger(root="...")
```

or:

```text
%jupy_root ...
```

---

## 8. First magic logging test

The first logged notebook artifact was a Markdown note using HTML
`details/summary`.

```python
%%jupy_log --label details-summary-tip --mime text/markdown
<details>
<summary>Click to see something hidden</summary>

Here is something hidden.

</details>
```

The artifact was written to:

```text
jupy_log/artifacts/
```

The filename included a timestamp and the label:

```text
..._details-summary-tip.md
```

This confirmed that `%%jupy_log` can log literal cell text without executing
it.

---

## 9. Inspect, validate, and export from notebook

The manifest was inspected and validated from notebook magics:

```python
%jupy_inspect
print("\n-----\n")
%jupy_validate
```

Expected result:

```text
Rows: 1

By kind:
  text: 1

By MIME:
  text/markdown: 1

Missing artifacts: 0
```

Then Markdown and HTML timelines were exported:

```python
%jupy_markdown
%jupy_html
```

Expected files:

```text
jupy_log/timeline.md
jupy_log/timeline.html
```

This confirmed the basic notebook-driven path:

```text
Jupyter cell
  -> %%jupy_log
  -> artifact file
  -> manifest row
  -> inspect/validate
  -> Markdown timeline
  -> HTML timeline
```

---

## 10. First smoke-test checklist

Completed:

* [x] Branch ready
* [x] Repo working tree initially clean
* [x] Package directory renamed/split
* [x] `metadata.py` created
* [x] `logger.py` created
* [x] `magics.py` created
* [x] `mmjl_cli.py` created
* [x] `__init__.py` created
* [x] `requirements.txt` created
* [x] venv created
* [x] requirements installed
* [x] Jupyter kernel installed
* [x] package import works from PowerShell
* [x] command interface help works
* [x] command interface `inspect` works
* [x] command interface `validate` works
* [x] JupyterLab launches
* [x] notebook uses `Python (MMJL Test)` kernel
* [x] notebook imports package
* [x] logger instantiates
* [x] magics register
* [x] `%%jupy_log` logs Markdown text
* [x] `%jupy_inspect` sees the logged artifact
* [x] `%jupy_validate` reports no missing artifacts
* [x] `%jupy_markdown` writes a timeline
* [x] `%jupy_html` writes a timeline

Not yet completed:

* [ ] test `%jupy_file`
* [ ] test command-line `log-file`
* [ ] test generated matplotlib PNG
* [ ] test generated WAV audio
* [ ] test generated GIF animation
* [ ] test generated MP4/video if ffmpeg is available
* [ ] test HTML timeline rendering in browser
* [ ] test Markdown timeline rendering
* [ ] test notebook save/reopen workflow
* [ ] decide whether to ignore generated `jupy_log/` in git
* [ ] decide whether demo artifacts belong under `assets/`
* [ ] add configurable logger root for magics
* [ ] add timestamped log-root option
* [ ] add PDF export
* [ ] add `%%jupy_capture` (and alias `%%jupy_tee` to it.

---

## 11. Notes from this pass

### Timestamped roots

For overwrite prevention, a future root strategy could use:

```text
jupy_log_<epoch_timestamp>/
```

Example:

```text
jupy_log_1781400000/
```

This is adequate for internal program use and avoids over-engineering the
first version.

Possible later strategies:

```text
jupy_log/
jupy_log_<timestamp>/
<notebook_base>_jupy_log/
<notebook_base>_jupy_log_<timestamp>/
```

This should be separated from core smoke testing.

### Root mismatch

Current behavior:

```text
manual logger instance -> mmjl_test_log
registered magics      -> jupy_log
```

This is acceptable for smoke testing. Later, root configuration should be
added.

Possible future interface:

```python
register_jupy_logger(root="mmjl_test_log")
```

or notebook magic:

```python
%jupy_root mmjl_test_log
```

### Log philosophy

MMJL should default to provenance-preserving behavior:

```text
include input
include output
include metadata
include artifacts
```

Presentation-clean exports should be opt-in.

---

## 12. Next testing phase

The next phase should continue in the saved smoke-test notebook or a fresh
notebook using the same kernel.

Recommended order:

### 12.1 Reopen and confirm basics

* [ ] Reopen the saved notebook.
* [ ] Confirm the kernel is `Python (MMJL Test)`.
* [ ] Re-run import/setup cell.
* [ ] Re-register magics.
* [ ] Run `%jupy_inspect`.
* [ ] Run `%jupy_validate`.

### 12.2 Test simple Markdown/HTML note

Repeat or extend the `details/summary` test:

```python
%%jupy_log --label details-summary-tip-2 --mime text/markdown
<details>
<summary>Click to see something hidden</summary>

Here is something hidden.

</details>
```

Then:

```python
%jupy_markdown
%jupy_html
```

Check that the exported HTML renders the collapsible detail block.

### 12.3 Test “forwards wrong, backwards right” notebook-state example

Create a small notebook-state example where the visible cell order is not
the true dependency order.

Conceptual dependency order:

```text
CELL C:
  create numbers

CELL B:
  use numbers to create squared_numbers

CELL A:
  use squared_numbers to compute avg_value and plot
```

This is important because notebooks can appear organized while depending on
hidden kernel state. MMJL should help preserve the actual learning trail:
inputs, outputs, artifacts, and notes.

Test goals:

* [ ] log the explanatory Markdown note
* [ ] log the code snippets
* [ ] generate printed output
* [ ] generate a matplotlib plot
* [ ] log the plot as an image artifact
* [ ] export Markdown and HTML timelines

### 12.4 Test static L^p unit-ball plot

Create a static subplot grid for Minkowski / (L^p) unit balls.

Suggested values:

```text
p = 1, 2, 3, 5, 8, 16, 20, 25, infinity
```

Test goals:

* [ ] generate static matplotlib figure
* [ ] save/log PNG artifact
* [ ] log explanatory Markdown
* [ ] export timeline
* [ ] validate artifact paths

### 12.5 Test animated L^p transition

Use `matplotlib.animation.FuncAnimation` to animate the transition from
the (L^1) diamond toward the (L^\infty)-like square.

Test goals:

* [ ] generate HTML animation output with `ani.to_jshtml()`
* [ ] optionally save/log GIF using Pillow writer
* [ ] optionally save/log MP4 if ffmpeg is available
* [ ] confirm HTML timeline behavior

### 12.6 Test generated audio

Generate a simple WAV from Python data.

Possible test cases:

* sine wave
* chirp
* plucked-string-like toy signal
* small data-sonification example

Test goals:

* [ ] write WAV
* [ ] log WAV with `%jupy_file` or logger API
* [ ] confirm HTML timeline includes playable audio control

### 12.7 Test external generated audio

Optional later test using SoX:

```bash
sox -n bell.ogg synth 1.5 pluck A3 vol 0.1
```

Test goals:

* [ ] log OGG
* [ ] confirm MIME detection or explicit MIME works
* [ ] confirm HTML audio control renders

---

## 13. Pre-PR gate

Before opening a pull request, pass at least:

* [ ] import test
* [ ] CLI help test
* [ ] CLI inspect/validate test
* [ ] Jupyter magic registration test
* [ ] `%%jupy_log` Markdown artifact test
* [ ] `%jupy_markdown` export test
* [ ] `%jupy_html` export test
* [ ] one generated image artifact test
* [ ] one generated audio or animation artifact test
* [ ] check `git status`
* [ ] confirm generated local logs are ignored or intentionally committed
* [ ] update README roadmap if needed

---

## 14. Current status

The first MMJL smoke test passed. The project is ready for a commit of the
current split package and setup notes, followed by the next testing phase.

*End of document*