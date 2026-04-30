"""Core chemistry calculators with transparent equations and beginner-friendly outputs."""

from dataclasses import dataclass
from .exceptions import ValidationError


def _require_positive(value: float, name: str) -> None:
    if value <= 0:
        raise ValidationError(f"{name} must be greater than zero.")


def molarity_from_mass(grams: float, molar_mass_g_per_mol: float, volume_l: float) -> dict:
    _require_positive(grams, "Mass")
    _require_positive(molar_mass_g_per_mol, "Molar mass")
    _require_positive(volume_l, "Volume")
    moles = grams / molar_mass_g_per_mol
    molarity = moles / volume_l
    return {"moles": moles, "molarity": molarity, "equation": "M = (g / MW) / V"}


def grams_for_molarity(target_m: float, molar_mass_g_per_mol: float, volume_l: float) -> dict:
    _require_positive(target_m, "Target molarity")
    _require_positive(molar_mass_g_per_mol, "Molar mass")
    _require_positive(volume_l, "Volume")
    moles = target_m * volume_l
    grams = moles * molar_mass_g_per_mol
    return {"moles": moles, "grams": grams, "equation": "g = M × V × MW"}


def volume_for_molarity(grams: float, molar_mass_g_per_mol: float, target_m: float) -> dict:
    _require_positive(grams, "Mass")
    _require_positive(molar_mass_g_per_mol, "Molar mass")
    _require_positive(target_m, "Target molarity")
    moles = grams / molar_mass_g_per_mol
    volume_l = moles / target_m
    return {"moles": moles, "volume_l": volume_l, "equation": "V = (g / MW) / M"}


def dilution(c1: float | None, v1: float | None, c2: float | None, v2: float | None) -> dict:
    values = [c1, v1, c2, v2]
    if sum(x is None for x in values) != 1:
        raise ValidationError("Provide exactly one unknown field (leave one blank).")
    for name, v in [("C1", c1), ("V1", v1), ("C2", c2), ("V2", v2)]:
        if v is not None and v <= 0:
            raise ValidationError(f"{name} must be greater than zero.")
    if c1 is None:
        c1 = c2 * v2 / v1
        solved = "C1"
    elif v1 is None:
        v1 = c2 * v2 / c1
        solved = "V1"
    elif c2 is None:
        c2 = c1 * v1 / v2
        solved = "C2"
    else:
        v2 = c1 * v1 / c2
        solved = "V2"
    return {"C1": c1, "V1": v1, "C2": c2, "V2": v2, "solved": solved, "equation": "C1V1 = C2V2"}


def solvent_mix(final_volume_ml: float, target_fraction: float, stock_purity_fraction: float) -> dict:
    _require_positive(final_volume_ml, "Final volume")
    if not (0 < target_fraction < 1):
        raise ValidationError("Target solvent fraction must be between 0 and 1.")
    if not (0 < stock_purity_fraction <= 1):
        raise ValidationError("Stock purity fraction must be between 0 and 1.")
    if target_fraction > stock_purity_fraction:
        raise ValidationError("Impossible target: desired solvent fraction is higher than stock purity.")

    target_solvent_ml = final_volume_ml * target_fraction
    stock_solution_ml = target_solvent_ml / stock_purity_fraction
    stock_water_ml = stock_solution_ml * (1 - stock_purity_fraction)
    added_water_ml = final_volume_ml - stock_solution_ml
    final_water_ml = stock_water_ml + added_water_ml
    return {
        "stock_solution_ml": stock_solution_ml,
        "added_water_ml": added_water_ml,
        "final_solvent_ml": target_solvent_ml,
        "final_water_ml": final_water_ml,
        "equation": "stock volume = target solvent / stock purity",
    }


def equivalents(reference_mmol: float, target_equiv: float, molar_mass: float, purity_fraction: float = 1.0,
                density_g_ml: float | None = None, concentration_mol_l: float | None = None) -> dict:
    _require_positive(reference_mmol, "Reference mmol")
    _require_positive(target_equiv, "Equivalent ratio")
    _require_positive(molar_mass, "Molar mass")
    if not (0 < purity_fraction <= 1):
        raise ValidationError("Purity must be between 0 and 1.")
    mmol_needed = reference_mmol * target_equiv
    mol_needed = mmol_needed / 1000
    pure_grams = mol_needed * molar_mass
    actual_grams = pure_grams / purity_fraction
    out = {"mmol": mmol_needed, "mol": mol_needed, "grams": actual_grams, "equation": "mmol = ref_mmol × equiv"}
    if density_g_ml:
        out["ml_neat"] = actual_grams / density_g_ml
    if concentration_mol_l:
        out["ml_solution"] = (mol_needed / concentration_mol_l) * 1000
    return out


def limiting_reagent(reagents: list[dict], product_molar_mass: float, product_coeff: float = 1.0) -> dict:
    _require_positive(product_molar_mass, "Product molar mass")
    _require_positive(product_coeff, "Product stoichiometric coefficient")
    normalized = []
    for r in reagents:
        purity = r.get("purity", 1.0)
        if not (0 < purity <= 1):
            raise ValidationError("Reagent purity must be between 0 and 1.")
        moles = (r["amount_mol"] * purity) / r["coeff"]
        normalized.append({**r, "effective_moles_per_coeff": moles})
    limiting = min(normalized, key=lambda x: x["effective_moles_per_coeff"])
    reaction_extent = limiting["effective_moles_per_coeff"]
    product_moles = reaction_extent * product_coeff
    product_grams = product_moles * product_molar_mass
    for n in normalized:
        n["excess_equiv"] = n["effective_moles_per_coeff"] / reaction_extent
    return {
        "limiting_reagent": limiting["name"],
        "product_moles": product_moles,
        "product_grams": product_grams,
        "reagents": normalized,
    }


def theoretical_yield(limiting_moles: float, product_coeff: float, product_molar_mass: float,
                      actual_grams: float | None = None, product_purity_fraction: float = 1.0) -> dict:
    _require_positive(limiting_moles, "Limiting reagent moles")
    _require_positive(product_coeff, "Product coefficient")
    _require_positive(product_molar_mass, "Product molar mass")
    if not (0 < product_purity_fraction <= 1):
        raise ValidationError("Product purity must be between 0 and 1.")
    theo_moles = limiting_moles * product_coeff
    theo_grams_pure = theo_moles * product_molar_mass
    theo_grams_corrected = theo_grams_pure / product_purity_fraction
    out = {"theoretical_mmol": theo_moles * 1000, "theoretical_grams": theo_grams_corrected,
           "equation": "theoretical = limiting_moles × coeff × MW"}
    if actual_grams is not None:
        _require_positive(actual_grams, "Actual yield grams")
        out["percent_yield"] = (actual_grams / theo_grams_corrected) * 100
    return out
