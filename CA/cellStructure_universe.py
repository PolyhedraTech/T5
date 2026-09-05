import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

# 1. Definición del Dodecaedro Rómbico Base (Centrado en 0,0,0)
# Los 14 vértices del dodecaedro rómbico canónico
BASE_VERTICES = np.array([
    [ 1,  1,  0], [-1,  1,  0], [ 1, -1,  0], [-1, -1,  0],  # Grado 4 (4)
    [ 1,  0,  1], [-1,  0,  1], [ 1,  0, -1], [-1,  0, -1],  # Grado 4 (4)
    [ 0,  1,  1], [ 0, -1,  1], [ 0,  1, -1], [ 0, -1, -1],  # Grado 4 (4) -> Réplica/Coordenadas FCC
    [ 0,  0,  2], [ 0,  0, -2],                              # Axial Z (+2, -2)
    [ 2,  0,  0], [-2,  0,  0],                              # Axial X (+2, -2)
    [ 0,  2,  0], [ 0, -2,  0]                               # Axial Y (+2, -2)
])

# Re-mapeo geométrico exacto: 12 vértices en (±1, ±1, 0) y permutaciones, más 2 por eje
VERTICES = np.array([
    # 8 vértices tipo cubo (±1, ±1, ±1)
    [ 1,  1,  1], [ 1,  1, -1], [ 1, -1,  1], [ 1, -1, -1],
    [-1,  1,  1], [-1,  1, -1], [-1, -1,  1], [-1, -1, -1],
    # 6 vértices axiales (±2, 0, 0), (0, ±2, 0), (0, 0, ±2)
    [ 2,  0,  0], [-2,  0,  0],
    [ 0,  2,  0], [ 0, -2,  0],
    [ 0,  0,  2], [ 0,  0, -2]
])

# Definición de las 12 caras rómbicas a través de sus índices de vértices
FACES_INDICES = [
    [8, 0, 10, 4],  [8, 4, 12, 0],  [8, 12, 5, 10], [8, 5, 1, 10],  # Caras superiores/intermedias
    [9, 2, 11, 6],  [9, 6, 13, 2],  [9, 13, 7, 11], [9, 7, 3, 11],  # Caras inferiores/intermedias
    [0, 12, 2, 8],  [4, 12, 6, 5],  [1, 10, 3, 11], [0, 8, 2, 9]   # Caras de cierre lateral
]

# Ajuste fino manual de las 12 caras rómbicas estándar del Dodecaedro Rómbico (FCC)
def get_rhombic_dodecahedron_faces(center):
    """ Genera la geometría de las 12 caras rómbicas desplazadas al centro dado. """
    v = np.array([
        # 8 vértices cúbicos
        [1, 1, 1], [1, 1, -1], [1, -1, 1], [1, -1, -1],
        [-1, 1, 1], [-1, 1, -1], [-1, -1, 1], [-1, -1, -1],
        # 6 vértices axiales
        [2, 0, 0], [-2, 0, 0], [0, 2, 0], [0, -2, 0], [0, 0, 2], [0, 0, -2]
    ]) / 2.0  # Normalizar escala
    
    # Índices exactos de los 4 vértices de cada una de las 12 caras rómbicas
    faces_idx = [
        [8, 0, 10, 1], [8, 1, 11, 3], [8, 3, 9, 2], [8, 2, 10, 0],
        [12, 0, 10, 4], [12, 4, 11, 5], [12, 5, 9, 7], [12, 7, 10, 6],
        [13, 1, 10, 5], [13, 5, 11, 7], [13, 7, 9, 3], [13, 3, 10, 1]
    ]
    
    # Mapeo directo simplificado mediante envolvente coordinada de vectores
    # Usaremos una representación de caras para cada desplazamiento FCC:
    
    # Vectores de dirección a las 12 celdas vecinas (Red FCC)
    directions = np.array([
        [ 1,  1,  0], [-1,  1,  0], [ 1, -1,  0], [-1, -1,  0],
        [ 1,  0,  1], [-1,  0,  1], [ 1,  0, -1], [-1,  0, -1],
        [ 0,  1,  1], [ 0, -1,  1], [ 0,  1, -1], [ 0, -1, -1]
    ])
    
    faces = []
    # Generación de la malla visual del poliedro mediante combinación de vértices
    for d in directions:
        # Puntos de la cara ortogonal a la dirección
        pass

    # Utilizaremos la definición canónica por coordenadas de vértices:
    v_centered = v + center
    
    # 12 Caras Rómbicas canónicas
    faces_coords = [
        [v_centered[12], v_centered[0], v_centered[8], v_centered[4]],
        [v_centered[12], v_centered[4], v_centered[9], v_centered[6]],
        [v_centered[12], v_centered[6], v_centered[11], v_centered[2]],
        [v_centered[12], v_centered[2], v_centered[8], v_centered[0]],
        [v_centered[13], v_centered[1], v_centered[8], v_centered[5]],
        [v_centered[13], v_centered[5], v_centered[9], v_centered[7]],
        [v_centered[13], v_centered[7], v_centered[11], v_centered[3]],
        [v_centered[13], v_centered[3], v_centered[8], v_centered[1]],
        [v_centered[10], v_centered[0], v_centered[8], v_centered[1]],
        [v_centered[10], v_centered[4], v_centered[9], v_centered[5]],
        [v_centered[11], v_centered[2], v_centered[8], v_centered[3]],
        [v_centered[11], v_centered[6], v_centered[9], v_centered[7]]
    ]
    return faces_coords

