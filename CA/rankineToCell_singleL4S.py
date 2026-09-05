import sys
import numpy as np
import pyvista as pv
from pyvistaqt import BackgroundPlotter
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QComboBox, QDoubleSpinBox, QPushButton, QGroupBox
)

class SimuladorVorticeGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Simulador de Vórtices de Rankine 3D - Disco Mecánico")
        self.setGeometry(100, 100, 1300, 800)

        # Widget Principal y Layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)

        # Panel Izquierdo: Controles
        control_panel = self.crear_panel_control()
        main_layout.addWidget(control_panel, stretch=1)

        # Panel Derecho: Visor 3D PyVista
        self.plotter = BackgroundPlotter(show=False)
        main_layout.addWidget(self.plotter.interactor, stretch=4)

        # Ejecutar simulación inicial
        self.actualizar_simulacion()

    def crear_panel_control(self):
        group_box = QGroupBox("Parámetros del Sistema")
        layout = QVBoxLayout()

        # 1. Sentido Vórtice Superior
        layout.addWidget(QLabel("Sentido Vórtice Superior (Z > 0):"))
        self.combo_sup = QComboBox()
        self.combo_sup.addItems(["Antihorario (+1)", "Horario (-1)", "Apagado (0)"])
        layout.addWidget(self.combo_sup)

        # 2. Sentido Vórtice Inferior
        layout.addWidget(QLabel("Sentido Vórtice Inferior (Z < 0):"))
        self.combo_inf = QComboBox()
        self.combo_inf.addItems(["Horario (-1)", "Antihorario (+1)", "Apagado (0)"])
        layout.addWidget(self.combo_inf)

        # 3. Densidad del Fluido (kg/m³)
        layout.addWidget(QLabel("Densidad del Fluido (kg/m³):"))
        self.spin_densidad = QDoubleSpinBox()
        self.spin_densidad.setRange(0.1, 2000.0)
        self.spin_densidad.setValue(998.2)  # Agua
        self.spin_densidad.setSingleStep(10.0)
        layout.addWidget(self.spin_densidad)

        # 4. Velocidad Angular Máxima (rad/s)
        layout.addWidget(QLabel("Velocidad Angular Ω (rad/s):"))
        self.spin_omega = QDoubleSpinBox()
        self.spin_omega.setRange(0.1, 50.0)
        self.spin_omega.setValue(12.0)
        layout.addWidget(self.spin_omega)

        # 5. Radio del Núcleo del Vórtice (m)
        layout.addWidget(QLabel("Radio del Núcleo R_v (m):"))
        self.spin_radio = QDoubleSpinBox()
        self.spin_radio.setRange(0.05, 1.0)
        self.spin_radio.setValue(0.35)
        self.spin_radio.setSingleStep(0.05)
        layout.addWidget(self.spin_radio)

        layout.addStretch()

        # Botón de Ejecución
        btn_simular = QPushButton("Ejecutar Simulación")
        btn_simular.setStyleSheet("font-weight: bold; background-color: #007ACC; color: white; padding: 10px;")
        btn_simular.clicked.connect(self.actualizar_simulacion)
        layout.addWidget(btn_simular)

        group_box.setLayout(layout)
        return group_box

    def obtener_sentido(self, combo):
        texto = combo.currentText()
        if "Antihorario" in texto:
            return 1
        elif "Horario" in texto:
            return -1
        return 0

    def actualizar_simulacion(self):
        # 1. Limpieza de escena
        self.plotter.clear()
        self.plotter.set_background("#1e1e24")

        # 2. Lectura de parámetros
        sentido_sup = self.obtener_sentido(self.combo_sup)
        sentido_inf = self.obtener_sentido(self.combo_inf)
        densidad = self.spin_densidad.value()
        omega_max = self.spin_omega.value()
        radio_vortice = self.spin_radio.value()

        # 3. Renderizado del Disco (Diámetro 1m) y Caja (5x5x5m)
        disco = pv.Cylinder(center=(0, 0, 0), direction=(0, 0, 1), radius=0.5, height=0.02)
        self.plotter.add_mesh(disco, color="silver", metallic=0.8, roughness=0.2, show_edges=True)

        caja = pv.Box(bounds=[-2.5, 2.5, -2.5, 2.5, -2.5, 2.5])
        self.plotter.add_mesh(caja, color="white", style="wireframe", opacity=0.2)

        # 4. Generación Exacta Paramétrica de las Líneas de Vórtice (360° Completos)
        def generar_linea_vortice(r, z_base, sentido, n_vueltas=3, n_puntos=300):
            # Ecuación del perfil de velocidad de Rankine
            if r <= radio_vortice:
                v_theta = omega_max * r
            else:
                v_theta = (omega_max * (radio_vortice**2)) / r

            # Factor de atenuación vertical
            decaimiento_z = 1.2
            atenuacion = np.exp(-decaimiento_z * np.abs(z_base))
            v_theta_efectiva = v_theta * atenuacion

            # Ángulo azimutal de 0 a 2*PI * n_vueltas
            theta = np.linspace(0, 2 * np.pi * n_vueltas, n_puntos)
            if sentido == -1:
                theta = -theta  # Invierte el sentido del giro

            # Trayectoria helicoidal suave en 3D
            dz = 0.05 * np.sign(z_base) * (theta / (2 * np.pi))
            
            x = r * np.cos(theta)
            y = r * np.sin(theta)
            z = np.full_like(theta, z_base) + dz

            puntos = np.column_stack((x, y, z))
            
            # Crear malla de tipo PolyData para la curva
            num_pts = len(puntos)
            cells = np.hstack([[num_pts], np.arange(num_pts)])
            poly = pv.PolyData(puntos, lines=cells)
            
            # Asignar magnitud de velocidad a los puntos para el mapa de color
            velocidad_mag = np.full(num_pts, v_theta_efectiva)
            poly.point_data["Velocidad (m/s)"] = velocidad_mag
            
            return poly

        # Configuración de niveles verticales (Z) y radios (R)
        niveles_z_sup = [0.2, 0.7, 1.4] if sentido_sup != 0 else []
        niveles_z_inf = [-0.2, -0.7, -1.4] if sentido_inf != 0 else []
        radios_muestreo = [0.15, 0.35, 0.6, 1.0, 1.5]

        # Dibuja Vórtice Superior
        for z_val in niveles_z_sup:
            for r_val in radios_muestreo:
                linea = generar_linea_vortice(r_val, z_val, sentido_sup)
                tubo = linea.tube(radius=0.012)
                self.plotter.add_mesh(tubo, scalars="Velocidad (m/s)", cmap="turbo", clim=[0, omega_max * radio_vortice])

        # Dibuja Vórtice Inferior
        for z_val in niveles_z_inf:
            for r_val in radios_muestreo:
                linea = generar_linea_vortice(r_val, z_val, sentido_inf)
                tubo = linea.tube(radius=0.012)
                self.plotter.add_mesh(tubo, scalars="Velocidad (m/s)", cmap="turbo", clim=[0, omega_max * radio_vortice])

        # Anotaciones
        self.plotter.add_axes(line_width=3)
        self.plotter.add_text(
            f"Fluido: {densidad} kg/m³\nSup: {self.combo_sup.currentText()} | Inf: {self.combo_inf.currentText()}",
            position="upper_left", font_size=10, color="white"
        )

# ==============================================================================
# EJECUCIÓN
# ==============================================================================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SimuladorVorticeGUI()
    window.show()
    sys.exit(app.exec_())