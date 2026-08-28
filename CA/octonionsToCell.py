# =============================================================================
# Code Author / Maintainer: 
#   Pau Fonseca i Casas, Ph.D. <pau@fib.upc.edu>
#   Universitat Politècnica de Catalunya
#   Dept. Statistics and Operations Research
# 
# This code is part of Theory-5, developed by:
#   Jorge Luis Silva de Barcellos
#   Pau Fonseca i Casas, Ph.D.
#
# Extension: Complete Octonion & Quaternion Subalgebra Projection Analysis
# =============================================================================

import itertools
import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial import ConvexHull
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

# Plano de Fano: 7 tríadas orientadas de los octoniones
FANO_TRIPLETS = [
    (1, 2, 3), (1, 4, 5), (1, 7, 6),
    (2, 4, 6), (2, 5, 7), (3, 4, 7), (3, 6, 5)
]

def octonion_multiply(a, b):
    """
    Producto exacto de dos octoniones a y b en R^8.
    """
    res = np.zeros(8)
    res[0] = a[0] * b[0] - np.dot(a[1:], b[1:])
    res[1:] = a[0] * b[1:] + b[0] * a[1:]
    
    for i, j, k in FANO_TRIPLETS:
        res[k] += a[i] * b[j] - a[j] * b[i]
        res[i] += a[j] * b[k] - a[k] * b[j]
        res[j] += a[k] * b[i] - a[i] * b[k]
        
    return res

def generate_octonion_points(proj_type):
    """
    Genera los puntos proyectados según la configuración seleccionada.
    """
    base_range = np.array([-1, 0, 1])
    
    if proj_type == 1:
        # SUBÁLGEBRA CUATERNIÓNICA PURA H (e0..e3 activa, e4..e7 = 0) -> EXACTAMENTE 14 VÉRTICES
        grid_4d = np.array(list(itertools.product(base_range, repeat=4)))
        grid = np.zeros((len(grid_4d), 8))
        grid[:, :4] = grid_4d
    else:
        # GRILLA OCTONIÓNICA COMPLETA O (8D)
        grid = np.array(list(itertools.product(base_range, repeat=8)))
        
    # Filtrar vector nulo y acotar norma
    norms = np.linalg.norm(grid, axis=1)
    grid = grid[(norms > 0) & (norms <= 2)]
    
    # Producto de todos los pares únicos
    products = []
    n = len(grid)
    for i in range(n):
        for j in range(i, n):
            prod = octonion_multiply(grid[i], grid[j])
            products.append(prod[1:]) # Extraer parte imaginaria 7D
            
    pts_7d = np.unique(np.array(products), axis=0)
    
    if proj_type in [1, 2]:
        # Proyección directa sobre e1, e2, e3
        pts_3d = pts_7d[:, :3]
    else:
        # Proyección Ortogonal PCA / SVD de 7D a 3D
        pts_centered = pts_7d - np.mean(pts_7d, axis=0)
        u, s, vh = np.linalg.svd(pts_centered, full_matrices=False)
        pts_3d = np.dot(pts_centered, vh[:3].T)
        
    return np.unique(np.round(pts_3d, decimals=5), axis=0)

