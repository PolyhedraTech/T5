import numpy as np

nombre_archivo = "L4SDistribution.txt"

# La caja de 50x50x50m va de -25m a +25m
# Definimos el paso base de 10m y el desfase de 5m
paso = 10.0
desfase = 5.0

posiciones = []

# Filas a lo largo de Y y Z
y_niveles = np.arange(-20.0, 20.0 + paso, paso)
z_niveles = np.arange(-20.0, 20.0 + paso, paso)

for j, y in enumerate(y_niveles):
    for k, z in enumerate(z_niveles):
        # Alternamos el desplazamiento en X según la fila/plano actual
        # Las filas pares usan (0, 10, 20...), las impares usan (5, 15, 25...)
        shift = desfase if (j + k) % 2 != 0 else 0.0
        
        # Rango en X de -20 a 20 ajustado por el desfase
        x_base = np.arange(-20.0, 20.0 + paso, paso)
        x_fila = x_base + shift
        
        for x in x_fila:
            # Mantener los discos estrictamente dentro del volumen de la caja (±25m)
            if -25.0 <= x <= 25.0:
                posiciones.append((x, y, z))

# Guardar en L4SDistribution.txt
with open(nombre_archivo, "w") as f:
    f.write(f"# Distribución entrelazada tipo roca de sal (Estructura iónica alternada)\n")
    f.write(f"# Filas pares: [-20, -10, 0, 10, 20] | Filas impares: [-15, -5, 5, 15, 25]\n")
    for pos in posiciones:
        f.write(f"{pos[0]:.1f}, {pos[1]:.1f}, {pos[2]:.1f}\n")

print(f"Archivo '{nombre_archivo}' generado con {len(posiciones)} discos entrelazados.")