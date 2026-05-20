import sys
from PySide6.QtWidgets import QApplication
from window import MainWindow

def main():
    # Create the application and main window
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()