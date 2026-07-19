# Initial MMJL implementation: core logger, magics, portable paths,
# capture workflow, and SageMaker validation

## Summary

This is the first pull request for `multimodal-jupy-logger`, merging the
initial implementation branch `initial-code-and-pdf-and-tee` back into
`main`.

This PR establishes the first usable version of MMJL as a lightweight,
portable notebook logging tool. It adds the core logger, Jupyter magics,
artifact capture, manifest inspection and validation, Markdown and HTML
timeline generation, environment checks, portable source discovery, and the
first documented workflows for local Windows and AWS SageMaker/Jupyter use.

The main purpose is to make selected notebook work easier to preserve without
turning the whole notebook into the sole source of truth.

The intended durable unit is the complete notebook-specific log directory:

```text
jupy_log_<notebook_slug>/
├── artifacts/
├── staging/
├── timelines/
│   ├── timeline.html
│   └── timeline.md
└── manifest.tsv
```

When that directory is moved, zipped, downloaded, or archived as a unit, its
relative links continue to work.

## What changed

### Core logging

- Added the main `MultimodalJupyLogger` implementation.
- Added artifact logging for text, bytes, files, and MIME bundles.
- Added persistent artifact and capture sequencing.
- Added a tab-separated manifest for logged artifacts.
- Added manifest inspection and validation helpers.
- Preserved artifact bytes and MIME metadata separately from rendering.
- Kept capture, persistence, replay, and transformation as separate concerns.

The bytes-plus-MIME approach allows notebook output to be preserved without
requiring the logger to understand every media library or rendering frontend.

### MIME-aware artifact persistence

MMJL records notebook outputs as MIME-aware artifacts rather than treating all
output as undifferentiated text.

Current examples include:

- `text/plain`
- `text/html`
- Markdown
- `image/png`
- `image/jpeg`
- source input
- stdout
- stderr
- traceback and exception text
- arbitrary existing files

This makes it possible for replay mechanisms to evolve independently of
capture mechanisms.

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

The capture magics can execute cells while logging selected input, output,
rich display data, stdout, stderr, and exceptions.

### Literal notes

`%%jupy_log` stores literal cell contents without executing them.

A label is optional. Unlabeled notes use the automatic `cell` labeling path,
which keeps quick notebook observations low-friction while still producing
stable manifest entries and filenames.

### Capture and pin modes

Added selected-memory capture options:

```text
--pin
--pin-input
--pin-output
--label NAME
--jupy-display on|off
```

Intended behavior:

```text
--pin
  capture input + output, automatic pin label

--pin-input
  capture input only, automatic label unless --label is supplied

--pin-output
  capture output only, automatic label unless --label is supplied

--label NAME
  deliberate human-readable name

--label NAME with no explicit pin mode
  automatically behaves like --pin

--jupy-display off
  capture output without replaying it into the notebook
```

Only one of `--pin`, `--pin-input`, and `--pin-output` may be used at a
time.

### Hidden-output capture

The following pattern is useful for verbose material that belongs in the
research record but should not crowd the notebook:

```python
%%jupy_capture \
    --label model-training \
    --jupy-display off

history = model.fit(
    train_x,
    train_y,
    epochs=50,
    verbose=1,
)
```

This captures input, stdout, stderr, displayed values, rich output, and
exceptions while suppressing normal replay into the notebook.

Useful examples include:

- model-training logs
- hyperparameter searches
- package-installation output
- verbose diagnostics
- large tables
- exploratory debugging output

### Automatic labels

When explicit labels are omitted, MMJL generates deterministic,
monotonically increasing labels such as:

```text
pin-000001
pin-000002
pin-000003
```

Automatic labeling keeps capture friction low while maintaining stable,
inspectable references in manifests and exported timelines.

Explicit labels remain recommended for important milestones and reference
artifacts.

### Failure-tolerant exception preservation

If a captured cell raises an exception, MMJL preserves:

- the input cell
- stdout generated before failure
- exception and traceback output
- related metadata and ordering

