import tkinter as tk
from tkinter import simpledialog, ttk, messagebox
import random
from collections import deque

CELL_SIZE = 20
ZOOM = 1.0
WALL_WIDTH = 2  # Grosor de las paredes

# Modos de interacción: "normal", "select_points" (para definir inicio/fin) y "select_waypoints"
mode = "normal"
point_selection_step = 0  # 0: seleccionar inicio, 1: seleccionar fin
start_point = None
end_point = None
waypoints = []  # Lista de waypoints (ordenados)

# Crear la ventana raíz antes de declarar variables Tkinter
root = tk.Tk()
root.title("Laberinto - Versión con Controles de Visualización")

# Variables para contadores en el panel derecho
sol_count_var = tk.StringVar(root, value="C. Solución: 0")
dead_count_var = tk.StringVar(root, value="Callejones: 0")
shortcut_count_var = tk.StringVar(root, value="C. Atajos: 0")  # Actualmente sin uso
uncolored_count_var = tk.StringVar(root, value="Sin Color: 0")
inaccessible_count_var = tk.StringVar(root, value="Inaccesibles: 0")

# Variables para controlar la visibilidad de elementos
show_solution_var = tk.BooleanVar(root, value=True)
show_deadends_var = tk.BooleanVar(root, value=True)
show_waypoints_var = tk.BooleanVar(root, value=True)
show_inaccessible_var = tk.BooleanVar(root, value=True)

class Maze:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        # Cada celda inicia con las 4 paredes activadas
        self.maze = [[{'top': True, 'right': True, 'bottom': True, 'left': True} for _ in range(width)] for _ in range(height)]
        self.visited = [[False]*width for _ in range(height)]
        self.shortcuts = []  # Funcionalidad pendiente, no se usa en esta versión
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
        # Función de atajos pendiente de redefinición.
        self.shortcuts.clear()
        for _ in range(num_shortcuts):
            x, y = random.randint(0, self.width-1), random.randint(0, self.height-1)
            directions = ['top', 'right', 'bottom', 'left']
            random.shuffle(directions)
            for direction in directions:
                dx, dy = {'top': (0, -1), 'right': (1, 0), 'bottom': (0, 1), 'left': (-1, 0)}[direction]
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    if self.maze[y][x][direction] and self.maze[ny][nx][{'top': 'bottom', 'right': 'left', 'bottom': 'top', 'left': 'right'}[direction]]:
                        self.maze[y][x][direction] = False
                        self.maze[ny][nx][{'top': 'bottom', 'right': 'left', 'bottom': 'top', 'left': 'right'}[direction]] = False
                        self.shortcuts.append((x, y, nx, ny))
                        break

def find_path_bfs(maze_obj, start, end):
    queue = deque([start])
    prev = {start: None}
    while queue:
        current = queue.popleft()
        if current == end:
            break
        x, y = current
        for direction, (dx, dy) in {'top': (0, -1), 'right': (1, 0), 'bottom': (0, 1), 'left': (-1, 0)}.items():
            if not maze_obj.maze[y][x][direction]:
                nx, ny = x + dx, y + dy
                if (nx, ny) not in prev:
                    prev[(nx, ny)] = (x, y)
                    queue.append((nx, ny))
    path = []
    cur = end
    if cur in prev:
        while cur is not None:
            path.append(cur)
            cur = prev[cur]
        path.reverse()
    return path

def get_reachable(maze_obj, start):
    reachable = set()
    q = deque([start])
    reachable.add(start)
    while q:
        x, y = q.popleft()
        for direction, (dx, dy) in {'top': (0, -1), 'right': (1, 0), 'bottom': (0, 1), 'left': (-1, 0)}.items():
            if not maze_obj.maze[y][x][direction]:
                nx, ny = x+dx, y+dy
                if (nx, ny) not in reachable:
                    reachable.add((nx, ny))
                    q.append((nx, ny))
    return reachable

def flood_fill_count(maze_obj, start):
    return len(get_reachable(maze_obj, start))

