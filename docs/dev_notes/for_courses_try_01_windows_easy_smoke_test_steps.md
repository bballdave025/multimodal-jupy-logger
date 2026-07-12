You are in exactly the right place:

```text
(.venv_mmjl_test) PS D:\David\tmp\try_1>
```

For **Try 1**, we will:

```text
existing repo source
        ↓
PowerShell import checks
        ↓
launch Jupyter from try_1
        ↓
make one Boolean-controlled notebook adjustment
        ↓
run the portable smoke test incrementally
```

The canonical notebook in the repository stays untouched. We edit only the disposable copy in `try_1`.

# Part A — From-shell smoke tests

## 1. Define the real repository and source paths

Copy and run:

```powershell
$repoRoot = `
  "D:\David\my_repos_dwb\multimodal-jupy-logger"

$mmjlSrc = `
  "$repoRoot\src"
```

Check them:

```powershell
$repoRoot
$mmjlSrc
```

Expected:

```text
D:\David\my_repos_dwb\multimodal-jupy-logger
D:\David\my_repos_dwb\multimodal-jupy-logger\src
```

## 2. Set `PYTHONPATH` for this PowerShell process

```powershell
$env:PYTHONPATH = $mmjlSrc
```

Verify:

```powershell
$env:PYTHONPATH
```

Expected:

```text
D:\David\my_repos_dwb\multimodal-jupy-logger\src
```

This applies to commands run from this PowerShell window and to Jupyter launched from it.

## 3. Confirm which Python is active

```powershell
python -c "import sys; print(sys.executable)"
```

Expected:

```text
D:\David\my_repos_dwb\multimodal-jupy-logger\.venv_mmjl_test\Scripts\python.exe
```

Do not continue if it points to some unrelated global Python.

## 4. Test the core package import without touching PDF explicitly

```powershell
python -c "import multimodal_jupy_logger; print('core package import ok'); print(multimodal_jupy_logger.__file__)"
```

Expected:

```text
core package import ok
D:\David\my_repos_dwb\multimodal-jupy-logger\src\multimodal_jupy_logger\__init__.py
```

This answers:

> Does importing the package root work without PDF support breaking it?

## 5. Test the public logger symbols

```powershell
python -c "from multimodal_jupy_logger import MultimodalJupyLogger, register_jupy_logger; print('public logger symbols ok')"
```

Expected:

```text
public logger symbols ok
```

## 6. Test the PDF submodule import separately

```powershell
python -c "import multimodal_jupy_logger.jupy_pdf_utils; print('PDF submodule import ok')"
```

Expected:

```text
PDF submodule import ok
```

## 7. Test the PDF symbols

```powershell
python -c "from multimodal_jupy_logger.jupy_pdf_utils import export_notebook_to_pdf, register_pdf_magics; print('PDF symbols ok')"
```

Expected:

```text
PDF symbols ok
```

## 8. Confirm safe behavior outside IPython

```powershell
python -c "from multimodal_jupy_logger.jupy_pdf_utils import register_pdf_magics; print('registered:', register_pdf_magics())"
```

Expected:

```text
registered: False
```

That is a **pass**, not a failure.

It means:

```text
plain Python process
→ no active IPython shell
→ do not register notebook magic
→ return False cleanly
```

## 9. Test the PDF module CLI parser

This does not attempt a PDF conversion:

```powershell
python -m multimodal_jupy_logger.jupy_pdf_utils --help
```

Expected:

* usage text,
* argument descriptions,
* no traceback.

This verifies that the module is callable from the command line.

## 10. Compile the package source

```powershell
python -m compileall -q $mmjlSrc
```

PowerShell should print nothing if everything compiles.

Then add an explicit success marker:

```powershell
if ($LASTEXITCODE -eq 0) {
  Write-Host "[PASS] MMJL source compilation passed."
} else {
  Write-Host "[FAIL] MMJL source compilation failed."
}
```

Expected:

```text
[PASS] MMJL source compilation passed.
```

## 11. One combined shell checkpoint

```powershell
python -c "import multimodal_jupy_logger; from multimodal_jupy_logger import MultimodalJupyLogger, register_jupy_logger; from multimodal_jupy_logger.jupy_pdf_utils import export_notebook_to_pdf, register_pdf_magics; print('[PASS] core import'); print('[PASS] public symbols'); print('[PASS] PDF import'); print('[PASS] PDF symbols'); print('registered outside IPython:', register_pdf_magics())"
```

