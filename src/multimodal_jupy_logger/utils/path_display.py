'''
@file path_display.py

Small path and file utilities used during MMJL development.

@author Dave Black     GitHub @bballdave025     comments signed "DWB"
@since  : 2026-06-1x, mid-June 2026

Part of the `multimodal-jupy-logger` project, which can potentially be
a package.

The module itself acts as the namespace. Typical use:

    from multimodal_jupy_logger.utils import path_display as dpypd

    dpypd.tree(...)
    dpypd.count_lines(...)
    dpypd.print_file(...)

Individual functions may also be imported through the utils package:

    from multimodal_jupy_logger.utils import tree

@TODO 
  Consider adding optional stream parameters to text-only display helpers: 
  
  
      from typing import TextIO 
      import sys 
      
      def tree(..., 
            file: TextIO = sys.stdout
          ) -> None: 
        
        print(line, file=file) 
  
  
  This would allow callers to capture output with `io.StringIO` for
  filtering, testing, or later logging. Alternative for one-off 
  capture: use `contextlib.redirect_stdout(buffer)` around existing
  print-based helpers. 
  
  Do not mix this into rich notebook display helpers yet; MMJL owns that richer display/capture path separately.
'''

from __future__ import annotations

#import sys
#import io
import pathlib
#import contextlib

#  New (sys, io, contextlib) imports not used yet here, but setting up 
#+ up scaffolding for something like:
#+
#+
#+     # 1. Create an in-memory text stream buffer
#+     buffer = io.StringIO()
#+
#+     # 2. Temporarily redirect all print statements 
#+     #+   inside tree() to our buffer
#+     with contextlib.redirect_stdout(buffer):
#+       tree(".")  # Runs normally, but prints nothing to the screen
#+     ##endof:  with
#+     # 3. Extract the full string content from the buffer
#+     tree_output_string = buffer.getvalue()
#+
#+     # 4. Perform line-by-line grep filter
#+     grep_results = [
#+         line 
#+         for line in tree_output_string.splitlines() 
#+         if "abc-" in line and "-pass-b-" in line
#+     ]
#+
#+     print(grep_results)
#
#
#  Looked at a similar solution, adding another parameter to the
#+ tree function itself:
#+
#+
#+        file=sys.stdout,
#+    ) -> None:
#+
#+    #  Now, inside the tree functions, I would just need to make
#+    #+ that all print statements look something like:
#+    #+     print(that_string, file=file)


def _path_part_has_match(
      path_part: str,
      exclusion_items: list[str],
    ) -> bool:
  '''
  Return True if an exclusion string occurs within one path part.
  '''
  
  return any(
      exclusion_item in path_part
      for exclusion_item in exclusion_items
  )
##endof:  _path_part_has_match(...)



def _any_path_part_has_match(
      path_parts: tuple[str, ...],
      exclusion_items: list[str],
    ) -> bool:
  '''
  Return True if an exclusion string matches any path component.
  '''
  
  return any(
      _path_part_has_match(
          path_part,
          exclusion_items,
      )
      for path_part in path_parts
  )
##endof:  _any_path_part_has_match(...)



def _should_exclude_path(
      child_item_path: pathlib.Path,
      root_dir: pathlib.Path,
      dirs_to_exclude: list[str],
      files_to_exclude: list[str],
    ) -> bool:
  '''
  Return True when a path should be omitted from tree output.

  Directory exclusions are tested against relative directory path
  components. File exclusions are tested against the filename only.
  '''
  
  dir_parts_to_check: tuple[str, ...] = ()
  relative_path = None
  this_is_dir = False
  this_is_file = False
  
  relative_path = child_item_path.relative_to(root_dir)
  this_is_dir = child_item_path.is_dir()
  this_is_file = child_item_path.is_file()
  
  if this_is_dir:
    dir_parts_to_check = relative_path.parts
  else:
    dir_parts_to_check = relative_path.parts[:-1]
  ##endof:  if this_is_dir
  
  if _any_path_part_has_match(
        dir_parts_to_check,
        dirs_to_exclude,
      ):
    return True
  ##endof:  if _any_path_part_has_match(...)
  
  if (
        this_is_file
        and _path_part_has_match(
            child_item_path.name,
            files_to_exclude,
        )
      ):
    return True
  ##endof:  if this_is_file and ...
  
  return False
