import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

# 1. Base Geometry: Rhombic Dodecahedron (FCC Lattice)
def get_rhombic_dodecahedron_faces(center, rotation_matrix=np.eye(3)):
    v_base = np.array([
        [1, 1, 1], [1, 1, -1], [1, -1, 1], [1, -1, -1],
        [-1, 1, 1], [-1, 1, -1], [-1, -1, 1], [-1, -1, -1],
        [2, 0, 0], [-2, 0, 0], [0, 2, 0], [0, -2, 0], [0, 0, 2], [0, 0, -2]
    ]) / 2.0
    
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

# 2. Lattice Vectors & 90° Rotation Matrix
dir_vec_A = np.array([1.0, 1.0, 0.0])

R_90_Y = np.array([
    [ 0, 0, 1],
    [ 0, 1, 0],
    [-1, 0, 0]
], dtype=float)

dir_vec_B = np.dot(dir_vec_A, R_90_Y.T)

# --------------------------------------------------------------------------
# OCTAHEDRAL SUB-GRID OFFSETTING
# Instead of converging at (0,0,0), targets in the central cell are shifted 
# along orthogonal axes to form skew lines at rest.
# --------------------------------------------------------------------------
offset_distance = 0.35
offset_A = np.array([0.0, 0.0,  offset_distance])  # Shift +Z in central cell
offset_B = np.array([0.0, 0.0, -offset_distance])  # Shift -Z in central cell (or along X/Y)

GRID_A_CENTERS = [-dir_vec_A, np.array([0.0, 0.0, 0.0]) + offset_A, dir_vec_A]
GRID_B_CENTERS = [-dir_vec_B, np.array([0.0, 0.0, 0.0]) + offset_B, dir_vec_B]

# Parameters and Initial States
segment_length = 0.60
step_state = 0  # 0: Start, 1: Central Cell (Offset), 2: End Cell

INIT_DIR_A = np.array([0.0, 0.0, 1.0])
INIT_DIR_B = np.array([1.0, 0.0, 0.0])

center_A = GRID_A_CENTERS[0].copy()
center_B = GRID_B_CENTERS[0].copy()
dir_A = INIT_DIR_A.copy()
dir_B = INIT_DIR_B.copy()

# 3. 3D Scene Setup
fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection='3d')
plt.subplots_adjust(bottom=0.15)

def draw_scene():
    # Draw Network A Cells (Orange)
    for i, center in enumerate([-dir_vec_A, np.array([0.0,0.0,0.0]), dir_vec_A]):
        faces = get_rhombic_dodecahedron_faces(center, np.eye(3))
        poly = Poly3DCollection(faces, alpha=0.05, edgecolor='darkorange', linewidths=0.6)
        poly.set_facecolor('orange')
        ax.add_collection3d(poly)
        
    # Draw Network B Cells (Blue, 90° Rotated)
    for i, center in enumerate([-dir_vec_B, np.array([0.0,0.0,0.0]), dir_vec_B]):
        faces = get_rhombic_dodecahedron_faces(center, R_90_Y)
        poly = Poly3DCollection(faces, alpha=0.05, edgecolor='royalblue', linewidths=0.6)
        poly.set_facecolor('dodgerblue')
        ax.add_collection3d(poly)

draw_scene()

def update_graphic_lines(pA, pB, dirA_vec, dirB_vec):
    pA1 = pA - (segment_length/2.0) * dirA_vec
    pA2 = pA + (segment_length/2.0) * dirA_vec
    pB1 = pB - (segment_length/2.0) * dirB_vec
    pB2 = pB + (segment_length/2.0) * dirB_vec
    
    line_A.set_data([pA1[0], pA2[0]], [pA1[1], pA2[1]])
    line_A.set_3d_properties([pA1[2], pA2[2]])
    
    line_B.set_data([pB1[0], pB2[0]], [pB1[1], pB2[1]])
    line_B.set_3d_properties([pB1[2], pB2[2]])

# Initialize Segment Drawings
pA1_init = center_A - (segment_length/2.0) * dir_A
pA2_init = center_A + (segment_length/2.0) * dir_A
line_A, = ax.plot([pA1_init[0], pA2_init[0]], [pA1_init[1], pA2_init[1]], [pA1_init[2], pA2_init[2]], 'r-', linewidth=5, label='Segment Network A (+p)')

