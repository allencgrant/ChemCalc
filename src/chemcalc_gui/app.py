import json
from pathlib import Path
from PySide6.QtWidgets import (
    QApplication, QHBoxLayout, QLabel, QLineEdit, QMainWindow, QMessageBox,
    QPushButton, QTabWidget, QTextEdit, QVBoxLayout, QWidget
)
from chemcalc_core.calculators import (
    dilution, equivalents, grams_for_molarity, limiting_reagent,
    molarity_from_mass, solvent_mix, theoretical_yield, volume_for_molarity,
)
from chemcalc_core.exceptions import ValidationError

DATA_FILE = Path("data/recipes.json")

class CalcTab(QWidget):
    def __init__(self, title: str, fields: list[str], on_calc):
        super().__init__()
        self.on_calc = on_calc
        self.inputs = {}
        layout = QVBoxLayout()
        for f in fields:
            row = QHBoxLayout(); row.addWidget(QLabel(f)); e = QLineEdit(); row.addWidget(e); self.inputs[f] = e; layout.addLayout(row)
        btn_row = QHBoxLayout()
        calc_btn = QPushButton("Calculate"); calc_btn.clicked.connect(self.calculate)
        reset_btn = QPushButton("Reset"); reset_btn.clicked.connect(self.reset)
        btn_row.addWidget(calc_btn); btn_row.addWidget(reset_btn)
        layout.addLayout(btn_row)
        self.result = QTextEdit(); self.result.setReadOnly(True)
        self.explain = QTextEdit(); self.explain.setReadOnly(True)
        layout.addWidget(QLabel("Result")); layout.addWidget(self.result)
        layout.addWidget(QLabel("Equation / explanation")); layout.addWidget(self.explain)
        self.setLayout(layout)

    def calculate(self):
        try:
            values = {k: v.text().strip() for k, v in self.inputs.items()}
            result, explanation = self.on_calc(values)
            self.result.setPlainText(result)
            self.explain.setPlainText(explanation)
        except ValidationError as e:
            QMessageBox.warning(self, "Validation error", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Unexpected error: {e}")

    def reset(self):
        for w in self.inputs.values(): w.clear()
        self.result.clear(); self.explain.clear()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__(); self.setWindowTitle("ChemCalc Lab")
        tabs = QTabWidget()
        tabs.addTab(self.build_molarity_tab(), "Molarity")
        tabs.addTab(self.build_dilution_tab(), "Dilution")
        tabs.addTab(self.build_solvent_tab(), "Solvent Mixtures")
        tabs.addTab(self.build_equiv_tab(), "Equivalents")
        tabs.addTab(self.build_limit_tab(), "Limiting Reagent")
        tabs.addTab(self.build_yield_tab(), "Yield")
        tabs.addTab(self.build_recipes_tab(), "Saved Recipes")
        self.setCentralWidget(tabs)

    def build_molarity_tab(self):
        def run(v):
            mode = v["Mode (from_mass|from_target|from_volume)"]
            if mode == "from_mass":
                r = molarity_from_mass(float(v["Mass g"]), float(v["Molar mass g/mol"]), float(v["Volume L"]))
                return f"Molarity: {r['molarity']:.6g} M", f"Moles={r['moles']:.6g}; {r['equation']}"
            if mode == "from_target":
                r = grams_for_molarity(float(v["Target M"]), float(v["Molar mass g/mol"]), float(v["Volume L"]))
                return f"Required grams: {r['grams']:.6g} g", f"Moles={r['moles']:.6g}; {r['equation']}"
            r = volume_for_molarity(float(v["Mass g"]), float(v["Molar mass g/mol"]), float(v["Target M"]))
            return f"Required volume: {r['volume_l']:.6g} L", f"Moles={r['moles']:.6g}; {r['equation']}"
        return CalcTab("Molarity", ["Mode (from_mass|from_target|from_volume)","Mass g","Molar mass g/mol","Volume L","Target M"], run)

    def build_dilution_tab(self):
        def parse(x): return None if x == "" else float(x)
        return CalcTab("Dilution", ["C1","V1","C2","V2"], lambda v: (str(dilution(parse(v['C1']), parse(v['V1']), parse(v['C2']), parse(v['V2']))), "C1V1=C2V2"))

    def build_solvent_tab(self):
        return CalcTab("Solvent", ["Final volume mL","Target fraction (0-1)","Stock purity (0-1)"],
            lambda v: (str(solvent_mix(float(v['Final volume mL']), float(v['Target fraction (0-1)']), float(v['Stock purity (0-1)']))), "Non-anhydrous v/v correction"))

    def build_equiv_tab(self):
        return CalcTab("Equiv", ["Reference mmol","Target equiv","Molar mass","Purity (0-1)","Density g/mL (optional)","Concentration mol/L (optional)"],
            lambda v: (str(equivalents(float(v['Reference mmol']), float(v['Target equiv']), float(v['Molar mass']), float(v['Purity (0-1)'] or 1.0),
                float(v['Density g/mL (optional)']) if v['Density g/mL (optional)'] else None,
                float(v['Concentration mol/L (optional)']) if v['Concentration mol/L (optional)'] else None)), "Equivalent-based scaling"))

    def build_limit_tab(self):
        return CalcTab("Limiting", ["Reagents JSON list","Product MW","Product coeff"],
            lambda v: (str(limiting_reagent(json.loads(v['Reagents JSON list']), float(v['Product MW']), float(v['Product coeff']))), "Find minimum amount/coefficient"))

    def build_yield_tab(self):
        return CalcTab("Yield", ["Limiting moles","Product coeff","Product MW","Actual grams (optional)","Product purity (0-1)"],
            lambda v: (str(theoretical_yield(float(v['Limiting moles']), float(v['Product coeff']), float(v['Product MW']),
                float(v['Actual grams (optional)']) if v['Actual grams (optional)'] else None, float(v['Product purity (0-1)'] or 1.0))), "Yield and %yield equations"))

    def build_recipes_tab(self):
        w = QWidget(); layout = QVBoxLayout();
        self.recipes_box = QTextEdit();
        load_btn = QPushButton("Load recipes"); save_btn = QPushButton("Save recipes")
        load_btn.clicked.connect(self.load_recipes); save_btn.clicked.connect(self.save_recipes)
        layout.addWidget(load_btn); layout.addWidget(save_btn); layout.addWidget(self.recipes_box); w.setLayout(layout); return w

    def load_recipes(self):
        DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
        if DATA_FILE.exists(): self.recipes_box.setPlainText(DATA_FILE.read_text(encoding='utf-8'))
        else: self.recipes_box.setPlainText("[]")

    def save_recipes(self):
        try:
            parsed = json.loads(self.recipes_box.toPlainText())
            DATA_FILE.write_text(json.dumps(parsed, indent=2), encoding='utf-8')
            QMessageBox.information(self, "Saved", "Recipes saved.")
        except json.JSONDecodeError:
            QMessageBox.warning(self, "Invalid JSON", "Please enter valid JSON.")

def main():
    app = QApplication([])
    window = MainWindow(); window.resize(900, 700); window.show()
    app.exec()