# 2. Direcciones de movimiento (Vectores a los 12 vecinos directos)
NEIGHBOR_VECTORS = np.array([
    [ 1,  1,  0], [-1,  1,  0], [ 1, -1,  0], [-1, -1,  0],
    [ 1,  0,  1], [-1,  0,  1], [ 1,  0, -1], [-1,  0, -1],
    [ 0,  1,  1], [ 0, -1,  1], [ 0,  1, -1], [ 0, -1, -1]
], dtype=float)

# Posición central inicial de las 13 celdas (1 Central + 12 Vecinas)
CENTRAL_CELL_POS = np.array([0.0, 0.0, 0.0])
GRID_CENTERS = [CENTRAL_CELL_POS] + [vec for vec in NEIGHBOR_VECTORS]

# Estado global de la posición del punto rojo
current_point_pos = np.array([0.0, 0.0, 0.0])

# 3. Configuración de la Figura y Malla 3D
fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection='3d')
plt.subplots_adjust(bottom=0.15)

def draw_grid():
    """ Dibuja la celda central y las 12 celdas vecinas translúcidas. """
    for idx, center in enumerate(GRID_CENTERS):
        faces = get_rhombic_dodecahedron_faces(center)
        
        # Diferenciar celda central de las vecinas por color
        if idx == 0:
            color = 'orange'
            alpha = 0.25  # Alta translucidez para ver el punto interno
        else:
            color = 'cyan'
            alpha = 0.12
            
        poly3d = Poly3DCollection(faces, alpha=alpha, edgecolor='black', linewidths=0.8)
        poly3d.set_facecolor(color)
        ax.add_collection3d(poly3d)

# Dibujar la malla estática
draw_grid()

# Dibujar el punto rojo inicial
point_plot, = ax.plot([current_point_pos[0]], 
                      [current_point_pos[1]], 
                      [current_point_pos[2]], 
                      'ro', markersize=12, label='Agent')

# Ajustes de ejes y perspectiva
ax.set_xlim([-2.5, 2.5])
ax.set_ylim([-2.5, 2.5])
ax.set_zlim([-2.5, 2.5])
ax.set_xlabel('Eje X')
ax.set_ylabel('Eje Y')
ax.set_zlabel('Eje Z')
ax.set_title('Malla autómata: Dodecaedro Rómbico (1 Celda Central + 12 Vecinas)')

# 4. Función de Evolución (Disparada por el Botón)
def evolutionFunction(event):
    global current_point_pos
    
    # 1. Generar número aleatorio entre 1 y 12
    random_neighbor_idx = np.random.randint(1, 13)
    
    # 2. Seleccionar el vector de movimiento correspondiente (índice 0 a 11)
    selected_vector = NEIGHBOR_VECTORS[random_neighbor_idx - 1]
    
    # 3. Mover el punto rojo hacia la celda vecina elegida
    current_point_pos = CENTRAL_CELL_POS + selected_vector
    
    # 4. Actualizar la posición gráfica del punto rojo
    point_plot.set_data([current_point_pos[0]], [current_point_pos[1]])
    point_plot.set_3d_properties([current_point_pos[2]])
    
    print(f"[Evolution] Selección aleatoria: Vecino {random_neighbor_idx} -> Moviendo a vector: {selected_vector}")
    fig.canvas.draw_idle()

# 5. Botón de Interfaz de Usuario
ax_button = plt.axes([0.35, 0.03, 0.3, 0.06])  # [left, bottom, width, height]
btn_evolute = Button(ax_button, 'Ejecutar evolutionFunction', color='lightgray', hovercolor='0.85')
btn_evolute.on_clicked(evolutionFunction)

plt.show()