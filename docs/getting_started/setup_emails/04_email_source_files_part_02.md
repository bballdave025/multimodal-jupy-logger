# MMJL Source Transfer — Part 2 of 4

For each section, open the stated destination file, paste only the contents inside its code fence, and save the file.

## File: `README.md`

Save as:

```text
~/multimodal-jupy-logger/README.md
```

```markdown
# Multimodal Jupy Logger

Personal general-purpose tooling for logging, preserving, and replaying
multimodal Jupyter/IPython notebook workflows.

Highlights include the ability to:
- Treat notebook outputs as MIME bundles rather than plain text.
- Preserve artifact bytes and MIME metadata separately from rendering.
- Allow replay mechanisms to evolve independently of capture mechanisms.

Quick and accessible description of the mechanisms for these highlights can be found near the end of this `README`, in 

## Quick Start

MMJL is currently designed to be used as a drop-in source tree. The notebook
makes source selection, environment state, and log naming explicit near the
top.

Detailed guides:

- [SageMaker portable setup](docs/getting_started/sagemaker_portable_setup.md)
- [Windows explicit-source setup](docs/getting_started/windows_explicit_source_setup.md)
- [Portable smoke-test workflow](docs/getting_started/portable_smoke_test_workflow.md)
- [Inline environment checks without `environment_checks.py`](docs/getting_started/manual_environment_checks_without_module.md)

### Expected directory layout

A SageMaker-style portable layout keeps MMJL and the notebook project as
siblings:

```text
~
├── multimodal-jupy-logger/
│   └── src/
│       └── multimodal_jupy_logger/
└── mlu-wjupy-lab/
    ├── some_course_notebook.ipynb
    └── jupy_log_<notebook_slug>/
```

A Windows development checkout may instead use an explicit source path.

### Setup cell 1 — locate MMJL and inspect the environment

Use:

```python
USE_EXPLICIT_MMJL_SRC = False
```

for the SageMaker sibling layout.

Use:

```python
USE_EXPLICIT_MMJL_SRC = True
```

with a local `EXPLICIT_MMJL_SRC` for Windows development.

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
    if (
        candidate_src
        / "multimodal_jupy_logger"
    ).is_dir():
        mmjl_src = candidate_src
        break
    ##endof:  if (...).is_dir()
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

OPTIONAL_PACKAGES = {
    "nbformat": "nbformat",
    "nbconvert": "nbconvert",
    "traitlets": "traitlets",
    "numpy": "numpy",
    "pandas": "pandas",
    "sklearn": "scikit-learn",
    "torch": "torch",
    "tensorflow": "tensorflow",
}

environment_report = print_environment_check(
    required_packages=REQUIRED_PACKAGES,
    investigation_packages=OPTIONAL_PACKAGES,
    show_import_paths=False,
)

if environment_report["required_missing"]:
    install_text = " ".join(
        environment_report["required_missing"]
    )

    raise RuntimeError(
        "Required packages are missing.\n\n"
        f"Run: %pip install {install_text}\n\n"
        "Then restart the kernel."
    )
##endof:  if environment_report["required_missing"]

print()
print("[PASS] Required notebook environment is ready.")
print("MMJL source mode:", (
    "explicit"
    if USE_EXPLICIT_MMJL_SRC
    else "portable discovery"
))
print("MMJL source:", mmjl_src)
```

The environment report includes:

- Python executable
- Python version
- kernel information
- working directory
- home directory
- platform
- selected package availability and versions

Edit the package maps for the current notebook. For example, move `torch`
into `REQUIRED_PACKAGES` when the notebook must use PyTorch.

### Setup cell 2 — choose a notebook-specific log

A descriptive slug is strongly recommended:

```python
NOTEBOOK_SLUG = "mlu_jupyter_magics_l01"

USE_TIMESTAMP_IF_SLUG_EMPTY = True

ALLOW_DESTRUCTIVE_LOG_RESET = False

MARK_LOG_AS_DISPOSABLE = False
```

The resulting directory is:

```text
jupy_log_mlu_jupyter_magics_l01/
```

