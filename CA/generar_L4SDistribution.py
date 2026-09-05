import numpy as np

# Definición del dominio de la caja de 50x50x50m
paso = 10.0  # Espaciado de 10 metros entre discos
rango = np.arange(-20.0, 20.0 + paso, paso)  # [-20, -10, 0, 10, 20]

posiciones = []

for x in rango:
    for y in rango:
        for z in rango:
            posiciones.append((x, y, z))

# Guardar en el archivo L4SDistribution.txt
nombre_archivo = "L4SDistribution.txt"
with open(nombre_archivo, "w") as f:
    f.write(f"# Distribución en rejilla 3D cada {paso}m (Total: {len(posiciones)} discos)\n")
    for pos in posiciones:
        f.write(f"{pos[0]:.1f}, {pos[1]:.1f}, {pos[2]:.1f}\n")

print(f"Archivo '{nombre_archivo}' generado con éxito. Se crearon {len(posiciones)} discos en la rejilla.")