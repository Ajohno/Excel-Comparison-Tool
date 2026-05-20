from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QFileDialog, QComboBox, QMessageBox
)
import pandas as pd

from core.io_utils import load_excel_file, write_results_to_excel
from core.comparison import compare_dataframes


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Excel Comparison Tool")
        self.resize(700, 300)

        self.df1 = None
        self.df2 = None

        layout = QVBoxLayout()

        # File 1 row
        row1 = QHBoxLayout()
        self.file1_edit = QLineEdit()
        btn1 = QPushButton("Browse File 1")
        btn1.clicked.connect(self.pick_file1)
        row1.addWidget(QLabel("File 1:"))
        row1.addWidget(self.file1_edit)
        row1.addWidget(btn1)
        layout.addLayout(row1)

        # File 2 row
        row2 = QHBoxLayout()
        self.file2_edit = QLineEdit()
        btn2 = QPushButton("Browse File 2")
        btn2.clicked.connect(self.pick_file2)
        row2.addWidget(QLabel("File 2:"))
        row2.addWidget(self.file2_edit)
        row2.addWidget(btn2)
        layout.addLayout(row2)

        # Single-layer mapping (first milestone)
        map_row = QHBoxLayout()
        self.col1_combo = QComboBox()
        self.col2_combo = QComboBox()
        map_row.addWidget(QLabel("File 1 Column:"))
        map_row.addWidget(self.col1_combo)
        map_row.addWidget(QLabel("File 2 Column:"))
        map_row.addWidget(self.col2_combo)
        layout.addLayout(map_row)

        # Run
        run_btn = QPushButton("Run Comparison")
        run_btn.clicked.connect(self.run_comparison)
        layout.addWidget(run_btn)

        self.setLayout(layout)

    def pick_file1(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select File 1", "", "Excel Files (*.xlsx *.xls)")
        if not path:
            return
        self.file1_edit.setText(path)
        self.df1 = load_excel_file(path)
        self.col1_combo.clear()
        self.col1_combo.addItems([str(c) for c in self.df1.columns])

    def pick_file2(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select File 2", "", "Excel Files (*.xlsx *.xls)")
        if not path:
            return
        self.file2_edit.setText(path)
        self.df2 = load_excel_file(path)
        self.col2_combo.clear()
        self.col2_combo.addItems([str(c) for c in self.df2.columns])

    def run_comparison(self):
        if self.df1 is None or self.df2 is None:
            QMessageBox.warning(self, "Missing files", "Please select both Excel files.")
            return

        col1 = self.col1_combo.currentText()
        col2 = self.col2_combo.currentText()
        if not col1 or not col2:
            QMessageBox.warning(self, "Missing columns", "Please select columns for comparison.")
            return

        matched, not_found, review_log = compare_dataframes(
            self.df1.copy(),
            self.df2.copy(),
            [col1],
            [col2],
        )

        out_path, _ = QFileDialog.getSaveFileName(self, "Save results", "Comparison_Result.xlsx", "Excel Files (*.xlsx)")
        if not out_path:
            return

        write_results_to_excel(matched, not_found, review_log, out_path)

        QMessageBox.information(
            self,
            "Done",
            f"Comparison complete.\nMatched: {len(matched)}\nNot Found: {len(not_found)}"
        )