# ChemCalc Lab

ChemCalc Lab is a local/offline Windows-friendly desktop calculator for chemistry solution preparation and reaction calculations.

## Features
- Molarity calculations
- Dilution calculator (`C1V1 = C2V2`)
- Solvent v/v correction for non-anhydrous stocks
- Equivalents calculator
- Limiting reagent and theoretical product
- Theoretical/percent yield
- Saved recipes in editable JSON

## Project layout
- `src/chemcalc_core/` pure Python calculation engine (no GUI dependency)
- `src/chemcalc_gui/` PySide6 desktop GUI
- `data/` JSON recipes/presets
- `tests/` pytest tests

## Windows PowerShell setup (Python 3.12+)
```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -e .[dev]
```

## Run app
```powershell
python -m chemcalc_gui
```

Optional console entry point:
```powershell
chemcalc-lab
```

## Run tests
```powershell
pytest
```

## Build a Windows executable (after testing dev mode)
```powershell
pyinstaller --noconfirm --windowed --name ChemCalcLab --paths src src/chemcalc_gui/__main__.py
```

## Future Android paths (not part of V1)
- Kivy + Buildozer
- BeeWare / Briefcase
- Local web app / PWA wrapping the same `chemcalc_core`
- Possible future PySide6 Android deployment

The app intentionally keeps chemistry math in `chemcalc_core` so future interfaces can reuse the same validated logic.
