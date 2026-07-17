# MMJL Getting-Started Guides

Use the guide matching the environment and task.

- [SageMaker portable setup](sagemaker_portable_setup.md)  
  Recommended drop-in setup for existing SageMaker course notebooks.

- [Windows explicit-source setup](windows_explicit_source_setup.md)  
  Use a canonical local checkout from a notebook outside the repository.

- [Portable smoke-test workflow](portable_smoke_test_workflow.md)  
  Regression and transfer validation, including guarded destructive reset.

- [Inline checks without `environment_checks.py`](manual_environment_checks_without_module.md)  
  Fallback for older or incomplete source transfers.

The setup philosophy is:

```text
make source selection visible
make kernel/environment state visible
make NOTEBOOK_SLUG visible
never delete a real log automatically
continue an existing named log deliberately
validate and export before leaving the environment
zip and download the complete jupy_log_* directory
```
