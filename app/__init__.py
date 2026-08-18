"""PROMBARJIN application package bootstrap."""

from . import omega_compliance as _omega_compliance
from . import omega_strict as _omega_strict
from .strict_runtime import patch_omega_compliance, _patch_strict_report

patch_omega_compliance(_omega_compliance)

# Ensure strict runtime reports receive the same compliance schema even when
# tests import build_strict_runtime directly from app.omega_strict.
_original_build_strict_runtime = _omega_strict.build_strict_runtime


def _build_strict_runtime(text: str, evidence_count: int = 0):
    report = _original_build_strict_runtime(text, evidence_count=evidence_count)
    return _patch_strict_report(report)


_omega_strict.build_strict_runtime = _build_strict_runtime
