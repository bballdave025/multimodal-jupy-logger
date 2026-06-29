'''
IPython/Jupyter magics for Multimodal Jupy Logger.
'''

from __future__ import annotations

import argparse
import shlex
import sys
import traceback

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
  ``%%jupy_capture`` executes a Python cell, records its input and output,
  and replays ordinary notebook output by default.
  ``%%jupy_tee`` is the visible-output alias for ``%%jupy_capture``.
  '''
  
  def __init__(self, shell):
    super().__init__(shell)
    self.logger = MultimodalJupyLogger()
  ##endof:  __init__(...)
  
  
  
  @staticmethod
  def _on_off_to_bool(value: str) -> bool:
    '''Convert an ``on`` or ``off`` command option to bool.'''
    
    return value == "on"
  ##endof:  _on_off_to_bool(...)
  
  
  
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
    logged_paths = []
    parser = None
    stderr_text = ""
    stdout_text = ""
    
    parser = argparse.ArgumentParser(prog=f"%%{magic_name}")
    parser.add_argument("--label", default="cell")
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
    )
    args = parser.parse_args(shlex.split(line))
    
    cell_text = cell or ""
    capture_sequence = self.logger.next_capture_sequence()
    display_is_on = self._on_off_to_bool(args.jupy_display)
    
    if force_display is not None:
      display_is_on = force_display
    ##endof:  if force_display is not None
    
    if self._on_off_to_bool(args.log_input):
      logged_paths.append(
          self.logger.log_text(
              cell_text,
              label=f"{args.label}-input",
              mime="text/x-python",
              capture_sequence=capture_sequence,
              role="input",
              announce=False,
          )
      )
    ##endof:  if self._on_off_to_bool(args.log_input)
    
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
    
    if stdout_text:
      logged_paths.append(
          self.logger.log_text(
              stdout_text,
              label=f"{args.label}-stdout",
              mime="text/plain",
              capture_sequence=capture_sequence,
              role="stdout",
              announce=False,
          )
      )
    ##endof:  if stdout_text
    
    if stderr_text:
      logged_paths.append(
          self.logger.log_text(
              stderr_text,
              label=f"{args.label}-stderr",
              mime="text/plain",
              capture_sequence=capture_sequence,
              role="stderr",
              announce=False,
          )
      )
    ##endof:  if stderr_text
    
    for output_number, rich_output in enumerate(
          captured.outputs,
          start=1,
        ):
      logged_paths.extend(
          self.logger.log_mime_bundle(
              rich_output.data,
              label=(
                  f"{args.label}-display-"
                  f"{output_number:02d}"
              ),
              capture_sequence=capture_sequence,
              role="display",
              announce=False,
          )
      )
    ##endof:  for output_number, rich_output in enumerate(...)
    
    error = (
        execution_result.error_before_exec
        or execution_result.error_in_exec
    )
    
    if error is not None:
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
              label=f"{args.label}-exception",
              mime="text/plain",
              capture_sequence=capture_sequence,
              role="exception",
              announce=False,
          )
      )
    ##endof:  if error is not None
    
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
    
    #just puts an object descriiption on screen#return execution_result
    # We choose
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
  ##endof:  jupy_save(...)
  
  
  
  @line_magic
  def jupy_file(self, line: str = ""):
    '''
    Log one or more existing files.
    '''
    
    parser = None
    args = None
    out = []
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
      out.append(
          self.logger.log_file(
              raw_path,
              label=label,
              mime=args.mime,
          )
      )
    ##endof:  for idx, raw_path in enumerate(args.paths, start=1)
    
    # ##    # not going to #    ##return out
    # #  Returning the   out   would clog up the
    # #+ Jupyter display with something like '[WindowsPath(...)]'
    # #+ So we choose to...
    #return None
    
    #DWB 2026-06-29# Not very sure about this. kamMA?!?!
    
    return out
    
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
    
    #  Returning the self.logger.log_text(...) would clog up the
    #+ Jupyter display with something like 'WindowsPath(...)'
    #+ So we choose to...
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
    return self.logger.build_markdown(out_path=out_path)
  ##endof:  jupy_markdown(...)
  
  
  
  @line_magic
  def jupy_html(self, line: str = ""):
    '''
    Build an HTML timeline.
    '''
    
    out_path = None
    out_path = line.strip() or None
    return self.logger.build_html(out_path=out_path)
  ##endof:  jupy_html(...)
  
  
  
  @line_magic
  def jupy_inspect(self, line: str = ""):
    '''
    Print a manifest summary.
    '''
    
    return self.logger.inspect_manifest()
  ##endof:  jupy_inspect(...)
  
  
  
  @line_magic
  def jupy_validate(self, line: str = ""):
    '''
    Validate that manifest paths exist.
    '''
    
    return self.logger.validate_manifest()
  ##endof:  jupy_validate(...)
##endof:  class MultimodalJupyLoggerMagics



def register_jupy_logger() -> None:
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
  
  ip.register_magics(MultimodalJupyLoggerMagics)
  
  print(
      (
          "[DONE] Registered: %jupy_save, %jupy_file, "
          "%%jupy_log, %%jupy_capture, %%jupy_tee, "
          "%jupy_markdown, %jupy_html, "
          "%jupy_inspect, %jupy_validate"
      )
  )
##endof:  register_jupy_logger()



def jupy_logger_register() -> None:
  '''
  Backward-compatible registration alias.
  '''
  
  register_jupy_logger()
##endof:  jupy_logger_register()
