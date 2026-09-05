import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

# 1. Geometría Base del Dodecaedro Rómbico (FCC)
def get_rhombic_dodecahedron_faces(center, rotation_matrix=np.eye(3)):
    v_base = np.array([
        [1, 1, 1], [1, 1, -1], [1, -1, 1], [1, -1, -1],
        [-1, 1, 1], [-1, 1, -1], [-1, -1, 1], [-1, -1, -1],
        [2, 0, 0], [-2, 0, 0], [0, 2, 0], [0, -2, 0], [0, 0, 2], [0, 0, -2]
    ]) / 2.0
    
    # Aplicar rotación a la malla si pertenece a la Red B
    v_rotated = np.dot(v_base, rotation_matrix.T)
    v_centered = v_rotated + center
    
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

# 2. Vectores Canónicos de Direcciones (Red A)
NEIGHBOR_VECTORS_A = np.array([
    [ 1,  1,  0], [-1,  1,  0], [ 1, -1,  0], [-1, -1,  0],
    [ 1,  0,  1], [-1,  0,  1], [ 1,  0, -1], [-1,  0, -1],
    [ 0,  1,  1], [ 0, -1,  1], [ 0,  1, -1], [ 0, -1, -1]
], dtype=float)

# Matriz de rotación a 90 grados alrededor del eje Y para la Red B
R_90_Y = np.array([
    [ 0, 0, 1],
    [ 0, 1, 0],
    [-1, 0, 0]
], dtype=float)

# Direcciones transformadas para la Red B
NEIGHBOR_VECTORS_B = np.dot(NEIGHBOR_VECTORS_A, R_90_Y.T)

# Centros de celdas
CENTRAL_POS = np.array([0.0, 0.0, 0.0])
GRID_A_CENTERS = [CENTRAL_POS] + [v for v in NEIGHBOR_VECTORS_A]
GRID_B_CENTERS = [CENTRAL_POS] + [v for v in NEIGHBOR_VECTORS_B]

# Estado de los Segmentos
segment_length = 0.55
center_A, dir_A = CENTRAL_POS.copy(), np.array([0.0, 0.0, 1.0])
center_B, dir_B = CENTRAL_POS.copy(), np.array([1.0, 0.0, 0.0]) # Perpendicular en reposo

# 3. Configuración de la Escena 3D
fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection='3d')
plt.subplots_adjust(bottom=0.15)

def draw_dual_grids():
    # Red A (Naranja)
    for center in GRID_A_CENTERS:
        faces = get_rhombic_dodecahedron_faces(center, np.eye(3))
        poly = Poly3DCollection(faces, alpha=0.05, edgecolor='darkorange', linewidths=0.5)
        poly.set_facecolor('orange')
        ax.add_collection3d(poly)
        
    # Red B (Azul, superpuesta a 90°)
    for center in GRID_B_CENTERS:
        faces = get_rhombic_dodecahedron_faces(center, R_90_Y)
        poly = Poly3DCollection(faces, alpha=0.05, edgecolor='royalblue', linewidths=0.5)
        poly.set_facecolor('dodgerblue')
        ax.add_collection3d(poly)

draw_dual_grids()

# Segmento Red A (Rojo / Dextrógiro)
pA1 = center_A - (segment_length/2.0)*dir_A
pA2 = center_A + (segment_length/2.0)*dir_A
line_A, = ax.plot([pA1[0], pA2[0]], [pA1[1], pA2[1]], [pA1[2], pA2[2]], 'r-', linewidth=4, label='Segmento Red A (+p)')

# Segmento Red B (Verde / Levógiro)
pB1 = center_B - (segment_length/2.0)*dir_B
pB2 = center_B + (segment_length/2.0)*dir_B
line_B, = ax.plot([pB1[0], pB2[0]], [pB1[1], pB2[1]], [pB1[2], pB2[2]], 'g-', linewidth=4, label='Segmento Red B (-p)')

ax.set_xlim([-2.5, 2.5]); ax.set_ylim([-2.5, 2.5]); ax.set_zlim([-2.5, 2.5])
ax.set_xlabel('X'); ax.set_ylabel('Y'); ax.set_zlabel('Z')
ax.set_title('Mallas Superpuestas a 90°: Screw Motion con Chirality Opuesta')
ax.legend(loc='upper right')

# 4. Simulación Simultánea sin Colisión (Quiralidades Contrapuestas)
def evolutionFunction(event):
    global center_A, dir_A, center_B, dir_B
    
    idx_A = np.random.randint(0, 12)
    idx_B = np.random.randint(0, 12)
    
    vec_A = NEIGHBOR_VECTORS_A[idx_A]
    vec_B = NEIGHBOR_VECTORS_B[idx_B]
    
    target_A = CENTRAL_POS + vec_A
    target_B = CENTRAL_POS + vec_B
    
    axis_A = vec_A / np.linalg.norm(vec_A)
    axis_B = vec_B / np.linalg.norm(vec_B)
    
    frames = 25
    # Asignación de quiralidad: Red A (+360° Dextrógiro), Red B (-360° Levógiro)
    pitch_A =  2 * np.pi
    pitch_B = -2 * np.pi 
    
    start_cA, start_dA = center_A.copy(), dir_A.copy()
    start_cB, start_dB = center_B.copy(), dir_B.copy()
    
    for f in range(1, frames + 1):
        t = f / float(frames)
        
        # Interp Traslacional
        curr_cA = (1 - t) * start_cA + t * target_A
        curr_cB = (1 - t) * start_cB + t * target_B
        
        # Rotación Rodrigues Red A
        ang_A = t * pitch_A
        rot_dA = (start_dA * np.cos(ang_A) + 
                  np.cross(axis_A, start_dA) * np.sin(ang_A) + 
                  axis_A * np.dot(axis_A, start_dA) * (1 - np.cos(ang_A)))
        
        # Rotación Rodrigues Red B
        ang_B = t * pitch_B
        rot_dB = (start_dB * np.cos(ang_B) + 
                  np.cross(axis_B, start_dB) * np.sin(ang_B) + 
                  axis_B * np.dot(axis_B, start_dB) * (1 - np.cos(ang_B)))
        
        # Actualización de Posiciones de los Segmentos
        pA_start = curr_cA - (segment_length/2.0) * rot_dA
        pA_end   = curr_cA + (segment_length/2.0) * rot_dA
        pB_start = curr_cB - (segment_length/2.0) * rot_dB
        pB_end   = curr_cB + (segment_length/2.0) * rot_dB
        
        line_A.set_data([pA_start[0], pA_end[0]], [pA_start[1], pA_end[1]])
        line_A.set_3d_properties([pA_start[2], pA_end[2]])
        
        line_B.set_data([pB_start[0], pB_end[0]], [pB_start[1], pB_end[1]])
        line_B.set_3d_properties([pB_start[2], pB_end[2]])
        
        plt.pause(0.01)
        
    center_A, dir_A = target_A, rot_dA / np.linalg.norm(rot_dA)
    center_B, dir_B = target_B, rot_dB / np.linalg.norm(rot_dB)

# 5. Botón de Control
ax_button = plt.axes([0.3, 0.03, 0.4, 0.06])
btn_evolute = Button(ax_button, 'Mover Ambos Segmentos (Screw)', color='lightgray', hovercolor='0.85')
btn_evolute.on_clicked(evolutionFunction)

plt.show()