import tkinter as tk
from tkinter import simpledialog, ttk, messagebox
import random
from collections import deque

CELL_SIZE = 20
ZOOM = 1.0
WALL_WIDTH = 2  # Grosor de las paredes

# Modos:
# "normal" = modo por defecto (editar paredes)
# "select_points" = seleccionar puntos de inicio y fin
# "select_waypoints" = agregar waypoints
# "edit_walls" = modo de editar paredes (toggle)
mode = "normal"
point_selection_step = 0  # 0: seleccionar inicio, 1: seleccionar fin
start_point = None
end_point = None
waypoints = []  # Lista de waypoints, se dibujan con número

# Crear la ventana raíz antes de definir variables Tkinter
root = tk.Tk()
root.title("Laberinto - Avanzado con Recorrido Forzado")

# Label para mensajes de carga (para que el usuario sepa que se está trabajando)
loading_label = tk.StringVar(root, value="")

# Variables para contadores
sol_count_var = tk.StringVar(root, value="C. Solución: 0")
dead_count_var = tk.StringVar(root, value="Callejones: 0")
shortcut_count_var = tk.StringVar(root, value="C. Atajos: 0")  # Sin uso en esta versión
uncolored_count_var = tk.StringVar(root, value="Sin Color: 0")
inaccessible_count_var = tk.StringVar(root, value="Inaccesibles: 0")

class Maze:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        # Cada celda inicia con las 4 paredes
        self.maze = [[{'top': True, 'right': True, 'bottom': True, 'left': True} for _ in range(width)] for _ in range(height)]
        self.visited = [[False]*width for _ in range(height)]
        self.shortcuts = []  # Funcionalidad pendiente
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

def flood_fill_count(maze_obj, start):
    visited = [[False]*maze_obj.width for _ in range(maze_obj.height)]
    q = deque([start])
    visited[start[1]][start[0]] = True
    count = 1
    while q:
        x, y = q.popleft()
        for direction, (dx, dy) in {'top': (0, -1), 'right': (1, 0), 'bottom': (0, 1), 'left': (-1, 0)}.items():
            if not maze_obj.maze[y][x][direction]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < maze_obj.width and 0 <= ny < maze_obj.height and not visited[ny][nx]:
                    visited[ny][nx] = True
                    count += 1
                    q.append((nx, ny))
    return count

def start_loading(msg="Calculando, espere..."):
    loading_label.set(msg)
    root.update_idletasks()

def end_loading():
    loading_label.set("")
    root.update_idletasks()

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
    # Dibujar callejones (dead ends) en azul
    for x, y in maze.find_dead_ends():
        x1 = x * CELL_SIZE * ZOOM + CELL_SIZE * ZOOM // 4
        y1 = y * CELL_SIZE * ZOOM + CELL_SIZE * ZOOM // 4
        x2 = x1 + CELL_SIZE * ZOOM // 2
        y2 = y1 + CELL_SIZE * ZOOM // 2
        canvas.create_oval(x1, y1, x2, y2, fill="blue", outline="blue")
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
        canvas.create_text(cx, cy, text="F", fill="white")

def draw_waypoints(canvas):
    for i, wp in enumerate(waypoints):
        x, y = wp
        cx = x * CELL_SIZE * ZOOM + CELL_SIZE * ZOOM / 2
        cy = y * CELL_SIZE * ZOOM + CELL_SIZE * ZOOM / 2
        r = CELL_SIZE * ZOOM / 2
        canvas.create_oval(cx - r, cy - r, cx + r, cy + r, fill="yellow", outline="black")
        canvas.create_text(cx, cy, text=str(i + 1), fill="black")

def draw_solution():
    if start_point is None or end_point is None or maze_obj is None:
        return
    # Si existen waypoints, forzamos que la solución incluya el recorrido en ese orden.
    if waypoints:
        ordered = [start_point] + waypoints + [end_point]
        main_path = []
        for i in range(len(ordered) - 1):
            seg = find_path_bfs(maze_obj, ordered[i], ordered[i + 1])
            if seg:
                if main_path and seg[0] == main_path[-1]:
                    main_path.extend(seg[1:])
                else:
                    main_path.extend(seg)
    else:
        main_path = find_path_bfs(maze_obj, start_point, end_point)
    # Dibujar camino principal en rojo
    if main_path and len(main_path) >= 2:
        pts = [(x * CELL_SIZE * ZOOM + CELL_SIZE * ZOOM / 2, y * CELL_SIZE * ZOOM + CELL_SIZE * ZOOM / 2) for x, y in main_path]
        canvas.create_line(pts, fill="red", width=2, smooth=True)
    # Calcular contadores:
    blue_total = 0
    blue_cells = set()
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
    sol_count_var.set(f"C. Solución: {len(main_path)}")
    dead_count_var.set(f"Callejones: {blue_total}")
    shortcut_count_var.set(f"C. Atajos: {len(maze_obj.shortcuts)}")
    colored_cells = set(main_path) | blue_cells
    if start_point: colored_cells.add(start_point)
    if end_point: colored_cells.add(end_point)
    for wp in waypoints: colored_cells.add(wp)
    total_cells = maze_obj.width * maze_obj.height
    uncolored = total_cells - len(colored_cells)
    uncolored_count_var.set(f"Sin Color: {uncolored}")
    reachable = flood_fill_count(maze_obj, start_point) if start_point else 0
    inaccessible = total_cells - reachable
    inaccessible_count_var.set(f"Inaccesibles: {inaccessible}")

def on_mousewheel(event):
    global ZOOM
    if event.delta > 0:
        ZOOM *= 1.1
    else:
        ZOOM *= 0.9
    draw_maze(canvas, maze_obj)
    draw_solution()

