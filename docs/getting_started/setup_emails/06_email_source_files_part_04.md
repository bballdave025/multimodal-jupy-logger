# MMJL Source Transfer — Part 4 of 4

For each section, open the stated destination file, paste only the contents inside its code fence, and save the file.

## File: `src/multimodal_jupy_logger/environment_checks.py`

Save as:

```text
~/multimodal-jupy-logger/src/multimodal_jupy_logger/environment_checks.py
```

```python
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
```

## File: `src/multimodal_jupy_logger/jupy_pdf_utils.py`

Save as:

```text
~/multimodal-jupy-logger/src/multimodal_jupy_logger/jupy_pdf_utils.py
```

```python
from __future__ import annotations

'''
Standalone PDF backup utility for Jupyter notebooks.

@file   : jupy_pdf_utils.py
@author : David Black        GitHub: @bballdave025     comments signed "DWB"
@since  : 2026-06-11

Standalone PDF backup utility for Jupyter notebooks. STILL EXPERIMENTAL

This module is intentionally usable as a drop-in side module inside
`multimodal_jupy_logger`.

Main uses:

  Python:
    from multimodal_jupy_logger.jupy_pdf_utils import export_notebook_to_pdf

    export_notebook_to_pdf(
      input_path="analysis.ipynb",
      output_path=None,
      hide_code=False,
    )

  Notebook:
    import multimodal_jupy_logger.jupy_pdf_utils
    %backup_pdf

  CLI:
    python -m multimodal_jupy_logger.jupy_pdf_utils analysis.ipynb
'''

import argparse
import datetime
import os
import pathlib
import socket
import sys
import time

import nbformat

from IPython import get_ipython
#replaced with below 3# #from IPython.core.magic import register_line_magic
from IPython.core.magic import Magics
from IPython.core.magic import magics_class
from IPython.core.magic import line_magic
from IPython.display import Javascript
from IPython.display import display
from nbconvert import WebPDFExporter
from traitlets.config import Config


# @TODO:
#   This module is currently being kept as a safe, drop-in MVP.
#   Later, consider integrating it with the broader MMJL magic framework
#   so PDF backup can share the same option parsing / logging conventions
#   as %%jupy_log, %%jupy_capture, %%jupy_tee, etc.
#   For now: do not over-integrate. Keep the PDF utility runnable.


def get_system_metadata() -> dict[str, str]:
  '''
  Gather cross-platform environment, machine, and timestamp metadata.
  '''

  username = os.environ.get(
      "USERNAME",
      os.environ.get(
          "USER",
          "unknown",
      ),
  )

  try:
    username = os.getlogin()
  except OSError:
    pass
  ##endof:  try/except OSError

  machine = socket.gethostname()

  if sys.platform.startswith("win"):
    workgroup_or_domain = os.environ.get("USERDOMAIN", "WORKGROUP")
    domain_prefix = f"{workgroup_or_domain}\\"
  else:
    domain_prefix = "(+NIX-type)\\"
  ##endof:  if/else sys.platform.startswith("win")

  now = datetime.datetime.now(datetime.timezone.utc).astimezone()

  epoch_timestamp = int(now.timestamp())

  timestamp_str = (
      f"{epoch_timestamp}_{now.strftime('%Y-%m-%dT%H%M%S%z')}"
  )

  return {
      "username": username,
      "machine": machine,
      "domain_prefix": domain_prefix,
      "timestamp": timestamp_str,
  }
##endof:  get_system_metadata()


def detect_active_notebook_path() -> pathlib.Path:
  '''
  Fetch the file path of the currently executing notebook session.

  This depends on Jupyter/IPython making `__session__` available.
  If that is unavailable, callers should pass an explicit input path.
  '''

  ip = get_ipython()

  if ip is not None and "__session__" in ip.user_ns:
    session_path = ip.user_ns["__session__"]

    if session_path and session_path.endswith(".ipynb"):
      return pathlib.Path(session_path)
    ##endof:  if session_path and session_path.endswith(".ipynb")
  ##endof:  if ip is not None and "__session__" in ip.user_ns

  raise RuntimeError(
      "Could not dynamically detect the active notebook name.\n"
      "Ensure you are running inside a live Jupyter session and\n"
      "that you have saved the file at least once.\n"
      "If neither of those are your problem, go on ahead and\n"
      "pass the filename explicitly."
  )
##endof:  detect_active_notebook_path()


def export_notebook_to_pdf(
      input_path: str | None = None,
      output_path: str | None = None,
      hide_code: bool = False,
  ) -> None:
  '''
  Core execution engine.

  Handles active-notebook resolution, optional frontend save,
  metadata header injection, and PDF rendering.
  '''
  
  input_file = "default.ipynb"
  
  if not input_path:
    try:
      input_file = detect_active_notebook_path()
    except RuntimeError as e:
      print(
          (
              "Problem detecting the active notebook path\n"
              "in export_notebook_to_pdf.\nDetails are\n"
              f"Error: {e}"
          ),
          file=sys.stderr,
      )
      return
    ##endof:  try/except RuntimeError
  else:
    input_file = pathlib.Path(input_path)
  ##endof:  if/else not input_path

  base_filename = input_file.stem

  ip = get_ipython()

  if ip is not None and "IPKernelApp" in ip.config:
    print("Triggering notebook save via frontend JavaScript...")

    js_save_command = '''
try {
    if (window.Jupyter && window.Jupyter.notebook) {
        window.Jupyter.notebook.save_checkpoint();
    } else if (window.jupyterlab) {
        var apps = Object.values(window.jupyterlab._apps);
        if (apps && apps.length > 0 && apps.commands) {
            apps.commands.execute("docmanager:save");
        }
    }
} catch (e) {
    console.error("Jupyter auto-save failed:", e);
}
'''

    display(Javascript(js_save_command))
    time.sleep(3.5)
  else:
    print(
        "CLI/Non-interactive context. "
        "Skipping frontend browser save module.\n"
        "You might want to save your notebook and run this again."
    )
  ##endof:  if/else ip is not None and "IPKernelApp" in ip.config

  meta = get_system_metadata()

  if not output_path:
    output_path = (
        f"{base_filename}_{meta['timestamp']}_ipynb.pdf"
    )
  ##endof:  if not output_path

  output_file = pathlib.Path(output_path)

  with open(input_file, "r", encoding="utf-8") as ifh:
    notebook_content = nbformat.read(ifh, as_version=4)
  ##endof:  with open(input_file)

  header_markdown = f'''**Notebook Backup**

Jupyter Notebook Filename: {input_file.name}

Base Filename ({base_filename})

Timestamp at backup: {meta['timestamp']}

Machine, user, etc.:
    {meta['domain_prefix']}{meta['username']}@{meta['machine']}

This file: {base_filename}_{meta['timestamp']}_ipynb.pdf

---

---

Begin COMPLETE NOTEBOOK backup (PDF)

---
'''

  header_cell = nbformat.v4.new_markdown_cell(
      source=header_markdown,
  )

  notebook_content.cells.insert(0, header_cell)

  c = Config()

  c.WebPDFExporter.allow_chromium_download = True

  exporter = WebPDFExporter(config=c)

  if hide_code:
    exporter.exclude_input = True
    exporter.exclude_output_prompt = True
  ##endof:  if hide_code

  print(f"Generating optimized layout PDF for {input_file.name}...")

  pdf_data, _ = exporter.from_notebook_node(notebook_content)

  with open(output_file, "wb") as ofh:
    ofh.write(pdf_data)
  ##endof:  with open(output_file)

  print(
      (
          "Successfully generated report payload layout:\n"
          f"{output_file.name}"
      )
  )
##endof:  export_notebook_to_pdf()


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
  
  print(
      (
          "[DONE] Registered: %backup_pdf from the file,\n"
          "         src/multimodal_jupy_logger/jupy_pdf_utils.py"
      )
  )

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


def main() -> None:
  '''
  Terminal argument parser interface.
  '''

  parser = argparse.ArgumentParser(
      description="Convert Jupyter Notebook directly to PDF. EXPERIMENTAL!",
  )

  parser.add_argument(
      "input",
      help="Target path to the local input .ipynb file.",
  )

  parser.add_argument(
      "-o",
      "--output",
      help="Custom output path for the destination PDF.",
      default=None,
  )

  parser.add_argument(
      "--show-code",
      action="store_false",
      dest="hide_code",
      help="Include code input cells in the PDF.",
  )

  args = parser.parse_args()

  export_notebook_to_pdf(
      input_path=args.input,
      output_path=args.output,
      hide_code=args.hide_code,
  )
##endof:  main()


if __name__ == "__main__":
  main()
##endof:  if __name__ == "__main__"
```