If no slug is chosen and timestamp fallback is enabled, MMJL should print a
loud warning and generate a timestamp-based slug.

If the target log already contains `manifest.tsv`, MMJL may safely continue
appending to it across multiple days. The setup should print this state
clearly before registration. Change `NOTEBOOK_SLUG` when a separate record is
desired.

Real notebooks must not delete existing logs automatically.

Destructive reset is reserved for disposable smoke tests and should require:

- an explicit Boolean opt-in
- a disposable-log sentinel
- a visible countdown
- an opportunity to interrupt the kernel before deletion

See the
[portable smoke-test workflow](docs/getting_started/portable_smoke_test_workflow.md)
for the complete guarded-reset cell.

### Setup cell 3 — register MMJL

The scaffolding is set up and the system is ready for logging after the registration is complete. Use this next code in a Jupyter
code cell to kick things off.

```python
from pathlib import Path

from multimodal_jupy_logger import (
    register_jupy_logger,
)

log_root = (
    Path.cwd()
    / f"jupy_log_{NOTEBOOK_SLUG}"
)

register_jupy_logger(
    root=log_root,
)

print("MMJL log root:")
print(f"  {log_root.resolve()}")
```

The detailed SageMaker guide contains the complete slug normalization,
timestamp fallback, manifest-state inspection, guarded reset, disposable
sentinel, and countdown cells.

### Record the environment report

After registration, rerun the check under MMJL capture:

```python
%%jupy_capture --label environment-check --pin-output
print_environment_check(
    required_packages=REQUIRED_PACKAGES,
    investigation_packages=OPTIONAL_PACKAGES,
    show_import_paths=False,
)
```

This creates a compact, task-scoped environment record without the noise of a
complete `pip freeze`.

### Continuation-Friendly Logging

MMJL is designed for long-running notebooks that span multiple sessions
or multiple days.

If an existing manifest and log directory are found, MMJL appends new
events rather than overwriting prior history.

This makes it practical to treat notebook logs as an evolving research
record rather than a disposable execution artifact.

Users are encouraged to select descriptive notebook slugs to avoid
accidentally continuing an unrelated log history.

## MMJL Usage Cheat Sheet

### Take a literal note

The cell is stored but not executed. A label is optional; the default is
`cell`.

```python
%%jupy_log --mime text/markdown
### Question

Why does the dual basis appear naturally here?
```

Named note:

```python
%%jupy_log --label projection-note --mime text/markdown
### Projection insight
lo
The residual is orthogonal to the target subspace.
```

#### Automatic Labels for `%%jupy_log`

When no label is supplied, MMJL generates deterministic labels such as:

```text
cell-000001
cell-000002
cell-000003
```

These labels are monotonically increasing during notebook execution and
provide stable references inside manifests and exported timelines.

Explicit labels are still recommended for important notebook events and
research milestones.

### Capture input and output

```python
%%jupy_capture --pin
values = [1, 2, 3, 4]
print(sum(values))
```

A label by itself behaves like `--pin`:

```python
%%jupy_capture --label l2-norm-example
import numpy as np

vector = np.array([3.0, 4.0])
np.linalg.norm(vector)
```


#### Automatic Labels for `%%jupy_capture`

When no label is supplied, MMJL generates deterministic labels such as:

```text
pin-000001
pin-000002
pin-000003
```

These labels are monotonically increasing during notebook execution and
provide stable references inside manifests and exported timelines.

Explicit labels are still recommended for important notebook events and
research milestones.

### Capture input only

```python
%%jupy_capture --label optimizer-setup --pin-input
learning_rate = 0.001
epochs = 100
```

### Capture output only

```python
%%jupy_capture --label final-metrics --pin-output
metrics
```

### Tee visible output

```python
%%jupy_tee --label visible-result
print("Displayed in Jupyter and logged by MMJL.")
```

### Log an existing file

```python
%jupy_file --label trained-model model.pkl
```

High-resolution plot:

```python
plt.savefig(
    "plot_300dpi.png",
    dpi=300,
    bbox_inches="tight",
)
```

