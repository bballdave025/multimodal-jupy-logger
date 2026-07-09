# Dev Tip — Windows PDF Debugging

## Purpose

This note records the current hypothesis and debugging path for MMJL PDF
export failures on Windows.

The PDF export code is useful, but it should not block the core MMJL
capture/logging work. In particular, the core logger should still work even
if PDF export is unavailable or platform-dependent.

---

## Observed failure mode

When importing or using PDF-related helpers from a plain Python process on
Windows, PDF export/debugging exposed two separate concerns:

1. IPython magic registration should not happen at module import time.
2. `nbconvert` WebPDF export may fail on Windows because Playwright needs an
   event loop policy that supports subprocess creation.

The second issue showed up in a stack trace involving:

```text
WebPDFExporter
Playwright
asyncio subprocess
NotImplementedError
```

This suggests that the failure may be related to the Windows asyncio event
loop policy rather than the notebook content itself.

---

## Import-time magic registration problem

A module should not register IPython magics just by being imported.

This is fragile:

```python
from IPython.core.magic import register_line_magic

@register_line_magic
def backup_pdf(line: str) -> None:
  ...
##endof:  backup_pdf(...)
```

That can fail outside a live IPython shell with an error like:

```text
AttributeError: 'NoneType' object has no attribute 'register_magic_function'
```

The safer pattern is:

```python
from IPython import get_ipython
from IPython.core.magic import Magics, line_magic, magics_class


@magics_class
class JupyPdfMagics(Magics):

  @line_magic
  def backup_pdf(self, line: str = "") -> None:
    ...
  ##endof:  backup_pdf(...)

##endof:  class JupyPdfMagics


def register_pdf_magics(ip=None) -> bool:
  if ip is None:
    ip = get_ipython()
  ##endof:  if ip is None

  if ip is None:
    return False
  ##endof:  if ip is None

  ip.register_magics(JupyPdfMagics)
  return True
##endof:  register_pdf_magics(...)


def load_ipython_extension(ip) -> None:
  register_pdf_magics(ip=ip)
##endof:  load_ipython_extension(...)
```

That way:

```python
import multimodal_jupy_logger.jupy_pdf_utils
```

does not require an active notebook kernel.

---

## Windows Playwright / asyncio hypothesis

If WebPDF export fails on Windows with a subprocess-related
`NotImplementedError`, try temporarily switching to the Windows proactor
event loop policy around the export call.

Sketch:

```python
import asyncio
import sys


old_event_loop_policy = None

if sys.platform.startswith("win"):
  old_event_loop_policy = asyncio.get_event_loop_policy()
  asyncio.set_event_loop_policy(
      asyncio.WindowsProactorEventLoopPolicy(),
  )
##endof:  if sys.platform.startswith("win")

try:
  pdf_data, resources = exporter.from_notebook_node(notebook_content)
finally:
  if old_event_loop_policy is not None:
    asyncio.set_event_loop_policy(old_event_loop_policy)
  ##endof:  if old_event_loop_policy is not None
##endof:  try/finally
```

This is only a debugging hypothesis until tested.

---

## Minimal import test

From the repository root:

```bash
python -c "from multimodal_jupy_logger.jupy_pdf_utils import export_notebook_to_pdf, register_pdf_magics; print('pdf imports ok')"
```

If this fails, the PDF module is not import-safe yet.

That should be fixed before exporting PDF helpers from
`multimodal_jupy_logger.__init__`.

---

## Minimal Linux / SageMaker test

On AWS SageMaker or another Linux Jupyter environment, first test import
safety:

```python
from multimodal_jupy_logger.jupy_pdf_utils import (
    export_notebook_to_pdf,
    register_pdf_magics,
)

print("pdf imports ok")
```

Then test magic registration without exporting a large notebook:

```python
registered = register_pdf_magics()
print("registered:", registered)
```

If that works, test against a tiny disposable notebook rather than a real MLU
lab notebook.

---

## Do not dagger real notebooks

