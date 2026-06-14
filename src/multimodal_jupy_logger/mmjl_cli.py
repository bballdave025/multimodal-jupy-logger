#!/usr/bin/env python3
'''
Command interface for Multimodal Jupy Logger.

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
