# grid.py
import json, math
from model.tile_consts import EMPTY, WALL, START, GOAL, PLAYER

class Grid:
    DIRS8 = [(0,-1),(1,-1), (1,0), (1,1), (0,1), (-1,1), (-1,0), (-1,-1)]

    def __init__(self, cols, rows):
        self.cols, self.rows = cols, rows
        self.tiles = [[EMPTY] * rows for _ in range(cols)] # 2차원 맵
        self.start = None  # 시작점
        self.goal = None   # 도착점

    # 좌표 유효성 검사
    def in_bounds(self, x, y):
        return 0 <= x < self.cols and 0 <= y < self.rows
    
    # 타일 접근
    def get(self, x, y):
        if not self.in_bounds(x, y):
            return
        return self.tiles[x][y]
    
    # 타일 설정
    def set(self, x, y, val):
        if not self.in_bounds(x, y):
            return
        if val == START: self.start = (x, y)
        elif val == GOAL: self.goal = (x, y)
        self.tiles[x][y] = val
    
    # 이웃 리턴
    def neighbors(self, x, y):
        for i in range(8):
            nx = x + Grid.DIRS8[i][0]
            ny = y + Grid.DIRS8[i][1]
            if self.in_bounds(nx, ny) and self.get(nx, ny) != WALL:
                yield nx, ny, self._get_cost(i)

    # 초기화
    def clear(self):
        self.tiles = [[EMPTY] * self.rows for _ in range(self.cols)]
        self.start = None  # 시작점
        self.goal = None   # 도착점

    def _get_cost(self, dir):
        if dir%2==0: return 10 # 상하좌우 10
        else: return 14        # 대각선 14