Expected ending:

```text
[PASS] core import
[PASS] public symbols
[PASS] PDF import
[PASS] PDF symbols
registered outside IPython: False
```

At that point the **Try 1 shell checks are green**.

# Part B — Prepare the notebook source-selection Boolean

There is one important detail:

Setting `PYTHONPATH` is enough for ordinary Python imports, but the portable notebook’s first cell performs its **own filesystem search** before importing MMJL.

Because the notebook is here:

```text
D:\David\tmp\try_1
```

and the repository is here:

```text
D:\David\my_repos_dwb\multimodal-jupy-logger
```

the notebook’s normal search will not discover the source automatically.

We will use a Boolean-controlled explicit path.

## Optional: register the notebook kernel

Run once for a new MMJL virtual environment:

```powershell
python -m ipykernel install `
  --user `
  --name mmjl-test `
  --display-name "Python (MMJL test)"
```

Verify registration:

```powershell
jupyter kernelspec list
```

Then select:

```text
Python (MMJL test)
```

inside JupyterLab.

This step only needs to be repeated if:

* a new venv is created,
* the old venv is deleted,
* or the kernelspec is manually removed.

## 12. Launch JupyterLab from `try_1`

You should still be here:

```text
D:\David\tmp\try_1
```

Run:

```powershell
python -m jupyter lab
```

Open:

```text
mmjl_portable_smoke_test.ipynb
```

Select the kernel using:

```text
D:\David\my_repos_dwb\multimodal-jupy-logger\.venv_mmjl_test
```

or the corresponding named kernel.

# Part C — Change only the first code cell

## 13. Replace the first code cell with this

Use four-space indentation in the notebook cell:

```python
from pathlib import Path
import importlib
import os
import shutil
import sys

USE_EXPLICIT_MMJL_SRC = True

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
    if (candidate_src / "multimodal_jupy_logger").is_dir():
        mmjl_src = candidate_src
        break
    ##endof:  if (candidate_src / ...)
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

print("source mode:", (
    "explicit"
    if USE_EXPLICIT_MMJL_SRC
    else "portable discovery"
))
print("starting_dir:", starting_dir)
print("mmjl_src:", mmjl_src)
print("python:", sys.executable)
```

This gives us one clear switch:

```python
USE_EXPLICIT_MMJL_SRC = True
```

For this Windows Try 1:

```text
True
```

For the real SageMaker home layout:

```text
False
```

No commenting and uncommenting blocks. No dropdown.

## 14. Save the notebook copy

Use:

```text
File → Save Notebook
```

or:

```text
Ctrl+S
```

This changes only:

```text
D:\David\tmp\try_1\mmjl_portable_smoke_test.ipynb
```

It does not change the repository copy.

# Part D — Run the notebook incrementally

## 15. Restart with clean state

In JupyterLab:

```text
Kernel
→ Restart Kernel and Clear Outputs of All Cells
```

Then run only the first code cell.

Expected:

```text
source mode: explicit
starting_dir: D:\David\tmp\try_1
mmjl_src: D:\David\my_repos_dwb\multimodal-jupy-logger\src
python: D:\David\my_repos_dwb\multimodal-jupy-logger\.venv_mmjl_test\Scripts\python.exe
```

Check these three facts:

```text
source mode = explicit
mmjl_src = real repo src
python = .venv_mmjl_test Python
```

Stop immediately if any one of those is wrong.

## 16. Run the registration cell

The next code cell imports:

```python
from multimodal_jupy_logger import (
    MultimodalJupyLogger,
    register_jupy_logger,
)
```

and registers:

```python
log_root = Path.cwd() / "jupy_log_smoke_test"
```

Expected:

```text
MMJL log root: D:\David\tmp\try_1\jupy_log_smoke_test
log root exists: True
```

That confirms:

```text
source code:
  real repository

generated test data:
  disposable try_1 directory