The cell still fails normally in Jupyter. MMJL preserves the failure rather
than converting it into a silent success or discarding the partial execution
history.

This behavior has already proven useful in exploratory work, including
iterative attempts to define and use notebook magics and aliases.

### Quiet magic behavior

Updated line and cell magics so they return `None` instead of displaying
internal Python objects such as `Path(...)`, lists of paths, or validation
lists in the notebook output area.

The underlying logger methods still return useful objects for direct Python
use, but the notebook magic wrappers avoid visual clutter.

### Configurable and portable log roots

Added support for registering MMJL with an explicit log root:

```python
from pathlib import Path
from multimodal_jupy_logger import register_jupy_logger

register_jupy_logger(
    root=Path.cwd() / "jupy_log_example",
)
```

Current documentation recommends a notebook-specific slug:

```python
NOTEBOOK_SLUG = "mlu_jupyter_magics_l01"

log_root = (
    Path.cwd()
    / f"jupy_log_{NOTEBOOK_SLUG}"
)
```

This makes continuation and archive boundaries visible near the top of the
notebook.

### Continuation-friendly logging

MMJL supports notebooks that span multiple sessions or days.

If the selected log root already contains an MMJL manifest, the setup
workflow reports that state and allows MMJL to continue appending to the
existing history.

This makes a log directory an evolving research record rather than disposable
scratch output.

A new notebook or investigation should normally use a new descriptive slug.

### Guarded destructive smoke-test reset

Real notebook logs are non-destructive by default.

The portable smoke test may use a destructive reset, but the documented
workflow requires all of the following:

- explicit Boolean opt-in
- the log marked as disposable
- a disposable-log sentinel inside the target directory
- a visible countdown
- an opportunity to interrupt the kernel before deletion

A target directory without the sentinel is refused rather than deleted.

This allows `Run All` to remain possible while preventing an accidental
Boolean change or incorrect `log_root` from removing an unrelated directory.

### Root-relative manifest paths

Updated manifest writing so artifact paths are stored relative to the MMJL
log root when possible.

Example:

```text
artifacts/000001_cell-input.py
```

instead of a machine-specific absolute path.

This makes the complete `jupy_log_<slug>/` directory portable between
machines and environments.

### Timeline-relative artifact links

Updated Markdown and HTML timeline generation so exported timelines link to
artifacts relative to the timeline file location.

For example, a timeline in:

```text
jupy_log_example/timelines/timeline.html
```

can link to artifacts using paths like:

```text
../artifacts/...
```

This allows the generated timelines to continue working after moving,
zipping, downloading, or extracting the complete log directory.

### Environment checks

Added notebook-oriented environment checks intended to run near the top of a
notebook before MMJL registration.

The report includes:

- Python executable
- Python version
- active IPython/kernel implementation
- working directory
- home directory
- platform and operating-system information
- required-package availability and versions
- optional investigation-package availability and versions
- optional import locations
- structured return values for later logging or programmatic inspection

Notebook-local package maps make assumptions visible:

```python
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
```

After MMJL registration, the report can be captured as a compact,
task-scoped provenance record:

```python
%%jupy_capture \
    --label environment-check \
    --pin-output

print_environment_check(
    required_packages=REQUIRED_PACKAGES,
    investigation_packages=OPTIONAL_PACKAGES,
    show_import_paths=False,
)
```

This provides a focused alternative to filling the notebook timeline with a
complete `pip freeze`.

### Portable source discovery

The setup cells support both:

```python
USE_EXPLICIT_MMJL_SRC = True
```

for a Windows or local development checkout, and:

```python
USE_EXPLICIT_MMJL_SRC = False
```

for a SageMaker-style sibling layout:

```text
~
├── multimodal-jupy-logger/
│   └── src/
│       └── multimodal_jupy_logger/
└── mlu-wjupy-lab/
    └── some_course_notebook.ipynb
```

The source path remains explicit and visible in the notebook rather than being
hidden behind an installation process during the current drop-in MVP phase.

