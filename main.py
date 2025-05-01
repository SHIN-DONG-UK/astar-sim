from PyQt6.QtWidgets import QApplication
from model.grid   import Grid
from ui.pyqt_view import PyQtView
from ui.controller   import Controller
import sys

app   = QApplication(sys.argv)
grid  = Grid(40, 30)
view  = PyQtView(grid)
ctrl  = Controller(grid, view)

view.resize(1100, 750)
view.show()
sys.exit(app.exec())
