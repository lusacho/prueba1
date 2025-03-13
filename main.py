import tkinter as tk
from tkinter import simpledialog, ttk, messagebox
from maze import Maze
from event_handlers import (
    on_mousewheel, canvas_click_handler, 
    generate_new_maze, generate_forced_maze, 
    seleccionar_puntos, seleccionar_waypoints, 
    add_waypoint, remove_waypoint, add_wall, 
    remove_wall, toggle_edit_mode, actualizar_solucion
)
from draw_functions import draw_maze, draw_solution

CELL_SIZE = 20
ZOOM = 1.0
WALL_WIDTH = 2  # Grosor de las paredes

mode = "normal"
point_selection_step = 0  # 0: seleccionar inicio, 1: seleccionar fin
start_point = None
end_point = None
waypoints = []

root = tk.Tk()
root.title("Laberinto - Avanzado con Recorrido Forzado")

loading_label = tk.StringVar(root, value="")

sol_count_var = tk.StringVar(root, value="C. Solución: 0")
dead_count_var = tk.StringVar(root, value="Callejones: 0")
shortcut_count_var = tk.StringVar(root, value="C. Atajos: 0")
uncolored_count_var = tk.StringVar(root, value="Sin Color: 0")
inaccessible_count_var = tk.StringVar(root, value="Inaccesibles: 0")

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

param_labels = ["Calles verticales", "Calles horizontales", "Atajos"]
param_entries = {}
for i, label_text in enumerate(param_labels):
    ttk.Label(control_frame, text=label_text + ":").grid(row=i, column=0, sticky="w", pady=2)
    ent = ttk.Entry(control_frame, width=8)
    ent.insert(0, "20")
    ent.grid(row=i, column=1, pady=2)
    param_entries[label_text] = ent

ttk.Button(control_frame, text="Generar Laberinto", command=generate_new_maze).grid(row=3, column=0, columnspan=2, pady=5, sticky="ew")
ttk.Button(control_frame, text="Generar Laberinto con Recorrido", command=generate_forced_maze).grid(row=4, column=0, columnspan=2, pady=5, sticky="ew")
ttk.Button(control_frame, text="Seleccionar Puntos", command=seleccionar_puntos).grid(row=5, column=0, columnspan=2, pady=5, sticky="ew")

# Botón para añadir waypoints
ttk.Button(control_frame, text="+ Way", command=add_waypoint).grid(row=6, column=0, pady=5, sticky="ew")

# Botón para eliminar waypoints
ttk.Button(control_frame, text="- Way", command=remove_waypoint).grid(row=6, column=1, pady=5, sticky="ew")

# Botón para añadir pared
ttk.Button(control_frame, text="+ Pared", command=add_wall).grid(row=7, column=0, pady=5, sticky="ew")

# Botón para eliminar pared
ttk.Button(control_frame, text="- Pared", command=remove_wall).grid(row=7, column=1, pady=5, sticky="ew")

ttk.Button(control_frame, text="Actualizar Solución", command=actualizar_solucion).grid(row=8, column=0, columnspan=2, pady=5, sticky="ew")

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