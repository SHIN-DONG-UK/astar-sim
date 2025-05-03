# 1. 디렉터리 구조
```bash
astarsim/
│
├─ model/
│   ├─ astar.py         # A* 알고리즘
│   ├─ grid.py          # 격자·타일 상태
│   └─ tile_consts.py   # 격자 상태 변수
│
├─ ui/
│   ├─ controller.py     # 이벤트·시뮬레이션 흐름
│   └─ pyqt_view.py    # 화면 그리기만 담당
│
└─ main.py               # 진입점

```

# 2. 시작하기

### 의존성
```bash
pip install -r requirements.txt
```

### 실행
```bash
python main.py
```

# 3. 주요 기능
### 1. 벽 그리기
<img src="data/그리기.gif">

### 2. 시뮬레이션1
<img src="data/런.gif">

### 3. 시뮬레이션2
<img src="data/런2.gif">


# 4. 업데이트

## 4-1. version 0.1
### 요구사항 추가
- astar-solver로 탐색한 칸들을 Run했을 때 다 보여주려고 함

- 실제 이동 칸은 가장 진하게, 그리고 유망한 순서대로 진하게 표시