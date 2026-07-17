# MMJL Email Source Bundle

Recommended email order:

1. `01_mmjl_email_core_source.md`
2. `02_mmjl_email_magics_and_utils.md`
3. `03_mmjl_email_optional_pdf_and_cli.md`

The first two messages contain the core MVP source. The third contains the
PDF helper and current CLI module. PDF rendering remains optional for the PR,
but `jupy_pdf_utils.py` should still be copied so import safety can be tested.

The portable notebook JSON is intentionally separate, because the current
Windows Try 1 copy contains setup-cell changes that are not present in the
earlier transfer-kit notebook. Export/copy the final updated notebook after
Try 2 is settled.
