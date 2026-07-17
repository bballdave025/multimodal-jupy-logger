# MMJL Source Email 1 of 3 — Core Logger
Paste each file body into the matching path created by the setup instructions. Copy only the text inside each code fence.

## `src/multimodal_jupy_logger/__init__.py`

````python
'''
Public package interface for Multimodal Jupy Logger.
'''

from multimodal_jupy_logger.logger import MultimodalJupyLogger
from multimodal_jupy_logger.magics import (
  MultimodalJupyLoggerMagics,
  jupy_logger_register,
  register_jupy_logger,
)

__all__ = [
  "MultimodalJupyLogger",
  "MultimodalJupyLoggerMagics",
  "jupy_logger_register",
  "register_jupy_logger",
]

##endof:  __all__
````

## `src/multimodal_jupy_logger/metadata.py`

````python
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
````

## `src/multimodal_jupy_logger/logger.py`

````python
'''
Core logging engine for Multimodal Jupy Logger.
'''

from __future__ import annotations

import base64
import html
import json
import os
import re
from pathlib import Path
from urllib.parse import quote

from multimodal_jupy_logger.metadata import build_log_header, jupy_stamp


MIME_INFO = {
    "image/png": ("image", "png"),
    "image/jpeg": ("image", "jpg"),
    "image/gif": ("image", "gif"),
    "image/webp": ("image", "webp"),
    "image/svg+xml": ("image", "svg"),
    
    "video/mp4": ("video", "mp4"),
    "video/webm": ("video", "webm"),
    "video/ogg": ("video", "ogv"),
    "video/quicktime": ("video", "mov"),
    
    "audio/wav": ("audio", "wav"),
    "audio/x-wav": ("audio", "wav"),
    "audio/mpeg": ("audio", "mp3"),
    "audio/mp3": ("audio", "mp3"),
    "audio/ogg": ("audio", "ogg"),
    "audio/flac": ("audio", "flac"),
    "audio/mp4": ("audio", "m4a"),
    
    "text/plain": ("text", "txt"),
    "text/markdown": ("text", "md"),
    "text/x-python": ("text", "py"),
    "text/html": ("html", "html"),
    "application/json": ("json", "json"),
}


MANIFEST_COLUMNS = [
    "artifact_sequence",
    "capture_sequence",
    "timestamp",
    "kind",
    "mime",
    "role",
    "label",
    "path",
]

MANIFEST_HEADER = "\t".join(MANIFEST_COLUMNS)
SEQUENCE_WIDTH = 6


def safe_label(label: str) -> str:
  '''
  Convert a label into a conservative filename component.
  '''
  
  safe = ""
  
  safe = str(label).strip()
  safe = re.sub(r"[^A-Za-z0-9._-]+", "-", safe)
  safe = safe.strip("-")
  
  if not safe:
    safe = "artifact"
  ##endof:  if not safe
  
  return safe
##endof:  safe_label(label)



def detect_media_bytes(data: bytes) -> str | None:
  '''
  Detect a small set of common media MIME types from file headers.

  @TODO  Add optional python-magic integration.
  @TODO  Add stronger MIME/header validation.
  '''
  
  brand = b""
  
  if data.startswith(bytes.fromhex("89504E470D0A1A0A")):
    return "image/png"
  ##endof:  if data.startswith(...)
  
  if data.startswith(bytes.fromhex("FFD8FF")):
    return "image/jpeg"
  ##endof:  if data.startswith(...)
  
  if data.startswith(b"GIF87a") or data.startswith(b"GIF89a"):
    return "image/gif"
  ##endof:  if data.startswith(...)
  
  if data.startswith(b"RIFF") and data[8:12] == b"WEBP":
    return "image/webp"
  ##endof:  if data.startswith(...)
  
  if len(data) >= 12 and data[4:8] == b"ftyp":
    brand = data[8:12]
    
    if brand == b"qt  ":
      return "video/quicktime"
    ##endof:  if brand == b"qt  "
    
    if brand in [b"isom", b"iso2", b"mp41", b"mp42", b"avc1", b"M4V "]:
      return "video/mp4"
    ##endof:  if brand in [...]
  ##endof:  if len(data) >= 12 and data[4:8] == b"ftyp"
  
  if data.startswith(b"\x1A\x45\xDF\xA3"):
    return "video/webm"
  ##endof:  if data.startswith(...)
  
  if data.startswith(b"RIFF") and data[8:12] == b"WAVE":
    return "audio/wav"
  ##endof:  if data.startswith(...)
  
  if data.startswith(b"ID3") or data.startswith(bytes.fromhex("FFFB")):
    return "audio/mpeg"
  ##endof:  if data.startswith(...)
  
  if data.startswith(b"OggS"):
    return "audio/ogg"
  ##endof:  if data.startswith(...)
  
  if data.startswith(b"fLaC"):
    return "audio/flac"
  ##endof:  if data.startswith(...)
  
  return None