Avoid testing PDF export directly on large or important notebooks first.

Use a tiny throwaway notebook with:

```python
print("hello pdf")
```

and maybe one simple Markdown cell.

The first goal is only to answer:

```text
Can this environment export a tiny notebook to PDF at all?
```

Only after that should larger notebooks be attempted.

---

## Commit-scope recommendation

For the portable-path / pin-mode commit, it is acceptable to leave PDF export
out of the main success criteria.

Recommended commit boundary:

```text
Include:
  - root-relative manifest paths
  - timeline-relative artifact links
  - register_jupy_logger(root=...)
  - quiet magic wrappers
  - --pin / --pin-input / --pin-output
  - --label behaving like --pin

Do not require:
  - working Windows PDF export
  - working SageMaker PDF export
  - Playwright installation
  - browser-based PDF rendering
```

PDF export can be a follow-up commit once import safety and platform behavior
are known.

---

## Package-root export rule

Only export PDF helpers from `multimodal_jupy_logger.__init__` if this import
is safe:

```python
from multimodal_jupy_logger.jupy_pdf_utils import (
    export_notebook_to_pdf,
    register_pdf_magics,
)
```

If that import is not safe, keep PDF helpers out of `__init__.py` temporarily
and import them directly from the submodule during development.

---

## Current preferred stance

PDF support is useful, especially on Linux/SageMaker, but it should be treated
as optional until proven stable.

The core MMJL logger should remain useful without PDF export.

---

---

##Lots of details

### The actual exception

```Windows Powershell
(.venv_mmjl_test) PS D:\David\my_repos_dwb\multimodal-jupy-logger\src\multimodal_jupy_logger> tree /f
Folder PATH listing for volume Data
Volume serial number is XXXXXXXXX
D:.
│   jupy_pdf_utils.py
│   logger.py
│   magics.py
│   metadata.py
│   mmjl_cli.py
│   __init__.py
│
└───utils
        path_display.py
        __init__.py


(.venv_mmjl_test) PS D:\David\my_repos_dwb\multimodal-jupy-logger\src\multimodal_jupy_logger> python -c "import sys; print(sys.executable)"
D:\David\my_repos_dwb\multimodal-jupy-logger\.venv_mmjl_test\Scripts\python.exe

(.venv_mmjl_test) PS D:\David\my_repos_dwb\multimodal-jupy-logger\src\multimodal_jupy_logger> python -c "import jupy_pdf_utils; help(jupy_pdf_utils)"
Traceback (most recent call last):
  File "<string>", line 1, in <module>
    import jupy_pdf_utils; help(jupy_pdf_utils)
    ^^^^^^^^^^^^^^^^^^^^^
  File "D:\David\my_repos_dwb\multimodal-jupy-logger\src\multimodal_jupy_logger\jupy_pdf_utils.py", line 263, in <module>
    @register_line_magic
     ^^^^^^^^^^^^^^^^^^^
  File "D:\David\my_repos_dwb\multimodal-jupy-logger\.venv_mmjl_test\Lib\site-packages\IPython\core\magic.py", line 257, in magic_deco
    ip.register_magic_function(func, magic_kind, name)  # type: ignore[arg-type]
    ^^^^^^^^^^^^^^^^^^^^^^^^^^
AttributeError: 'NoneType' object has no attribute 'register_magic_function'

(.venv_mmjl_test) PS D:\David\my_repos_dwb\multimodal-jupy-logger\src\multimodal_jupy_logger>
```

### Ideas

Yes. The failure is exactly where I’d start, and it is a clean one:

```python
AttributeError: 'NoneType' object has no attribute 'register_magic_function'
```

That means `@register_line_magic` ran at module import time, but there was no active IPython shell object. In a notebook, that decorator often works. In normal Python / PowerShell / `help(jupy_pdf_utils)`, `get_ipython()` is effectively absent, so the decorator explodes before `help()` can even run.

The fix is: do not register the magic at import time. Define the function normally, then register it only when an IPython shell exists.