def toggle_wall(event):
    # Función que alterna (añade o quita) la pared en la celda y dirección clicada.
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

def canvas_click_handler(event):
    global mode
    if mode == "select_points":
        select_point(event)
    elif mode == "select_waypoints":
        add_waypoint(event)
    elif mode == "edit_walls":
        toggle_wall(event)
    else:
        # Por defecto, modo editar paredes.
        toggle_wall(event)

def check_connectivity(maze_obj):
    count = flood_fill_count(maze_obj, (0, 0))
    return count == maze_obj.width * maze_obj.height

def force_solution_path(maze_obj, ordered):
    # Para cada par consecutivo en la lista ordenada (inicio, waypoints, fin),
    # se "carven" las paredes a lo largo de un camino Manhattan simple.
    for i in range(len(ordered) - 1):
        x1, y1 = ordered[i]
        x2, y2 = ordered[i + 1]
        # Movimiento horizontal:
        if x1 < x2:
            for x in range(x1, x2):
                maze_obj.maze[y1][x]['right'] = False
                maze_obj.maze[y1][x+1]['left'] = False
        elif x1 > x2:
            for x in range(x2, x1):
                maze_obj.maze[y1][x+1]['left'] = False
                maze_obj.maze[y1][x]['right'] = False
        # Movimiento vertical:
        if y1 < y2:
            for y in range(y1, y2):
                maze_obj.maze[y][x2]['bottom'] = False
                maze_obj.maze[y+1][x2]['top'] = False
        elif y1 > y2:
            for y in range(y2, y1):
                maze_obj.maze[y+1][x2]['top'] = False
                maze_obj.maze[y][x2]['bottom'] = False

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
    start_loading("Generando laberinto...")
    maze_obj.generate_maze()
    if atajos:
        maze_obj.add_shortcuts(atajos)
    end_loading()
    if not check_connectivity(maze_obj):
        messagebox.showwarning("Conectividad", "El laberinto no es completamente accesible.")
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
    # Se mantiene lo que haya en waypoints; si no hay, se usan los puntos por defecto.
    if start_point is None: start_point = (0, 0)
    if end_point is None: end_point = (ancho - 1, alto - 1)
    mode = "normal"
    maze_obj = Maze(ancho, alto)
    start_loading("Generando laberinto forzado...")
    maze_obj.generate_maze()
    if atajos:
        maze_obj.add_shortcuts(atajos)
    # Forzar que la solución incluya la secuencia: inicio, waypoints y fin
    ordered = [start_point] + waypoints + [end_point]
    force_solution_path(maze_obj, ordered)
    end_loading()
    if not check_connectivity(maze_obj):
        messagebox.showwarning("Conectividad", "El laberinto no es completamente accesible.")
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

# Configuración de la interfaz
main_frame = ttk.Frame(root)
main_frame.pack(fill=tk.BOTH, expand=True)

# Panel izquierdo: Canvas
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

# Panel derecho: Controles y parámetros
control_frame = ttk.Frame(main_frame, padding=10)
control_frame.grid(row=0, column=1, sticky="nsew")

param_labels = ["Calles verticales", "Calles horizontales", "Atajos"]
param_entries = {}
for i, label_text in enumerate(param_labels):
    ttk.Label(control_frame, text=label_text + ":").grid(row=i, column=0, sticky="w", pady=2)
    ent = ttk.Entry(control_frame, width=8)
    ent.insert(0, "20")
    ent.grid(row=i, column=1, pady=2)
    param_entries[label_text] = ent

# Botones
ttk.Button(control_frame, text="Generar Laberinto", command=generate_new_maze).grid(row=3, column=0, columnspan=2, pady=5, sticky="ew")
ttk.Button(control_frame, text="Generar Laberinto con Recorrido", command=generate_forced_maze).grid(row=4, column=0, columnspan=2, pady=5, sticky="ew")
ttk.Button(control_frame, text="Seleccionar Puntos", command=seleccionar_puntos).grid(row=5, column=0, columnspan=2, pady=5, sticky="ew")
ttk.Button(control_frame, text="Seleccionar Waypoints", command=seleccionar_waypoints).grid(row=6, column=0, columnspan=2, pady=5, sticky="ew")
ttk.Button(control_frame, text="Toggle Modo: Waypoints/Editar Paredes", command=toggle_edit_mode).grid(row=7, column=0, columnspan=2, pady=5, sticky="ew")
ttk.Button(control_frame, text="Actualizar Solución", command=actualizar_solucion).grid(row=8, column=0, columnspan=2, pady=5, sticky="ew")

# Contadores y mensaje de carga
ttk.Label(control_frame, textvariable=sol_count_var).grid(row=9, column=0, columnspan=2, pady=3, sticky="w")
ttk.Label(control_frame, textvariable=dead_count_var).grid(row=10, column=0, columnspan=2, pady=3, sticky="w")
ttk.Label(control_frame, textvariable=shortcut_count_var).grid(row=11, column=0, columnspan=2, pady=3, sticky="w")
ttk.Label(control_frame, textvariable=uncolored_count_var).grid(row=12, column=0, columnspan=2, pady=3, sticky="w")
ttk.Label(control_frame, textvariable=inaccessible_count_var).grid(row=13, column=0, columnspan=2, pady=3, sticky="w")
ttk.Label(control_frame, textvariable=loading_label, foreground="blue").grid(row=14, column=0, columnspan=2, pady=3, sticky="w")

main_frame.columnconfigure(0, weight=3)
main_frame.columnconfigure(1, weight=1)

canvas.bind("<MouseWheel>", on_mousewheel)
canvas.bind("<Button-1>", canvas_click_handler)

maze_obj = None

root.mainloop()
