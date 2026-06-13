# Multimodal Jupy Logger

Personal general-purpose tooling for logging, preserving, and replaying
multimodal Jupyter/IPython notebook workflows.

## Purpose

`multimodal-jupy-logger` is an experimental notebook logging utility for
capturing notebook activity as a durable multimodal event stream.

It is designed to support:

- source-code logging
- stdout/stderr capture
- rich display output capture
- image, audio, and video artifact logging
- MIME-aware persistence
- HTML and Markdown timeline export
- notebook backup workflows
- optional PDF export support

The guiding idea is that notebook workflows are not just source-code cells.
They are interactive, stateful, multimodal execution traces.

## Status

Early experimental tooling.

The current implementation focuses on a small, inspectable core:

- Jupyter/IPython magics
- manifest-based artifact logging
- MIME-to-file persistence
- replay-oriented HTML/Markdown output
- notebook backup helpers

The project is intentionally lightweight and text-first.

## Design Principles

- Preserve first; transform later.
- Treat notebook outputs as MIME bundles.
- Keep capture, persistence, replay, and transformation separate.
- Avoid coupling to specific media libraries when possible.
- Prefer deterministic plain-text manifests.
- Make logs useful outside the original notebook frontend.
- Keep employer-specific workflows, data, and implementations out of scope.

## Intended Use

This project is intended for:

- personal notebook workflows
- ML/AI experimentation
- multimodal notebook logging
- OCR/HTR experimentation
- educational notebook tooling
- provenance-aware exploratory coding
- workflow reconstruction

## Not Intended For

This repository is not:

- an employer-specific notebook system
- a proprietary workflow implementation
- a confidential data pipeline
- a replacement for full experiment-tracking platforms
- a media transcoding framework

Heavyweight media conversion should generally be delegated to external tools
such as `ffmpeg`.

## IP / Provenance Classification

See the [classification scheme](https://github.com/bballdave025/dwb-ip-notes/blob/main/IP_Classification_Framework_rev2026-06-08.md) in my `dwb-ip-notes` repository for more details.

Primary classification:

- D — Personal General-Purpose Tooling

Secondary classification:

- E — Potentially Integrable Independent Tooling

This project is maintained as independent, organization-agnostic tooling.
It does not include proprietary datasets, confidential workflows, internal
systems, or employer-specific implementations.

## PDF Export Notes

PDF export support is based on notebook backup/export ideas using Jupyter
`nbconvert`, `WebPDFExporter`, metadata headers, and optional notebook-save
integration. HTML export remains the preferred primary path because it better
preserves multimodal notebook output. PDF support is useful for portable
snapshots and archival/reporting workflows.

## License

MIT License.

*End of document*
