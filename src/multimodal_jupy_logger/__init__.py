'''
Public package interface for Multimodal Jupy Logger.

@file   : __init__.py
          specifically, src/multimodal_jupy_logger/__init__.py
@author : David Black        GitHub: @bballdave025     comments signed "DWB"
@since  : 2026-06-1x, mid-June 2026

Part of the `multimodal-jupy-logger` project, which can potentially be
a package.
'''

from multimodal_jupy_logger.environment_checks import (
  check_packages,
  print_environment_check,
  print_package_checks,
)
from multimodal_jupy_logger.logger import MultimodalJupyLogger
from multimodal_jupy_logger.magics import (
  MultimodalJupyLoggerMagics,
  jupy_logger_register,
  register_jupy_logger,
)

__all__ = [
  "MultimodalJupyLogger",
  "MultimodalJupyLoggerMagics",
  "check_packages",
  "jupy_logger_register",
  "print_environment_check",
  "print_package_checks",
  "register_jupy_logger",
]

##endof:  __all__