## File: `src/multimodal_jupy_logger/mmjl_cli.py`

Save as:

```text
~/multimodal-jupy-logger/src/multimodal_jupy_logger/mmjl_cli.py
```

```python
#!/usr/bin/env python3
'''
Command interface for Multimodal Jupy Logger.

@file   : jupy_pdf_utils.py
@author : David Black        GitHub: @bballdave025
@since  : 2026-06-1x, mid-June 2026

Part of the `multimodal-jupy-logger` project, which can potentially be
a package.

This module is intentionally importable as Python code and runnable as a
command-line module.

Examples:

  python -m multimodal_jupy_logger.mmjl_cli inspect


  python -m multimodal_jupy_logger.mmjl_cli \
    --root mlu_wjupy_log \
    html \
    --out artifacts/timeline.html
  
  # that last one, but for Windows PowerShell instead of bash
  python -m multimodal_jupy_logger.mmjl_cli `
    --root mlu_wjupy_log `
    html `
    --out artifacts/timeline.html

  from multimodal_jupy_logger import mmjl_cli
  mmjl_cli.main(["inspect"])
'''

from __future__ import annotations

import argparse

from multimodal_jupy_logger.logger import MultimodalJupyLogger


def build_arg_parser() -> argparse.ArgumentParser:
  '''
  Build the command-line parser.

  @TODO  Add PDF export command.
  @TODO  Add richer output-format controls.
  @TODO  Add strict validation modes.
  @TODO  Add relative-path manifest controls.
  '''
  
  parser = None
  subparsers = None
  html_parser = None
  markdown_parser = None
  log_file_parser = None
  inspect_parser = None
  validate_parser = None
  
  parser = argparse.ArgumentParser(
      description="Multimodal Jupy Logger command interface."
  )
  parser.add_argument(
      "--root",
      default="jupy_log",
      help="MMJL root logging directory.",
  )
  
  subparsers = parser.add_subparsers(
      dest="command",
      required=True,
  )
  
  html_parser = subparsers.add_parser(
      "html",
      help="Build HTML timeline from the manifest.",
  )
  html_parser.add_argument(
      "--out",
      default=None,
      help="Optional output HTML path.",
  )
  
  markdown_parser = subparsers.add_parser(
      "markdown",
      help="Build Markdown timeline from the manifest.",
  )
  markdown_parser.add_argument(
      "--out",
      default=None,
      help="Optional output Markdown path.",
  )
  
  log_file_parser = subparsers.add_parser(
      "log-file",
      help="Log one or more existing files as MMJL artifacts.",
  )
  log_file_parser.add_argument(
      "--label",
      default="artifact",
      help="Label prefix for logged files.",
  )
  log_file_parser.add_argument(
      "--mime",
      default=None,
      help="Optional explicit MIME type.",
  )
  log_file_parser.add_argument(
      "paths",
      nargs="+",
      help="File paths to log.",
  )
  
  inspect_parser = subparsers.add_parser(
      "inspect",
      help="Print a basic manifest summary.",
  )
  
  validate_parser = subparsers.add_parser(
      "validate",
      help="Check that manifest artifact paths exist.",
  )
  
  return parser
##endof:  build_arg_parser()



def main(argv: list[str] | None = None):
  '''
  Run the command interface.
  '''
  
  parser = None
  args = None
  logger = None
  out_paths = []
  idx = 0
  raw_path = ""
  label = ""
  
  parser = build_arg_parser()
  args = parser.parse_args(argv)
  logger = MultimodalJupyLogger(root=args.root)
  
  if args.command == "html":
    return logger.build_html(out_path=args.out)
  ##endof:  if args.command == "html"
  
  if args.command == "markdown":
    return logger.build_markdown(out_path=args.out)
  ##endof:  if args.command == "markdown"
  
  if args.command == "log-file":
    for idx, raw_path in enumerate(args.paths, start=1):
      label = f"{args.label}-{idx:02d}"
      out_paths.append(
          logger.log_file(
              raw_path,
              label=label,
              mime=args.mime,
          )
      )
    ##endof:  for idx, raw_path in enumerate(args.paths, start=1)
    
    return out_paths
  ##endof:  if args.command == "log-file"
  
  if args.command == "inspect":
    return logger.inspect_manifest()
  ##endof:  if args.command == "inspect"
  
  if args.command == "validate":
    return logger.validate_manifest()
  ##endof:  if args.command == "validate"
  
  parser.error(f"Unknown command: {args.command}")
##endof:  main(...)



if __name__ == "__main__":
  main()
##endof:  if __name__ == "__main__"
```

## File: `requirements.txt`

Save as:

```text
~/multimodal-jupy-logger/requirements.txt
```

```text
jupyterlab
ipykernel
matplotlib
```

## File: `requirements-ml.txt`

Save as:

```text
~/multimodal-jupy-logger/requirements-ml.txt
```

```text
-r requirements.txt

numpy
scipy
scikit-learn

torch

# # and, as needed
# torchvision
# torchaudio
```

## File: `requirements-experimental-pdf.txt`

Save as:

```text
~/multimodal-jupy-logger/requirements-experimental-pdf.txt
```

```text
-r requirements.txt

nbformat
nbconvert[webpdf]
traitlets
```

## File: `requirements-all-experimental.txt`

Save as:

```text
~/multimodal-jupy-logger/requirements-all-experimental.txt
```

```text
-r requirements.txt
-r requirements-ml.txt
-r requirements-exprmntl-pdf.txt
```
