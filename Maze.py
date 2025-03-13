import random

class Maze:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.maze = [[{'top': True, 'right': True, 'bottom': True, 'left': True} for _ in range(width)] for _ in range(height)]
        self.visited = [[False]*width for _ in range(height)]
        self.shortcuts = []
        self.solution_path = []

    def generate_maze(self, cx=0, cy=0):
        self.visited[cy][cx] = True
        directions = [('top', (0, -1)), ('right', (1, 0)), ('bottom', (0, 1)), ('left', (-1, 0))]
        random.shuffle(directions)
        for direction, (dx, dy) in directions:
            nx, ny = cx + dx, cy + dy
            if 0 <= nx < self.width and 0 <= ny < self.height and not self.visited[ny][nx]:
                self.maze[cy][cx][direction] = False
                opposite = {'top': 'bottom', 'right': 'left', 'bottom': 'top', 'left': 'right'}
                self.maze[ny][nx][opposite[direction]] = False
                self.generate_maze(nx, ny)

    def find_dead_ends(self):
        dead_ends = []
        for y in range(self.height):
            for x in range(self.width):
                walls = sum(self.maze[y][x].values())
                if walls == 3:
                    dead_ends.append((x, y))
        return dead_ends

    def add_shortcuts(self, num_shortcuts):
        self.shortcuts.clear()
        for _ in range(num_shortcuts):
            x, y = random.randint(0, self.width-1), random.randint(0, self.height-1)
            directions = ['top', 'right', 'bottom', 'left']
            random.shuffle(directions)
            for direction in directions:
                dx, dy = {'top': (0, -1), 'right': (1, 0), 'bottom': (0, 1), 'left': (-1, 0)}[direction]
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    if self.maze[y][x][direction] and self.maze[ny][nx][{'top':'bottom','right':'left','bottom':'top','left':'right'}[direction]]:
                        self.maze[y][x][direction] = False
                        self.maze[ny][nx][{'top':'bottom','right':'left','bottom':'top','left':'right'}[direction]] = False
                        self.shortcuts.append((x, y, nx, ny))
                        break