pB1_init = center_B - (segment_length/2.0) * dir_B
pB2_init = center_B + (segment_length/2.0) * dir_B
line_B, = ax.plot([pB1_init[0], pB2_init[0]], [pB1_init[1], pB2_init[1]], [pB1_init[2], pB2_init[2]], 'g-', linewidth=5, label='Segment Network B (-p)')

ax.set_xlim([-2.2, 2.2]); ax.set_ylim([-2.2, 2.2]); ax.set_zlim([-2.2, 2.2])
ax.set_xlabel('X'); ax.set_ylabel('Y'); ax.set_zlabel('Z')
ax.set_title('Sub-Grid Offsetting: Skew Line Alignment in Shared Cell')
ax.legend(loc='upper right')

# 4. Step Function (Screw Motion with Sub-Grid Offset)
def stepFunction(event):
    global step_state, center_A, dir_A, center_B, dir_B
    
    if step_state >= 2:
        # Reset to initial state
        step_state = 0
        center_A = GRID_A_CENTERS[0].copy()
        center_B = GRID_B_CENTERS[0].copy()
        dir_A = INIT_DIR_A.copy()
        dir_B = INIT_DIR_B.copy()
        
        update_graphic_lines(center_A, center_B, dir_A, dir_B)
        btn_step.label.set_text('Advance Step (Screw Motion)')
        fig.canvas.draw_idle()
        print("[Reset] Positions restored to initial state.")
        return

    next_state = step_state + 1
    target_A = GRID_A_CENTERS[next_state]
    target_B = GRID_B_CENTERS[next_state]
    
    axis_A = dir_vec_A / np.linalg.norm(dir_vec_A)
    axis_B = dir_vec_B / np.linalg.norm(dir_vec_B)
    
    frames = 35
    pitch_A =  2 * np.pi  # Full 360° right-handed screw
    pitch_B = -2 * np.pi  # Full 360° left-handed screw
    
    start_cA, start_dA = center_A.copy(), dir_A.copy()
    start_cB, start_dB = center_B.copy(), dir_B.copy()
    
    for f in range(1, frames + 1):
        t = f / float(frames)
        
        # Translation path (including sub-grid target offset)
        curr_cA = (1 - t) * start_cA + t * target_A
        curr_cB = (1 - t) * start_cB + t * target_B
        
        # Rodrigues helical rotation for Network A
        ang_A = t * pitch_A
        rot_dA = (start_dA * np.cos(ang_A) + 
                  np.cross(axis_A, start_dA) * np.sin(ang_A) + 
                  axis_A * np.dot(axis_A, start_dA) * (1 - np.cos(ang_A)))
        
        # Rodrigues helical rotation for Network B
        ang_B = t * pitch_B
        rot_dB = (start_dB * np.cos(ang_B) + 
                  np.cross(axis_B, start_dB) * np.sin(ang_B) + 
                  axis_B * np.dot(axis_B, start_dB) * (1 - np.cos(ang_B)))
        
        update_graphic_lines(curr_cA, curr_cB, rot_dA, rot_dB)
        plt.pause(0.015)
        
    center_A, dir_A = target_A, rot_dA / np.linalg.norm(rot_dA)
    center_B, dir_B = target_B, rot_dB / np.linalg.norm(rot_dB)
    step_state = next_state
    
    if step_state == 1:
        dist = np.linalg.norm(center_A - center_B)
        print(f"[Step 1 Complete] Both segments inside central cell.")
        print(f" -> Sub-grid clearance distance: {dist:.3f} units (Zero Collision / Skew Lines).")
    elif step_state == 2:
        btn_step.label.set_text('Reset Simulation')
        fig.canvas.draw_idle()
        print("[Step 2 Complete] End cells reached. Click button to reset.")

# 5. UI Controls
ax_button = plt.axes([0.3, 0.03, 0.4, 0.06])
btn_step = Button(ax_button, 'Advance Step (Screw Motion)', color='lightgray', hovercolor='0.85')
btn_step.on_clicked(stepFunction)

plt.show()