##endof:  _should_exclude_path(...)



def tree(
      this_dir: pathlib.Path | str | None = None,
      indent_length: int = 4,
      dirs_to_exclude: list[str] | None = None,
      files_to_exclude: list[str] | None = None,
#     file=sys.stdout, #can add this & make sure all  print(s,file=file)
    ) -> None:
  '''
  Print a quick tree-style representation of a directory.

  Directory exclusions are compared with relative directory path parts.
  File exclusions are compared with filenames.

  Exclusion matching uses substring tests rather than exact equality.
  '''
  
  current_depth = 0
  relative_path = None
  root_dir = None
  suffix = ""
  this_indent = ""
  
  if this_dir is None:
    root_dir = pathlib.Path.cwd()
  else:
    root_dir = pathlib.Path(this_dir)
  ##endof:  if this_dir is None
  
  root_dir = root_dir.expanduser().resolve()
  
  if dirs_to_exclude is None:
    dirs_to_exclude = []
  ##endof:  if dirs_to_exclude is None
  
  if files_to_exclude is None:
    files_to_exclude = []
  ##endof:  if files_to_exclude is None
  
  print(f"+ {root_dir}")
  
  for child_item_path in sorted(root_dir.rglob("*")):
    if _should_exclude_path(
          child_item_path=child_item_path,
          root_dir=root_dir,
          dirs_to_exclude=dirs_to_exclude,
          files_to_exclude=files_to_exclude,
        ):
      continue
    ##endof:  if _should_exclude_path(...)
    
    relative_path = child_item_path.relative_to(root_dir)
    current_depth = len(relative_path.parts)
    this_indent = " " * indent_length * current_depth
    suffix = "/" if child_item_path.is_dir() else ""
    
    print(f"{this_indent}+ {child_item_path.name}{suffix}")
  ##endof:  for child_item_path in sorted(root_dir.rglob("*"))
##endof:  tree(...)



def count_lines(
      filename: pathlib.Path | str,
      do_print: bool = False,
    ) -> int:
  '''
  Count lines in a file using binary mode.

  Binary mode avoids unnecessary text decoding because line counting
  does not require interpreting the file's characters.
  '''
  
  num_lines = 0
  path = None
  
  path = pathlib.Path(filename).expanduser()
  
  with path.open("rb") as file_handle:
    num_lines = sum(1 for _ in file_handle)
  ##endof:  with path.open("rb") as file_handle
  
  if do_print:
    print(f"{path} has {num_lines} line(s)")
  ##endof:  if do_print
  
  return num_lines
##endof:  count_lines(...)



def print_file(
      filename: pathlib.Path | str,
      encoding: str = "utf-8",
      errors: str = "replace",
      show_line_numbers: bool = False,
    ) -> None:
  '''
  Print a text file without loading the entire file into memory.

  UTF-8 is explicit so Windows does not accidentally use a local code
  page when reading UTF-8 project files.
  '''
  
  path = None
  
  path = pathlib.Path(filename).expanduser()
  
  with path.open(
        "r",
        encoding=encoding,
        errors=errors,
      ) as file_handle:
    for line_number, line in enumerate(file_handle, start=1):
      if show_line_numbers:
        print(f"{line_number:>5}: {line}", end="")
      else:
        print(line, end="")
      ##endof:  if show_line_numbers
    ##endof:  for line_number, line in enumerate(...)
  ##endof:  with path.open(...) as file_handle
##endof:  print_file(...)