### High-resolution artifact workflow

Notebook display bundles are useful for normal capture, but archival figures
may require a deliberately higher-resolution artifact.

The documented pattern is:

```python
plt.savefig(
    "plot_300dpi.png",
    dpi=300,
    bbox_inches="tight",
)
```

followed by:

```python
%jupy_file \
  --label high-resolution-plot \
  plot_300dpi.png
```

This preserves the explicitly generated file independently of the notebook
frontend's normal display resolution.

### Documentation and transfer artifacts

Added or prepared:

- expanded root README usage guidance
- SageMaker portable setup instructions
- Windows explicit-source setup instructions
- portable smoke-test workflow
- fallback inline environment checks
- setup-email transfer artifacts
- complete notebook JSON transfer workflow
- portable smoke-test notebook
- development notes for PDF and future CLI directions

The email-copy workflow allows the current source and smoke-test notebook to
be reconstructed in SageMaker without Git access, while keeping the personal
Git repository as the canonical source of truth.

## Recommended notebook startup workflow

The preferred startup pattern is now:

1. locate MMJL source;
2. inspect executable, kernel, and environment;
3. choose a notebook-specific slug;
4. derive and print the intended log root;
5. inspect existing directory and manifest state;
6. apply non-destructive or guarded smoke-test policy;
7. register MMJL;
8. rerun and capture the environment report;
9. begin selective notebook capture.

These choices remain visible in setup cells because they are meaningful
notebook state and policy, not incidental implementation details.

## Intended usage example

### Setup

```python
from pathlib import Path
import importlib
import sys

USE_EXPLICIT_MMJL_SRC = False

mmjl_src = (
    Path.home()
    / "multimodal-jupy-logger"
    / "src"
)

if str(mmjl_src) not in sys.path:
    sys.path.insert(0, str(mmjl_src))
##endof:  if str(mmjl_src) not in sys.path

importlib.invalidate_caches()

from multimodal_jupy_logger import (
    print_environment_check,
    register_jupy_logger,
)

NOTEBOOK_SLUG = "mlu_jupyter_magics_l01"

log_root = (
    Path.cwd()
    / f"jupy_log_{NOTEBOOK_SLUG}"
)

register_jupy_logger(
    root=log_root,
)
```

### Literal note

```python
%%jupy_log --mime text/markdown
### Question

Why does the dual basis appear naturally here?
```

### Capture input and output

```python
%%jupy_capture --label first-test-cell
print("hello MMJL")
```

### Capture output only

```python
%%jupy_capture --pin-output
display(...)
```

### Capture without notebook replay

```python
%%jupy_capture \
    --label training-details \
    --jupy-display off

print("verbose output preserved only in the MMJL record")
```

### Validate and export

```python
%jupy_save
%jupy_inspect
%jupy_validate
%jupy_markdown
%jupy_html
```

To stop using MMJL, stop adding MMJL magics to cells.

## Testing completed

### Windows

Completed using a dedicated virtual environment and an external notebook
pointed at the canonical repository source.

Confirmed:

- core package import
- public symbol imports
- optional PDF-module import safety
- plain-Python `register_pdf_magics()` returns `False`
- command-line help for the PDF module
- package source compilation
- logger registration
- literal-note logging
- pin-family behavior
- hidden internal return values
- rich display and image capture
- exception capture and continued kernel use
- manifest validation
- Markdown export
- HTML export
- root-relative manifest paths
- timeline-relative artifact links

### AWS SageMaker / Jupyter

Completed using the intended sibling-directory source layout and the
provisioned notebook kernel.

Confirmed:

- email/copy-paste source reconstruction works
- MMJL and the course workspace remain separate
- package imports work from the portable source tree
- the default course kernel can run MMJL
- log directories remain inside the intended course workspace
- literal notes, pin modes, plot capture, and exception capture work
- `manifest.tsv` is generated
- Markdown and HTML timelines are generated
- `%jupy_validate` reports zero missing artifacts
- the complete log directory can be zipped and downloaded
- `timeline.html` continues working after extraction on another machine
- linked plot artifacts remain visible after transfer
- no unexpected MMJL writes outside the intended home/course directories
  were observed

