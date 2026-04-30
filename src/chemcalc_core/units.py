"""Unit conversion helpers used by chemistry calculators."""

from .exceptions import ValidationError


MASS_TO_G = {"g": 1.0, "mg": 0.001}
MOLES_TO_MOL = {"mol": 1.0, "mmol": 0.001}
VOL_TO_L = {"L": 1.0, "mL": 0.001}


def _check_non_negative(value: float, name: str) -> None:
    if value < 0:
        raise ValidationError(f"{name} cannot be negative.")


def mass_to_g(value: float, unit: str) -> float:
    _check_non_negative(value, "Mass")
    if unit not in MASS_TO_G:
        raise ValidationError(f"Unsupported mass unit: {unit}")
    return value * MASS_TO_G[unit]


def moles_to_mol(value: float, unit: str) -> float:
    _check_non_negative(value, "Amount of substance")
    if unit not in MOLES_TO_MOL:
        raise ValidationError(f"Unsupported mole unit: {unit}")
    return value * MOLES_TO_MOL[unit]


def volume_to_l(value: float, unit: str) -> float:
    _check_non_negative(value, "Volume")
    if unit not in VOL_TO_L:
        raise ValidationError(f"Unsupported volume unit: {unit}")
    return value * VOL_TO_L[unit]


def g_to_unit(value_g: float, unit: str) -> float:
    if unit not in MASS_TO_G:
        raise ValidationError(f"Unsupported mass unit: {unit}")
    return value_g / MASS_TO_G[unit]


def mol_to_unit(value_mol: float, unit: str) -> float:
    if unit not in MOLES_TO_MOL:
        raise ValidationError(f"Unsupported mole unit: {unit}")
    return value_mol / MOLES_TO_MOL[unit]


def l_to_unit(value_l: float, unit: str) -> float:
    if unit not in VOL_TO_L:
        raise ValidationError(f"Unsupported volume unit: {unit}")
    return value_l / VOL_TO_L[unit]
