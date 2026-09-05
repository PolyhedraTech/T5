import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

# 1. Geometría Base del Dodecaedro Rómbico (FCC)
def get_rhombic_dodecahedron_faces(center):
    v = np.array([
        [1, 1, 1], [1, 1, -1], [1, -1, 1], [1, -1, -1],
        [-1, 1, 1], [-1, 1, -1], [-1, -1, 1], [-1, -1, -1],
        [2, 0, 0], [-2, 0, 0], [0, 2, 0], [0, -2, 0], [0, 0, 2], [0, 0, -2]
    ]) / 2.0
    
    v_centered = v + center
    
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

# 2. Vectores de movimiento a las 12 celdas vecinas
NEIGHBOR_VECTORS = np.array([
    [ 1,  1,  0], [-1,  1,  0], [ 1, -1,  0], [-1, -1,  0],
    [ 1,  0,  1], [-1,  0,  1], [ 1,  0, -1], [-1,  0, -1],
    [ 0,  1,  1], [ 0, -1,  1], [ 0,  1, -1], [ 0, -1, -1]
], dtype=float)

CENTRAL_CELL_POS = np.array([0.0, 0.0, 0.0])
GRID_CENTERS = [CENTRAL_CELL_POS] + [vec for vec in NEIGHBOR_VECTORS]

# Estado actual de posición y orientación del segmento (inicio y fin)
segment_length = 0.6
current_center = np.array([0.0, 0.0, 0.0])
# Inicialmente orientado a lo largo del eje Z
current_segment_dir = np.array([0.0, 0.0, 1.0]) 

# Configuración Visual
fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection='3d')
plt.subplots_adjust(bottom=0.15)

def draw_grid():
    for idx, center in enumerate(GRID_CENTERS):
        faces = get_rhombic_dodecahedron_faces(center)
        if idx == 0:
            color, alpha = 'orange', 0.20
        else:
            color, alpha = 'cyan', 0.08
            
        poly3d = Poly3DCollection(faces, alpha=alpha, edgecolor='black', linewidths=0.6)
        poly3d.set_facecolor(color)
        ax.add_collection3d(poly3d)

draw_grid()

# Dibujar el Segmento Inicial (En color rojo con puntos en los extremos)
p_start = current_center - (segment_length / 2.0) * current_segment_dir
p_end = current_center + (segment_length / 2.0) * current_segment_dir

segment_line, = ax.plot([p_start[0], p_end[0]], 
                        [p_start[1], p_end[1]], 
                        [p_start[2], p_end[2]], 
                        'r-', linewidth=4, label='Segmento Extenso')
segment_ends, = ax.plot([p_start[0], p_end[0]], 
                        [p_start[1], p_end[1]], 
                        [p_start[2], p_end[2]], 
                        'ro', markersize=6)

ax.set_xlim([-2.5, 2.5]); ax.set_ylim([-2.5, 2.5]); ax.set_zlim([-2.5, 2.5])
ax.set_xlabel('X'); ax.set_ylabel('Y'); ax.set_zlabel('Z')
ax.set_title('Screw Motion (Tornillo) del Segmento en Celda Rómbica')

# 3. Función del Movimiento Helicoidal (Screw Motion)
def evolutionFunction(event):
    global current_center, current_segment_dir
    
    # Seleccionar celda vecina aleatoria (1 a 12)
    random_idx = np.random.randint(0, 12)
    move_vector = NEIGHBOR_VECTORS[random_idx]
    target_center = CENTRAL_CELL_POS + move_vector
    
    # Eje de traslación/rotación helicoidal (normalizado)
    axis = move_vector / np.linalg.norm(move_vector)
    
    # Configuración de la animación Screw Motion (Animación de 20 frames)
    frames = 20
    pitch_angle = 2 * np.pi  # Rotación completa de 360 grados sobre el eje de avance
    
    start_c = current_center.copy()
    start_dir = current_segment_dir.copy()
    
    for f in range(1, frames + 1):
        t = f / float(frames)
        
        # A) Traslación lineal a lo largo del vector hacia la celda vecina
        interp_center = (1 - t) * start_c + t * target_center
        
        # B) Rotación de Rodrigues alrededor del eje de movimiento (Screw/Rosca)
        angle = t * pitch_angle
        cos_a, sin_a = np.cos(angle), np.sin(angle)
        
        # Fórmula de rotación de Rodrigues para el vector de dirección del segmento
        rotated_dir = (start_dir * cos_a + 
                       np.cross(axis, start_dir) * sin_a + 
                       axis * np.dot(axis, start_dir) * (1 - cos_a))
        
        # C) Recalcular extremos del segmento
        p1 = interp_center - (segment_length / 2.0) * rotated_dir
        p2 = interp_center + (segment_length / 2.0) * rotated_dir
        
        # Actualizar gráfico
        segment_line.set_data([p1[0], p2[0]], [p1[1], p2[1]])
        segment_line.set_3d_properties([p1[2], p2[2]])
        
        segment_ends.set_data([p1[0], p2[0]], [p1[1], p2[1]])
        segment_ends.set_3d_properties([p1[2], p2[2]])
        
        plt.pause(0.02)  # Pausa para renderizado continuo
    
    # Actualizar estado global final
    current_center = target_center
    current_segment_dir = rotated_dir / np.linalg.norm(rotated_dir)
    print(f"[Screw Motion] Segmento desplazado hacia vecino {random_idx + 1}: {move_vector}")

# 4. Botón de Control
ax_button = plt.axes([0.3, 0.03, 0.4, 0.06])
btn_evolute = Button(ax_button, 'Ejecutar Screw Motion', color='lightgray', hovercolor='0.85')
btn_evolute.on_clicked(evolutionFunction)

plt.show()