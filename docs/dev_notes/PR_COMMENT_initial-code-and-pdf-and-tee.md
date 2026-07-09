nitial MMJL implementation: core logger, magics, portable paths, and capture workflow

## Summary

This is the first pull request for `multimodal-jupy-logger`, merging the initial implementation branch `initial-code-and-pdf-and-tee` back into `main`.

This PR establishes the first usable version of MMJL as a lightweight notebook logging tool. It adds the core logger, Jupyter magics, timeline generation, artifact capture, and the first portability improvements needed for moving logs between local notebooks and AWS SageMaker/Jupyter environments.

The main purpose is to make selected notebook work easier to preserve without turning the whole notebook into the source of truth.

## What changed

### Core logging

- Added the main `MultimodalJupyLogger` implementation.
- Added artifact logging for text, bytes, files, and MIME bundles.
- Added persistent artifact and capture sequencing.
- Added a tab-separated manifest for logged artifacts.
- Added manifest inspection and validation helpers.

### Jupyter magics

Added notebook-facing magics:

- `%jupy_save`
- `%jupy_file`
- `%%jupy_log`
- `%%jupy_capture`
- `%%jupy_tee`
- `%jupy_markdown`
- `%jupy_html`
- `%jupy_inspect`
- `%jupy_validate`

The capture magics can now execute cells while logging selected input, output, rich display data, stdout, stderr, and exceptions.

### Quiet magic behavior

Updated line and cell magics so they return `None` instead of displaying internal Python objects such as `Path(...)`, lists of paths, or validation lists in the notebook output area.

The underlying logger methods still return useful objects for direct Python use, but the notebook magic wrappers avoid visual clutter.

### Portable log roots

Added support for registering MMJL with an explicit log root:

```python
from pathlib import Path
from multimodal_jupy_logger import register_jupy_logger

register_jupy_logger(root=Path.cwd() / "jupy_log")
```

This makes MMJL easier to drop into local Jupyter, VS Code notebooks, and AWS SageMaker/Jupyter environments without needing an installed package workflow first.

### Root-relative manifest paths

Updated manifest writing so artifact paths are stored relative to the MMJL log root when possible.

Example:

```text
artifacts/000001_cell-input.py
```

instead of a machine-specific absolute path.

This makes a complete `jupy_log/` directory more portable between machines and environments.

### Timeline-relative artifact links

Updated Markdown and HTML timeline generation so exported timelines link to artifacts relative to the timeline file location.

For example, a timeline in:

```text
jupy_log/timelines/timeline.html
```

can link to artifacts using paths like:

```text
../artifacts/...
```

This helps the generated timeline continue to work after moving or downloading the whole log directory.

### Pin modes

Added selected-memory capture options:

```text
--pin
--pin-input
--pin-output
--label NAME
```

Intended behavior:

```text
--pin
  capture input + output, auto label

--pin-input
  capture input only, auto label unless --label supplied

--pin-output
  capture output only, auto label unless --label supplied

--label NAME
  deliberate human-readable name

--label NAME with no pin mode
  automatically behaves like --pin
```

Only one of `--pin`, `--pin-input`, and `--pin-output` may be used at a time.

### PDF notes

PDF export utilities are present in the repo, but working PDF export is not required for this PR.

A development note was added for Windows PDF debugging and future PDF work:

```text
docs/dev_notes/dev_tip_-_windows_pdf_debug.md
```

PDF export should be treated as optional/follow-up work until import safety and platform behavior are confirmed.

## Intended usage example

In a notebook:

```python
from pathlib import Path
import sys

mmjl_src = Path.home() / "multimodal-jupy-logger" / "src"

if str(mmjl_src) not in sys.path:
  sys.path.insert(0, str(mmjl_src))
##endof:  if str(mmjl_src) not in sys.path

from multimodal_jupy_logger import register_jupy_logger

register_jupy_logger(root=Path.cwd() / "jupy_log")
```

Then:

```python
%%jupy_capture --label first-test-cell
print("hello MMJL")
```

or:

```python
%%jupy_capture --pin-output
display(...)
```

Generate timelines:

```python
%jupy_validate
%jupy_markdown
%jupy_html
```

## Testing checklist

- [ ] Run `python -m py_compile` against package source files.
- [ ] Run a minimal local notebook smoke test.
- [ ] Confirm `register_jupy_logger(root=Path.cwd() / "jupy_log")` works.
- [ ] Confirm `%%jupy_log` logs literal cell text without execution.
- [ ] Confirm `%%jupy_capture` logs input and output.
- [ ] Confirm `%%jupy_tee` displays output while logging it.
- [ ] Confirm `--pin` captures input and output.
- [ ] Confirm `--pin-input` captures input only.
- [ ] Confirm `--pin-output` captures output only.
- [ ] Confirm `--label NAME` without an explicit pin mode behaves like `--pin`.
- [ ] Confirm mutually exclusive pin arguments reject invalid combinations.
- [ ] Confirm magic commands do not display unwanted Python return objects.
- [ ] Confirm manifest paths are root-relative when artifacts are inside the log root.
- [ ] Confirm `%jupy_validate` resolves root-relative manifest paths correctly.
- [ ] Confirm `%jupy_markdown` produces a timeline with relative artifact links.
- [ ] Confirm `%jupy_html` produces a timeline with relative artifact links.
- [ ] Confirm generated timelines still work after moving/downloading the whole `jupy_log/` directory.
- [ ] Test on Windows laptop.
- [ ] Test in AWS SageMaker/Jupyter Linux environment.
- [ ] Confirm PDF helper imports do not break core package imports.
- [ ] Decide whether PDF helpers should be exported from package root in this PR or a later one.

## Known limitations / follow-up work

- PDF export is not part of the success criteria for this PR.
- Windows PDF export may require separate debugging around `nbconvert`, Playwright, and asyncio event loop behavior.
- A cleaner committed smoke-test notebook may be added later.
- Additional documentation should be added after the first working notebook/SageMaker pass.
- Richer examples and README usage instructions can follow once the core API stabilizes.
- `--pin-input` currently logs only the input artifact, even if the cell raises an exception. This matches the literal meaning of “input only,” so it should not block this PR. However, a follow-up design decision is needed: `--pin-input` may eventually log input plus any exception artifact, since an error is often important context for why that input cell was worth preserving.

## Commit boundary

This PR is intended to establish the first working MMJL foundation:

```text
Included:
  - core logger
  - Jupyter magics
  - capture / tee workflow
  - root-configurable logging
  - root-relative manifest paths
  - timeline-relative artifact links
  - quiet magic wrappers
  - pin modes

Not required:
  - fully working PDF export
  - finalized docs
  - finalized example notebooks
  - packaging polish
```


