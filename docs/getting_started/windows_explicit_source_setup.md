# Windows Explicit-Source Setup

Use this mode when the notebook is outside the repository but should execute
the canonical MMJL source from a local development checkout.

```python
USE_EXPLICIT_MMJL_SRC = True

EXPLICIT_MMJL_SRC = Path(
    r"D:\David\my_repos_dwb\multimodal-jupy-logger\src"
)
```

Use the same environment-check, slug, log-policy, registration, and
end-of-session cells documented in
[`sagemaker_portable_setup.md`](sagemaker_portable_setup.md).

The source-selection Boolean is the main difference:

```text
Windows development:
  USE_EXPLICIT_MMJL_SRC = True

SageMaker / portable sibling layout:
  USE_EXPLICIT_MMJL_SRC = False
```

For an independent Windows test, create a dedicated venv, install the desired
requirements file, register an IPython kernel, and select that kernel in
JupyterLab.

```powershell
python -m venv .venv_mmjl_test

.\.venv_mmjl_test\Scripts\Activate.ps1

python -m pip install `
  -r .\requirements.txt

python -m ipykernel install `
  --user `
  --name mmjl-test `
  --display-name "Python (MMJL test)"
```

Verify the selected notebook kernel by checking the Python executable in the
environment report.
