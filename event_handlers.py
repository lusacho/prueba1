from tkinter import simpledialog, messagebox
from maze import Maze
from draw_functions import draw_maze, draw_solution
from collections import deque

CELL_SIZE = 20
ZOOM = 1.0
WALL_WIDTH = 2

mode = "normal"
point_selection_step = 0
start_point = None
end_point = None
waypoints = []
maze_obj = None
canvas = None

def on_mousewheel(event):
    global ZOOM
    if event.delta > 0:
        ZOOM *= 1.1
    else:
        ZOOM *= 0.9
    draw_maze(canvas, maze_obj)
    draw_solution()

def toggle_wall(event):
    x = int(canvas.canvasx(event.x) // (CELL_SIZE * ZOOM))
    y = int(canvas.canvasy(event.y) // (CELL_SIZE * ZOOM))
    closest = canvas.find_closest(canvas.canvasx(event.x), canvas.canvasy(event.y))
    if closest:
        tag = canvas.gettags(closest[0])
        if tag and len(tag[0].split(',')) == 3:
            cx, cy, direction = tag[0].split(',')
            cx, cy = int(cx), int(cy)
            if maze_obj.maze[cy][cx][direction]:
                maze_obj.maze[cy][cx][direction] = False
                opposite = {'top':'bottom','right':'left','bottom':'top','left':'right'}[direction]
                dx, dy = {'top': (0,-1), 'right': (1,0), 'bottom': (0,1), 'left': (-1,0)}[direction]
                nx, ny = cx + dx, cy + dy
                if 0 <= nx < maze_obj.width and 0 <= ny < maze_obj.height:
                    maze_obj.maze[ny][nx][opposite] = False
            else:
                maze_obj.maze[cy][cx][direction] = True
                opposite = {'top':'bottom','right':'left','bottom':'top','left':'right'}[direction]
                dx, dy = {'top': (0,-1), 'right': (1,0), 'bottom': (0,1), 'left': (-1,0)}[direction]
                nx, ny = cx + dx, cy + dy
                if 0 <= nx < maze_obj.width and 0 <= ny < maze_obj.height:
                    maze_obj.maze[ny][nx][opposite] = True
            draw_maze(canvas, maze_obj)
            draw_solution()

def select_point(event):
    global point_selection_step, start_point, end_point, mode
    x = int(canvas.canvasx(event.x) // (CELL_SIZE * ZOOM))
    y = int(canvas.canvasy(event.y) // (CELL_SIZE * ZOOM))
    if point_selection_step == 0:
        start_point = (x, y)
        point_selection_step = 1
        messagebox.showinfo("Selección de puntos", f"Punto de inicio seleccionado en ({x}, {y}). Selecciona el punto de fin.")
    elif point_selection_step == 1:
        end_point = (x, y)
        mode = "normal"
        point_selection_step = 0
        messagebox.showinfo("Selección de puntos", f"Punto de fin seleccionado en ({x}, {y}).")
        draw_maze(canvas, maze_obj)
        draw_solution()

def add_waypoint(event):
    global waypoints
    x = int(canvas.canvasx(event.x) // (CELL_SIZE * ZOOM))
    y = int(canvas.canvasy(event.y) // (CELL_SIZE * ZOOM))
    waypoints.append((x, y))
    draw_maze(canvas, maze_obj)
    draw_solution()

def remove_waypoint(event):
    global waypoints
    x = int(canvas.canvasx(event.x) // (CELL_SIZE * ZOOM))
    y = int(canvas.canvasy(event.y) // (CELL_SIZE * ZOOM))
    waypoints = [wp for wp in waypoints if wp != (x, y)]
    draw_maze(canvas, maze_obj)
    draw_solution()

def add_wall(event):
    # Implementar lógica para añadir paredes
    pass

def remove_wall(event):
    # Implementar lógica para eliminar paredes
    pass

def canvas_click_handler(event):
    global mode
    if mode == "select_points":
        select_point(event)
    elif mode == "select_waypoints":
        add_waypoint(event)
    elif mode == "edit_walls":
        toggle_wall(event)
    elif mode == "add_wall":
        add_wall(event)
    elif mode == "remove_wall":
        remove_wall(event)
    else:
        toggle_wall(event)

def generate_new_maze():
    global maze_obj, ZOOM, start_point, end_point, mode, waypoints
    try:
        ancho = int(param_entries["Calles verticales"].get())
        alto = int(param_entries["Calles horizontales"].get())
        atajos = int(param_entries["Atajos"].get())
    except Exception:
        messagebox.showerror("Error", "Revisa los parámetros numéricos.")
        return
    canvas_width = 600
    canvas_height = 600
    ZOOM = min(canvas_width/(ancho*CELL_SIZE), canvas_height/(alto*CELL_SIZE))
    waypoints = []
    start_point = (0, 0)
    end_point = (ancho - 1, alto - 1)
    mode = "normal"
    maze_obj = Maze(ancho, alto)
    maze_obj.generate_maze()
    if atajos:
        maze_obj.add_shortcuts(atajos)
    draw_maze(canvas, maze_obj)
    draw_solution()

def generate_forced_maze():
    global maze_obj, ZOOM, start_point, end_point, mode, waypoints
    try:
        ancho = int(param_entries["Calles verticales"].get())
        alto = int(param_entries["Calles horizontales"].get())
        atajos = int(param_entries["Atajos"].get())
    except Exception:
        messagebox.showerror("Error", "Revisa los parámetros numéricos.")
        return
    canvas_width = 600
    canvas_height = 600
    ZOOM = min(canvas_width/(ancho*CELL_SIZE), canvas_height/(alto*CELL_SIZE))
    if start_point is None: start_point = (0, 0)
    if end_point is None: end_point = (ancho - 1, alto - 1)
    mode = "normal"
    maze_obj = Maze(ancho, alto)
    maze_obj.generate_maze()
    if atajos:
        maze_obj.add_shortcuts(atajos)
    ordered = [start_point] + waypoints + [end_point]
    draw_maze(canvas, maze_obj)
    draw_solution()

def seleccionar_puntos():
    global mode, point_selection_step
    mode = "select_points"
    point_selection_step = 0
    messagebox.showinfo("Selección de puntos", "Haz clic para seleccionar el punto de inicio y luego el de fin.")

def seleccionar_waypoints():
    global mode
    mode = "select_waypoints"
    messagebox.showinfo("Waypoints", "Haz clic para añadir waypoints (en orden de paso obligatorio).")

def toggle_edit_mode():
    global mode
    if mode == "edit_walls":
        mode = "select_waypoints"
        messagebox.showinfo("Modo", "Modo: Seleccionar Waypoints")
    else:
        mode = "edit_walls"
        messagebox.showinfo("Modo", "Modo: Editar Paredes (click para alternar pared)")

def actualizar_solucion():
    draw_maze(canvas, maze_obj)
    draw_solution()