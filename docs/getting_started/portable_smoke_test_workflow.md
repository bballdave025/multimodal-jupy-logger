# Portable Smoke-Test Workflow

Run the portable smoke test after recreating MMJL in a new notebook
environment.

The smoke test reinforces the standard operational sequence:

```text
transfer source
→ check environment and kernel
→ choose a notebook slug
→ inspect the target log state
→ register MMJL
→ capture notes, input, output, plots, and exceptions
→ validate
→ export HTML and Markdown
→ zip and download the complete log directory
```

Recommended smoke-test configuration:

```python
NOTEBOOK_SLUG = "portable_smoke_test"
USE_TIMESTAMP_IF_SLUG_EMPTY = True
ALLOW_DESTRUCTIVE_LOG_RESET = True
MARK_LOG_AS_DISPOSABLE = True
DESTRUCTIVE_RESET_DELAY_SECONDS = 7
```

Destructive reset has three guards:

1. it must be explicitly enabled;
2. the log must be marked as disposable;
3. an existing directory must contain the MMJL disposable-log sentinel.

A visible countdown gives the user time to interrupt the kernel before a
verified disposable directory is removed.

Expected final checks:

```text
Missing artifacts: 0
[PASS] Portable relative-path smoke test passed.
```

Before leaving SageMaker:

```bash
cd ~/mlu-wjupy-lab

zip -r \
  jupy_log_portable_smoke_test.zip \
  jupy_log_portable_smoke_test
```

Download that zip and verify that
`timelines/timeline.html` still displays linked artifacts after extraction.
