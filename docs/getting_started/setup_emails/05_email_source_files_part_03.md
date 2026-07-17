# MMJL Source Transfer — Part 3 of 4

For each section, open the stated destination file, paste only the contents inside its code fence, and save the file.

## File: `src/multimodal_jupy_logger/magics.py`

Save as:

```text
~/multimodal-jupy-logger/src/multimodal_jupy_logger/magics.py
```

```python
'''
IPython/Jupyter magics for Multimodal Jupy Logger.

@file   : jupy_pdf_utils.py
@author : David Black        GitHub: @bballdave025     comments signed "DWB"
@since  : 2026-06-1x, mid-June 2026

Part of the `multimodal-jupy-logger` project, which can potentially be
a package.
'''

from __future__ import annotations

import argparse
import shlex
import sys
import traceback
from pathlib import Path

from IPython import get_ipython
from IPython.core.magic import Magics, cell_magic, line_magic, magics_class
from IPython.display import Javascript, display
from IPython.utils.capture import capture_output

from multimodal_jupy_logger.logger import (
  SEQUENCE_WIDTH,
  MultimodalJupyLogger,
)


@magics_class
class MultimodalJupyLoggerMagics(Magics):
  '''
  Thin Jupyter magic wrappers around the core logger.

  ``%%jupy_log`` stores literal cell text without execution.
  ``%%jupy_capture`` executes a Python cell, records selected input and
  output artifacts, and replays ordinary notebook output by default.
  ``%%jupy_tee`` is the visible-output alias for ``%%jupy_capture``.
  '''

  def __init__(self, shell, root: str | Path = "jupy_log"):
    super().__init__(shell)
    self.logger = MultimodalJupyLogger(root=root)
  ##endof:  __init__(...)



  @staticmethod
  def _on_off_to_bool(value: str) -> bool:
    '''Convert an ``on`` or ``off`` command option to bool.'''

    return value == "on"
  ##endof:  _on_off_to_bool(...)



  @staticmethod
  def _build_capture_parser(magic_name: str) -> argparse.ArgumentParser:
    '''Build the parser for ``%%jupy_capture`` and ``%%jupy_tee``.'''

    parser = argparse.ArgumentParser(
        prog=f"%%{magic_name}",
        description=(
            "Execute a Python cell while logging selected notebook "
            "memory artifacts."
        ),
        epilog=(
            "MMJL is for selected notebook memory. "
            "Use --pin when a cell is worth keeping. "
            "Use --label NAME when a cell is worth keeping and you "
            "already know its name. "
            "Use --pin-input when the code matters more than the output. "
            "Use --pin-output when the result matters more than the code. "
            "Important: --label NAME by itself behaves like --pin."
        ),
    )
    pin_group = None

    parser.add_argument(
        "--label",
        default=None,
        help=(
            "Human-readable capture label. If supplied without an "
            "explicit pin mode, this behaves like --pin."
        ),
    )

    pin_group = parser.add_mutually_exclusive_group()
    pin_group.add_argument(
        "--pin",
        action="store_true",
        help="Keep input and output. Uses an automatic label if needed.",
    )
    pin_group.add_argument(
        "--pin-input",
        action="store_true",
        help="Keep only the input/code. Uses an automatic label if needed.",
    )
    pin_group.add_argument(
        "--pin-output",
        action="store_true",
        help="Keep only the output/display. Uses an automatic label if needed.",
    )

    parser.add_argument(
        "--jupy-display",
        "--display",
        dest="jupy_display",
        choices=["on", "off"],
        default="on",
    )
    parser.add_argument(
        "--log-input",
        choices=["on", "off"],
        default="on",
        help=(
            "Backward-compatible input logging switch. Pin modes override "
            "this when they specify input/output behavior."
        ),
    )

    return parser
  ##endof:  _build_capture_parser(...)



  @staticmethod
  def _capture_mode_from_args(args: argparse.Namespace) -> str:
    '''Return ``both``, ``input``, or ``output`` for parsed capture args.'''

    if args.pin_input:
      return "input"
    ##endof:  if args.pin_input

    if args.pin_output:
      return "output"
    ##endof:  if args.pin_output

    if args.pin:
      return "both"
    ##endof:  if args.pin

    if args.label is not None:
      return "both"
    ##endof:  if args.label is not None

    if args.log_input == "off":
      return "output"
    ##endof:  if args.log_input == "off"

    return "both"
  ##endof:  _capture_mode_from_args(...)



  @staticmethod
  def _label_from_args(
        args: argparse.Namespace,
        capture_sequence: int,
        mode: str,
      ) -> str:
    '''Return a human or automatic base label for one capture.'''

    if args.label is not None:
      return args.label
    ##endof:  if args.label is not None

    if args.pin_input:
      return f"pin-input-{capture_sequence:0{SEQUENCE_WIDTH}d}"
    ##endof:  if args.pin_input

    if args.pin_output:
      return f"pin-output-{capture_sequence:0{SEQUENCE_WIDTH}d}"
    ##endof:  if args.pin_output

    if args.pin:
      return f"pin-{capture_sequence:0{SEQUENCE_WIDTH}d}"
    ##endof:  if args.pin

    return "cell"
  ##endof:  _label_from_args(...)



  def _capture_and_execute(
        self,
        line: str,
        cell: str | None,
        magic_name: str,
        force_display: bool | None = None,
      ) -> None:
    '''
    Log Python input, execute it, capture outputs, and optionally replay.

    Exact stdout/stderr/display interleaving is not yet represented in
    the manifest. Artifacts are nevertheless ordered authoritatively by
    persistent artifact sequence and grouped by capture sequence.
    '''

    args = None
    captured = None
    capture_sequence = 0
    cell_text = ""
    display_is_on = True
    error = None
    error_text = ""
    execution_result = None
    label = ""
    logged_paths = []
    log_input = True
    log_output = True
    mode = "both"
    parser = None
    stderr_text = ""
    stdout_text = ""

    parser = self._build_capture_parser(magic_name)
    args = parser.parse_args(shlex.split(line))

    cell_text = cell or ""
    capture_sequence = self.logger.next_capture_sequence()
    mode = self._capture_mode_from_args(args)
    label = self._label_from_args(args, capture_sequence, mode)
    display_is_on = self._on_off_to_bool(args.jupy_display)

    if force_display is not None:
      display_is_on = force_display
    ##endof:  if force_display is not None

    log_input = mode in ["both", "input"]
    log_output = mode in ["both", "output"]

    if log_input:
      logged_paths.append(
          self.logger.log_text(
              cell_text,
              label=f"{label}-input",
              mime="text/x-python",
              capture_sequence=capture_sequence,
              role="input",
              announce=False,
          )
      )
    ##endof:  if log_input

    with capture_output(
          stdout=True,
          stderr=True,
          display=True,
        ) as captured:
      execution_result = self.shell.run_cell(
          cell_text,
          store_history=False,
      )
    ##endof:  with capture_output(...) as captured

    stdout_text = captured.stdout
    stderr_text = captured.stderr

    if log_output and stdout_text:
      logged_paths.append(
          self.logger.log_text(
              stdout_text,
              label=f"{label}-stdout",
              mime="text/plain",
              capture_sequence=capture_sequence,
              role="stdout",
              announce=False,
          )
      )
    ##endof:  if log_output and stdout_text

    if log_output and stderr_text:
      logged_paths.append(
          self.logger.log_text(
              stderr_text,
              label=f"{label}-stderr",
              mime="text/plain",
              capture_sequence=capture_sequence,
              role="stderr",
              announce=False,
          )
      )
    ##endof:  if log_output and stderr_text

    if log_output:
      for output_number, rich_output in enumerate(
            captured.outputs,
            start=1,
          ):
        logged_paths.extend(
            self.logger.log_mime_bundle(
                rich_output.data,
                label=(
                    f"{label}-display-"
                    f"{output_number:02d}"
                ),
                capture_sequence=capture_sequence,
                role="display",
                announce=False,
            )
        )
      ##endof:  for output_number, rich_output in enumerate(...)
    ##endof:  if log_output

    error = (
        execution_result.error_before_exec
        or execution_result.error_in_exec
    )

    if log_output and error is not None:
      error_text = "".join(
          traceback.format_exception(
              type(error),
              error,
              error.__traceback__,
          )
      )
      logged_paths.append(
          self.logger.log_text(
              error_text,
              label=f"{label}-exception",
              mime="text/plain",
              capture_sequence=capture_sequence,
              role="exception",
              announce=False,
          )
      )
    ##endof:  if log_output and error is not None

    if display_is_on:
      captured.show()
    ##endof:  if display_is_on

    print(
        (
            f"[DONE] Capture "
            f"{capture_sequence:0{SEQUENCE_WIDTH}d}: "
            f"logged {len(logged_paths)} artifact(s)."
        )
    )

    if error is not None:
      print(
          f"[MMJL] %%{magic_name} captured an execution error.",
          file=sys.stderr,
      )
    ##endof:  if error is not None

    return None
  ##endof:  _capture_and_execute(...)



  @line_magic
  def jupy_save(self, line: str = ""):
    '''
    Request a frontend notebook save.
    '''

    display(Javascript("""
    try {
      if (window.jupyterapp) {
        window.jupyterapp.commands.execute('docmanager:save');
      } else if (window.Jupyter && Jupyter.notebook) {
        Jupyter.notebook.save_notebook();
      }
    } catch (err) {
      console.warn("Notebook save request failed:", err);
    }
    """))

    print("[DONE] Save requested.")
    return None
  ##endof:  jupy_save(...)



  @line_magic
  def jupy_file(self, line: str = ""):
    '''
    Log one or more existing files.
    '''

    parser = None
    args = None
    idx = 0
    raw_path = ""
    label = ""

    parser = argparse.ArgumentParser(prog="%jupy_file")
    parser.add_argument("--label", default="artifact")
    parser.add_argument("--mime", default=None)
    parser.add_argument("paths", nargs="+")
    args = parser.parse_args(shlex.split(line))

    for idx, raw_path in enumerate(args.paths, start=1):
      label = f"{args.label}-{idx:02d}"
      self.logger.log_file(
          raw_path,
          label=label,
          mime=args.mime,
      )
    ##endof:  for idx, raw_path in enumerate(args.paths, start=1)

    return None
  ##endof:  jupy_file(...)



  @cell_magic
  def jupy_log(self, line: str = "", cell: str | None = None):
    '''
    Log literal cell text without executing it.
    '''

    parser = None
    args = None

    parser = argparse.ArgumentParser(prog="%%jupy_log")
    parser.add_argument("--label", default="cell")
    parser.add_argument("--mime", default="text/plain")
    args = parser.parse_args(shlex.split(line))

    self.logger.log_text(
        cell or "",
        args.label,
        mime=args.mime,
        role="literal",
    )

    return None
  ##endof:  jupy_log(...)



  @cell_magic
  def jupy_capture(
        self,
        line: str = "",
        cell: str | None = None,
      ):
    '''
    Execute a Python cell while logging input and captured outputs.
    '''

    return self._capture_and_execute(
        line=line,
        cell=cell,
        magic_name="jupy_capture",
    )
  ##endof:  jupy_capture(...)



  @cell_magic
  def jupy_tee(
        self,
        line: str = "",
        cell: str | None = None,
      ):
    '''
    Visible-output alias for ``%%jupy_capture``.
    '''

    return self._capture_and_execute(
        line=line,
        cell=cell,
        magic_name="jupy_tee",
        force_display=True,
    )
  ##endof:  jupy_tee(...)



  @line_magic
  def jupy_markdown(self, line: str = ""):
    '''
    Build a Markdown timeline.
    '''

    out_path = None
    out_path = line.strip() or None
    self.logger.build_markdown(out_path=out_path)
    return None
  ##endof:  jupy_markdown(...)



  @line_magic
  def jupy_html(self, line: str = ""):
    '''
    Build an HTML timeline.
    '''

    out_path = None
    out_path = line.strip() or None
    self.logger.build_html(out_path=out_path)
    return None
  ##endof:  jupy_html(...)



  @line_magic
  def jupy_inspect(self, line: str = ""):
    '''
    Print a manifest summary.
    '''

    self.logger.inspect_manifest()
    return None
  ##endof:  jupy_inspect(...)



  @line_magic
  def jupy_validate(self, line: str = ""):
    '''
    Validate that manifest paths exist.
    '''

    self.logger.validate_manifest()
    return None
  ##endof:  jupy_validate(...)
##endof:  class MultimodalJupyLoggerMagics



def register_jupy_logger(root: str | Path = "jupy_log") -> None:
  '''
  Register MMJL magics in the active IPython session.
  '''

  ip = None

  try:
    ip = get_ipython()
  except NameError:
    ip = None
  ##endof:  try/except NameError

  if ip is None:
    raise RuntimeError("No active IPython session found.")
  ##endof:  if ip is None

  class BoundMultimodalJupyLoggerMagics(MultimodalJupyLoggerMagics):
    def __init__(self, shell):
      super().__init__(shell, root=root)
    ##endof:  __init__(...)
  ##endof:  BoundMultimodalJupyLoggerMagics

  ip.register_magics(BoundMultimodalJupyLoggerMagics)

  print(
      (
          "[DONE] Registered: %jupy_save, %jupy_file, "
          "%%jupy_log, %%jupy_capture, %%jupy_tee, "
          "%jupy_markdown, %jupy_html, "
          "%jupy_inspect, %jupy_validate"
      )
  )
##endof:  register_jupy_logger()



def jupy_logger_register(root: str | Path = "jupy_log") -> None:
  '''
  Backward-compatible registration alias.
  '''

  register_jupy_logger(root=root)
##endof:  jupy_logger_register()
```

