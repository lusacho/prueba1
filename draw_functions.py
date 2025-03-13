from tkinter import Canvas

CELL_SIZE = 20
ZOOM = 1.0
WALL_WIDTH = 2

def draw_maze(canvas, maze):
    canvas.delete("all")
    canvas.config(scrollregion=(0, 0, maze.width * CELL_SIZE * ZOOM, maze.height * CELL_SIZE * ZOOM))
    for y in range(maze.height):
        for x in range(maze.width):
            x1 = x * CELL_SIZE * ZOOM
            y1 = y * CELL_SIZE * ZOOM
            x2 = x1 + CELL_SIZE * ZOOM
            y2 = y1 + CELL_SIZE * ZOOM
            if maze.maze[y][x]['top']:
                canvas.create_line(x1, y1, x2, y1, tags=f"{x},{y},top", width=WALL_WIDTH)
            if maze.maze[y][x]['right']:
                canvas.create_line(x2, y1, x2, y2, tags=f"{x},{y},right", width=WALL_WIDTH)
            if maze.maze[y][x]['bottom']:
                canvas.create_line(x1, y2, x2, y2, tags=f"{x},{y},bottom", width=WALL_WIDTH)
            if maze.maze[y][x]['left']:
                canvas.create_line(x1, y1, x1, y2, tags=f"{x},{y},left", width=WALL_WIDTH)
    draw_points(canvas)
    draw_waypoints(canvas)

def draw_points(canvas):
    if start_point is not None:
        x, y = start_point
        cx = x * CELL_SIZE * ZOOM + CELL_SIZE * ZOOM / 2
        cy = y * CELL_SIZE * ZOOM + CELL_SIZE * ZOOM / 2
        r = CELL_SIZE * ZOOM / 2
        canvas.create_oval(cx - r, cy - r, cx + r, cy + r, fill="green", outline="black")
        canvas.create_text(cx, cy, text="S", fill="white")

    if end_point is not None:
        x, y = end_point
        cx = x * CELL_SIZE * ZOOM + CELL_SIZE * ZOOM / 2
        cy = y * CELL_SIZE * ZOOM + CELL_SIZE * ZOOM / 2
        r = CELL_SIZE * ZOOM / 2
        canvas.create_oval(cx - r, cy - r, cx + r, cy + r, fill="red", outline="black")
        canvas