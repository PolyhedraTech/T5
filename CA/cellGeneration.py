import numpy as np
import pyvista as pv

def generar_maxima_presion_dodecaedro():
    # 1. Malla 3D de 50x50x50 metros
    L = 50.0
    puntos = 100
    x = np.linspace(-L/2, L/2, puntos)
    y = np.linspace(-L/2, L/2, puntos)
    z = np.linspace(-L/2, L/2, puntos)
    X, Y, Z = np.meshgrid(x, y, z, indexing='ij')

    # Frecuencia para escalar 1 celda completa en el centro
    k = (2.0 * np.pi) / 25.0 

    # 12 Direcciones de la red FCC
    k_vecs = [
        np.array([ 1,  1,  0]), np.array([ 1, -1,  0]), np.array([-1,  1,  0]), np.array([-1, -1,  0]),
        np.array([ 1,  0,  1]), np.array([ 1,  0, -1]), np.array([-1,  0,  1]), np.array([-1,  0, -1]),
        np.array([ 0,  1,  1]), np.array([ 0,  1, -1]), np.array([ 0, -1,  1]), np.array([ 0, -1, -1]),
    ]

    # 2. Campo de Presión: INVERSIÓN DE SIGNO (-cos)
    # Al usar -cos(), los máximos de presión se mueven a las fronteras inter-vórtice (Remanso)
    P_campo = np.zeros_like(X)
    for vec in k_vecs:
        P_campo -= np.cos(k * (vec[0]*X + vec[1]*Y + vec[2]*Z))

    # Mapeo a presión física
    P_base = 101325.0
    dP = 1000.0
    P_estatica = P_base + dP * (P_campo / 12.0)

    # 3. Crear Malla ImageData
    grid = pv.ImageData()
    grid.dimensions = (puntos, puntos, puntos)
    grid.origin = (-L/2, -L/2, -L/2)
    grid.spacing = (L/(puntos-1), L/(puntos-1), L/(puntos-1))
    grid.point_data["Presion (Pa)"] = P_estatica.ravel(order='F')

    p_min = np.min(P_estatica)
    p_max = np.max(P_estatica)

    # 4. VALOR DE CORTE PARA ALTA PRESIÓN (Paredes de Remanso)
    # Selecciona exactamente la cresta de presión continua entre nodos
    p_corte_maxima = p_min + 0.65 * (p_max - p_min)

    isosuperficie = grid.contour(isosurfaces=[p_corte_maxima], scalars="Presion (Pa)")

    # 5. Renderizado
    plotter = pv.Plotter()
    plotter.add_mesh(
        isosuperficie, 
        color="#E74C3C",          # Rojo / Máxima Presión
        opacity=0.75, 
        show_edges=True, 
        edge_color="black",
        line_width=1.2,
        smooth_shading=True
    )

    plotter.add_mesh(grid.outline(), color="white", opacity=0.3)
    plotter.show_axes()
    plotter.show()

if __name__ == "__main__":
    generar_maxima_presion_dodecaedro()