## File: `src/multimodal_jupy_logger/metadata.py`

Save as:

```text
~/multimodal-jupy-logger/src/multimodal_jupy_logger/metadata.py
```

```python
'''
Metadata helpers for Multimodal Jupy Logger.

@file   : jupy_pdf_utils.py
@author : David Black        GitHub: @bballdave025     comments signed "DWB"
@since  : 2026-06-1x, mid-June 2026

Part of the `multimodal-jupy-logger` project, which can potentially be
a package.
'''

from __future__ import annotations

import getpass
import os
import socket
from datetime import datetime


def jupy_stamp() -> str:
  '''
  Return a filesystem-safe timestamp with Unix epoch milliseconds.

  Example:

    1781604242123_2026-06-16T095402123-0400

  The leading epoch-millisecond value is useful for machine ordering.
  The local timestamp is useful for human inspection.
  '''
  
  epoch_milliseconds = 0
  local_timestamp = ""
  now = None
  stamp = ""
  
  now = datetime.now().astimezone()
  epoch_milliseconds = int(now.timestamp() * 1000)
  local_timestamp = (
      f"{now.strftime('%Y-%m-%dT%H%M%S')}"
      f"{now.microsecond // 1000:03d}"
      f"{now.strftime('%z')}"
  )
  stamp = f"{epoch_milliseconds}_{local_timestamp}"
  
  return stamp
##endof:  jupy_stamp()



def get_system_metadata() -> dict[str, str]:
  '''
  Get simple local provenance metadata.

  This intentionally avoids employer/project-specific information.

  @TODO  Add optional git commit metadata.
  @TODO  Add optional Python/Jupyter/IPython version metadata.
  @TODO  Add optional platform metadata.
  '''
  
  username = ""
  machine = ""
  domain_prefix = ""
  timestamp_str = ""
  
  timestamp_str = jupy_stamp()
  username = getpass.getuser()
  machine = socket.gethostname()
  
  if os.name == "nt":
    domain_prefix = os.environ.get("USERDOMAIN", "WORKGROUP")
  else:
    domain_prefix = "*NIX-type"
  ##endof:  if os.name == "nt"
  
  return {
      "username": username,
      "machine": machine,
      "domain_prefix": domain_prefix,
      "timestamp": timestamp_str,
  }
##endof:  get_system_metadata()



def build_log_header(
      title: str = "Multimodal Jupy Logger Backup",
      source_name: str | None = None,
      output_name: str | None = None,
    ) -> str:
  '''
  Build a reusable Markdown provenance header.

  @TODO  Add project/repo metadata.
  @TODO  Add manifest path.
  @TODO  Add configurable privacy redaction.
  '''
  
  meta = {}
  source_line = ""
  output_line = ""
  
  meta = get_system_metadata()
  
  if source_name is not None:
    source_line = f"Source: {source_name}\n"
  ##endof:  if source_name is not None
  
  if output_name is not None:
    output_line = f"This log file: {output_name}\n"
  ##endof:  if output_name is not None
  
  return f'''**{title}**

{source_line}{output_line}Timestamp: {meta["timestamp"]}
Machine, user, etc.: {meta["domain_prefix"]} {meta["username"]}@{meta["machine"]}

---

---

Begin Timeline or Other Log

---
'''
##endof:  build_log_header(...)
```

