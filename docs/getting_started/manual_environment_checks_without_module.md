# Inline Environment Checks Without `environment_checks.py`

The recommended setup uses
`multimodal_jupy_logger.environment_checks`.

This fallback is useful when:

- `environment_checks.py` has not yet been transferred;
- testing an older MMJL snapshot;
- diagnosing source-transfer problems before importing the package.

```python
from pathlib import Path
import importlib.metadata
import importlib.util
import os
import platform
import sys

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


def package_version(package_name):
    try:
        return importlib.metadata.version(package_name)
    except importlib.metadata.PackageNotFoundError:
        return None
    ##endof:  try/except
##endof:  package_version(...)


def print_package_checks(title, packages):
    missing = []

    print(title)
    print("-" * len(title))

    for module_name, package_name in packages.items():
        found = (
            importlib.util.find_spec(module_name)
            is not None
        )

        version = package_version(package_name)

        if found:
            print(
                f"[FOUND]   {module_name:<16} "
                f"{str(version):<16} "
                f"pip: {package_name}"
            )
        else:
            missing.append(package_name)

            print(
                f"[MISSING] {module_name:<16} "
                f"{'':16} "
                f"pip: {package_name}"
            )
        ##endof:  if found
    ##endof:  for module_name, package_name in packages.items()

    print()

    return missing
##endof:  print_package_checks(...)


print("=" * 72)
print("MMJL / NOTEBOOK ENVIRONMENT CHECK")
print("=" * 72)
print("Python executable:", sys.executable)
print("Python version:   ", sys.version.replace("\n", " "))
print("Working directory:", Path.cwd())
print("Home directory:   ", Path.home())
print("Platform:         ", platform.platform())
print("Operating system: ", os.name)
print()

required_missing = print_package_checks(
    "Required packages",
    REQUIRED_PACKAGES,
)

optional_missing = print_package_checks(
    "Optional packages",
    OPTIONAL_PACKAGES,
)

if required_missing:
    install_text = " ".join(required_missing)

    raise RuntimeError(
        "Required packages are missing.\n\n"
        "Install into the active notebook kernel with:\n\n"
        f"  %pip install {install_text}\n\n"
        "Then restart the kernel and rerun this cell."
    )
##endof:  if required_missing

print("[PASS] Required notebook environment is ready.")
```

This fallback intentionally checks only the selected packages relevant to the
notebook. It is a compact, task-scoped alternative to a complete
`pip freeze`.
