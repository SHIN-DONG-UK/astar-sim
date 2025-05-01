import heapq
from math import inf
from model.grid import Grid

'''
우선순위
1. f가 작은 순
2. x가 작은 순
3. y가 작은 순
'''
class AStarSolver:
    def __init__(self, grid):
        self.grid = grid
        self.h = self._manhattan # 확장 가능
        self.openNode = []
        self.gcost = {}          # (x, y) -> g
        self.parent= {}          # (x, y) -> (px, px)
        self.path = []

    def init(self):
        self.openNode = []
        self.gcost = {}          # (x, y) -> g
        self.parent= {}          # (x, y) -> (px, px)
        self.path = []

        sx, sy = self.grid.start
        self.gcost[(sx,sy)] = 0
        heapq.heappush(self.openNode, (0, sx, sy))
    
    # 경로 iterator 제공
    def get_path_iter(self):
        """
        최단 경로를 한 칸씩 내보내는 generator.
        solve() 가 성공한 뒤에만 호출해야 함.
        start 노드는 제외시켜 애니메이션에 쓰기 좋게 함.
        """
        if not hasattr(self, "_path") or self._path is None:
            raise RuntimeError("solve() 가 먼저 호출되어야 합니다.")
        for node in self._path[1:]:       # [1:] → start 제외
            yield node

    def solve(self):
        """A* 를 한번에 다 돌려 _path 를 채운다."""
        if not (self.grid.start and self.grid.goal):
            return False

        self.init()                       # openNode 초기화
        found, path = self._search()      # 기존 _get_path() 내용 → _search
        if found:
            self._path = path             # 인스턴스에 보관
        else:
            self._path = None
        return found

    '''
    return 완료, 경로
    '''
    def _search(self):        
        while self.openNode:
            f, x, y = heapq.heappop(self.openNode)

            if (x, y) == self.grid.goal:
                return True, self._reconstruct((x,y))

            g_here = self.gcost[(x,y)]
            for nx, ny, dist in self.grid.neighbors(x,y):
                g_new = g_here + dist
                # 이미 방문했다 -> g_new가 더 작으면 갱신
                # 방문 안했다 -> inf -> 무조건 갱신
                if g_new < self.gcost.get((nx, ny), inf):
                    self.gcost[(nx,ny)] = g_new
                    self.parent[(nx,ny)] = (x, y)
                    f_new = g_new + self.h(x, y, *self.grid.goal)
                    heapq.heappush(self.openNode, (f_new, nx, ny))

        # 도착하지 못하고 종료
        return False, None

    def clear(self):
        self.openNode = []
        self.gcost = {}          # (x, y) -> g
        self.parent= {}          # (x, y) -> (px, px)
        self.path = []
        
    @staticmethod
    def _manhattan(x, y, gx, gy):
        dx = abs(gx - x)
        dy = abs(gy - y)
        return 10 * (dx + dy)

    def _reconstruct(self, v):
        path = [v]
        while v in self.parent:
            v = self.parent[v]
            path.append(v)
        path.reverse()
        return path