## File: `src/multimodal_jupy_logger/__init__.py`

Save as:

```text
~/multimodal-jupy-logger/src/multimodal_jupy_logger/__init__.py
```

```python
'''
Public package interface for Multimodal Jupy Logger.

@file   : __init__.py
          specifically, src/multimodal_jupy_logger/__init__.py
@author : David Black        GitHub: @bballdave025     comments signed "DWB"
@since  : 2026-06-1x, mid-June 2026

Part of the `multimodal-jupy-logger` project, which can potentially be
a package.
'''

from multimodal_jupy_logger.environment_checks import (
  check_packages,
  print_environment_check,
  print_package_checks,
)
from multimodal_jupy_logger.logger import MultimodalJupyLogger
from multimodal_jupy_logger.magics import (
  MultimodalJupyLoggerMagics,
  jupy_logger_register,
  register_jupy_logger,
)

__all__ = [
  "MultimodalJupyLogger",
  "MultimodalJupyLoggerMagics",
  "check_packages",
  "jupy_logger_register",
  "print_environment_check",
  "print_package_checks",
  "register_jupy_logger",
]

##endof:  __all__
```

## File: `LICENSE`

Save as:

```text
~/multimodal-jupy-logger/LICENSE
```

```text
MIT License

Copyright (c) 2026 David Black

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