##endof:  detect_media_bytes(data)



class MultimodalJupyLogger:
  '''
  Core MMJL logging engine.

  This object should be usable from Python, Jupyter magics, tests, and
  the command interface.
  '''
  
  def __init__(self, root: str | Path = "jupy_log"):
    self.root = Path(root).expanduser().resolve()
    self.artifacts = self.root / "artifacts"
    self.staging = self.root / "staging"
    self.staging_dir = self.staging
    self.timelines = self.root / "timelines"
    self.manifest = self.root / "manifest.tsv"
    
    self.artifacts.mkdir(parents=True, exist_ok=True)
    self.staging.mkdir(parents=True, exist_ok=True)
    self.timelines.mkdir(parents=True, exist_ok=True)
    self._ensure_manifest_schema()
  ##endof:  __init__(...)
  
  
  
  def _ensure_manifest_schema(self) -> None:
    '''
    Create the manifest or migrate the original five-column schema.

    Existing rows are preserved. Legacy rows receive monotonically
    assigned artifact sequences, a blank capture sequence, and role
    ``legacy``.
    '''
    
    legacy_columns = [
        "timestamp",
        "kind",
        "mime",
        "label",
        "path",
    ]
    lines = []
    old_header = []
    out_lines = []
    values = []
    row = {}
    
    if not self.manifest.exists():
      self.manifest.write_text(
          f"{MANIFEST_HEADER}\n",
          encoding="utf-8",
      )
      return
    ##endof:  if not self.manifest.exists()
    
    lines = self.manifest.read_text(
        encoding="utf-8"
    ).splitlines()
    
    if not lines:
      self.manifest.write_text(
          f"{MANIFEST_HEADER}\n",
          encoding="utf-8",
      )
      return
    ##endof:  if not lines
    
    old_header = lines[0].split("\t")
    
    if old_header == MANIFEST_COLUMNS:
      return
    ##endof:  if old_header == MANIFEST_COLUMNS
    
    if old_header != legacy_columns:
      raise RuntimeError(
          "Unsupported manifest schema: "
          f"{self.manifest} has columns {old_header!r}."
      )
    ##endof:  if old_header != legacy_columns
    
    out_lines = [MANIFEST_HEADER]
    
    for artifact_sequence, line in enumerate(lines[1:], start=1):
      if not line.strip():
        continue
      ##endof:  if not line.strip()
      
      values = line.split("\t")
      row = dict(zip(legacy_columns, values))
      out_lines.append(
          "\t".join([
              f"{artifact_sequence:0{SEQUENCE_WIDTH}d}",
              "",
              row.get("timestamp", ""),
              row.get("kind", ""),
              row.get("mime", ""),
              "legacy",
              row.get("label", ""),
              row.get("path", ""),
          ])
      )
    ##endof:  for artifact_sequence, line in enumerate(...)
    
    self.manifest.write_text(
        "\n".join(out_lines) + "\n",
        encoding="utf-8",
    )
  ##endof:  _ensure_manifest_schema()
  
  
  
  def _next_sequence(self, column_name: str) -> int:
    '''
    Return one greater than the largest numeric sequence in a column.

    Reading from the manifest on allocation keeps the counter persistent
    across kernel restarts and separate logger instances using one root.
    '''
    
    max_sequence = 0
    raw_value = ""
    rows = []
    
    rows = self.read_manifest_rows()
    
    for row in rows:
      raw_value = row.get(column_name, "").strip()
      
      if not raw_value:
        continue
      ##endof:  if not raw_value
      
      try:
        max_sequence = max(max_sequence, int(raw_value))
      except ValueError:
        continue
      ##endof:  try/except ValueError
    ##endof:  for row in rows
    
    return max_sequence + 1
  ##endof:  _next_sequence(...)
  
  
  
  def next_artifact_sequence(self) -> int:
    '''Return the next persistent artifact sequence.'''
    
    return self._next_sequence("artifact_sequence")
  ##endof:  next_artifact_sequence()
  
  
  
  def next_capture_sequence(self) -> int:
    '''Return the next persistent capture-group sequence.'''
    
    return self._next_sequence("capture_sequence")
  ##endof:  next_capture_sequence()
  
  
  
  def append(
        self,
        artifact_sequence: int,
        capture_sequence: int | None,
        stamp: str,
        kind: str,
        mime: str,
        role: str,
        label: str,
        path: str | Path,
      ) -> None:
    '''
    Append one artifact row to the manifest.

    Artifact sequence is authoritative within one log root. Capture
    sequence groups artifacts produced by one ``%%jupy_capture`` run.
    '''
    
    clean_label = ""
    clean_role = ""
    capture_text = ""
    
    clean_label = str(label).replace("\t", " ").replace("\n", " ")
    clean_role = str(role).replace("\t", " ").replace("\n", " ")
    
    if capture_sequence is not None:
      capture_text = f"{capture_sequence:0{SEQUENCE_WIDTH}d}"
    ##endof:  if capture_sequence is not None
    
    with self.manifest.open("a", encoding="utf-8") as handle:
      handle.write(
          "\t".join([
              f"{artifact_sequence:0{SEQUENCE_WIDTH}d}",
              capture_text,
              stamp,
              kind,
              mime,
              clean_role,
              clean_label,
              self._manifest_path_text(path),
          ])
          + "\n"
      )
    ##endof:  with self.manifest.open(...)
  ##endof:  append(...)
  
  
  
  def _manifest_path_text(self, path: str | Path) -> str:
    '''
    Store paths relative to the log root when possible.

    This keeps ``manifest.tsv`` portable when a whole ``jupy_log``
    directory is moved between machines or exported from SageMaker.
    '''

    path_obj = Path(path).expanduser().resolve()

    try:
      return path_obj.relative_to(self.root).as_posix()
    except ValueError:
      return str(path_obj)
    ##endof:  try/except ValueError
  ##endof:  _manifest_path_text(...)



  def _resolve_artifact_path(self, path: str | Path) -> Path:
    '''
    Resolve manifest paths that may be absolute or log-root-relative.
    '''

    path_obj = Path(path).expanduser()

    if path_obj.is_absolute():
      return path_obj.resolve()
    ##endof:  if path_obj.is_absolute()

    return (self.root / path_obj).resolve()
  ##endof:  _resolve_artifact_path(...)



  def _url_from_timeline(
        self,
        artifact_path: str | Path,
        out_path: str | Path,
      ) -> str:
    '''
    Build a portable URL from a timeline file to an artifact.
    '''

    resolved_artifact = self._resolve_artifact_path(artifact_path)
    resolved_out_path = Path(out_path).expanduser().resolve()

    try:
      relative_path = os.path.relpath(
          resolved_artifact,
          start=resolved_out_path.parent,
      )
      url = Path(relative_path).as_posix()
    except ValueError:
      url = resolved_artifact.as_uri()
    ##endof:  try/except ValueError

    return quote(url)
  ##endof:  _url_from_timeline(...)



  def log_bytes(
        self,
        data: bytes,
        label: str = "artifact",
        mime: str | None = None,
        capture_sequence: int | None = None,
        role: str = "artifact",
        announce: bool = True,
      ) -> Path:
    '''
    Log bytes as a detected or explicitly supplied MIME artifact.
    '''
    
    artifact_sequence = 0
    kind = ""
    suffix = ""
    stamp = ""
    path = None
    clean_label = ""
    
    mime = mime or detect_media_bytes(data)
    
    if mime not in MIME_INFO:
      raise ValueError(f"Unsupported or undetected MIME type: {mime}")
    ##endof:  if mime not in MIME_INFO
    
    artifact_sequence = self.next_artifact_sequence()
    kind, suffix = MIME_INFO[mime]
    stamp = jupy_stamp()
    clean_label = safe_label(label)
    path = self.artifacts / (
        f"{artifact_sequence:0{SEQUENCE_WIDTH}d}_"
        f"{stamp}_{clean_label}.{suffix}"
    )
    
    path.write_bytes(data)
    self.append(
        artifact_sequence=artifact_sequence,
        capture_sequence=capture_sequence,
        stamp=stamp,
        kind=kind,
        mime=mime,
        role=role,
        label=label,
        path=path,
    )
    
    if announce:
      print(f"[DONE] Logged {kind}: {path}")
    ##endof:  if announce
    
    return path
  ##endof:  log_bytes(...)
  
  
  
  def log_text(
        self,
        text: str,
        label: str = "text",
        mime: str = "text/plain",
        capture_sequence: int | None = None,
        role: str = "literal",
        announce: bool = True,
      ) -> Path:
    '''
    Log text, source code, Markdown, HTML, or JSON-like text.
    '''
    
    artifact_sequence = 0
    kind = ""
    suffix = ""
    stamp = ""
    path = None
    clean_label = ""
    
    if mime not in MIME_INFO:
      raise ValueError(f"Unsupported text MIME type: {mime}")
    ##endof:  if mime not in MIME_INFO
    
    artifact_sequence = self.next_artifact_sequence()
    kind, suffix = MIME_INFO[mime]
    stamp = jupy_stamp()
    clean_label = safe_label(label)
    path = self.artifacts / (
        f"{artifact_sequence:0{SEQUENCE_WIDTH}d}_"
        f"{stamp}_{clean_label}.{suffix}"
    )
    
    path.write_text(str(text), encoding="utf-8")
    self.append(
        artifact_sequence=artifact_sequence,
        capture_sequence=capture_sequence,
        stamp=stamp,
        kind=kind,
        mime=mime,
        role=role,
        label=label,
        path=path,
    )
    
    if announce:
      print(f"[DONE] Logged text: {path}")
    ##endof:  if announce
    
    return path
  ##endof:  log_text(...)
  
  
  
  def log_file(
        self,
        src_path: str | Path,
        label: str = "artifact",
        mime: str | None = None,
        capture_sequence: int | None = None,
        role: str = "file",
        announce: bool = True,
      ) -> Path:
    '''
    Log an existing file.

    @TODO  Preserve original filename in manifest metadata.
    @TODO  Optionally copy files without MIME detection.
    '''
    
    data = b""
    path = None
    
    path = Path(src_path).expanduser().resolve()

    if not path.exists():
      raise FileNotFoundError(
          "MMJL cannot log the requested file because it "
          "does not exist.\n"
          f"Input path: {src_path}\n"
          f"Resolved path: {path}\n"
          f"Current working directory: {Path.cwd()}"
      )
    ##endof:  if not path.exists()

    if not path.is_file():
      raise IsADirectoryError(
          "MMJL expected a file, but the resolved path is "
          f"not a file: {path}"
      )
    ##endof:  if not path.is_file()

    data = path.read_bytes()
    
    return self.log_bytes(
        data,
        label=label,
        mime=mime,
        capture_sequence=capture_sequence,
        role=role,
        announce=announce,
    )
  ##endof:  log_file(...)
  
  
  
  def log_mime_bundle(
        self,
        bundle: dict,
        label: str = "bundle",
        capture_sequence: int | None = None,
        role: str = "display",
        announce: bool = True,
      ) -> list[Path]:
    '''
    Log supported items from an IPython MIME bundle.

    All supported representations are retained for provenance. A later
    presentation layer may choose preferred representations.
    '''
    
    out_paths = []
    idx = 0
    item_label = ""
    kind = ""
    payload_text = ""
    payload_bytes = b""
    
    for idx, (mime, payload) in enumerate(bundle.items(), start=1):
      if mime not in MIME_INFO:
        continue
      ##endof:  if mime not in MIME_INFO
      
      kind, _suffix = MIME_INFO[mime]
      item_label = f"{label}-{idx:02d}-{kind}"
      
      if mime.startswith("text/") or mime == "application/json":
        if mime == "application/json":
          payload_text = json.dumps(payload, indent=2)
        else:
          payload_text = str(payload)
        ##endof:  if mime == "application/json"
        
        out_paths.append(
            self.log_text(
                payload_text,
                item_label,
                mime=mime,
                capture_sequence=capture_sequence,
                role=role,
                announce=False,
            )
        )
      
      elif mime == "image/svg+xml" and isinstance(payload, str):
        out_paths.append(
            self.log_text(
                payload,
                item_label,
                mime=mime,
                capture_sequence=capture_sequence,
                role=role,
                announce=False,
            )
        )
      
      else:
        if isinstance(payload, bytes):
          payload_bytes = payload
        else:
          payload_bytes = base64.b64decode(payload)
        ##endof:  if isinstance(payload, bytes)
        
        out_paths.append(
            self.log_bytes(
                payload_bytes,
                item_label,
                mime=mime,
                capture_sequence=capture_sequence,
                role=role,
                announce=False,
            )
        )
      ##endof:  if mime.startswith("text/") ...
    ##endof:  for idx, (mime, payload) in enumerate(...)
    
    if announce:
      print(f"[DONE] Logged {len(out_paths)} MIME item(s).")
    ##endof:  if announce
    
    return out_paths
  ##endof:  log_mime_bundle(...)
  
  
  
  def read_manifest_rows(self) -> list[dict[str, str]]:
    '''
    Read manifest rows as dictionaries.

    This is intentionally small and TSV-based for now.
    '''
    
    rows = []
    manifest_lines = []
    header = []
    values = []
    
    if not self.manifest.exists():
      return rows
    ##endof:  if not self.manifest.exists()
    
    manifest_lines = self.manifest.read_text(
        encoding="utf-8"
    ).splitlines()
    
    if not manifest_lines:
      return rows
    ##endof:  if not manifest_lines
    
    header = manifest_lines[0].split("\t")
    
    for line in manifest_lines[1:]:
      if not line.strip():
        continue
      ##endof:  if not line.strip()
      
      values = line.split("\t")
      rows.append(dict(zip(header, values)))
    ##endof:  for line in manifest_lines[1:]
    
    return rows
  ##endof:  read_manifest_rows()
  
  
  
  def inspect_manifest(self) -> list[dict[str, str]]:
    '''
    Print a small manifest summary.

    @TODO  Print time ranges.
    @TODO  Print total artifact sizes.
    @TODO  Print recent artifacts.
    '''
    
    rows = []
    kind_counts = {}
    mime_counts = {}
    kind = ""
    mime = ""
    
    rows = self.read_manifest_rows()
    
    for row in rows:
      kind = row.get("kind", "unknown")
      mime = row.get("mime", "unknown")
      kind_counts[kind] = kind_counts.get(kind, 0) + 1
      mime_counts[mime] = mime_counts.get(mime, 0) + 1
    ##endof:  for row in rows
    
    print(f"Manifest: {self.manifest}")
    print(f"Root: {self.root}")
    print(f"Artifacts: {self.artifacts}")
    print(f"Staging: {self.staging}")
    print(f"Timelines: {self.timelines}")
    print(f"Rows: {len(rows)}")
    
    print("\nBy kind:")
    for kind, count in sorted(kind_counts.items()):
      print(f"  {kind}: {count}")
    ##endof:  for kind, count in sorted(kind_counts.items())
    
    print("\nBy MIME:")
    for mime, count in sorted(mime_counts.items()):
      print(f"  {mime}: {count}")
    ##endof:  for mime, count in sorted(mime_counts.items())
    
    return rows
  ##endof:  inspect_manifest()
  
  
  
  def validate_manifest(self) -> list[Path]:
    '''
    Validate that manifest artifact paths exist.

    This first-pass validator intentionally checks only basic file
    presence. Later versions can add MIME/header consistency checks.

    @TODO  Add MIME/header consistency checks.
    @TODO  Add relative-path repair suggestions.
    @TODO  Add optional strict mode with nonzero CLI exit codes.
    '''
    
    rows = []
    missing = []
    path = None
    
    rows = self.read_manifest_rows()
    
    for row in rows:
      path = self._resolve_artifact_path(row.get("path", ""))
      
      if not path.exists():
        missing.append(path)
      ##endof:  if not path.exists()
    ##endof:  for row in rows
    
    print(f"Manifest: {self.manifest}")
    print(f"Rows checked: {len(rows)}")
    print(f"Missing artifacts: {len(missing)}")
    
    for path in missing:
      print(f"  MISSING: {path}")
    ##endof:  for path in missing
    
    return missing
  ##endof:  validate_manifest()
  
  
  
  def build_html(self, out_path: str | Path | None = None) -> Path:
    '''
    Build an HTML timeline from the manifest.

    @TODO  Add relative paths for portable exported directories.
    @TODO  Add optional collapsible code/input sections.
    @TODO  Add richer styling.
    '''
    
    out_path = Path(out_path or self.timelines / "timeline.html").expanduser().resolve()
    rows = self.read_manifest_rows()
    parts = []
    stamp = ""
    kind = ""
    mime = ""
    label = ""
    path = ""
    path_obj = None
    safe_path = ""
    safe_label = ""
    text = ""
    
    parts = [
        "<html>",
        "<body>",
        "<h1>Jupyter Log Timeline</h1>",
        "<pre>",
        html.escape(
            build_log_header(
                title="Multimodal Jupy Logger HTML Timeline",
                output_name=self._manifest_path_text(out_path),
            )
        ),
        "</pre>",
    ]
    
    for row in rows:
      stamp = row.get("timestamp", "")
      kind = row.get("kind", "")
      mime = row.get("mime", "")
      label = row.get("label", "")
      path = row.get("path", "")
      path_obj = self._resolve_artifact_path(path)
      safe_path = html.escape(
          self._url_from_timeline(path, out_path),
          quote=True,
      )
      safe_label = html.escape(label)
      
      parts.append("<hr>")
      parts.append(f"<h3>{safe_label}</h3>")
      parts.append(
          f"<p><code>{html.escape(stamp)}</code> — "
          f"{html.escape(kind)} — {html.escape(mime)}</p>"
      )
      
      if kind == "image":
        if mime == "image/svg+xml":
          parts.append(path_obj.read_text(encoding="utf-8"))
        else:
          parts.append(
              f'<img src="{safe_path}" '
              f'style="max-width:100%; height:auto;">'
          )
        ##endof:  if mime == "image/svg+xml"
      
      elif kind == "video":
        parts.append(
            f'<video controls src="{safe_path}" '
            f'style="max-width:100%; height:auto;"></video>'
        )
      
      elif kind == "audio":
        parts.append(f'<audio controls src="{safe_path}"></audio>')
      
      elif kind in ["text", "json"]:
        text = path_obj.read_text(encoding="utf-8")
        parts.append(f"<pre>{html.escape(text)}</pre>")
      
      elif kind == "html":
        parts.append(path_obj.read_text(encoding="utf-8"))
      
      else:
        parts.append(f'<a href="{safe_path}">{safe_path}</a>')
      ##endof:  if kind == "image"
    ##endof:  for row in rows
    
    parts.append("</body>")
    parts.append("</html>")
    
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(parts), encoding="utf-8")
    
    print(f"[DONE] HTML timeline written: {out_path}")
    return out_path
  ##endof:  build_html(...)
  
  
  
  def build_markdown(self, out_path: str | Path | None = None) -> Path:
    '''
    Build a Markdown timeline from the manifest.

    @TODO  Add optional collapsible code/input sections.
    @TODO  Add relative paths for portable exported directories.
    @TODO  Add frontmatter option.
    '''
    
    out_path = Path(out_path or self.timelines / "timeline.md").expanduser().resolve()
    rows = self.read_manifest_rows()
    parts = []
    stamp = ""
    kind = ""
    mime = ""
    label = ""
    path = ""
    path_obj = None
    safe_label = ""
    text = ""
    fence = ""
    artifact_url = ""
    
    parts = [
        "# Jupyter Log Timeline",
        "",
        build_log_header(
            title="Multimodal Jupy Logger Markdown Timeline",
            output_name=self._manifest_path_text(out_path),
        ),
        "",
    ]
    
    for row in rows:
      stamp = row.get("timestamp", "")
      kind = row.get("kind", "")
      mime = row.get("mime", "")
      label = row.get("label", "")
      path = row.get("path", "")
      path_obj = self._resolve_artifact_path(path)
      artifact_url = self._url_from_timeline(path, out_path)
      safe_label = label.replace("\n", " ")
      
      parts.append("---")
      parts.append("")
      parts.append(f"## {safe_label}")
      parts.append("")
      parts.append(f"`{stamp}` — `{kind}` — `{mime}`")
      parts.append("")
      
      if kind == "image":
        parts.append(f"![{safe_label}]({artifact_url})")
      
      elif kind == "video":
        parts.append(
            f'<video controls src="{artifact_url}" '
            f'style="max-width:100%; height:auto;"></video>'
        )
      
      elif kind == "audio":
        parts.append(f'<audio controls src="{artifact_url}"></audio>')
      
      elif kind in ["text", "json"]:
        text = path_obj.read_text(encoding="utf-8")
        fence = "json" if kind == "json" else ""
        parts.append(f"```{fence}")
        parts.append(text)
        parts.append("```")
      
      elif kind == "html":
        parts.append(path_obj.read_text(encoding="utf-8"))
      
      else:
        parts.append(f"[Artifact]({artifact_url})")
      ##endof:  if kind == "image"
      
      parts.append("")
    ##endof:  for row in rows
    
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(parts), encoding="utf-8")
    
    print(f"[DONE] Markdown timeline written: {out_path}")
    return out_path
  ##endof:  build_markdown(...)
##endof:  class MultimodalJupyLogger
````
