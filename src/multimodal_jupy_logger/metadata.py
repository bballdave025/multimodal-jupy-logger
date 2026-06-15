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
  Return a filesystem-safe timestamp.

  This is the Python equivalent of:

    date +'%s_%Y-%m-%dT%H%M%S%z'
  '''
  
  now = None
  stamp = ""
  
  now = datetime.now().astimezone()
  stamp = (
      f"{int(now.timestamp())}_"
      f"{now.strftime('%Y-%m-%dT%H%M%S%z')}"
  )
  
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

---
'''
##endof:  build_log_header(...)