def plot_octonion_polyhedron(points, proj_type):
    try:
        hull = ConvexHull(points, qhull_options="QJ")
    except Exception:
        hull = ConvexHull(points)
    
    n_vtx = len(hull.vertices)
    n_facets = len(hull.simplices)
    n_edges = n_vtx + n_facets - 2
    
    fig = plt.figure(figsize=(11, 9))
    ax = fig.add_subplot(111, projection='3d')
    
    if proj_type == 1:
        title = "Opción 1: Subálgebra Cuaterniónica Pura H (e1, e2, e3)"
        poly_name = "Dodecaedro Rómbico (Dual del Cuboctaedro)"
        c_pts, c_vtx, c_face = 'navy', 'red', 'mediumpurple'
        xl, yl, zl = 'e1', 'e2', 'e3'
    elif proj_type == 2:
        title = "Opción 2: Grilla Octoniónica Completa O (e1, e2, e3)"
        poly_name = "Politopo Octoniónico Global Proyectado"
        c_pts, c_vtx, c_face = 'darkgreen', 'crimson', 'lightgreen'
        xl, yl, zl = 'e1', 'e2', 'e3'
    else:
        title = "Opción 3: Grilla Octoniónica Completa O (Ortogonal PCA / SVD)"
        poly_name = "Envolvente Espectral de Máxima Varianza"
        c_pts, c_vtx, c_face = 'teal', 'darkorange', 'gold'
        xl, yl, zl = 'PC 1', 'PC 2', 'PC 3'

    # Puntos internos
    ax.scatter(points[:, 0], points[:, 1], points[:, 2], 
               c=c_pts, s=15, alpha=0.3, label='Productos Octoniónicos')
    
    # Vértices exteriores
    outer_vtx = points[hull.vertices]
    ax.scatter(outer_vtx[:, 0], outer_vtx[:, 1], outer_vtx[:, 2], 
               c=c_vtx, s=60, zorder=5, label=f'Vértices Exteriores ({n_vtx})')
    
    # Caras
    faces = [points[simplex] for simplex in hull.simplices]
    poly_collection = Poly3DCollection(
        faces, facecolors=c_face, edgecolors='black', linewidths=0.5, alpha=0.45
    )
    ax.add_collection3d(poly_collection)

    ax.set_title(f"{title}\n{poly_name}\nVértices: {n_vtx} | Aristas: {n_edges} | Caras: {n_facets}", 
                 fontsize=11, fontweight='bold')
    ax.set_xlabel(xl)
    ax.set_ylabel(yl)
    ax.set_zlabel(zl)
    
    # Panel Informativo
    info = (
        "ANÁLISIS DE TEORÍA-5 DE OCTONIONES:\n"
        f"• Vértices Exteriores (V): {n_vtx}\n"
        f"• Caras (F): {n_facets}\n"
        f"• Aristas Deducidas (E = V+F-2): {n_edges}\n"
        "_________________________________________\n\n"
        "AUTORÍA Y MANTENIMIENTO:\n"
        "• Pau Fonseca i Casas, Ph.D. <pau@fib.upc.edu>\n"
        "• Universitat Politècnica de Catalunya (UPC)\n"
        "• Dept. de Estadística e Investigación Operativa\n"
        "• Theory-5: J. L. Silva de Barcellos & P. Fonseca i Casas\n"
        "_________________________________________\n\n"
        "REFERENCIA TEÓRICA:\n"
        "• O'Neill, C. C. (2019).\n"
        "  Dimensional Gate Quaternion Multiplication."
    )
    
    fig.text(0.02, 0.96, info, fontsize=8, verticalalignment='top',
             bbox=dict(boxstyle='round,pad=0.5', facecolor='white', edgecolor='gray', alpha=0.85))

    ax.legend(loc='upper right')
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    print("="*65)
    print("       OCTONION POLYHEDRON 3D GENERATOR (THEORY-5)")
    print("="*65)
    print("Seleccione el análisis proyectivo deseado:")
    print("  [1] Subálgebra Cuaterniónica H (e0..e3 -> 14 Vértices exactos)")
    print("  [2] Octoniones Completo O en (e1, e2, e3) -> 74 Vértices exactos")
    print("  [3] Octoniones Completo O con PCA / SVD (7D -> 3D)")
    print("="*65)
    
    choice = input("Selección (1, 2 o 3): ").strip()
    proj = int(choice) if choice in ['1', '2', '3'] else 2
    
    print("\nEjecutando cálculo del producto...")
    pts = generate_octonion_points(proj_type=proj)
    plot_octonion_polyhedron(pts, proj_type=proj)