'''
Metadata helpers for Multimodal Jupy Logger.
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
