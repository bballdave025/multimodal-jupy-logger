from __future__ import annotations

'''
@file   : jupy_pdf_utils.py
@author : David Black        GitHub: @bballdave025
@since  : 2026-06-11

Standalone PDF backup utility for Jupyter notebooks.

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
      description="Convert Jupyter Notebook directly to PDF.",
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
