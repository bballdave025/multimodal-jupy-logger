# MMJL Smoke Test Progression

The goal is:

```text
Can I import MMJL?
↓
Can I import the PDF module safely?
↓
Can I run MMJL in a notebook?
↓
Can I run the portable smoke notebook?
↓
Can I do the same thing on another machine?
```

---

# Phase 1 — Windows PowerShell

## 1. Unzip

```powershell
Expand-Archive `
  mmjl_transfer_kit.zip `
  -DestinationPath D:\David\mmjl_transfer_test
```

---

## 2. Create venv

From repo root:

```powershell
cd D:\David\mmjl_transfer_test

python -m venv .venv_mmjl_test
```

Activate:

```powershell
.\.venv_mmjl_test\Scripts\Activate.ps1
```

Verify:

```powershell
python -c "import sys; print(sys.executable)"
```

Expected:

```text
...\mmjl_transfer_test\.venv_mmjl_test\Scripts\python.exe
```

---

## 3. Install minimum dependencies

For import safety only:

```powershell
pip install ipython nbformat nbconvert
```

---

## 4. Verify package structure

```powershell
Get-ChildItem src\multimodal_jupy_logger
```

You should see:

```text
__init__.py
logger.py
magics.py
metadata.py
mmjl_cli.py
jupy_pdf_utils.py
utils\
```

---

## 5. Raw module import

```powershell
cd src\multimodal_jupy_logger
```

```powershell
python -c "import jupy_pdf_utils; print('import ok')"
```

---

## 6. Help smoke test

```powershell
python -c "import jupy_pdf_utils; help(jupy_pdf_utils)"
```

Success means:

```text
help text appears
```

Failure means:

```text
AttributeError:
'NoneType' object has no attribute
'register_magic_function'
```

which means import-time magic registration still exists.

---

## 7. Symbol import smoke test

```powershell
python -c "from jupy_pdf_utils import export_notebook_to_pdf, register_pdf_magics; print('symbols ok')"
```

Expected:

```text
symbols ok
```

---

## 8. Registration smoke test

Outside IPython:

```powershell
python -c "from jupy_pdf_utils import register_pdf_magics; print(register_pdf_magics())"
```

Expected:

```text
False
```

---

## 9. Package import smoke test

Back to repo root:

```powershell
cd ..\..
```

```powershell
$env:PYTHONPATH="src"
```

```powershell
python -c "from multimodal_jupy_logger import jupy_pdf_utils; print('package import ok')"
```

Expected:

```text
package import ok
```

---

## 10. Compile everything

From repo root:

```powershell
python -m compileall src
```

or:

```powershell
Get-ChildItem src -Recurse *.py |
  ForEach-Object {
    python -m py_compile $_.FullName
  }
```

---

# Phase 2 — VS Code Notebook

Install notebook dependencies:

```powershell
pip install -r requirements.txt
```

If NumPy gives trouble:

```powershell
pip install jupyterlab ipykernel ipywidgets matplotlib
```

---

## Open notebook

Open:

```text
examples/mmjl_portable_smoke_test.ipynb
```

Select:

```text
.venv_mmjl_test
```

as kernel.

---

## Run first cell only

Expected:

```text
starting_dir:
mmjl_src:
python:
```

Verify:

```text
mmjl_src points to src/
```

---

## Run second cell

Expected:

```text
MMJL log root:
log root exists: True
```

---

## Run `%jupy_inspect`

Expected:

```text
manifest exists
artifact counts shown
```

No:

```text
WindowsPath(...)
```

output.

---

## Run literal logging test

Expected:

```text
[DONE] Logged text:
```

No:

```text
WindowsPath(...)
[]
PosixPath(...)
```

---

## Run pin tests

Verify:

```text
--pin
--label
--pin-input
--pin-output
```

behave correctly.

---

## Run plot test

Verify:

```text
artifact image created
timeline links relative
```

---

## Run exception test

Expected:

```text
ValueError
```

and:

```text
subsequent cells still work
```

---

## Run export section

Expected:

```text
timeline.md
timeline.html
manifest.tsv
```

---

## Final assertion cell

Expected:

```text
[PASS] Portable relative-path smoke test passed.
```

This is your first major green checkmark.

---

# Phase 3 — SageMaker

Upload:

```text
mmjl_transfer_kit.zip
```

Unzip into:

```text
~/multimodal-jupy-logger/
```

Expected layout:

```text
~/multimodal-jupy-logger
├── src
├── docs
└── examples
```

---

## Install dependencies

Inside SageMaker terminal:

```bash
pip install ipywidgets matplotlib nbformat nbconvert
```

---

## Open notebook

Open:

```text
examples/mmjl_portable_smoke_test.ipynb
```

---

## Run All

The notebook was explicitly designed to find:

```text
./src
```

or:

```text
~/multimodal-jupy-logger/src
```

automatically.

No edits should be required.

---

## Success criteria

```text
imports succeed
magics register
logging works
pin family works
validation succeeds
relative paths survive
timeline exports work
```

If all of that passes:

```text
MMJL portable MVP confirmed.
```

At that point I would personally merge the PR unless something very surprising turns up during PDF work.
