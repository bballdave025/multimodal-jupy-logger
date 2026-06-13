# multimodal_jupy_logger.py

from __future__ import annotations

import argparse
import base64
import html
import json
import shlex
from datetime import datetime
from pathlib import Path

from IPython.core.magic import Magics, line_magic, cell_magic, magics_class
from IPython.display import Javascript, display


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
    "text/html": ("html", "html"),
    "application/json": ("json", "json"),
}


def jupy_stamp():
    return datetime.now().astimezone().strftime("%s_%Y-%m-%dT%H%M%S%f%z")


def detect_media_bytes(data):
    if data.startswith(bytes.fromhex("89504E470D0A1A0A")):
        return "image/png"
    if data.startswith(bytes.fromhex("FFD8FF")):
        return "image/jpeg"
    if data.startswith(b"GIF87a") or data.startswith(b"GIF89a"):
        return "image/gif"
    if data.startswith(b"RIFF") and data[8:12] == b"WEBP":
        return "image/webp"

    if len(data) >= 12 and data[4:8] == b"ftyp":
        brand = data[8:12]
        if brand == b"qt  ":
            return "video/quicktime"
        if brand in [b"isom", b"iso2", b"mp41", b"mp42", b"avc1", b"M4V "]:
            return "video/mp4"
    if data.startswith(b"\x1A\x45\xDF\xA3"):
        return "video/webm"

    if data.startswith(b"RIFF") and data[8:12] == b"WAVE":
        return "audio/wav"
    if data.startswith(b"ID3") or data.startswith(bytes.fromhex("FFFB")):
        return "audio/mpeg"
    if data.startswith(b"OggS"):
        return "audio/ogg"
    if data.startswith(b"fLaC"):
        return "audio/flac"

    return None


