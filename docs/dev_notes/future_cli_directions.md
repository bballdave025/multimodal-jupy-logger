## Future CLI directions

MMJL should continue separating notebook-only interfaces from transformations
that are useful in plain Python or from a terminal.

The notebook magics should remain thin wrappers over reusable Python APIs.
Where a transformation does not require a live IPython kernel, it should also
be callable through the command line.

Likely out-of-notebook operations include:

```text
notebook file -> PDF
notebook file -> HTML
notebook file -> Markdown
log root -> inspect manifest
log root -> validate artifacts
log root -> build Markdown timeline
log root -> build HTML timeline
artifact directory -> archive, export, or integrity check
```

Possible Python APIs:

```python
export_notebook_to_pdf(
    input_path,
    output_path=None,
    hide_code=True,
)

export_notebook_to_html(
    input_path,
    output_path=None,
    hide_code=False,
)

export_notebook_to_markdown(
    input_path,
    output_dir=None,
)

inspect_manifest(root)
validate_log(root)
build_timeline_markdown(root)
build_timeline_html(root)
```

The existing PDF module already suggests a module-level CLI pattern:

```bash
python -m multimodal_jupy_logger.jupy_pdf_utils \
  analysis.ipynb \
  -o analysis.pdf
```

A future unified MMJL CLI could expose commands such as:

```bash
python -m multimodal_jupy_logger.mmjl_cli \
  inspect jupy_log

python -m multimodal_jupy_logger.mmjl_cli \
  validate jupy_log

python -m multimodal_jupy_logger.mmjl_cli \
  markdown jupy_log

python -m multimodal_jupy_logger.mmjl_cli \
  html jupy_log

python -m multimodal_jupy_logger.mmjl_cli \
  export-notebook-html analysis.ipynb

python -m multimodal_jupy_logger.mmjl_cli \
  export-notebook-pdf analysis.ipynb
```

The conceptual split should remain:

```text
Notebook-only:
  - line and cell magics
  - live cell execution and capture
  - IPython display hooks
  - active-kernel interactions

Out-of-notebook:
  - notebook-file conversion
  - manifest inspection
  - artifact validation
  - timeline generation
  - archive and export operations
```

Whole-notebook PDF and HTML conversion are especially natural CLI and Python
API operations. They may also have notebook-magic frontends, but they should
not require a notebook environment merely to perform the underlying
transformation.

This is follow-up direction rather than part of the current PR success
criteria.