def draw_maze(canvas, maze):
    canvas.delete("all")
    canvas.config(scrollregion=(0, 0, maze.width*CELL_SIZE*ZOOM, maze.height*CELL_SIZE*ZOOM))
    # Dibujar paredes
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
    # Dibujar callejones (en azul) si están activados
    if show_deadends_var.get():
        for x, y in maze.find_dead_ends():
            x1 = x * CELL_SIZE * ZOOM + CELL_SIZE*ZOOM//4
            y1 = y * CELL_SIZE * ZOOM + CELL_SIZE*ZOOM//4
            x2 = x1 + CELL_SIZE*ZOOM//2
            y2 = y1 + CELL_SIZE*ZOOM//2
            canvas.create_oval(x1, y1, x2, y2, fill="blue", outline="blue")
    # Dibujar celdas inaccesibles (en naranja) si están activadas
    if show_inaccessible_var.get() and start_point is not None:
        reachable = get_reachable(maze, start_point)
        for y in range(maze.height):
            for x in range(maze.width):
                if (x, y) not in reachable:
                    x1 = x * CELL_SIZE * ZOOM
                    y1 = y * CELL_SIZE * ZOOM
                    x2 = x1 + CELL_SIZE * ZOOM
                    y2 = y1 + CELL_SIZE * ZOOM
                    canvas.create_rectangle(x1, y1, x2, y2, fill="orange", stipple="gray50", outline="")
    draw_points(canvas)
    if show_waypoints_var.get():
        draw_waypoints(canvas)

def draw_points(canvas):
    if start_point is not None:
        x, y = start_point
        cx = x * CELL_SIZE * ZOOM + CELL_SIZE*ZOOM/2
        cy = y * CELL_SIZE * ZOOM + CELL_SIZE*ZOOM/2
        r = 5
        canvas.create_oval(cx-r, cy-r, cx+r, cy+r, fill="green", outline="green")
    if end_point is not None:
        x, y = end_point
        cx = x * CELL_SIZE * ZOOM + CELL_SIZE*ZOOM/2
        cy = y * CELL_SIZE * ZOOM + CELL_SIZE*ZOOM/2
        r = 5
        canvas.create_oval(cx-r, cy-r, cx+r, cy+r, fill="red", outline="red")

def draw_waypoints(canvas):
    # Mostrar cada waypoint como círculo amarillo con diámetro igual a la celda y con número en su interior
    for idx, wp in enumerate(waypoints, start=1):
        x, y = wp
        cx = x * CELL_SIZE * ZOOM + CELL_SIZE*ZOOM/2
        cy = y * CELL_SIZE * ZOOM + CELL_SIZE*ZOOM/2
        diam = CELL_SIZE * ZOOM
        r = diam/2
        canvas.create_oval(cx - r, cy - r, cx + r, cy + r, fill="yellow", outline="black")
        canvas.create_text(cx, cy, text=str(idx), fill="black")

def draw_solution():
    if start_point is None or end_point is None or maze_obj is None:
        return
    # Calcular la solución principal utilizando waypoints si existen
    if waypoints:
        segments = []
        current_start = start_point
        for wp in waypoints:
            seg = find_path_bfs(maze_obj, current_start, wp)
            segments.append(seg)
            current_start = wp
        seg = find_path_bfs(maze_obj, current_start, end_point)
        segments.append(seg)
        main_path = []
        for seg in segments:
            if seg:
                if main_path and seg[0] == main_path[-1]:
                    main_path.extend(seg[1:])
                else:
                    main_path.extend(seg)
    else:
        main_path = find_path_bfs(maze_obj, start_point, end_point)
    # Dibujar camino solución en rojo si está activado
    if show_solution_var.get() and main_path and len(main_path) >= 2:
        pts = [(x*CELL_SIZE*ZOOM + CELL_SIZE*ZOOM/2, y*CELL_SIZE*ZOOM + CELL_SIZE*ZOOM/2) for x, y in main_path]
        canvas.create_line(pts, fill="red", width=2, smooth=True)
    # Dibujar caminos secundarios (callejones) en azul si están activados
    blue_total = 0
    blue_cells = set()
    if show_deadends_var.get():
        for dead_end in maze_obj.find_dead_ends():
            best_blue = None
            best_len = float('inf')
            for point in main_path:
                sub_path = find_path_bfs(maze_obj, point, dead_end)
                if sub_path and len(sub_path) < best_len:
                    best_blue = sub_path
                    best_len = len(sub_path)
            if best_blue:
                blue_total += len(best_blue)
                blue_cells.update(best_blue)
                pts = [(x*CELL_SIZE*ZOOM + CELL_SIZE*ZOOM/2, y*CELL_SIZE*ZOOM + CELL_SIZE*ZOOM/2) for x, y in best_blue]
                canvas.create_line(pts, fill="blue", width=1, smooth=True)
    # Actualizar contadores
    sol_count_var.set(f"C. Solución: {len(main_path)}")
    dead_count_var.set(f"Callejones: {blue_total}")
    shortcut_count_var.set(f"C. Atajos: {len(maze_obj.shortcuts)}")
    # Celdas coloreadas: aquellas que están en solución, callejones, inicio, fin y waypoints
    colored_cells = set(main_path) | blue_cells
    if start_point:
        colored_cells.add(start_point)
    if end_point:
        colored_cells.add(end_point)
    for wp in waypoints:
        colored_cells.add(wp)
    total_cells = maze_obj.width * maze_obj.height
    uncolored = total_cells - len(colored_cells)
    uncolored_count_var.set(f"Sin Color: {uncolored}")
    # Celdas inaccesibles según flood fill desde el inicio
    if start_point:
        reachable = get_reachable(maze_obj, start_point)
    else:
        reachable = set()
    inaccessible = total_cells - len(reachable)
    inaccessible_count_var.set(f"Inaccesibles: {inaccessible}")

