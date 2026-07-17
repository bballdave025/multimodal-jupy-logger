# Email 01 — MMJL SageMaker Transfer and Setup Instructions

Suggested subject:

> MMJL SageMaker transfer and setup instructions

## Target SageMaker layout

```text
~
├── multimodal-jupy-logger/
│   ├── README.md
│   ├── LICENSE
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
│           ├── mmjl_cli.py
│           ├── jupy_pdf_utils.py
│           └── utils/
│               ├── __init__.py
│               └── path_display.py
│
└── mlu-wjupy-lab/
    └── mmjl_portable_smoke_test.ipynb
```

The course directory may have a different name. Replace
`mlu-wjupy-lab` with the actual course directory when necessary.

## Create directories

```bash
mkdir -p \
  ~/multimodal-jupy-logger/src/multimodal_jupy_logger/utils

mkdir -p \
  ~/mlu-wjupy-lab
```

## Create the files

```bash
touch \
  ~/multimodal-jupy-logger/README.md \
  ~/multimodal-jupy-logger/LICENSE \
  ~/multimodal-jupy-logger/requirements.txt \
  ~/multimodal-jupy-logger/requirements-ml.txt \
  ~/multimodal-jupy-logger/requirements-experimental-pdf.txt \
  ~/multimodal-jupy-logger/requirements-all-experimental.txt \
  ~/multimodal-jupy-logger/src/multimodal_jupy_logger/__init__.py \
  ~/multimodal-jupy-logger/src/multimodal_jupy_logger/environment_checks.py \
  ~/multimodal-jupy-logger/src/multimodal_jupy_logger/logger.py \
  ~/multimodal-jupy-logger/src/multimodal_jupy_logger/magics.py \
  ~/multimodal-jupy-logger/src/multimodal_jupy_logger/metadata.py \
  ~/multimodal-jupy-logger/src/multimodal_jupy_logger/mmjl_cli.py \
  ~/multimodal-jupy-logger/src/multimodal_jupy_logger/jupy_pdf_utils.py \
  ~/multimodal-jupy-logger/src/multimodal_jupy_logger/utils/__init__.py \
  ~/multimodal-jupy-logger/src/multimodal_jupy_logger/utils/path_display.py \
  ~/mlu-wjupy-lab/mmjl_portable_smoke_test.ipynb
```

## Paste the transferred contents

Use the remaining emails in order:

1. Email 02 contains the complete notebook JSON.
2. Emails 03–06 contain all transferred repository-file contents.

For each file section:

1. Open the destination file in the SageMaker editor.
2. Paste only the contents inside its code fence.
3. Save the file.
4. Continue with the next section.

## Kernel and dependency policy

Open the actual course notebook or smoke-test notebook using the kernel
already provisioned for the course.

The course kernel already contains the lesson-specific dependencies. MMJL is
the additional layer.

The smoke-test notebook:

- prints the Python executable;
- prints Python and kernel information;
- checks required packages;
- reports optional investigation packages;
- tells the user which `%pip install ...` command would be required if a
  required package is missing;
- does not silently install packages.

## Run the smoke test

Open:

```text
~/mlu-wjupy-lab/mmjl_portable_smoke_test.ipynb
```

Restart the kernel and clear outputs.

Run incrementally the first time.

The notebook uses:

```python
USE_EXPLICIT_MMJL_SRC = False
```

and should discover:

```text
~/multimodal-jupy-logger/src
```

The expected smoke-test slug is:

```text
portable_smoke_test
```

The resulting log root is:

```text
jupy_log_portable_smoke_test/
```

The exception test intentionally raises a `ValueError`. Continue manually
after that cell.

## Destructive-reset safety

The smoke-test log is disposable, but an existing directory is deleted only
when all of these conditions are true:

- destructive reset is explicitly enabled;
- the log is explicitly marked disposable;
- the expected disposable sentinel exists;
- the visible countdown completes without the kernel being interrupted.

A directory without the sentinel is refused rather than deleted.

Real course and personal notebooks should use:

```python
ALLOW_DESTRUCTIVE_LOG_RESET = False
MARK_LOG_AS_DISPOSABLE = False
```

## Expected success markers

Look for:

```text
[PASS] Required notebook environment is ready.
[DONE] MMJL registered.
Missing artifacts: 0
[PASS] Portable relative-path smoke test passed.
```

The notebook should create:

```text
jupy_log_portable_smoke_test/
├── artifacts/
├── staging/
├── timelines/
│   ├── timeline.html
│   └── timeline.md
└── manifest.tsv
```

## Zip and download the portable record

Try installing `zip`, even if SageMaker reports it is already installed:

```bash
sudo apt install zip
```

Move to the course directory:

```bash
cd ~/mlu-wjupy-lab/
```

Create the archive:

```bash
zip -r \
  jupy_log_portable_smoke_test.zip \
  ./jupy_log_portable_smoke_test/
```

In the JupyterLab GUI, select:

```text
~/mlu-wjupy-lab/jupy_log_portable_smoke_test.zip
```

and click the download button, `⤓`.

After extraction on another machine, open:

```text
jupy_log_portable_smoke_test/timelines/timeline.html
```

The plot and other linked artifacts should still render.

## Real notebook use

For each course or personal notebook:

1. keep the notebook's provisioned kernel;
2. add the source-discovery and environment-check cells near the top;
3. choose a descriptive `NOTEBOOK_SLUG`;
4. keep destructive reset disabled;
5. register MMJL;
6. capture the environment report;
7. log only useful notes, inputs, outputs, failures, and artifacts;
8. validate and export;
9. zip and download the complete notebook-specific `jupy_log_*` directory.

To stop using MMJL, stop adding MMJL magics to cells.
