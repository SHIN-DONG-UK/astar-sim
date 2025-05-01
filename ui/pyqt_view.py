# ui/pyqt_view.py
from PyQt6.QtWidgets import (
    QWidget, QMainWindow, QPushButton, QVBoxLayout,
    QHBoxLayout, QLabel, QComboBox, QSlider, QApplication, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QSize
from PyQt6.QtGui import QPainter, QColor, QPen, QMouseEvent

from model.tile_consts import EMPTY, WALL, START, GOAL, PLAYER
CELL = 20   # px

# ───────────────────────────────────
# 1) 캔버스
# ───────────────────────────────────
class GridCanvas(QWidget):
    cellClicked = pyqtSignal(int, int, int)    # x, y, Qt.MouseButton
    cellDragged = pyqtSignal(int, int, int)

    def __init__(self, grid, parent=None):
        super().__init__(parent)
        self.grid = grid
        w, h = grid.cols * CELL, grid.rows * CELL
        self.setMinimumSize(QSize(w, h))
        self.setMouseTracking(True)
        self._mouse_down = False

    # 페인팅
    def paintEvent(self, e):
        qp = QPainter(self)
        self._draw_grid(qp)
        self._draw_tiles(qp)
        self._draw_player(qp)
        self._draw_path(qp)

    # View -> Controller
    def mousePressEvent(self, ev: QMouseEvent):
        self._mouse_down = True
        x, y = ev.position().toPoint().x() // CELL, ev.position().toPoint().y() // CELL
        self.cellClicked.emit(x, y, ev.button())

    def mouseMoveEvent(self, ev):
        if not self._mouse_down:
            return
        x, y = ev.position().toPoint().x() // CELL, ev.position().toPoint().y() // CELL
        self.cellDragged.emit(x, y, ev.buttons())

    def mouseReleaseEvent(self, ev):
        self._mouse_down = False

    # 내부 헬퍼들
    def _draw_grid(self, qp: QPainter):
        pen = QPen(QColor(200, 200, 200))
        qp.setPen(pen)
        # 수직
        for c in range(self.grid.cols + 1):
            qp.drawLine(c * CELL, 0, c * CELL, self.grid.rows * CELL)
        # 수평
        for r in range(self.grid.rows + 1):
            qp.drawLine(0, r * CELL, self.grid.cols * CELL, r * CELL)

    def _draw_tiles(self, qp):
        for x in range(self.grid.cols):
            for y in range(self.grid.rows):
                t = self.grid.get(x, y)
                color = {EMPTY: None, WALL: QColor("black"), START: QColor("green"),
                         GOAL: QColor("red"), PLAYER: QColor("red")}.get(t)
                if color:
                    qp.fillRect(x*CELL+1, y*CELL+1, CELL-1, CELL-1, color)

    def _draw_player(self, qp):
        if getattr(self.grid, "player", None):
            x, y = self.grid.player
            qp.fillRect(x*CELL+4, y*CELL+4, CELL-8, CELL-8, QColor("red"))

    # ① 궤적 / 최종 경로 그리기
    def _draw_path(self, qp):
        if not getattr(self.grid, "trail", None) or len(self.grid.trail) < 2:
            return
        pen = QPen(QColor(30, 144, 255), 3)   # DodgerBlue, 두께 3
        qp.setPen(pen)

        # trail 에 저장된 모든 좌표를 “셀 중심” 픽셀로 변환
        pts = [ (x*CELL + CELL//2, y*CELL + CELL//2) for x, y in self.grid.trail ]
        # poly-line 그리기
        for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
            qp.drawLine(x1, y1, x2, y2)

# ───────────────────────────────────
# 2) 컨트롤 패널
# ───────────────────────────────────
class ControlPanel(QFrame):
    tileSelected = pyqtSignal(int)         # 0=벽,1=시작,2=목표,3=지우기
    runClicked   = pyqtSignal()
    stepClicked  = pyqtSignal()
    speedChanged = pyqtSignal(int)
    heuristicChanged = pyqtSignal(str)
    clearClicked = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setFrameShape(QFrame.Shape.StyledPanel)
        lay = QVBoxLayout(self)
        # 타일 버튼 그룹
        for text, code in [("벽",WALL), ("시작",START), ("목표",GOAL), ("지우기",EMPTY)]:
            btn = QPushButton(text); lay.addWidget(btn)
            btn.clicked.connect(lambda _, c=code: self.tileSelected.emit(c))
        # 실행 / 스텝
        self.run_btn  = QPushButton("▶ Run"); lay.addWidget(self.run_btn)
        self.step_btn = QPushButton("⏭ Step"); lay.addWidget(self.step_btn)
        self.run_btn.clicked.connect(self.runClicked)
        self.step_btn.clicked.connect(self.stepClicked)
        # 휴리스틱 선택
        lay.addWidget(QLabel("Heuristic"))
        self.combo = QComboBox(); lay.addWidget(self.combo)
        self.combo.addItems(["manhattan","euclidean","chebyshev"])
        self.combo.currentTextChanged.connect(self.heuristicChanged)
        # 속도 슬라이더
        lay.addWidget(QLabel("Speed"))
        slider = QSlider(Qt.Orientation.Horizontal); lay.addWidget(slider)
        slider.setRange(1, 120); slider.setValue(60)
        slider.valueChanged.connect(self.speedChanged)
        lay.addStretch()
        # 맵 클리어
        self.clear_btn = QPushButton("🗑 Clear Path"); lay.addWidget(self.clear_btn)
        self.clear_btn.clicked.connect(self.clearClicked)

# ───────────────────────────────────
# 3) View 파사드
# ───────────────────────────────────
class PyQtView(QMainWindow):
    def __init__(self, grid):
        super().__init__()
        self.setWindowTitle("A* Simulator – PyQt")
        self.canvas = GridCanvas(grid)
        self.panel  = ControlPanel()

        # 중앙 레이아웃
        central = QWidget(); root = QHBoxLayout(central)
        root.addWidget(self.canvas); root.addWidget(self.panel)
        self.setCentralWidget(central)

        self.statusBar().showMessage("Ready")

    # Controller 가 호출하는 랜더링 트리거
    def update_view(self):
        self.canvas.update()          # QWidget.repaint
