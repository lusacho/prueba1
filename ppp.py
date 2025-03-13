import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

# Colores (en formato RGB, adaptados para Matplotlib)
COLOR_FONDO = (1, 1, 1)  # blanco
COLOR_GRID = (0.9, 0.9, 0.9)  # gris claro
COLOR_PARED = (0, 0, 0)       # negro
COLOR_INICIO = (0, 1, 0)      # verde
COLOR_FIN = (1, 0, 0)         # rojo
COLOR_SOLUCION = (1, 0, 0)    # rojo (solución manual)
COLOR_CALLEJON_MANUAL = (0, 0, 1)  # azul
COLOR_CALLEJON_AUTO = (1, 0.65, 0)  # naranja

# Dimensiones de la ventana
ANCHO_VENTANA = 1200
ALTO_VENTANA = 800
# El lienzo ocupará el 70% del ancho y el panel el 30%
ANCHO_LIENZO = int(ANCHO_VENTANA * 0.7)
ANCHO_PANEL = ANCHO_VENTANA - ANCHO_LIENZO

# Variables globales de la cuadrícula y del laberinto
grid = None            # matriz 2D que representa el grid
num_filas = 0
num_columnas = 0
tam_celda = 0

# Variables para los puntos de entrada y salida, y para el recorrido
punto_inicio = None   # (fila, columna)
punto_fin = None      # (fila, columna)
recorrido = []        # lista de celdas en el recorrido (solución)
callejones_manual = []  # lista de celdas marcadas como callejón manual
paredes = {}          # diccionario que guarda información de paredes (puede ser refinado)
zoom_factor = 1.0     # Factor de zoom para el grid