```

Exactly what we want.

## 17. Run the first `%jupy_inspect`

Expected:

* the magic runs,
* no traceback,
* no unwanted trailing `WindowsPath(...)`,
* no unwanted `[]`.

An empty manifest at this point is fine.

## 18. Run the literal logging test

Run the `%%jupy_log` cell.

Expected:

```text
[DONE] Logged text: ...
```

Also expected:

* no `WindowsPath(...)`,
* no list displayed afterward,
* one Markdown artifact created.

## 19. Run `--pin`

Run:

```python
%%jupy_capture --pin
pin_message = "pin captures input and output"
print(pin_message)
```

Expected notebook output:

```text
pin captures input and output
```

Expected logging:

* input artifact,
* stdout/output artifact,
* automatic label.

## 20. Run label-only behavior

Run:

```python
%%jupy_capture --label named-pin-default
named_message = "label alone behaves like pin"
print(named_message)
```

Expected:

* input logged,
* output logged,
* label is `named-pin-default`.

This confirms:

```text
--label NAME
→ defaults to --pin
```

## 21. Run `--pin-input`

Expected:

* code/input logged,
* visible output still appears in Jupyter,
* output is not stored as the selected capture output.

## 22. Run `--pin-output`

Expected:

* output logged,
* input not logged as the selected capture input,
* value `42` appears or is captured appropriately.

## 23. Run the plot cell

Expected:

* the plot displays,
* stdout is logged,
* an image artifact is created,
* no extra Python return object appears.

## 24. Run the intentional exception cell

It should fail with:

```text
ValueError: Expected MMJL smoke-test exception
```

That is expected.

Check:

* input was logged,
* exception was logged,
* kernel remains alive.

Then manually run the next cell.

## 25. Run inspect, validate, Markdown, and HTML

Run:

```python
%jupy_inspect
%jupy_validate
%jupy_markdown
%jupy_html
```

Expected:

* zero missing artifacts,
* Markdown timeline created,
* HTML timeline created,
* no `WindowsPath(...)`,
* no empty list displayed as notebook output.

## 26. Run the final assertions

Expected final line:

```text
[PASS] Portable relative-path smoke test passed.
```

Do not settle for “probably passed.” That exact line is your green checkpoint.

# Part E — Inspect from PowerShell

## 27. Save the notebook and stop JupyterLab

Save first.

Then return to PowerShell and stop JupyterLab with:

```text
Ctrl+C
```

Confirm shutdown if prompted.

## 28. Inspect the output tree

From:

```text
D:\David\tmp\try_1
```

run:

```powershell
tree .\jupy_log_smoke_test /A /F
```

Expected core structure:

```text
jupy_log_smoke_test
+---artifacts
+---staging
+---timelines
|       timeline.html
|       timeline.md
|
\---manifest.tsv
```

## 29. Inspect manifest paths

```powershell
Import-Csv `
  .\jupy_log_smoke_test\manifest.tsv `
  -Delimiter "`t" |
  Select-Object sequence, kind, mime_type, label, path |
  Format-Table -AutoSize
```

Paths should resemble:

```text
artifacts/000001_...
```

They should not contain:

```text
D:\David\
```

## 30. Search for absolute path leakage

```powershell
Select-String `
  -Path .\jupy_log_smoke_test\timelines\timeline.* `
  -Pattern "D:\\David\\"
```

Expected:

```text
no output
```

## 31. Confirm relative artifact links

```powershell
Select-String `
  -Path .\jupy_log_smoke_test\timelines\timeline.* `
  -Pattern "\.\./artifacts/"
```

Expected:

```text
one or more matches
```

# Try 1 definition of done

You can call Try 1 green when all of these are true:

```text
[ ] core package import passed
[ ] public symbols imported
[ ] PDF submodule imported
[ ] PDF symbols imported
[ ] register_pdf_magics() returned False in plain Python
[ ] PDF CLI --help worked
[ ] source compilation passed
[ ] notebook used explicit repo src
[ ] notebook wrote logs under try_1
[ ] pin family behaved correctly
[ ] plot capture worked
[ ] exception capture worked
[ ] validation found no missing artifacts
[ ] Markdown timeline was created
[ ] HTML timeline was created
[ ] final portable-path assertion passed
[ ] timelines contain relative artifact links
[ ] timelines contain no D:\David absolute path
```

After this passes, Try 2 will reuse almost the same notebook cell. The only changes will be:

```python
USE_EXPLICIT_MMJL_SRC = True
```

and:

```python
EXPLICIT_MMJL_SRC = Path(
    r"D:\David\tmp\try_2\multimodal-jupy-logger\src"
)
```

Then, in SageMaker:

```python
USE_EXPLICIT_MMJL_SRC = False
```

and the unchanged portable branch will find:

```text
/home/sagemaker-user/multimodal-jupy-logger/src
```
