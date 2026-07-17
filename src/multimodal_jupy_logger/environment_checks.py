'''
Environment checks for Multimodal Jupy Logger notebooks.

@file   : environment_checks.py
@author : David Black        GitHub: @bballdave025     comments signed "DWB"
@since  : 2026-07-13

Part of the `multimodal-jupy-logger` project, which can potentially be
a package.
'''

from __future__ import annotations

import importlib
import importlib.metadata
import importlib.util
import os
import platform
import sys
from pathlib import Path
from typing import Mapping

from IPython import get_ipython


PackageMap = Mapping[str, str]


def _package_version(package_name: str) -> str | None:
  '''
  Return an installed distribution version when available.
  '''

  try:
    return importlib.metadata.version(package_name)
  except importlib.metadata.PackageNotFoundError:
    return None
  ##endof:  try/except
##endof:  _package_version(...)


def _kernel_description() -> str:
  '''
  Return a compact description of the active IPython kernel.
  '''

  ipython_shell = get_ipython()

  if ipython_shell is None:
    return "No active IPython shell"
  ##endof:  if ipython_shell is None

  shell_name = type(ipython_shell).__name__
  kernel = getattr(ipython_shell, "kernel", None)

  if kernel is None:
    return shell_name
  ##endof:  if kernel is None

  return (
      f"{shell_name} / "
      f"{type(kernel).__name__}"
  )
##endof:  _kernel_description(...)


def check_packages(
      packages: PackageMap,
    ) -> dict[str, dict[str, str | bool | None]]:
  '''
  Check import availability and installed distribution versions.

  ``packages`` maps an importable module name to its pip/distribution
  package name.

  Example:

  {
      "sklearn": "scikit-learn",
      "IPython": "ipython",
  }
  '''

  results = {}

  for module_name, package_name in packages.items():
    module_spec = importlib.util.find_spec(module_name)
    found = module_spec is not None
    import_path = None
    import_error = None
    version = _package_version(package_name)

    if found:
      try:
        module = importlib.import_module(module_name)
        import_path = getattr(module, "__file__", None)
      except Exception as error:
        found = False
        import_error = (
            f"{type(error).__name__}: {error}"
        )
      ##endof:  try/except
    ##endof:  if found

    results[module_name] = {
        "found": found,
        "package": package_name,
        "version": version,
        "import_path": import_path,
        "import_error": import_error,
    }
  ##endof:  for module_name, package_name in packages.items()

  return results
##endof:  check_packages(...)


def print_package_checks(
      title: str,
      packages: PackageMap,
    ) -> list[str]:
  '''
  Print visible package checks and return missing package names.
  '''

  results = check_packages(packages)
  missing_packages = []

  print(title)
  print("-" * len(title))

  for module_name, result in results.items():
    package_name = str(result["package"])
    version = result["version"]
    import_error = result["import_error"]

    if result["found"]:
      version_text = (
          str(version)
          if version is not None
          else "version unknown"
      )

      print(
          f"[FOUND]   {module_name:<16} "
          f"{version_text:<16} "
          f"pip: {package_name}"
      )
    else:
      missing_packages.append(package_name)

      print(
          f"[MISSING] {module_name:<16} "
          f"{'':16} "
          f"pip: {package_name}"
      )

      if import_error is not None:
        print(f"          import error: {import_error}")
      ##endof:  if import_error is not None
    ##endof:  if result["found"]
  ##endof:  for module_name, result in results.items()

  print()

  if missing_packages:
    print("Missing pip packages:")
    print("  " + " ".join(missing_packages))
  else:
    print("Missing pip packages: none")
  ##endof:  if missing_packages

  return missing_packages
##endof:  print_package_checks(...)


def print_environment_check(
      *,
      required_packages: PackageMap | None = None,
      investigation_packages: PackageMap | None = None,
      show_import_paths: bool = False,
    ) -> dict[str, object]:
  '''
  Print a visible environment and dependency report.

  Returns a structured dictionary so callers may inspect or log the same
  information programmatically.
  '''

  required_packages = required_packages or {}
  investigation_packages = investigation_packages or {}

  report = {
      "python_executable": sys.executable,
      "python_version": sys.version.replace("\n", " "),
      "platform": platform.platform(),
      "operating_system": os.name,
      "working_directory": str(Path.cwd()),
      "home_directory": str(Path.home()),
      "kernel": _kernel_description(),
      "required": check_packages(required_packages),
      "investigation": check_packages(
          investigation_packages
      ),
  }

  print("=" * 72)
  print("MMJL / NOTEBOOK ENVIRONMENT CHECK")
  print("=" * 72)
  print(f"Python executable: {report['python_executable']}")
  print(f"Python version:    {report['python_version']}")
  print(f"Kernel:            {report['kernel']}")
  print(f"Working directory: {report['working_directory']}")
  print(f"Home directory:    {report['home_directory']}")
  print(f"Platform:          {report['platform']}")
  print()

  required_missing = print_package_checks(
      "Required packages",
      required_packages,
  )

  investigation_missing = print_package_checks(
      "Optional investigation packages",
      investigation_packages,
  )

  if show_import_paths:
    print()
    print("Import locations")
    print("----------------")

    combined_results = {
        **report["required"],
        **report["investigation"],
    }

    for module_name, result in combined_results.items():
      import_path = result["import_path"]

      if import_path is not None:
        print(f"{module_name}:")
        print(f"  {import_path}")
      ##endof:  if import_path is not None
    ##endof:  for module_name, result in combined_results.items()
  ##endof:  if show_import_paths

  print()
  print("Summary")
  print("-------")
  print(
      "Required packages: "
      + (
          "PASS"
          if not required_missing
          else "MISSING"
      )
  )
  print(
      "Investigation packages: "
      + (
          "AVAILABLE"
          if not investigation_missing
          else "PARTIAL / OPTIONAL"
      )
  )
  print("=" * 72)

  report["required_missing"] = required_missing
  report["investigation_missing"] = (
      investigation_missing
  )

  return report
##endof:  print_environment_check(...)