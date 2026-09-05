import os
import sys
import numpy as np
import pyvista as pv
from pyvistaqt import BackgroundPlotter
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QComboBox, QDoubleSpinBox, QPushButton, QGroupBox
)

# ==============================================================================
# CLASE ENCAPSULADA: DISCO MECÁNICO
# ==============================================================================
class DiscoMecanico:
    """
    Representa un disco de 1m de diámetro situado en una posición 3D.
    """
    def __init__(self, posicion=(0.0, 0.0, 0.0), radio_disco=0.5, radio_vortice=3.0, 
                 omega_max=12.0, sentido_sup=1, sentido_inf=-1):
        self.posicion = np.array(posicion, dtype=float)
        self.radio_disco = radio_disco
        self.radio_vortice = radio_vortice
        self.omega_max = omega_max
        self.sentido_sup = sentido_sup
        self.sentido_inf = sentido_inf
        self.decaimiento_z = 0.12  # Atenuación vertical

    def calcular_velocidad_en_puntos(self, X, Y, Z):
        """Calcula el campo vectorial (Vx, Vy, Vz) inducido por este disco en una malla 3D."""
        X_loc = X - self.posicion[0]
        Y_loc = Y - self.posicion[1]
        Z_loc = Z - self.posicion[2]

        R = np.sqrt(X_loc**2 + Y_loc**2)
        R_safe = np.where(R == 0, 1e-6, R)
        Theta = np.arctan2(Y_loc, X_loc)

        # Perfil de Vórtice de Rankine
        V_theta_base = np.zeros_like(R)
        mask_core = R <= self.radio_vortice
        V_theta_base[mask_core] = self.omega_max * R[mask_core]
        
        mask_out = R > self.radio_vortice
        V_theta_base[mask_out] = (self.omega_max * (self.radio_vortice**2)) / R_safe[mask_out]

        # Sentidos de giro y atenuación en Z
        atenuacion_z = np.exp(-self.decaimiento_z * np.abs(Z_loc))
        factor_rotacion = np.zeros_like(Z_loc)

        if self.sentido_sup != 0:
            factor_rotacion[Z_loc > 0] = self.sentido_sup * atenuacion_z[Z_loc > 0]
        if self.sentido_inf != 0:
            factor_rotacion[Z_loc < 0] = self.sentido_inf * atenuacion_z[Z_loc < 0]

        V_theta_final = V_theta_base * factor_rotacion

        # Componentes Cartesianas de Velocidad
        Vx = -V_theta_final * np.sin(Theta)
        Vy =  V_theta_final * np.cos(Theta)
        
        # Leve componente axial de succión/expulsión para guiar numéricamente las trayectorias
        Vz = np.zeros_like(Vx)
        factor_succion = 0.03 * self.omega_max
        if self.sentido_sup != 0:
            Vz[Z_loc > 0] = -np.sign(Z_loc[Z_loc > 0]) * factor_succion * atenuacion_z[Z_loc > 0]
        if self.sentido_inf != 0:
            Vz[Z_loc < 0] = -np.sign(Z_loc[Z_loc < 0]) * factor_succion * atenuacion_z[Z_loc < 0]

        return Vx, Vy, Vz

    def obtener_malla_geometria(self):
        """Devuelve la geometría cilíndrica del disco."""
        return pv.Cylinder(center=self.posicion, direction=(0, 0, 1), radius=self.radio_disco, height=0.1)