# Modo de interacción actual ("grid", "situar_es", "recorrido_manual", "añadir_pared", "quitar_pared", "inicio_callejon", "fin_callejon")
modo = "grid"
def generar_grid(filas, columnas):
    global grid, num_filas, num_columnas, tam_celda
    num_filas = filas
    num_columnas = columnas
    # Calcular tamaño de cada celda para ajustar la cuadrícula al lienzo
    tam_celda = min(ANCHO_LIENZO // columnas, ALTO_VENTANA // filas)
    grid = np.zeros((filas, columnas))  # 0: celda vacía, 1: pared (si se requiere más tarde)
    # Reiniciar variables de entrada/solución
    global punto_inicio, punto_fin, recorrido, callejones_manual, paredes, modo
    punto_inicio = (0, 0)        # situar automáticamente la entrada en la celda (0,0)
    punto_fin = (1, 0)           # situar la salida en la celda contigua abajo de la entrada
    recorrido = [punto_inicio]
    callejones_manual = []
    paredes = {}  # Puede ser un diccionario con claves (fila, columna) y valor: lista de paredes presentes
    modo = "grid"
    actualizar_canvas()

def actualizar_canvas():
    ax.clear()
    # Dibujar cuadrícula: se dibuja cada celda
    for fila in range(num_filas):
        for col in range(num_columnas):
            x = col * tam_celda
            y = fila * tam_celda
            # Fondo de celda
            ax.add_patch(plt.Rectangle((x, y), tam_celda, tam_celda, facecolor=COLOR_GRID, edgecolor='none'))
            # Dibujar borde de celda
            ax.add_patch(plt.Rectangle((x, y), tam_celda, tam_celda, fill=False, edgecolor=COLOR_PARED, linewidth=1))
    # Dibujar punto de inicio y fin
    if punto_inicio:
        fila, col = punto_inicio
        x = col * tam_celda + tam_celda/2
        y = fila * tam_celda + tam_celda/2
        ax.plot(x, y, 'o', color=COLOR_INICIO, markersize=tam_celda/2)
    if punto_fin:
        fila, col = punto_fin
        x = col * tam_celda + tam_celda/2
        y = fila * tam_celda + tam_celda/2
        ax.plot(x, y, 'o', color=COLOR_FIN, markersize=tam_celda/2)
    # Dibujar recorrido (solución) en rojo
    if recorrido:
        pts_x = [col * tam_celda + tam_celda/2 for (fila, col) in recorrido]
        pts_y = [fila * tam_celda + tam_celda/2 for (fila, col) in recorrido]
        ax.plot(pts_x, pts_y, color=COLOR_SOLUCION, linewidth=2)
    # Dibujar callejones manual (en azul)
    for celda in callejones_manual:
        fila, col = celda
        x = col * tam_celda
        y = fila * tam_celda
        ax.add_patch(plt.Rectangle((x, y), tam_celda, tam_celda, facecolor=AZUL, alpha=0.3))
    # Dibujar paredes añadidas manualmente
    for key, lista in paredes.items():
        fila, col = key
        x = col * tam_celda
        y = fila * tam_celda
        for pared in lista:
            # Suponemos pared es una cadena 'N', 'S', 'E' o 'O'
            if pared == 'N':
                ax.plot([x, x+tam_celda], [y, y], color=COLOR_PARED, linewidth=2)
            elif pared == 'S':
                ax.plot([x, x+tam_celda], [y+tam_celda, y+tam_celda], color=COLOR_PARED, linewidth=2)
            elif pared == 'E':
                ax.plot([x+tam_celda, x+tam_celda], [y, y+tam_celda], color=COLOR_PARED, linewidth=2)
            elif pared == 'O':
                ax.plot([x, x], [y, y+tam_celda], color=COLOR_PARED, linewidth=2)
    ax.set_xlim(0, num_columnas * tam_celda)
    ax.set_ylim(num_filas * tam_celda, 0)
    ax.set_aspect('equal')
    canvas.draw()

# Configurar figura y canvas de Matplotlib
fig, ax = plt.subplots(figsize=(ANCHO_LIENZO/100, ALTO_VENTANA/100))
canvas = FigureCanvasTkAgg(fig, master=None)
def zoom_in():
    global tam_celda
    tam_celda = int(tam_celda * 1.1)
    actualizar_canvas()

def zoom_out():
    global tam_celda
    tam_celda = int(tam_celda * 0.9)
    actualizar_canvas()
def on_click(event):
    global punto_inicio, punto_fin, modo, recorrido
    if event.inaxes != ax:
        return
    col = int(event.xdata // tam_celda)
    fila = int(event.ydata // tam_celda)
    celda = (fila, col)
    # Si el modo es "situar_es", ya no pedimos que el usuario seleccione (los ubicamos automáticamente)
    # Según la nueva especificación, se sitúan la entrada y salida en dos celdas contiguas del lado izquierdo.
    if modo == "situar_es":
        punto_inicio = (num_calles_horizontales // 2 - 1, 0)
        punto_fin = (num_calles_horizontales // 2, 0)
        recorrido.clear()
        recorrido.append(punto_inicio)
        modo = "grid"  # Se desactiva este modo
        actualizar_canvas()
    elif modo == "recorrido_manual":
        # Permitir que el usuario modifique el recorrido con el ratón
        # Se establece la posición actual al hacer clic en una celda y se actualiza el recorrido
        if celda not in recorrido:
            recorrido.append(celda)
        else:
            indice = recorrido.index(celda)
            recorrido[:] = recorrido[:indice+1]
        actualizar_canvas()
    elif modo == "anadir_pared":
        # En esta modalidad, se añade la pared más cercana
        agregar_pared(celda)
        actualizar_canvas()
    elif modo == "quitar_pared":
        quitar_pared(celda)
        actualizar_canvas()

def on_key(event):
    global modo, recorrido, posicion_actual
    if modo == "recorrido_manual":
        if not recorrido:
            return
        ultima = recorrido[-1]
        f, c = ultima
        if event.keysym == 'Up' and f > 0:
            nueva = (f - 1, c)
        elif event.keysym == 'Down' and f < num_calles_horizontales - 1:
            nueva = (f + 1, c)
        elif event.keysym == 'Left' and c > 0:
            nueva = (f, c - 1)
        elif event.keysym == 'Right' and c < num_calles_verticales - 1:
            nueva = (f, c + 1)
        else:
            return
        if nueva in recorrido:
            indice = recorrido.index(nueva)
            recorrido[:] = recorrido[:indice+1]
        else:
            recorrido.append(nueva)
        actualizar_canvas()

def agregar_pared(celda):
    # Se añaden paredes en orden: N, E, S, O según la cercanía al clic
    global paredes
    if celda not in paredes:
        paredes[celda] = []
    orden = ['N', 'E', 'S', 'O']
    for p in orden:
        if p not in paredes[celda]:
            paredes[celda].append(p)
            break

def quitar_pared(celda):
    global paredes
    if celda in paredes and paredes[celda]:
        paredes[celda].pop(0)
class Aplicacion:
    def __init__(self, root):
        self.root = root
        self.root.title("Editor de Laberintos Manuales")
        self.crear_interfaz()
        self.bind_events()

    def crear_interfaz(self):
        # Dividir la ventana en dos partes: lienzo y panel de controles
        self.frame_canvas = tk.Frame(self.root, width=ANCHO_LIENZA, height=ALTO_VENTANA)
        self.frame_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.frame_control = tk.Frame(self.root, width=ANCHO_PANEL)
        self.frame_control.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Insertar botones y campos de entrada en el panel de control
        tk.Label(self.frame_control, text="Filas:").pack(pady=5)
        self.entry_filas = tk.Entry(self.frame_control)
        self.entry_filas.insert(0, "10")
        self.entry_filas.pack(pady=5)
        
        tk.Label(self.frame_control, text="Columnas:").pack(pady=5)
        self.entry_columnas = tk.Entry(self.frame_control)
        self.entry_columnas.insert(0, "10")
        self.entry_columnas.pack(pady=5)
        
        tk.Button(self.frame_control, text="Generar Grid", command=self.btn_generar_grid).pack(pady=5)
        tk.Button(self.frame_control, text="Situar E/S", command=self.btn_situar_es).pack(pady=5)
        tk.Button(self.frame_control, text="Recorrido Manual", command=self.btn_recorrido_manual).pack(pady=5)
        tk.Button(self.frame_control, text="+ Way", command=self.btn_agregar_way).pack(pady=5)
        tk.Button(self.frame_control, text="- Way", command=self.btn_eliminar_way).pack(pady=5)
        tk.Button(self.frame_control, text="+ Pared", command=self.btn_agregar_pared).pack(pady=5)
        tk.Button(self.frame_control, text="- Pared", command=self.btn_quitar_pared).pack(pady=5)
        tk.Button(self.frame_control, text="Generar Paredes", command=self.btn_generar_paredes).pack(pady=5)
        tk.Button(self.frame_control, text="Zoom In", command=zoom_in).pack(pady=5)
        tk.Button(self.frame_control, text="Zoom Out", command=zoom_out).pack(pady=5)
        
        # Panel de opciones de visualización
        self.var_mostrar_es = tk.BooleanVar(value=True)
        self.var_mostrar_sol = tk.BooleanVar(value=True)
        self.var_mostrar_way = tk.BooleanVar(value=True)
        self.var_mostrar_pared = tk.BooleanVar(value=True)
        tk.Checkbutton(self.frame_control, text="Mostrar E/S", variable=self.var_mostrar_es, command=actualizar_canvas).pack(pady=5)
        tk.Checkbutton(self.frame_control, text="Mostrar Solución", variable=self.var_mostrar_sol, command=actualizar_canvas).pack(pady=5)
        tk.Checkbutton(self.frame_control, text="Mostrar Waypoints", variable=self.var_mostrar_way, command=actualizar_canvas).pack(pady=5)
        tk.Checkbutton(self.frame_control, text="Mostrar Paredes", variable=self.var_mostrar_pared, command=actualizar_canvas).pack(pady=5)

    def bind_events(self):
        # Conectar eventos de clic y de teclado en el canvas de Matplotlib
        self.canvas = canvas  # Usamos el canvas global de Matplotlib
        self.canvas.mpl_connect("button_press_event", on_click)
        self.root.bind("<Key>", on_key)

    def btn_generar_grid(self):
        global num_calles_horizontales, num_calles_verticales
        try:
            num_calles_horizontales = int(self.entry_filas.get())
            num_calles_verticales = int(self.entry_columnas.get())
        except:
            messagebox.showerror("Error", "Valores inválidos para filas/columnas.")
            return
        generar_grid(num_calles_horizontales, num_calles_verticales)

    def btn_situar_es(self):
        global modo
        modo = "situar_es"
        
    def btn_recorrido_manual(self):
        global modo
        modo = "recorrido_manual"
        
    def btn_agregar_way(self):
        global modo
        # Aquí se implementaría la lógica para agregar waypoints a la solución
        modo = "agregar_way"
        
    def btn_eliminar_way(self):
        global modo
        # Aquí se implementaría la lógica para eliminar waypoints
        modo = "eliminar_way"
        
    def btn_agregar_pared(self):
        global modo
        modo = "anadir_pared"
        
    def btn_quitar_pared(self):
        global modo
        modo = "quitar_pared"
        
    def btn_generar_paredes(self):
        global modo
        # Aquí se implementaría la generación automática de paredes para cerrar el laberinto
        modo = "generar_paredes"
        # Por ejemplo, podrías llamar a una función que recalcule paredes para que todas las celdas sean accesibles
        # Esta función se dejará como placeholder
        messagebox.showinfo("Generar Paredes", "Funcionalidad no implementada aún.")
        actualizar_canvas()

def main():
    root = tk.Tk()
    app = Aplicacion(root)
    root.mainloop()

if __name__ == "__main__":
    root = tk.Tk()
    app = InterfazLaberinto(root)
    # Vincular eventos para el canvas de Matplotlib
    app.canvas.mpl_connect("button_press_event", app.on_click)
    root.bind("<Key>", app.on_key_press)
    root.mainloop()