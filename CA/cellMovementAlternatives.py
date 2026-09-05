import numpy as np
import matplotlib.pyplot as plt

# 1. Parámetros del desplazamiento (De Celda Central [0,0,0] a Vecina [1,1,0])
start_pos = np.array([0.0, 0.0, 0.0])
target_pos = np.array([1.0, 1.0, 0.0])
t = np.linspace(0, 1, 100)

fig = plt.figure(figsize=(12, 10))

# ----------------------------------------------------
# Opción 1: Lineal + Spin propio (Trayectoria Recta)
# ----------------------------------------------------
ax1 = fig.add_subplot(221, projection='3d')
lineal_path = np.outer(1 - t, start_pos) + np.outer(t, target_pos)

ax1.plot(lineal_path[:,0], lineal_path[:,1], lineal_path[:,2], 'b-', linewidth=2, label='Trayectoria del centro')
ax1.plot([start_pos[0]], [start_pos[1]], [start_pos[2]], 'go', markersize=8, label='Inicio')
ax1.plot([target_pos[0]], [target_pos[1]], [target_pos[2]], 'ro', markersize=8, label='Fin')

# Representar espín propio mediante pequeños giros transversales
spin_radius = 0.1
for i in range(0, 100, 15):
    angle = 4 * np.pi * t[i]
    dx = spin_radius * np.cos(angle)
    dy = -spin_radius * np.cos(angle)
    dz = spin_radius * np.sin(angle)
    ax1.plot([lineal_path[i,0], lineal_path[i,0] + dx],
             [lineal_path[i,1], lineal_path[i,1] + dy],
             [lineal_path[i,2], lineal_path[i,2] + dz], 'r-', alpha=0.6)

ax1.set_title("1. Lineal + Spin Propio\n(Atraviesa el centro compartido - Colisión)")
ax1.set_xlabel("X"); ax1.set_ylabel("Y"); ax1.set_zlabel("Z")

# ----------------------------------------------------
# Opción 2: Trayectoria Helicoidal (Screw Motion)
# ----------------------------------------------------
ax2 = fig.add_subplot(222, projection='3d')
helix_radius = 0.25
pitch = 2 * np.pi

# Eje principal de movimiento
axis_vector = target_pos - start_pos
axis_norm = axis_vector / np.linalg.norm(axis_vector)

# Vectores ortogonales al eje de movimiento para construir la hélice
u = np.array([-1.0, 1.0, 0.0]) / np.sqrt(2)
v = np.array([0.0, 0.0, 1.0])

helix_path = np.zeros((len(t), 3))
for i in range(len(t)):
    linear_part = start_pos + t[i] * axis_vector
    rot_part = helix_radius * (np.cos(pitch * t[i]) * u + np.sin(pitch * t[i]) * v)
    helix_path[i] = linear_part + rot_part

ax2.plot(helix_path[:,0], helix_path[:,1], helix_path[:,2], 'm-', linewidth=2, label='Hélice')
ax2.plot(lineal_path[:,0], lineal_path[:,1], lineal_path[:,2], 'k--', alpha=0.3, label='Eje Central')
ax2.plot([start_pos[0]], [start_pos[1]], [start_pos[2]], 'go', markersize=8)
ax2.plot([target_pos[0]], [target_pos[1]], [target_pos[2]], 'ro', markersize=8)

ax2.set_title("2. Trayectoria Helicoidal (Screw)\n(Orbita la cara periférica - Evita colisión)")
ax2.set_xlabel("X"); ax2.set_ylabel("Y"); ax2.set_zlabel("Z")

# ----------------------------------------------------
# Opción 3: Rotación de Cuaterniones (Arco Slerp)
# ----------------------------------------------------
ax3 = fig.add_subplot(223, projection='3d')

# Arco geodésico proyectado mediante elevación cuadrática sobre S3 -> R3
arc_height = 0.35
slerp_path = np.zeros((len(t), 3))
for i in range(len(t)):
    # Combinación de interpolación + elevación de curva geodésica
    base_pos = (1 - t[i]) * start_pos + t[i] * target_pos
    curve = arc_height * np.sin(np.pi * t[i]) * np.array([0.0, 0.0, 1.0])
    slerp_path[i] = base_pos + curve

ax3.plot(slerp_path[:,0], slerp_path[:,1], slerp_path[:,2], 'g-', linewidth=2.5, label='Arco Slerp')
ax3.plot(lineal_path[:,0], lineal_path[:,1], lineal_path[:,2], 'k--', alpha=0.3, label='Cuerda Directa')
ax3.plot([start_pos[0]], [start_pos[1]], [start_pos[2]], 'go', markersize=8)
ax3.plot([target_pos[0]], [target_pos[1]], [target_pos[2]], 'ro', markersize=8)

ax3.set_title("3. Rotación Cuaterniónica (Arco Slerp)\n(Geodésica natural - Esquiva el punto crítico)")
ax3.set_xlabel("X"); ax3.set_ylabel("Y"); ax3.set_zlabel("Z")

# ----------------------------------------------------
# Opción 4: Movimiento Alterno Temporal (Phase Shift)
# ----------------------------------------------------
ax4 = fig.add_subplot(224)

# Diagrama de pulsos temporales discretos
time_steps = np.array([0, 1, 2, 3, 4, 5])
red_A_active = np.array([1, 0, 1, 0, 1, 0])
red_B_active = np.array([0, 1, 0, 1, 0, 1])

ax4.step(time_steps, red_A_active, where='post', label='Red A (Activa en t)', color='orange', linewidth=2.5)
ax4.step(time_steps, red_B_active, where='post', label='Red B (Activa en t+0.5)', color='purple', linewidth=2.5)

ax4.set_ylim(-0.2, 1.3)
ax4.set_yticks([0, 1])
ax4.set_yticklabels(['Reposo', 'En Movimiento'])
ax4.set_xlabel("Pasos de Tiempo Discretos (t)")
ax4.set_title("4. Desfase Temporal / Multiplexado\n(Desacoplamiento lógico por fases)")
ax4.grid(True, linestyle=':', alpha=0.6)
ax4.legend(loc='upper right')

plt.tight_layout()
plt.show()