### Real course-notebook use

MMJL has also been used successfully for an actual MLU lecture notebook.

The resulting record preserved:

- iterative notebook-magic experiments
- failed attempts
- exception traces
- successful results
- narrative notes
- ordered input and output artifacts

This was the first practical use beyond the dedicated smoke test and supports
the current MVP boundary.

## Testing checklist

### Core source and imports

- [x] Run package source compilation checks.
- [x] Confirm the package root imports.
- [x] Confirm public logger symbols import.
- [x] Confirm optional PDF helper imports do not break core package imports.
- [x] Confirm PDF magic registration fails safely outside IPython.
- [x] Confirm PDF module command-line help loads.

### Notebook behavior

- [x] Run a local Windows notebook smoke test.
- [x] Confirm `register_jupy_logger(root=...)` works.
- [x] Confirm `%%jupy_log` logs literal cell text without execution.
- [x] Confirm `%%jupy_capture` logs input and output.
- [x] Confirm `%%jupy_tee` displays output while logging it.
- [x] Confirm `--pin` captures input and output.
- [x] Confirm `--pin-input` captures input only.
- [x] Confirm `--pin-output` captures output only.
- [x] Confirm `--label NAME` without an explicit pin mode behaves like
      `--pin`.
- [x] Confirm mutually exclusive pin arguments reject invalid combinations.
- [x] Confirm `--jupy-display off` logs output without replaying it into the
      notebook.
- [x] Confirm magic commands do not display unwanted Python return objects.
- [x] Confirm captured exceptions preserve input, partial stdout, and
      traceback information.
- [x] Confirm the kernel remains usable after an expected captured exception.

### Portability and export

- [x] Confirm manifest paths are root-relative for artifacts inside the log
      root.
- [x] Confirm `%jupy_validate` resolves root-relative paths correctly.
- [x] Confirm `%jupy_markdown` produces relative artifact links.
- [x] Confirm `%jupy_html` produces relative artifact links.
- [x] Confirm generated timelines work after moving or downloading the
      complete log directory.
- [x] Confirm downloaded HTML timelines display linked images on another
      machine.

### Platform testing

- [x] Test on Windows.
- [x] Test in AWS SageMaker/Jupyter Linux.
- [x] Confirm portable source discovery works in the intended SageMaker
      layout.
- [x] Confirm the existing course kernel can be augmented with MMJL without
      reconstructing all course dependencies.
- [x] Confirm a real course lecture can be captured successfully.
- [ ] Run the final SageMaker smoke test using the committed
      `environment_checks.py` and canonical updated smoke-test notebook.
- [ ] Merge after the final SageMaker test unless an unforeseen regression is
      found.

## PDF export status

`jupy_pdf_utils.py` remains included as an optional, experimental module.

Verified in this PR:

- importing the module from plain Python succeeds;
- requesting module help succeeds;
- public PDF symbols import successfully;
- magic registration fails safely when no IPython shell is active;
- importing the main `multimodal_jupy_logger` package does not trigger PDF
  rendering or browser provisioning.

Not required for this PR:

- successful PDF rendering on every supported environment;
- Playwright or browser provisioning;
- reliable active-notebook detection in every Jupyter frontend;
- PDF export from every SageMaker course kernel.

HTML remains the preferred primary timeline format because it preserves
multimodal output and relative artifact links naturally.

## Known limitations and follow-up work

- PDF export is not part of the success criteria for this PR.
- Windows PDF export may require separate work around `nbconvert`,
  Playwright, Chromium provisioning, and asyncio event-loop behavior.
- HTML timeline math rendering may eventually benefit from MathJax or KaTeX.
- `--pin-input` currently logs only input, even when the cell raises. This
  matches the literal meaning of input-only capture, but a future design may
  preserve exception artifacts as additional context.