# ==============================================================================
# INTERFAZ GRÁFICA Y SIMULADOR
# ==============================================================================
class SimuladorMultidiscoGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Simulador de Interferencia de Vórtices - Carga desde Archivo")
        self.setGeometry(100, 100, 1300, 800)

        self.archivo_config = "L4SDistribution.txt"

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)

        # Panel de Controles Generales
        control_panel = self.crear_panel_control()
        main_layout.addWidget(control_panel, stretch=1)

        # Visor PyVista
        self.plotter = BackgroundPlotter(show=False)
        main_layout.addWidget(self.plotter.interactor, stretch=4)

        self.actualizar_simulacion()

    def crear_panel_control(self):
        group_box = QGroupBox("Configuración Global de Discos")
        layout = QVBoxLayout()

        # Configuración compartida por todos los discos
        layout.addWidget(QLabel("Sentido Vórtice Superior:"))
        self.combo_sup = QComboBox()
        self.combo_sup.addItems(["Antihorario (+1)", "Horario (-1)", "Apagado (0)"])
        layout.addWidget(self.combo_sup)

        layout.addWidget(QLabel("Sentido Vórtice Inferior:"))
        self.combo_inf = QComboBox()
        self.combo_inf.addItems(["Horario (-1)", "Antihorario (+1)", "Apagado (0)"])
        layout.addWidget(self.combo_inf)

        layout.addWidget(QLabel("Velocidad Angular Ω (rad/s):"))
        self.spin_omega = QDoubleSpinBox()
        self.spin_omega.setRange(0.1, 50.0)
        self.spin_omega.setValue(12.0)
        layout.addWidget(self.spin_omega)

        layout.addWidget(QLabel("Radio del Núcleo R_v (m):"))
        self.spin_radio_v = QDoubleSpinBox()
        self.spin_radio_v.setRange(0.5, 10.0)
        self.spin_radio_v.setValue(3.0)
        layout.addWidget(self.spin_radio_v)

        layout.addWidget(QLabel("Densidad del Fluido (kg/m³):"))
        self.spin_densidad = QDoubleSpinBox()
        self.spin_densidad.setRange(0.1, 2000.0)
        self.spin_densidad.setValue(998.2)
        layout.addWidget(self.spin_densidad)

        layout.addStretch()

        btn_simular = QPushButton("Recargar Archivo y Simular")
        btn_simular.setStyleSheet("font-weight: bold; background-color: #007ACC; color: white; padding: 10px;")
        btn_simular.clicked.connect(self.actualizar_simulacion)
        layout.addWidget(btn_simular)

        group_box.setLayout(layout)
        return group_box

    def cargar_posiciones_desde_archivo(self):
        """Lee el archivo L4SDistribution.txt y extrae las coordenadas 3D."""
        posiciones = []
        if not os.path.exists(self.archivo_config):
            # Si no existe, genera un archivo por defecto con 2 discos
            with open(self.archivo_config, "w") as f:
                f.write("# Archivo de distribución de discos (X, Y, Z)\n")
                f.write("10.0, 10.0, 10.0\n")
                f.write("20.0, 20.0, 20.0\n")

        with open(self.archivo_config, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    partes = line.split(",")
                    if len(partes) == 3:
                        try:
                            coords = [float(p.strip()) for p in partes]
                            posiciones.append(coords)
                        except ValueError:
                            continue
        return posiciones

    def obtener_sentido(self, combo):
        texto = combo.currentText()
        if "Antihorario" in texto:
            return 1
        elif "Horario" in texto:
            return -1
        return 0

    def actualizar_simulacion(self):
        self.plotter.clear()
        self.plotter.set_background("#1e1e24")

        # Cargar posiciones desde el archivo
        posiciones_discos = self.cargar_posiciones_desde_archivo()
        if not posiciones_discos:
            posiciones_discos = [[10.0, 10.0, 10.0]]  # Fallback

        sent_sup = self.obtener_sentido(self.combo_sup)
        sent_inf = self.obtener_sentido(self.combo_inf)
        omega = self.spin_omega.value()
        r_vortice = self.spin_radio_v.value()
        densidad = self.spin_densidad.value()

        # Instanciar lista de discos
        discos = [
            DiscoMecanico(
                posicion=pos,
                radio_disco=0.5,
                radio_vortice=r_vortice,
                omega_max=omega,
                sentido_sup=sent_sup,
                sentido_inf=sent_inf
            )
            for pos in posiciones_discos
        ]

        # Configurar Dominio (Caja 50x50x50m centrada en el origen)
        L = 50.0
        puntos_malla = 40  # Resolución del volumen de simulación
        x = np.linspace(-L/2, L/2, puntos_malla)
        y = np.linspace(-L/2, L/2, puntos_malla)
        z = np.linspace(-L/2, L/2, puntos_malla)
        X, Y, Z = np.meshgrid(x, y, z, indexing='ij')

        # Acumular la superposición lineal de campos vectoriales: V_total = SUM(V_i)
        Vx_total = np.zeros_like(X)
        Vy_total = np.zeros_like(Y)
        Vz_total = np.zeros_like(Z)

        for disco in discos:
            vx, vy, vz = disco.calcular_velocidad_en_puntos(X, Y, Z)
            Vx_total += vx
            Vy_total += vy
            Vz_total += vz

        V_mag = np.sqrt(Vx_total**2 + Vy_total**2 + Vz_total**2)

        # Crear Malla Estructurada
        grid = pv.StructuredGrid(X, Y, Z)
        grid.point_data["Velocidad"] = np.column_stack((Vx_total.ravel(), Vy_total.ravel(), Vz_total.ravel()))
        grid.point_data["Magnitud (m/s)"] = V_mag.ravel()

        # Renderizar la Caja del Dominio
        caja = pv.Box(bounds=[-25.0, 25.0, -25.0, 25.0, -25.0, 25.0])
        self.plotter.add_mesh(caja, color="white", style="wireframe", opacity=0.2)

        # Renderizar cada Disco físico y sembrar sus puntos de origen para las líneas
        semillas_list = []
        for disco in discos:
            malla_disco = disco.obtener_malla_geometria()
            self.plotter.add_mesh(malla_disco, color="silver", metallic=0.8, roughness=0.2, show_edges=True)

            # Sembrar puntos alrededor de cada disco para capturar las deformaciones de flujo
            r_vals = [0.8, 2.0, 4.0]
            if disco.sentido_sup != 0:
                for z_h in [1.0, 3.0]:
                    for r_i in r_vals:
                        for th in np.linspace(0, 2*np.pi, 6, endpoint=False):
                            semillas_list.append([
                                disco.posicion[0] + r_i * np.cos(th),
                                disco.posicion[1] + r_i * np.sin(th),
                                disco.posicion[2] + z_h
                            ])
            if disco.sentido_inf != 0:
                for z_h in [-1.0, -3.0]:
                    for r_i in r_vals:
                        for th in np.linspace(0, 2*np.pi, 6, endpoint=False):
                            semillas_list.append([
                                disco.posicion[0] + r_i * np.cos(th),
                                disco.posicion[1] + r_i * np.sin(th),
                                disco.posicion[2] + z_h
                            ])

        # Integrar las líneas de corriente a partir del campo total superpuesto
        if semillas_list:
            puntos_semilla = pv.PolyData(np.array(semillas_list))
            streamlines = grid.streamlines_from_source(
                puntos_semilla,
                vectors="Velocidad",
                max_length=60.0,
                initial_step_length=0.01,
                integration_direction="both",
                integrator_type=45
            )

            self.plotter.add_mesh(
                streamlines.tube(radius=0.08),
                scalars="Magnitud (m/s)",
                cmap="turbo",
                opacity=0.85
            )

        # Anotaciones
        self.plotter.add_axes(line_width=3)
        self.plotter.add_text(
            f"Discos Cargados: {len(discos)}\nArchivo: {self.archivo_config}",
            position="upper_left", font_size=10, color="white"
        )

# ==============================================================================
# EJECUCIÓN
# ==============================================================================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SimuladorMultidiscoGUI()
    window.show()
    sys.exit(app.exec_())