"""PROMBARJIN application package bootstrap."""

from . import omega_compliance as _omega_compliance
from .strict_runtime import patch_omega_compliance

patch_omega_compliance(_omega_compliance)