Then:

```python
%jupy_file --label high-resolution-plot plot_300dpi.png
```

### Inspect and validate

```python
%jupy_inspect
%jupy_validate
```

Desired validation result:

```text
Missing artifacts: 0
```

### Export

```python
%jupy_markdown
%jupy_html
```

HTML is generally the easiest timeline to read directly. Keep the complete
log directory together so relative artifact links continue to work.

### End-of-session sequence

```python
%jupy_save
%jupy_inspect
%jupy_validate
%jupy_markdown
%jupy_html
```

Then zip and download the complete `jupy_log_<notebook_slug>/` directory.

For the SageMaker use case, this might involve the following, all of which
you should at least try, even if the output is that the step has already been
completed:

1. Install `zip`:

   ```bash
   sudo apt install zip
   ```

2. Move to the course directory:

   ```bash
   cd ~/{YOUR-COURSE-DIRECTORY}/
   ```

3. Create the archive:

   ```bash
   zip -r \
     jupy_log_{NOTEBOOK-SLUG}.zip \
     ./jupy_log_{NOTEBOOK-SLUG}/
   ```

4. Steps 2 and 3 encourage tab completion, as does step 5.

5. In the JupyterLab GUI, select:

   ```text
   ~/{YOUR-COURSE-DIRECTORY}/jupy_log_{NOTEBOOK-SLUG}.zip
   ```

   and click the download button, `⤓`.

After downloading, the safest direct-viewing path is usually:

```text
jupy_log_<notebook_slug>/timelines/timeline.html
```

Open that file in a browser and print it to PDF. This preserves the rendered
text and images without depending on the relative links afterward.

A Markdown editor such as VS Code can preview relative images when the
complete directory structure is intact. However, VS Code does not provide a
universally reliable built-in Markdown-to-PDF workflow. A browser-opened
`timeline.html` is usually the most dependable way to print the rendered
record to PDF.

Another reasonable option is a quick Git commit of the complete
`jupy_log_<notebook_slug>/` directory, then viewing the rendered Markdown on
GitHub before printing or archiving it.

The zipped log remains the authoritative portable record because it preserves
all linked image, video, audio, and other non-text artifacts.

To stop using MMJL, stop adding MMJL magics to cells.

## Purpose

`multimodal-jupyter-logger` is an experimental notebook logging utility for
capturing notebook activity as a durable multimodal event stream, with major goal behaviors being to
- Treat notebook outputs as MIME bundles rather than plain text.
- Preserve artifact bytes and MIME metadata separately from rendering.
- Allow replay mechanisms to evolve independently of capture mechanisms.

It is designed to support:

- source-code logging
- stdout/stderr capture
- rich display output capture
- image, audio, and video artifact logging
- MIME-aware persistence
- HTML and Markdown timeline export
- notebook backup workflows
- optional PDF export support

The guiding idea is that notebook workflows are not just source-code cells.

They are interactive, stateful, multimodal execution traces.

## Status

Early experimental tooling.

The current implementation focuses on a small, inspectable core:

- Jupyter/IPython magics
- manifest-based artifact logging
- MIME-to-file persistence
- replay-oriented HTML/Markdown output
- notebook backup helpers

The project is intentionally lightweight and text-first.

## Rich Artifact Preservation

MMJL records notebook outputs as MIME-aware artifacts.

Examples include:

- text/plain
- text/html
- image/png
- image/jpeg
- markdown
- traceback text
- arbitrary user files

Artifacts are persisted independently of the notebook frontend so that
logs remain useful after notebooks are moved, exported, archived, or
replayed elsewhere.

## Design Principles

- Preserve first; transform later.
- Treat notebook outputs as MIME bundles.
- Keep capture, persistence, replay, and transformation separate.
- Avoid coupling to specific media libraries when possible.
- Prefer deterministic plain-text manifests.
- Make logs useful outside the original notebook frontend.
- Keep employer-specific workflows, data, and implementations out of scope.

## Reliability Features

