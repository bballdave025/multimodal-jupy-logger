# Dev Notes on `jupy_pdf_utils.py`

Recovered from phone screenshots on 2026-06-27.

## Purpose

`jupy_pdf_utils.py` is a standalone utility for backing up a Jupyter notebook
to PDF, with metadata inserted at the top of the notebook before rendering.

It is intentionally being kept as a drop-in MVP rather than immediately being
folded into the broader `multimodal-jupy-logger` magic framework.

## Main workflows

### Workflow 1 — Inside a Jupyter notebook

```python
import multimodal_jupy_logger.jupy_pdf_utils
```

Then:

```python
%backup_pdf
```

or:

```python
%backup_pdf my_backup.pdf
```

The magic attempts to save the notebook through frontend JavaScript, waits
briefly, injects a metadata cell, and exports the notebook as PDF.

### Workflow 2 — Python API

```python
from multimodal_jupy_logger.jupy_pdf_utils import export_notebook_to_pdf

export_notebook_to_pdf(
  input_path="analysis.ipynb",
  output_path=None,
  hide_code=False,
)
```

### Workflow 3 — CLI

```bash
python -m multimodal_jupy_logger.jupy_pdf_utils analysis.ipynb
```

With output path:

```bash
python -m multimodal_jupy_logger.jupy_pdf_utils analysis.ipynb -o backup.pdf
```

Show code cells:

```bash
python -m multimodal_jupy_logger.jupy_pdf_utils analysis.ipynb --show-code
```

## Design notes

The module has three layers:

1. `export_notebook_to_pdf()` — execution engine.
2. `%backup_pdf` — notebook magic frontend.
3. `main()` — terminal CLI frontend.

This is deliberately simple and allows the module to remain usable before
deeper MMJL integration.

## IPython startup registration notes

To register `%backup_pdf` permanently, create an IPython startup file.

First create/check the profile:

```powershell
ipython profile create
```

Typical directory:

```text
C:\Users\<your_username>\.ipython\profile_default\
```

Inside that directory, use the `startup` folder.

Example:

```powershell
cd C:\Users\<your_username>\.ipython\profile_default\startup
```

Create a file such as:

```text
00-register-pdf-backup.py
```

Example contents:

```python
import sys

sys.path.append(
    r"C:\path\to\multimodal-jupy-logger\src"
)

import multimodal_jupy_logger.jupy_pdf_utils
```

Then restart all JupyterLab servers, launch fresh JupyterLab, and test:

```python
%backup_pdf
```

## Current intentional limitation

The notebook magic currently uses:

```python
active_notebook_name = "analysis.ipynb"
```

This is MVP-safe but not ideal. Later it should either:

- use reliable active-notebook detection,
- accept the notebook name explicitly,
- or integrate with MMJL's existing magic option parsing.

## Future integration idea

This PDF export should eventually become one backend in a broader notebook
logging and transformation system that can:

- log cell input,
- log cell output,
- log both,
- tee outputs,
- create notes/Markdown cells from code cells,
- inspect notebook state,
- validate generated notebook artifacts,
- and export durable PDF backups.

For now, keep this module off to the side and working.
