# controller.py
from PyQt6.QtCore import QObject, QTimer
from model.grid import Grid
from model.tile_consts import EMPTY, WALL, START, GOAL
from model.astar_solver import AStarSolver
from ui.pyqt_view import PyQtView


class Controller(QObject):
    def __init__(self, grid: Grid, view: PyQtView):
        super().__init__()
        self.grid  = grid
        self.view  = view
        self.solver: AStarSolver | None = None
        self.path = None

        # ─────────────────────────────
        # 1) View-신호 연결
        # ─────────────────────────────
        cv = self.view.canvas
        cv.cellClicked.connect(self.on_cell_clicked)
        cv.cellDragged.connect(self.on_cell_dragged)

        pnl = self.view.panel
        pnl.tileSelected.connect(self.on_tile_switch)
        pnl.runClicked.connect(self.on_run)
        pnl.stepClicked.connect(self.on_step)
        pnl.heuristicChanged.connect(self.on_heuristic_change)
        pnl.speedChanged.connect(self.on_speed_change)
        pnl.clearClicked.connect(self.on_clear)
        
        # ─────────────────────────────
        # 2) A* 실행용 타이머
        # ─────────────────────────────
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.on_tick)
        self.ms_per_tick = 50  # 기본 20 FPS
        self.path_iter = None

        # 현재 브러시(벽/시작/목표/지우기) 코드
        self.brush = WALL
        # 기본 휴리스틱
        self.heuristic = "manhattan"

        # 첫 화면 갱신
        self.view.update_view()

    # ───────────────────────────────
    # UI 핸들러
    # ───────────────────────────────
    def on_tile_switch(self, code: int):
        self.brush = code

    def on_cell_clicked(self, x, y):
        self.paint_cell(x, y)
        # self.debug_tiles()

    def on_cell_dragged(self, x, y, _):
        self.paint_cell(x, y)
        # self.debug_tiles()

    def paint_cell(self, x, y):
        self.grid.set(x, y, self.brush)
        # 타일 변경 후 즉시 화면 갱신
        self.view.update_view()
    
    def on_clear(self):
        # model
        self.grid.clear()
        # view
        self.view.canvas.final_path.clear()
        self.view.canvas.visited_nodes.clear()
        self.view.canvas.now_pos = None
        self.view.update_view()
    # ───────────────────────────────
    # 실행 / 스텝
    # ───────────────────────────────
    def on_run(self):
        self.view.canvas.visited_nodes.clear()
        self.view.canvas.final_path.clear()

        self.solver = AStarSolver(self.grid)
        if not self.solver.solve():
            self.view.statusBar().showMessage("No path")
            self.solver = None
            return

        # visited_nodes 그리기
        self.view.canvas.draw_visited_nodes(list(self.solver.gcost.keys()))
        self.path_iter = self.solver.get_path_iter()
        self.timer.timeout.disconnect()
        self.timer.timeout.connect(self.on_tick)
        self.timer.start(self.ms_per_tick)
        self.view.statusBar().showMessage("Running…")

    def on_step(self):
        pass
        # if not self.solver:
        #     self.solver = AStarSolver(self.grid)
        #     self.solver.init()
        # finished, path = self.solver.step()
        # self.view.canvas.update()          # 열린·닫힌 세트 표시하려면 추가 구현
        # if finished:
        #     if path:
        #         self.grid.player = path[-1]   # 도착점
        #     self.timer.stop()
        #     self.solver = None
        # self.view.update_view()

    # ───────────────────────────────
    # 휴리스틱·속도
    # ───────────────────────────────
    def on_heuristic_change(self, name: str):
        self.heuristic = name

    def on_speed_change(self, fps: int):
        self.ms_per_tick = int(1000 / fps)
        if self.timer.isActive():
            self.timer.start(self.ms_per_tick)

    # ───────────────────────────────
    # 타이머 Tick → A* Step
    # ───────────────────────────────
    def on_tick(self):
        try:
            x, y = next(self.path_iter)
            self.view.canvas.now_pos = (x, y)
            self.view.canvas.final_path.append((x, y))
            self.view.update_view()
        except StopIteration:           # 경로 다 소비
            self.timer.stop()
            self.solver = None
            self.view.statusBar().showMessage("Arrived!")

    def debug_tiles(self):
        for i in range(self.grid.rows):
            for j in range(self.grid.cols):
                print(self.grid.tiles[j][i], end='')
            print()