Immediate `jupy_pdf_utils.py` fix

Replace this part:

```python
from IPython.core.magic import register_line_magic
```

with:

```python
from IPython.core.magic import Magics
from IPython.core.magic import magics_class
from IPython.core.magic import line_magic
```

Then replace:

```python
@register_line_magic
def backup_pdf(line: str) -> None:
  ...
```

with this pattern:

```
@magics_class
class JupyPdfMagics(Magics):
  '''
  IPython/Jupyter magic interface for notebook PDF backup.
  '''

  @line_magic
  def backup_pdf(self, line: str) -> None:
    '''
    Jupyter line magic interface.

    Usage:
      %backup_pdf
      %backup_pdf optional_output_name.pdf
    '''

    target_output = line.strip() if line.strip() else None

    export_notebook_to_pdf(
        input_path=None,
        output_path=target_output,
    )
  ##endof:  backup_pdf()
##endof:  JupyPdfMagics


def register_pdf_magics(ip=None) -> bool:
  '''
  Register PDF backup magics when an IPython shell is available.

  Returns True if registration happened, False otherwise.
  '''

  if ip is None:
    ip = get_ipython()
  ##endof:  if ip is None

  if ip is None:
    return False
  ##endof:  if ip is None

  ip.register_magics(JupyPdfMagics)

  return True
##endof:  register_pdf_magics()


def load_ipython_extension(ip) -> None:
  '''
  IPython extension hook.

  Enables:

    %load_ext multimodal_jupy_logger.jupy_pdf_utils
  '''

  register_pdf_magics(ip)
##endof:  load_ipython_extension()
```

Now this should work from PowerShell:

```Windows Powershell
python -c "import jupy_pdf_utils; help(jupy_pdf_utils)"
```

And in a notebook you can use either:

```python
%load_ext multimodal_jupy_logger.jupy_pdf_utils
%backup_pdf
```

or:

```python
from multimodal_jupy_logger.jupy_pdf_utils import register_pdf_magics

register_pdf_magics()
%backup_pdf
```

#### Other notes

`pin*` family: repeated clean spec

The behavior should be:

```text
--pin
  keep input + output

--pin-nput
  keep input only

--pin-output
  keep output only

--label NAME
  use this human-readable name

--label NAME with no pin mode
  automatically behaves like --pin
```

So these are equivalent:

```python
%%jupy_capture --label lp-ball-static-grid
```


```python
%%jupy_capture --label lp-ball-static-grid --pin
```

That is the big note. `--label` alone means: “I deliberately selected and named this cell, so keep both input and output unless I explicitly say otherwise.”

The behavior table should be:

```text
%%jupy_capture
  existing default behavior, unless you intentionally change it later

%%jupy_capture --pin
  capture input + output with automatic pin label

%%jupy_capture --label NAME
  capture input + output with NAME

%%jupy_capture --label NAME --pin
  capture input + output with NAME

%%jupy_capture --pin-input
  capture input only with automatic pin label

%%jupy_capture --label NAME --pin-input
  capture input only with NAME

%%jupy_capture --pin-output
  capture output only with automatic pin label

%%jupy_capture --label NAME --pin-output
  capture output only with NAME
```

Conflict rule:

Only one of `--pin`, `--pin-input`, `--pin-output` may be used.

So this should error clearly:

```python
%%jupy_capture --pin-input --pin-output
```

Suggested help front-page:

```text
MMJL is for selected notebook memory.

Use --pin when a cell is worth keeping.
Use --label NAME when a cell is worth keeping and you already know its name.
Use --pin-input when the code matters more than the output.
Use --pin-output when the result matters more than the code.

Important:
  --label NAME by itself behaves like --pin.
  That means named captures keep both input and output unless narrowed by
  --pin-input or --pin-output.
```

Fix `jupy_pdf_utils.py` first because it is blocking import/help. Then the `pin` family goes into `magics.py`, probably in the argument parsing layer before the actual capture execution path.

