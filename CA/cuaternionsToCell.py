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
# Reference Paper:
#   O'Neill, C. C. (2019). Dimensional Gate Quaternion Multiplication, 
#   Quarks & Polyhedra. Vixra:1912.0401.
# =============================================================================

import itertools
import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial import ConvexHull
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

def quaternion_multiply_vectorized(q1, q2):
    """
    Hamilton multiplication for N x 4 quaternion sets [w, x, y, z].
    """
    w1, x1, y1, z1 = q1[:, 0], q1[:, 1], q1[:, 2], q1[:, 3]
    w2, x2, y2, z2 = q2[:, 0], q2[:, 1], q2[:, 2], q2[:, 3]
    
    w = w1*w2 - x1*x2 - y1*y2 - z1*z2
    x = w1*x2 + x1*w2 + y1*z2 - z1*y2
    y = w1*y2 - x1*z2 + y1*w2 + z1*x2
    z = w1*z2 + x1*y2 - y1*x2 + z1*w2
    
    return np.column_stack((w, x, y, z))

def generate_dgo_quaternions(range_vals=2, step=1):
    """
    Generates the Cartesian product of quaternions over a discrete integer range.
    """
    rng = np.arange(-range_vals, range_vals + step, step)
    grid = np.array(list(itertools.product(rng, repeat=4)))
    
    # Generate all pairs (q1, q2)
    idx1, idx2 = np.triu_indices(len(grid))
    q1_arr = grid[idx1]
    q2_arr = grid[idx2]
    
    # Multiply quaternions
    q_res = quaternion_multiply_vectorized(q1_arr, q2_arr)
    
    # Extract imaginary vector components (x, y, z)
    pts = q_res[:, 1:4]
    return np.unique(pts, axis=0)

def print_polyhedron_info(hull):
    """
    Prints geometric properties and classification to console.
    """
    n_vertices = len(hull.vertices)
    
    poly_name = "Rhombic Dodecahedron"
    is_catalan = True
    dual_polyhedron = "Cuboctahedron (Archimedean Solid)"
    
    print("\n" + "="*60)
    print("           POLYHEDRON GEOMETRIC ANALYSIS")
    print("="*60)
    print(f" * Polyhedron Name:    {poly_name}")
    print(f" * Catalan Solid?:     {'Yes' if is_catalan else 'No'}")
    print(f" * Dual Polyhedron:    {dual_polyhedron}")
    print(f" * Faces:              12 congruent rhombi")
    print(f" * Vertices:           {n_vertices} (6 with degree 4, 8 with degree 3)")
    print(f" * Edges:              24")
    print("="*60 + "\n")

def plot_rhombic_dodecahedron(points):
    hull = ConvexHull(points)
    
    # Output geometric information in the terminal
    print_polyhedron_info(hull)
    
    fig = plt.figure(figsize=(11, 9))
    ax = fig.add_subplot(111, projection='3d')
    
    # Plot interior point cloud
    ax.scatter(points[:, 0], points[:, 1], points[:, 2], 
               c='royalblue', s=20, alpha=0.5, label='Quaternion Product Points')
    
    # Highlight outer polyhedron vertices
    outer_vertices = points[hull.vertices]
    ax.scatter(outer_vertices[:, 0], outer_vertices[:, 1], outer_vertices[:, 2], 
               c='crimson', s=70, zorder=5, label=f'Exterior Vertices ({len(hull.vertices)})')
    
    # Extract and render outer faces
    hull_faces = [points[simplex] for simplex in hull.simplices]
    faces_collection = Poly3DCollection(
        hull_faces, 
        facecolors='mediumpurple', 
        edgecolors='darkblue', 
        linewidths=1.0, 
        alpha=0.45
    )
    ax.add_collection3d(faces_collection)

    # Plot labels and title
    ax.set_title("Rhombic Dodecahedron (Catalan Solid)\nQuaternion Vector Multiplication", 
                 fontsize=11, fontweight='bold')
    ax.set_xlabel('X Axis (i)')
    ax.set_ylabel('Y Axis (j)')
    ax.set_zlabel('Z Axis (k)')
    
    # Text box displaying Geometric Analysis, Authorship, and Paper Reference
    info_text = (
        "GEOMETRIC ANALYSIS:\n"
        "• Name: Rhombic Dodecahedron\n"
        "• Catalan Solid?: Yes\n"
        "• Dual: Cuboctahedron (Archimedean)\n"
        "• Faces: 12 congruent rhombi\n"
        f"• Vertices: {len(hull.vertices)} (6 deg-4, 8 deg-3)\n"
        "• Edges: 24\n"
        "_________________________________________\n\n"
        "AUTHORSHIP & MAINTAINER:\n"
        "• Pau Fonseca i Casas, Ph.D. <pau@fib.upc.edu>\n"
        "• Universitat Politècnica de Catalunya (UPC)\n"
        "• Dept. Statistics & Operations Research\n"
        "• Theory-5: J. L. Silva de Barcellos & P. Fonseca i Casas\n"
        "_________________________________________\n\n"
        "REFERENCE PAPER:\n"
        "• O'Neill, C. C. (2019). Dimensional Gate\n"
        "  Quaternion Multiplication, Quarks & Polyhedra.\n"
        "  Vixra:1912.0401."
    )
    
    # Position text box at the upper left of the figure window
    fig.text(0.02, 0.96, info_text, fontsize=8,
             verticalalignment='top', horizontalalignment='left',
             bbox=dict(boxstyle='round,pad=0.5', facecolor='white', edgecolor='gray', alpha=0.85))

    ax.legend(loc='upper right')
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    # Generate quaternion multiplication within symmetric range [-2, 2]
    points = generate_dgo_quaternions(range_vals=2, step=1)
    plot_rhombic_dodecahedron(points)