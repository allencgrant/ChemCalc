import pytest

from chemcalc_core.calculators import (
    dilution,
    equivalents,
    grams_for_molarity,
    limiting_reagent,
    molarity_from_mass,
    solvent_mix,
    theoretical_yield,
)
from chemcalc_core.exceptions import ValidationError
from chemcalc_core.units import g_to_unit, l_to_unit, mass_to_g, mol_to_unit, moles_to_mol, volume_to_l


def test_molarity():
    r = molarity_from_mass(5.844, 58.44, 0.1)
    assert r["molarity"] == pytest.approx(1.0)


def test_grams_for_molarity():
    r = grams_for_molarity(0.5, 58.44, 0.1)
    assert r["grams"] == pytest.approx(2.922)


def test_dilution_solve_v1():
    r = dilution(2.0, None, 0.5, 100)
    assert r["V1"] == pytest.approx(25.0)


def test_solvent_mix_impossible():
    with pytest.raises(ValidationError):
        solvent_mix(100, 0.95, 0.91)


def test_solvent_mix_valid():
    r = solvent_mix(300, 2/3, 0.91)
    assert r["stock_solution_ml"] == pytest.approx(219.7802, rel=1e-4)


def test_equivalents_basic():
    r = equivalents(10, 1.2, 100)
    assert r["mmol"] == pytest.approx(12)
    assert r["grams"] == pytest.approx(1.2)


def test_limiting_reagent():
    reagents = [
        {"name": "A", "amount_mol": 0.01, "coeff": 1, "purity": 1.0},
        {"name": "B", "amount_mol": 0.03, "coeff": 2, "purity": 1.0},
    ]
    r = limiting_reagent(reagents, product_molar_mass=150, product_coeff=1)
    assert r["limiting_reagent"] == "A"


def test_theoretical_yield_percent():
    r = theoretical_yield(0.01, 1, 100, actual_grams=0.8)
    assert r["theoretical_grams"] == pytest.approx(1.0)
    assert r["percent_yield"] == pytest.approx(80)


def test_unit_conversions():
    assert mass_to_g(1000, "mg") == pytest.approx(1)
    assert moles_to_mol(1000, "mmol") == pytest.approx(1)
    assert volume_to_l(250, "mL") == pytest.approx(0.25)
    assert g_to_unit(1, "mg") == pytest.approx(1000)
    assert mol_to_unit(1, "mmol") == pytest.approx(1000)
    assert l_to_unit(0.25, "mL") == pytest.approx(250)


def test_zero_input_error():
    with pytest.raises(ValidationError):
        molarity_from_mass(0, 58.44, 0.1)