class MultimodalJupyLogger:

    def __init__(self, root="jupy_log"):
        self.root = Path(root).expanduser().resolve()
        self.artifacts = self.root / "artifacts"
        self.manifest = self.root / "manifest.tsv"
        self.artifacts.mkdir(parents=True, exist_ok=True)

        if not self.manifest.exists():
            self.manifest.write_text(
                "timestamp\tkind\tmime\tlabel\tpath\n",
                encoding="utf-8",
            )

    def append(self, stamp, kind, mime, label, path):
        with self.manifest.open("a", encoding="utf-8") as f:
            f.write(f"{stamp}\t{kind}\t{mime}\t{label}\t{path}\n")

    def log_bytes(self, data, label="artifact", mime=None):
        mime = mime or detect_media_bytes(data)

        if mime not in MIME_INFO:
            raise ValueError(f"Unsupported or undetected MIME type: {mime}")

        kind, suffix = MIME_INFO[mime]
        stamp = jupy_stamp()
        path = self.artifacts / f"{stamp}_{label}.{suffix}"

        path.write_bytes(data)
        self.append(stamp, kind, mime, label, path)

        print(f"[DONE] Logged {kind}: {path}")
        return path

    def log_text(self, text, label="text", mime="text/plain"):
        kind, suffix = MIME_INFO[mime]
        stamp = jupy_stamp()
        path = self.artifacts / f"{stamp}_{label}.{suffix}"

        path.write_text(str(text), encoding="utf-8")
        self.append(stamp, kind, mime, label, path)

        print(f"[DONE] Logged text: {path}")
        return path

    def log_file(self, src_path, label="artifact", mime=None):
        src_path = Path(src_path).expanduser().resolve()
        data = src_path.read_bytes()
        return self.log_bytes(data, label=label, mime=mime)

    def log_mime_bundle(self, bundle, label="bundle"):
        out_paths = []

        for idx, (mime, payload) in enumerate(bundle.items(), start=1):
            if mime not in MIME_INFO:
                continue

            kind, _suffix = MIME_INFO[mime]
            item_label = f"{label}-{idx:02d}-{kind}"

            if mime.startswith("text/") or mime in ["application/json"]:
                if mime == "application/json":
                    payload = json.dumps(payload, indent=2)
                out_paths.append(self.log_text(payload, item_label, mime=mime))
            else:
                data = base64.b64decode(payload)
                out_paths.append(self.log_bytes(data, item_label, mime=mime))

        print(f"[DONE] Logged {len(out_paths)} MIME item(s).")
        return out_paths

    def build_html(self, out_path=None):
        out_path = Path(out_path or self.root / "timeline.html")
        rows = self.manifest.read_text(encoding="utf-8").splitlines()[1:]

        parts = ["<html><body>", "<h1>Jupyter Log Timeline</h1>"]

        for row in rows:
            stamp, kind, mime, label, path = row.split("\t")
            path_obj = Path(path)
            safe_path = html.escape(str(path_obj))
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

        parts.append("</body></html>")
        out_path.write_text("\n".join(parts), encoding="utf-8")

        print(f"[DONE] HTML timeline written: {out_path}")
        return out_path


    def build_markdown(self, out_path=None):
        out_path = Path(out_path or self.root / "timeline.md")
        rows = self.manifest.read_text(encoding="utf-8").splitlines()[1:]

        parts = ["# Jupyter Log Timeline", ""]

        for row in rows:
            stamp, kind, mime, label, path = row.split("\t")
            path_obj = Path(path)
            safe_label = label.replace("\n", " ")

            parts.append("---")
            parts.append("")
            parts.append(f"## {safe_label}")
            parts.append("")
            parts.append(f"`{stamp}` — `{kind}` — `{mime}`")
            parts.append("")

            if kind == "image":
                parts.append(f'![{safe_label}]({path_obj})')

            elif kind == "video":
                parts.append(
                    f'<video controls src="{path_obj}" '
                    f'style="max-width:100%; height:auto;"></video>'
                )

            elif kind == "audio":
                parts.append(f'<audio controls src="{path_obj}"></audio>')

            elif kind in ["text", "json"]:
                text = path_obj.read_text(encoding="utf-8")
                fence = "json" if kind == "json" else ""
                parts.append(f"```{fence}")
                parts.append(text)
                parts.append("```")

            elif kind == "html":
                parts.append(path_obj.read_text(encoding="utf-8"))

            else:
                parts.append(f"[Artifact]({path_obj})")

            parts.append("")

        out_path.write_text("\n".join(parts), encoding="utf-8")
        print(f"[DONE] Markdown timeline written: {out_path}")
        return out_path


@magics_class
class MultimodalJupyLoggerMagics(Magics):

    def __init__(self, shell):
        super().__init__(shell)
        self.logger = MultimodalJupyLogger()

    @line_magic
    def jupy_save(self, line=""):
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

    @line_magic
    def jupy_file(self, line=""):
        parser = argparse.ArgumentParser(prog="%jupy_file")
        parser.add_argument("--label", default="artifact")
        parser.add_argument("--mime", default=None)
        parser.add_argument("paths", nargs="+")
        args = parser.parse_args(shlex.split(line))

        out = []
        for idx, raw_path in enumerate(args.paths, start=1):
            label = f"{args.label}-{idx:02d}"
            out.append(
                self.logger.log_file(raw_path, label=label, mime=args.mime)
            )
        return out

    @cell_magic
    def jupy_log(self, line="", cell=None):
        parser = argparse.ArgumentParser(prog="%%jupy_log")
        parser.add_argument("--label", default="cell")
        parser.add_argument("--mime", default="text/plain")
        args = parser.parse_args(shlex.split(line))

        return self.logger.log_text(cell or "", args.label, mime=args.mime)

    @line_magic
    def jupy_markdown(self, line=""):
        return self.logger.build_markdown()

    @line_magic
    def jupy_html(self, line=""):
        return self.logger.build_html()


def register_jupy_logger():
    ip = get_ipython()
    ip.register_magics(MultimodalJupyLoggerMagics)
    print(
        (
            "[DONE] Registered: %jupy_save, %jupy_file, "
            "%%jupy_log, %jupy_markdown %jupy_html"
        )
    )

def jupy_logger_register():
    register_jupy_logger()