def on_mousewheel(event):
    global ZOOM
    if event.delta > 0:
        ZOOM *= 1.1
    else:
        ZOOM *= 0.9
    draw_maze(canvas, maze_obj)
    draw_solution()

def borrar_pared(event):
    x = int(canvas.canvasx(event.x) // (CELL_SIZE * ZOOM))
    y = int(canvas.canvasy(event.y) // (CELL_SIZE * ZOOM))
    closest = canvas.find_closest(canvas.canvasx(event.x), canvas.canvasy(event.y))
    if closest:
        tag = canvas.gettags(closest[0])
        if tag and len(tag[0].split(',')) == 3:
            cx, cy, direction = tag[0].split(',')
            cx, cy = int(cx), int(cy)
            maze_obj.maze[cy][cx][direction] = False
            opposite = {'top': 'bottom', 'right': 'left', 'bottom': 'top', 'left': 'right'}[direction]
            dx, dy = {'top': (0, -1), 'right': (1, 0), 'bottom': (0, 1), 'left': (-1, 0)}[direction]
            nx, ny = cx + dx, cy + dy
            if 0 <= nx < maze_obj.width and 0 <= ny < maze_obj.height:
                maze_obj.maze[ny][nx][opposite] = False
            draw_maze(canvas, maze_obj)
            draw_solution()

def select_point(event):
    global point_selection_step, start_point, end_point, mode
    x = int(canvas.canvasx(event.x) // (CELL_SIZE * ZOOM))
    y = int(canvas.canvasy(event.y) // (CELL_SIZE * ZOOM))
    if point_selection_step == 0:
        start_point = (x, y)
        point_selection_step = 1
        messagebox.showinfo("Selección de puntos", f"Punto de inicio seleccionado en ({x}, {y}). Ahora selecciona el punto de fin.")
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

def canvas_click_handler(event):
    global mode
    if mode == "select_points":
        select_point(event)
    elif mode == "select_waypoints":
        add_waypoint(event)
    else:
        borrar_pared(event)

def check_connectivity(maze_obj):
    count = flood_fill_count(maze_obj, (0, 0))
    return count == maze_obj.width * maze_obj.height

def generate_new_maze():
    global maze_obj, ZOOM, start_point, end_point, mode, waypoints
    try:
        ancho = int(param_entries["Calles verticales"].get())
        alto = int(param_entries["Calles horizontales"].get())
        atajos = int(param_entries["Atajos"].get())
    except Exception:
        messagebox.showerror("Error", "Revisa los parámetros numéricos.")
        return
    # Calcular zoom para que el laberinto se ajuste a un área de 600x600 píxeles
    canvas_width = 600
    canvas_height = 600
    ZOOM = min(canvas_width/(ancho*CELL_SIZE), canvas_height/(alto*CELL_SIZE))
    waypoints = []
    maze_obj = Maze(ancho, alto)
    maze_obj.generate_maze()
    if atajos:
        maze_obj.add_shortcuts(atajos)
    start_point = (0, 0)
    end_point = (ancho-1, alto-1)
    mode = "normal"
    if not check_connectivity(maze_obj):
        messagebox.showwarning("Conectividad", "El laberinto no es completamente accesible.")
    draw_maze(canvas, maze_obj)
    draw_solution()

def seleccionar_puntos():
    global mode, point_selection_step
    mode = "select_points"
    point_selection_step = 0
    messagebox.showinfo("Selección de puntos", "Haz clic en el laberinto para seleccionar el punto de inicio.")

def seleccionar_waypoints():
    global mode
    mode = "select_waypoints"
    messagebox.showinfo("Waypoints", "Haz clic en el laberinto para añadir waypoints (pasos obligados).")

def borrar_waypoints():
    global waypoints, mode
    waypoints = []
    mode = "normal"
    draw_maze(canvas, maze_obj)
    draw_solution()

def actualizar_solucion():
    draw_maze(canvas, maze_obj)
    draw_solution()

# Configuración de la interfaz: panel izquierdo con canvas y panel derecho con controles
main_frame = ttk.Frame(root)
main_frame.pack(fill=tk.BOTH, expand=True)

canvas_frame = ttk.Frame(main_frame)
canvas_frame.grid(row=0, column=0, sticky="nsew")
canvas = tk.Canvas(canvas_frame, bg="white", width=600, height=600)
vsb = ttk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
hsb = ttk.Scrollbar(canvas_frame, orient="horizontal", command=canvas.xview)
canvas.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
vsb.grid(row=0, column=1, sticky="ns")
hsb.grid(row=1, column=0, sticky="ew")
canvas.grid(row=0, column=0, sticky="nsew")
canvas_frame.rowconfigure(0, weight=1)
canvas_frame.columnconfigure(0, weight=1)

control_frame = ttk.Frame(main_frame, padding=10)
control_frame.grid(row=0, column=1, sticky="nsew")

# Parámetros básicos
param_labels = ["Calles verticales", "Calles horizontales", "Atajos"]
param_entries = {}
for i, label_text in enumerate(param_labels):
    ttk.Label(control_frame, text=label_text+":").grid(row=i, column=0, sticky="w", pady=2)
    ent = ttk.Entry(control_frame, width=8)
    ent.insert(0, "20")
    ent.grid(row=i, column=1, pady=2)
    param_entries[label_text] = ent

ttk.Button(control_frame, text="Generar Laberinto", command=generate_new_maze).grid(row=3, column=0, columnspan=2, pady=5, sticky="ew")
ttk.Button(control_frame, text="Seleccionar Puntos", command=seleccionar_puntos).grid(row=4, column=0, columnspan=2, pady=5, sticky="ew")
ttk.Button(control_frame, text="Seleccionar Waypoints", command=seleccionar_waypoints).grid(row=5, column=0, columnspan=2, pady=5, sticky="ew")
ttk.Button(control_frame, text="Borrar Waypoints", command=borrar_waypoints).grid(row=6, column=0, columnspan=2, pady=5, sticky="ew")
ttk.Button(control_frame, text="Actualizar Solución", command=actualizar_solucion).grid(row=7, column=0, columnspan=2, pady=5, sticky="ew")

# Sección de visibilidad de elementos
ttk.Label(control_frame, text="Visualización:").grid(row=8, column=0, columnspan=2, pady=(10,2))
ttk.Checkbutton(control_frame, text="Camino Solución (Rojo)", variable=show_solution_var, command=actualizar_solucion).grid(row=9, column=0, columnspan=2, sticky="w")
ttk.Checkbutton(control_frame, text="Callejones (Azul)", variable=show_deadends_var, command=actualizar_solucion).grid(row=10, column=0, columnspan=2, sticky="w")
ttk.Checkbutton(control_frame, text="Waypoints", variable=show_waypoints_var, command=actualizar_solucion).grid(row=11, column=0, columnspan=2, sticky="w")
ttk.Checkbutton(control_frame, text="Celdas Inaccesibles", variable=show_inaccessible_var, command=actualizar_solucion).grid(row=12, column=0, columnspan=2, sticky="w")

# Contadores
ttk.Label(control_frame, textvariable=sol_count_var).grid(row=13, column=0, columnspan=2, pady=3, sticky="w")
ttk.Label(control_frame, textvariable=dead_count_var).grid(row=14, column=0, columnspan=2, pady=3, sticky="w")
ttk.Label(control_frame, textvariable=shortcut_count_var).grid(row=15, column=0, columnspan=2, pady=3, sticky="w")
ttk.Label(control_frame, textvariable=uncolored_count_var).grid(row=16, column=0, columnspan=2, pady=3, sticky="w")
ttk.Label(control_frame, textvariable=inaccessible_count_var).grid(row=17, column=0, columnspan=2, pady=3, sticky="w")

main_frame.columnconfigure(0, weight=3)
main_frame.columnconfigure(1, weight=1)

canvas.bind("<MouseWheel>", on_mousewheel)
canvas.bind("<Button-1>", canvas_click_handler)

maze_obj = None

root.mainloop()