MMJL is designed to preserve notebook history faithfully, including
partial failures and exploratory dead ends.

### Exception Preservation

If a captured cell raises an exception, MMJL preserves:

- the notebook input cell
- any stdout produced before failure
- the complete traceback
- exception metadata

The notebook cell still fails normally inside Jupyter, preserving
expected interactive behavior.

MMJL attempts to fail gracefully and preserve as much information as
possible rather than silently discarding execution history.

This makes reconstruction of experiments and debugging sessions much
easier days or weeks later.

## Intended Use

This project is intended for:

- personal notebook workflows
- ML/AI experimentation
- multimodal notebook logging
- OCR/HTR experimentation
- educational notebook tooling
- provenance-aware exploratory coding
- workflow reconstruction

## Not Intended For

This repository is not:

- an employer-specific notebook system
- a proprietary workflow implementation
- a confidential data pipeline
- a replacement for full experiment-tracking platforms
- a media transcoding framework

Heavyweight media conversion should generally be delegated to external tools
such as `ffmpeg`.

## IP / Provenance Classification

See the
[classification scheme](https://github.com/bballdave025/dwb-ip-notes/blob/main/IP_Classification_Framework_rev2026-06-08.md)
in my `dwb-ip-notes` repository for more details.

Primary classification:

- D — Personal General-Purpose Tooling

Secondary classification:

- E — Potentially Integrable Independent Tooling

This project is maintained as independent, organization-agnostic tooling.
It does not include proprietary datasets, confidential workflows, internal
systems, or employer-specific implementations.

## Documentation

Situation-specific setup and transfer guidance lives under:

```text
docs/getting_started/
├── README.md
├── sagemaker_portable_setup.md
├── windows_explicit_source_setup.md
├── portable_smoke_test_workflow.md
└── manual_environment_checks_without_module.md
```

Start with the
[getting-started index](docs/getting_started/README.md).

## PDF Export Notes

PDF export support is based on notebook backup/export ideas using Jupyter
`nbconvert`, `WebPDFExporter`, metadata headers, and optional notebook-save
integration. HTML export remains the preferred primary path because it better
preserves multimodal notebook output. PDF support is useful for portable
snapshots and archival/reporting workflows.

Current PDF support should be considered optional and experimental.

Verified:

- importing `jupy_pdf_utils.py` succeeds;
- module help and public PDF symbols load;
- magic registration fails safely outside IPython;
- core MMJL imports do not depend on successful PDF rendering.

Not required for the current MVP:

- reliable PDF rendering in every environment;
- browser or Playwright provisioning;
- active-notebook detection in every Jupyter frontend;
- PDF export from every SageMaker course kernel.

## Short descriptions of efficient technical mechanisms

### Failure-Tolerant Capture

MMJL attempts to preserve execution history even when notebook cells
fail.

Successful output generated before an exception is retained alongside
the traceback itself.

This mirrors how laboratory notebooks preserve both successful and
unsuccessful experiments.

### Deterministic Artifact Naming

Artifacts receive timestamp-based names and stable labels that allow
timelines to be replayed and cross-referenced later.

This makes notebook histories easier to inspect manually and easier to
process programmatically.

### MIME-Aware Persistence

Rather than treating notebook output as undifferentiated text, MMJL
preserves MIME information associated with each artifact.

This allows HTML, images, markdown, tracebacks, plain text, and future
artifact types to coexist naturally in the same logging stream.

## License

MIT License.

*End of document*
```

## File: `src/multimodal_jupy_logger/utils/path_display.py`

Save as:

```text
~/multimodal-jupy-logger/src/multimodal_jupy_logger/utils/path_display.py
```

```python
'''
@file path_display.py

Small path and file utilities used during MMJL development.

@author Dave Black     GitHub @bballdave025     comments signed "DWB"
@since  : 2026-06-1x, mid-June 2026

Part of the `multimodal-jupy-logger` project, which can potentially be
a package.

The module itself acts as the namespace. Typical use:

    from multimodal_jupy_logger.utils import path_display as dpypd

    dpypd.tree(...)
    dpypd.count_lines(...)
    dpypd.print_file(...)

Individual functions may also be imported through the utils package:

    from multimodal_jupy_logger.utils import tree

@TODO 
  Consider adding optional stream parameters to text-only display helpers: 
  
  
      from typing import TextIO 
      import sys 
      
      def tree(..., 
            file: TextIO = sys.stdout
          ) -> None: 
        
        print(line, file=file) 
  
  
  This would allow callers to capture output with `io.StringIO` for
  filtering, testing, or later logging. Alternative for one-off 
  capture: use `contextlib.redirect_stdout(buffer)` around existing
  print-based helpers. 
  
  Do not mix this into rich notebook display helpers yet; MMJL owns that richer display/capture path separately.
'''

from __future__ import annotations

#import sys
#import io
import pathlib
#import contextlib

#  New (sys, io, contextlib) imports not used yet here, but setting up 
#+ up scaffolding for something like:
#+
#+
#+     # 1. Create an in-memory text stream buffer
#+     buffer = io.StringIO()
#+
#+     # 2. Temporarily redirect all print statements 
#+     #+   inside tree() to our buffer
#+     with contextlib.redirect_stdout(buffer):
#+       tree(".")  # Runs normally, but prints nothing to the screen
#+     ##endof:  with
#+     # 3. Extract the full string content from the buffer
#+     tree_output_string = buffer.getvalue()
#+
#+     # 4. Perform line-by-line grep filter
#+     grep_results = [
#+         line 
#+         for line in tree_output_string.splitlines() 
#+         if "abc-" in line and "-pass-b-" in line
#+     ]
#+
#+     print(grep_results)
#
#
#  Looked at a similar solution, adding another parameter to the
#+ tree function itself:
#+
#+
#+        file=sys.stdout,
#+    ) -> None:
#+
#+    #  Now, inside the tree functions, I would just need to make
#+    #+ that all print statements look something like:
#+    #+     print(that_string, file=file)


def _path_part_has_match(
      path_part: str,
      exclusion_items: list[str],
    ) -> bool:
  '''
  Return True if an exclusion string occurs within one path part.
  '''
  
  return any(
      exclusion_item in path_part
      for exclusion_item in exclusion_items
  )
##endof:  _path_part_has_match(...)



def _any_path_part_has_match(
      path_parts: tuple[str, ...],
      exclusion_items: list[str],
    ) -> bool:
  '''
  Return True if an exclusion string matches any path component.
  '''
  
  return any(
      _path_part_has_match(
          path_part,
          exclusion_items,
      )
      for path_part in path_parts
  )
##endof:  _any_path_part_has_match(...)



def _should_exclude_path(
      child_item_path: pathlib.Path,
      root_dir: pathlib.Path,
      dirs_to_exclude: list[str],
      files_to_exclude: list[str],
    ) -> bool:
  '''
  Return True when a path should be omitted from tree output.

  Directory exclusions are tested against relative directory path
  components. File exclusions are tested against the filename only.
  '''
  
  dir_parts_to_check: tuple[str, ...] = ()
  relative_path = None
  this_is_dir = False
  this_is_file = False
  
  relative_path = child_item_path.relative_to(root_dir)
  this_is_dir = child_item_path.is_dir()
  this_is_file = child_item_path.is_file()
  
  if this_is_dir:
    dir_parts_to_check = relative_path.parts
  else:
    dir_parts_to_check = relative_path.parts[:-1]
  ##endof:  if this_is_dir
  
  if _any_path_part_has_match(
        dir_parts_to_check,
        dirs_to_exclude,
      ):
    return True
  ##endof:  if _any_path_part_has_match(...)
  
  if (
        this_is_file
        and _path_part_has_match(
            child_item_path.name,
            files_to_exclude,
        )
      ):
    return True
  ##endof:  if this_is_file and ...
  
  return False
##endof:  _should_exclude_path(...)



def tree(
      this_dir: pathlib.Path | str | None = None,
      indent_length: int = 4,
      dirs_to_exclude: list[str] | None = None,
      files_to_exclude: list[str] | None = None,
#     file=sys.stdout, #can add this & make sure all  print(s,file=file)
    ) -> None:
  '''
  Print a quick tree-style representation of a directory.

  Directory exclusions are compared with relative directory path parts.
  File exclusions are compared with filenames.

  Exclusion matching uses substring tests rather than exact equality.
  '''
  
  current_depth = 0
  relative_path = None
  root_dir = None
  suffix = ""
  this_indent = ""
  
  if this_dir is None:
    root_dir = pathlib.Path.cwd()
  else:
    root_dir = pathlib.Path(this_dir)
  ##endof:  if this_dir is None
  
  root_dir = root_dir.expanduser().resolve()
  
  if dirs_to_exclude is None:
    dirs_to_exclude = []
  ##endof:  if dirs_to_exclude is None
  
  if files_to_exclude is None:
    files_to_exclude = []
  ##endof:  if files_to_exclude is None
  
  print(f"+ {root_dir}")
  
  for child_item_path in sorted(root_dir.rglob("*")):
    if _should_exclude_path(
          child_item_path=child_item_path,
          root_dir=root_dir,
          dirs_to_exclude=dirs_to_exclude,
          files_to_exclude=files_to_exclude,
        ):
      continue
    ##endof:  if _should_exclude_path(...)
    
    relative_path = child_item_path.relative_to(root_dir)
    current_depth = len(relative_path.parts)
    this_indent = " " * indent_length * current_depth
    suffix = "/" if child_item_path.is_dir() else ""
    
    print(f"{this_indent}+ {child_item_path.name}{suffix}")
  ##endof:  for child_item_path in sorted(root_dir.rglob("*"))
##endof:  tree(...)



def count_lines(
      filename: pathlib.Path | str,
      do_print: bool = False,
    ) -> int:
  '''
  Count lines in a file using binary mode.

  Binary mode avoids unnecessary text decoding because line counting
  does not require interpreting the file's characters.
  '''
  
  num_lines = 0
  path = None
  
  path = pathlib.Path(filename).expanduser()
  
  with path.open("rb") as file_handle:
    num_lines = sum(1 for _ in file_handle)
  ##endof:  with path.open("rb") as file_handle
  
  if do_print:
    print(f"{path} has {num_lines} line(s)")
  ##endof:  if do_print
  
  return num_lines
##endof:  count_lines(...)



def print_file(
      filename: pathlib.Path | str,
      encoding: str = "utf-8",
      errors: str = "replace",
      show_line_numbers: bool = False,
    ) -> None:
  '''
  Print a text file without loading the entire file into memory.

  UTF-8 is explicit so Windows does not accidentally use a local code
  page when reading UTF-8 project files.
  '''
  
  path = None
  
  path = pathlib.Path(filename).expanduser()
  
  with path.open(
        "r",
        encoding=encoding,
        errors=errors,
      ) as file_handle:
    for line_number, line in enumerate(file_handle, start=1):
      if show_line_numbers:
        print(f"{line_number:>5}: {line}", end="")
      else:
        print(line, end="")
      ##endof:  if show_line_numbers
    ##endof:  for line_number, line in enumerate(...)
  ##endof:  with path.open(...) as file_handle
##endof:  print_file(...)
```

## File: `src/multimodal_jupy_logger/utils/__init__.py`

Save as:

```text
~/multimodal-jupy-logger/src/multimodal_jupy_logger/utils/__init__.py
```

```python
'''
Utility helpers for Multimodal Jupy Logger development.

@file   : __init__.py
          specifically, src/multimodal_jupy_logger/utils/__init__.py
@author : David Black        GitHub: @bballdave025     comments signed "DWB"
@since  : 2026-06-1x, mid-June 2026

Part of the `multimodal-jupy-logger` project, which can potentially be
a package.
'''

from . import path_display
from .path_display import (
  count_lines,
  print_file,
  tree,
)

__all__ = [
  "path_display",
  "count_lines",
  "print_file",
  "tree",
]

##endof:  __all__
```
