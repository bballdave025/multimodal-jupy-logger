'''
IPython/Jupyter magics for Multimodal Jupy Logger.
'''

from __future__ import annotations

import argparse
import shlex

from IPython.core.magic import Magics, cell_magic, line_magic, magics_class
from IPython.display import Javascript, display

from multimodal_jupy_logger.logger import MultimodalJupyLogger


@magics_class
class MultimodalJupyLoggerMagics(Magics):
  '''
  Thin Jupyter magic wrappers around the core logger.

  @TODO  Add %%jupy_capture.
  @TODO  Add --jupy-display on|off.
  @TODO  Add --jupy-tee on|off compatibility alias.
  '''
  
  def __init__(self, shell):
    super().__init__(shell)
    self.logger = MultimodalJupyLogger()
  ##endof:  __init__(...)
  
  
  
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

    Usage:

      %jupy_file --label sample path/to/file.png
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
    
    return out
  ##endof:  jupy_file(...)
  
  
  
  @cell_magic
  def jupy_log(self, line: str = "", cell: str | None = None):
    '''
    Log literal cell text without executing it.

    Usage:

      %%jupy_log --label note --mime text/markdown
      # Markdown or text here.
    '''
    
    parser = None
    args = None
    
    parser = argparse.ArgumentParser(prog="%%jupy_log")
    parser.add_argument("--label", default="cell")
    parser.add_argument("--mime", default="text/plain")
    args = parser.parse_args(shlex.split(line))
    
    return self.logger.log_text(
        cell or "",
        args.label,
        mime=args.mime,
    )
  ##endof:  jupy_log(...)
  
  
  
  @line_magic
  def jupy_markdown(self, line: str = ""):
    '''
    Build a Markdown timeline.

    Usage:

      %jupy_markdown
      %jupy_markdown path/to/timeline.md
    '''
    
    out_path = None
    
    out_path = line.strip() or None
    
    return self.logger.build_markdown(out_path=out_path)
  ##endof:  jupy_markdown(...)
  
  
  
  @line_magic
  def jupy_html(self, line: str = ""):
    '''
    Build an HTML timeline.

    Usage:

      %jupy_html
      %jupy_html path/to/timeline.html
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
          "%%jupy_log, %jupy_markdown, %jupy_html, "
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