- The current drop-in workflow requires explicit setup cells rather than an
  installed-package experience.
- Notebook filename detection is not yet part of the environment report.
- Source-transfer emails are generated from committed source but are not
  themselves an installation or packaging system.

## Future directions

The current implementation intentionally focuses on a small, understandable,
portable core. The following ideas appear useful but were deliberately
deferred so they do not block the first merge.

### Environment-reporting additions

Possible later additions to `environment_checks.py` include:

- CUDA availability
- `torch.cuda.device_count()` reporting
- GPU model information
- git commit hash
- git branch
- repository dirty/clean state
- notebook filename detection
- conda environment name
- active kernel display name
- active Jupyter kernel identifier
- SageMaker image information
- available CPU count
- available memory

These are convenience and provenance enhancements rather than missing MVP
functionality.

### Registration policy

The current design keeps notebook policy visible in notebook setup cells.

Examples include:

- notebook slug selection
- continuation vs. new-log decisions
- destructive reset policy
- disposable smoke-test behavior
- environment and package requirements

A possible future direction is to support policy through registration
parameters:

```python
register_jupy_logger(
    root=log_root,
    notebook_slug=NOTEBOOK_SLUG,
    allow_existing=True,
    disposable=False,
)
```

or:

```python
register_jupy_logger(
    root=log_root,
    smoke_test=True,
)
```

The setup-cell approach was chosen for the MVP because it keeps important
state visible near the top of the notebook and encourages deliberate choices
about naming, continuation, and deletion.

### Environment-aware requirements

The current design expects notebooks to declare their own relevant package
maps.

A future direction could inspect selected `requirements*.txt` files or support
named environment bundles such as:

```text
requirements.txt
requirements-ml.txt
requirements-experimental-pdf.txt
requirements-all-experimental.txt
```

The current explicit notebook-local maps remain useful because they document
the requirements of the actual notebook rather than every possible MMJL
feature.

### Packaging and CLI

Possible later work includes:

```text
mmjl html export
mmjl pdf export
mmjl validate
mmjl inspect
mmjl archive
```

Future Python packaging may make MMJL installable rather than relying on
drop-in source discovery.

Interfaces should remain thin wrappers over common transformation backends.

### Math rendering

A future HTML enhancement may add MathJax or KaTeX support so LaTeX inside
Markdown notes renders directly in the timeline and in browser-generated PDFs.

The source Markdown and LaTeX are already preserved, so this is a rendering
enhancement rather than a preservation blocker.

### Long-running notebook workflows

Possible later additions include:

- explicit session boundaries
- continuation summaries
- log merging
- archive helpers
- automatic archive naming
- resumable state summaries
- notebook-to-log association metadata

### Richer examples and portfolio presentation

The README and examples may later include:

- a compact architecture diagram
- a failure-preservation example
- an automatic-label example
- a high-resolution plot example
- an MLU lecture-capture example
- links from a presentation/portfolio repository
- a concise developer-skills description for promotion or job applications

## Commit boundary

This PR establishes the first working MMJL foundation.

```text
Included:
  - core logger
  - Jupyter magics
  - text, bytes, file, and MIME-aware capture
  - capture and tee workflows
  - root-configurable logging
  - root-relative manifest paths
  - timeline-relative artifact links
  - quiet magic wrappers
  - pin modes
  - hidden-output capture
  - exception preservation
  - deterministic automatic labels
  - environment checks
  - continuation-friendly notebook setup
  - guarded disposable smoke-test reset
  - portable Windows and SageMaker source workflows
  - portable smoke-test notebook
  - initial README and getting-started documentation
  - experimental PDF helper kept import-safe

Not required:
  - fully reliable cross-platform PDF export
  - finalized packaging
  - complete CLI surface
  - automatic notebook filename detection
  - GPU/SageMaker-specific provenance reporting
  - MathJax-enabled timeline rendering
```

Unless the final committed-source SageMaker test reveals an unforeseen
regression, this branch is ready to merge.
