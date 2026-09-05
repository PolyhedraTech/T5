import os
import sys
import numpy as np
import pyvista as pv
from pyvistaqt import BackgroundPlotter
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QComboBox, QDoubleSpinBox, QPushButton, QGroupBox, QSpinBox
)

# ==============================================================================
# CLASE ENCAPSULADA: DISCO MECÁNICO (SOPORTA ORIENTACIÓN 90°)
# ==============================================================================
class DiscoMecanico:
    def __init__(self, posicion=(0.0, 0.0, 0.0), radio_disco=0.5, radio_vortice=2.5, 
                 omega_max=12.0, sentido_sup=1, sentido_inf=-1, es_rotado_90=False):
        self.posicion = np.array(posicion, dtype=float)
        self.radio_disco = radio_disco
        self.radio_vortice = radio_vortice
        self.omega_max = omega_max
        self.sentido_sup = sentido_sup
        self.sentido_inf = sentido_inf
        self.decaimiento_z = 0.15
        self.es_rotado_90 = es_rotado_90  # True si está orientado a 90 grados (Eje normal X)

    def calcular_velocidad_en_puntos(self, X, Y, Z):
        # Transformación de coordenadas según la orientación del disco
        if not self.es_rotado_90:
            # Orientación Estándar (Eje Z como normal)
            X_loc = X - self.posicion[0]
            Y_loc = Y - self.posicion[1]
            Z_loc = Z - self.posicion[2]
        else:
            # Orientación Rotada 90° (Eje X como normal)
            X_loc = Y - self.posicion[1]
            Y_loc = Z - self.posicion[2]
            Z_loc = X - self.posicion[0]

        R = np.sqrt(X_loc**2 + Y_loc**2)
        R_safe = np.where(R == 0, 1e-6, R)
        Theta = np.arctan2(Y_loc, X_loc)

        V_theta_base = np.zeros_like(R)
        mask_core = R <= self.radio_vortice
        V_theta_base[mask_core] = self.omega_max * R[mask_core]
        
        mask_out = R > self.radio_vortice
        V_theta_base[mask_out] = (self.omega_max * (self.radio_vortice**2)) / R_safe[mask_out]

        atenuacion_z = np.exp(-self.decaimiento_z * np.abs(Z_loc))
        factor_rotacion = np.zeros_like(Z_loc)

        if self.sentido_sup != 0:
            factor_rotacion[Z_loc > 0] = self.sentido_sup * atenuacion_z[Z_loc > 0]
        if self.sentido_inf != 0:
            factor_rotacion[Z_loc < 0] = self.sentido_inf * atenuacion_z[Z_loc < 0]

        V_theta_final = V_theta_base * factor_rotacion

        Vx_loc = -V_theta_final * np.sin(Theta)
        Vy_loc =  V_theta_final * np.cos(Theta)
        
        Vz_loc = np.zeros_like(Vx_loc)
        factor_succion = 0.02 * self.omega_max
        if self.sentido_sup != 0:
            Vz_loc[Z_loc > 0] = -np.sign(Z_loc[Z_loc > 0]) * factor_succion * atenuacion_z[Z_loc > 0]
        if self.sentido_inf != 0:
            Vz_loc[Z_loc < 0] = -np.sign(Z_loc[Z_loc < 0]) * factor_succion * atenuacion_z[Z_loc < 0]

        # Re-proyección al sistema global si está rotado 90°
        if not self.es_rotado_90:
            return Vx_loc, Vy_loc, Vz_loc
        else:
            return Vz_loc, Vx_loc, Vy_loc

    def obtener_malla_geometria(self):
        direccion = (1, 0, 0) if self.es_rotado_90 else (0, 0, 1)
        return pv.Cylinder(center=self.posicion, direction=direccion, radius=self.radio_disco, height=0.1)


# ==============================================================================
# INTERFAZ GRÁFICA Y SIMULADOR
# ==============================================================================
class SimuladorMultidiscoGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Simulador Multidisco 3D - Mallas Cruzadas (0° y 90°)")
        self.setGeometry(50, 50, 1400, 850)

        self.archivo_config = "L4SDistribution.txt"
        self.discos_malla_A = []  # Discos Estándar (Gris)
        self.discos_malla_B = []  # Discos Rotados 90° (Naranja)
        self.actor_texto = None

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)

        control_panel = self.crear_panel_control()
        main_layout.addWidget(control_panel, stretch=1)

        self.plotter = BackgroundPlotter(show=False)
        main_layout.addWidget(self.plotter.interactor, stretch=4)

        self.cambiar_configuracion()

    def crear_panel_control(self):
        group_box = QGroupBox("Panel de Control")
        layout = QVBoxLayout()

        layout.addWidget(QLabel("Seleccionar Configuración:"))
        self.combo_distribucion = QComboBox()
        self.combo_distribucion.addItems([
            "Rejilla Regular (10m)",
            "Estructura Tipo Sal (Desfase 5m)"
        ])
        self.combo_distribucion.currentIndexChanged.connect(self.cambiar_configuracion)
        layout.addWidget(self.combo_distribucion)

        # ------------------ MALLA A (0° - GRIS) ------------------
        gb_a = QGroupBox("Malla A - Estándar 0° (Gris)")
        lay_a = QVBoxLayout()
        
        lay_a.addWidget(QLabel("Sentido Sup / Inf:"))
        h_a = QHBoxLayout()
        self.combo_sup_A = QComboBox()
        self.combo_sup_A.addItems(["Antihorario (+1)", "Horario (-1)", "Apagado (0)"])
        self.combo_inf_A = QComboBox()
        self.combo_inf_A.addItems(["Horario (-1)", "Antihorario (+1)", "Apagado (0)"])
        h_a.addWidget(self.combo_sup_A)
        h_a.addWidget(self.combo_inf_A)
        lay_a.addLayout(h_a)

        lay_a.addWidget(QLabel("Velocidad Angular Ω_A (rad/s):"))
        self.spin_omega_A = QDoubleSpinBox()
        self.spin_omega_A.setRange(0.1, 50.0)
        self.spin_omega_A.setValue(12.0)
        lay_a.addWidget(self.spin_omega_A)
        gb_a.setLayout(lay_a)
        layout.addWidget(gb_a)

        # ------------------ MALLA B (90° - NARANJA) ------------------
        gb_b = QGroupBox("Malla B - Rotada 90° (Naranja)")
        lay_b = QVBoxLayout()

        lay_b.addWidget(QLabel("Sentido Sup / Inf:"))
        h_b = QHBoxLayout()
        self.combo_sup_B = QComboBox()
        self.combo_sup_B.addItems(["Antihorario (+1)", "Horario (-1)", "Apagado (0)"])
        self.combo_inf_B = QComboBox()
        self.combo_inf_B.addItems(["Horario (-1)", "Antihorario (+1)", "Apagado (0)"])
        h_b.addWidget(self.combo_sup_B)
        h_b.addWidget(self.combo_inf_B)
        lay_b.addLayout(h_b)

        lay_b.addWidget(QLabel("Velocidad Angular Ω_B (rad/s):"))
        self.spin_omega_B = QDoubleSpinBox()
        self.spin_omega_B.setRange(0.1, 50.0)
        self.spin_omega_B.setValue(12.0)
        lay_b.addWidget(self.spin_omega_B)
        gb_b.setLayout(lay_b)
        layout.addWidget(gb_b)

        # ------------------ PARÁMETROS GENERALES ------------------
        layout.addWidget(QLabel("Radio Núcleo Vórtices R_v (m):"))
        self.spin_radio_v = QDoubleSpinBox()
        self.spin_radio_v.setRange(0.5, 10.0)
        self.spin_radio_v.setValue(2.5)
        layout.addWidget(self.spin_radio_v)

        layout.addWidget(QLabel("Líneas Flujo / Radio Tubo:"))
        h_lineas = QHBoxLayout()
        self.spin_lineas_disco = QSpinBox()
        self.spin_lineas_disco.setRange(1, 12)
        self.spin_lineas_disco.setValue(2)
        self.spin_radio_tubo = QDoubleSpinBox()
        self.spin_radio_tubo.setRange(0.01, 0.5)
        self.spin_radio_tubo.setSingleStep(0.01)
        self.spin_radio_tubo.setValue(0.04)
        h_lineas.addWidget(self.spin_lineas_disco)
        h_lineas.addWidget(self.spin_radio_tubo)
        layout.addLayout(h_lineas)

        layout.addStretch()

        btn_simular = QPushButton("Calcular Simulación Completa")
        btn_simular.setStyleSheet("font-weight: bold; background-color: #007ACC; color: white; padding: 8px;")
        btn_simular.clicked.connect(self.ejecutar_simulacion)
        layout.addWidget(btn_simular)

        btn_simplify = QPushButton("Simplify (Flechas Inter-vórtice)")
        btn_simplify.setStyleSheet("font-weight: bold; background-color: #5CB85C; color: white; padding: 8px;")
        btn_simplify.clicked.connect(self.ejecutar_simplificacion)
        layout.addWidget(btn_simplify)

        btn_limpiar = QPushButton("Limpiar Malla")
        btn_limpiar.setStyleSheet("font-weight: bold; background-color: #D9534F; color: white; padding: 8px;")
        btn_limpiar.clicked.connect(self.mostrar_solo_configuracion)
        layout.addWidget(btn_limpiar)

        group_box.setLayout(layout)
        return group_box

    def actualizar_texto_info(self, texto):
        if self.actor_texto is not None:
            self.plotter.remove_actor(self.actor_texto)
        self.actor_texto = self.plotter.add_text(
            texto, position="upper_left", font_size=9, color="white", name="info_text"
        )

    def generar_archivo_rejilla_regular(self):
        paso = 10.0
        rango = np.arange(-20.0, 20.0 + paso, paso)
        posiciones = []
        for x in rango:
            for y in rango:
                for z in rango:
                    posiciones.append((x, y, z))

        with open(self.archivo_config, "w") as f:
            f.write("# Rejilla Regular 10m\n")
            for pos in posiciones:
                f.write(f"{pos[0]:.1f}, {pos[1]:.1f}, {pos[2]:.1f}\n")

    def generar_archivo_estructura_sal(self):
        paso = 10.0
        desfase = 5.0
        posiciones = []
        y_niveles = np.arange(-20.0, 20.0 + paso, paso)
        z_niveles = np.arange(-20.0, 20.0 + paso, paso)

        for j, y in enumerate(y_niveles):
            for k, z in enumerate(z_niveles):
                shift = desfase if (j + k) % 2 != 0 else 0.0
                x_fila = np.arange(-20.0, 20.0 + paso, paso) + shift
                for x in x_fila:
                    if -25.0 <= x <= 25.0:
                        posiciones.append((x, y, z))

        with open(self.archivo_config, "w") as f:
            f.write("# Estructura Tipo Sal (NaCl)\n")
            for pos in posiciones:
                f.write(f"{pos[0]:.1f}, {pos[1]:.1f}, {pos[2]:.1f}\n")

    def cargar_posiciones_desde_archivo(self):
        posiciones = []
        if os.path.exists(self.archivo_config):
            with open(self.archivo_config, "r") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        partes = line.split(",")
                        if len(partes) == 3:
                            try:
                                posiciones.append([float(p.strip()) for p in partes])
                            except ValueError:
                                continue
        return posiciones

    def cambiar_configuracion(self):
        opcion = self.combo_distribucion.currentIndex()
        if opcion == 0:
            self.generar_archivo_rejilla_regular()
        elif opcion == 1:
            self.generar_archivo_estructura_sal()

        self.mostrar_solo_configuracion()

    def obtener_sentido(self, combo):
        texto = combo.currentText()
        if "Antihorario" in texto:
            return 1
        elif "Horario" in texto:
            return -1
        return 0

    def instanciar_discos(self):
        posiciones_base = self.cargar_posiciones_desde_archivo()
        r_vortice = self.spin_radio_v.value()

        # Malla A (Discos Gris)
        sent_sup_A = self.obtener_sentido(self.combo_sup_A)
        sent_inf_A = self.obtener_sentido(self.combo_inf_A)
        omega_A = self.spin_omega_A.value()

        self.discos_malla_A = [
            DiscoMecanico(
                posicion=pos,
                radio_disco=0.5,
                radio_vortice=r_vortice,
                omega_max=omega_A,
                sentido_sup=sent_sup_A,
                sentido_inf=sent_inf_A,
                es_rotado_90=False
            )
            for pos in posiciones_base
        ]

        # Malla B (Discos Naranja - Ubicados en los huecos intermedios con desplazamiento de 5m)
        sent_sup_B = self.obtener_sentido(self.combo_sup_B)
        sent_inf_B = self.obtener_sentido(self.combo_inf_B)
        omega_B = self.spin_omega_B.value()

        offset = np.array([5.0, 5.0, 5.0])
        self.discos_malla_B = [
            DiscoMecanico(
                posicion=np.array(pos) + offset,
                radio_disco=0.5,
                radio_vortice=r_vortice,
                omega_max=omega_B,
                sentido_sup=sent_sup_B,
                sentido_inf=sent_inf_B,
                es_rotado_90=True
            )
            for pos in posiciones_base
            if np.all(np.abs(np.array(pos) + offset) <= 24.0)
        ]

    def obtener_todos_los_discos(self):
        return self.discos_malla_A + self.discos_malla_B

    def mostrar_solo_configuracion(self):
        """Limpia la escena y muestra la configuración dual (Gris y Naranja) sin simulación."""
        self.plotter.clear()
        self.actor_texto = None
        self.plotter.set_background("#18181c")

        self.instanciar_discos()

        caja = pv.Box(bounds=[-25.0, 25.0, -25.0, 25.0, -25.0, 25.0])
        self.plotter.add_mesh(caja, color="white", style="wireframe", opacity=0.15)

        # Malla A: Discos Grises
        if self.discos_malla_A:
            malla_A = pv.MultiBlock([d.obtener_malla_geometria() for d in self.discos_malla_A]).combine()
            self.plotter.add_mesh(malla_A, color="silver", opacity=0.85, label="Malla A (0°)")

        # Malla B: Discos Naranjas
        if self.discos_malla_B:
            malla_B = pv.MultiBlock([d.obtener_malla_geometria() for d in self.discos_malla_B]).combine()
            self.plotter.add_mesh(malla_B, color="orange", opacity=0.85, label="Malla B (90°)")

        self.plotter.add_axes(line_width=2)
        
        info_str = (
            f"Configuración: {self.combo_distribucion.currentText()}\n"
            f"Discos Malla A (Gris - 0°): {len(self.discos_malla_A)}\n"
            f"Discos Malla B (Naranja - 90°): {len(self.discos_malla_B)}\n"
            f"Total Discos en Escena: {len(self.obtener_todos_los_discos())}\n"
            f"--------------------------------------------------\n"
            f"Estado: [Sin simulación activa]"
        )
        self.actualizar_texto_info(info_str)

    def ejecutar_simulacion(self):
        self.mostrar_solo_configuracion()
        todos_los_discos = self.obtener_todos_los_discos()

        if not todos_los_discos:
            return

        lineas_por_disco = self.spin_lineas_disco.value()
        radio_tubo = self.spin_radio_tubo.value()

        L = 50.0
        puntos_malla = 32
        x = np.linspace(-L/2, L/2, puntos_malla)
        y = np.linspace(-L/2, L/2, puntos_malla)
        z = np.linspace(-L/2, L/2, puntos_malla)
        X, Y, Z = np.meshgrid(x, y, z, indexing='ij')

        Vx_total = np.zeros_like(X)
        Vy_total = np.zeros_like(Y)
        Vz_total = np.zeros_like(Z)

        for disco in todos_los_discos:
            vx, vy, vz = disco.calcular_velocidad_en_puntos(X, Y, Z)
            Vx_total += vx
            Vy_total += vy
            Vz_total += vz

        V_mag = np.sqrt(Vx_total**2 + Vy_total**2 + Vz_total**2)

        grid = pv.StructuredGrid(X, Y, Z)
        grid.point_data["Velocidad"] = np.column_stack((Vx_total.ravel(), Vy_total.ravel(), Vz_total.ravel()))
        grid.point_data["Magnitud (m/s)"] = V_mag.ravel()

        semillas_list = []
        for disco in todos_los_discos:
            angulos = np.linspace(0, 2 * np.pi, lineas_por_disco, endpoint=False)
            r_m = 1.5
            
            if not disco.es_rotado_90:
                if disco.sentido_sup != 0:
                    for th in angulos:
                        semillas_list.append([disco.posicion[0] + r_m * np.cos(th), disco.posicion[1] + r_m * np.sin(th), disco.posicion[2] + 1.0])
                if disco.sentido_inf != 0:
                    for th in angulos:
                        semillas_list.append([disco.posicion[0] + r_m * np.cos(th), disco.posicion[1] + r_m * np.sin(th), disco.posicion[2] - 1.0])
            else:
                if disco.sentido_sup != 0:
                    for th in angulos:
                        semillas_list.append([disco.posicion[0] + 1.0, disco.posicion[1] + r_m * np.cos(th), disco.posicion[2] + r_m * np.sin(th)])
                if disco.sentido_inf != 0:
                    for th in angulos:
                        semillas_list.append([disco.posicion[0] - 1.0, disco.posicion[1] + r_m * np.cos(th), disco.posicion[2] + r_m * np.sin(th)])

        if semillas_list:
            puntos_semilla = pv.PolyData(np.array(semillas_list))
            streamlines = grid.streamlines_from_source(
                puntos_semilla,
                vectors="Velocidad",
                max_length=40.0,
                initial_step_length=0.02,
                integration_direction="both",
                integrator_type=45
            )

            self.plotter.add_mesh(
                streamlines.tube(radius=radio_tubo),
                scalars="Magnitud (m/s)",
                cmap="turbo",
                opacity=0.75
            )

        info_str = (
            f"SIMULACIÓN COMPLETA - MALLA DOBLE:\n"
            f"• Discos Gris (0°): {len(self.discos_malla_A)} | Ω = {self.spin_omega_A.value()} rad/s\n"
            f"• Discos Naranja (90°): {len(self.discos_malla_B)} | Ω = {self.spin_omega_B.value()} rad/s\n"
            f"--------------------------------------------------\n"
            f"Escala Color: Azul (baja velocidad) -> Rojo (alta velocidad)."
        )
        self.actualizar_texto_info(info_str)

    def ejecutar_simplificacion(self):
        """Modo 'SIMPLIFY': Vectores direccionales entre vórtices adyacentes."""
        self.mostrar_solo_configuracion()
        todos_los_discos = self.obtener_todos_los_discos()

        if not todos_los_discos:
            return

        puntos_origen = []
        vectores_direccion = []
        magnitudes = []

        pos_array = np.array([disco.posicion for disco in todos_los_discos])
        n_discos = len(todos_los_discos)

        for i in range(n_discos):
            pos_i = pos_array[i]
            distancias = np.linalg.norm(pos_array - pos_i, axis=1)
            
            vecinos_idx = np.where((distancias > 0.1) & (distancias <= 12.0))[0]

            for idx_j in vecinos_idx:
                if i < idx_j:
                    pos_j = pos_array[idx_j]
                    p_medio = (pos_i + pos_j) / 2.0

                    vx_tot, vy_tot, vz_tot = 0.0, 0.0, 0.0
                    for disco in todos_los_discos:
                        vx, vy, vz = disco.calcular_velocidad_en_puntos(
                            np.array([p_medio[0]]), np.array([p_medio[1]]), np.array([p_medio[2]])
                        )
                        vx_tot += vx[0]
                        vy_tot += vy[0]
                        vz_tot += vz[0]

                    v_vec = np.array([vx_tot, vy_tot, vz_tot])
                    v_mag = np.linalg.norm(v_vec)

                    if v_mag > 0.05:
                        puntos_origen.append(p_medio)
                        vectores_direccion.append(v_vec / v_mag)
                        magnitudes.append(v_mag)

        if puntos_origen:
            pts = np.array(puntos_origen)
            vecs = np.array(vectores_direccion)
            mags = np.array(magnitudes)

            polydata = pv.PolyData(pts)
            polydata.point_data["Direccion"] = vecs
            polydata.point_data["Velocidad (m/s)"] = mags

            glifos_flechas = polydata.glyph(
                orient="Direccion",
                scale="Velocidad (m/s)",
                factor=0.8,
                geom=pv.Arrow(tip_length=0.35, tip_radius=0.15, shaft_radius=0.05)
            )

            self.plotter.add_mesh(
                glifos_flechas,
                scalars="Velocidad (m/s)",
                cmap="turbo",
                opacity=0.9
            )

        info_str = (
            f"MODO SIMPLIFICADO ('SIMPLIFY') - MALLA CRUZADA:\n"
            f"--------------------------------------------------\n"
            f"• Flechas Inter-vórtices: Calculadas en el espacio 3D resultante de ambas mallas.\n"
            f"• Tamaño y Color: Proporcionales a la velocidad combinada del campo de flujo."
        )
        self.actualizar_texto_info(info_str)


# ==============================================================================
# EJECUCIÓN
# ==============================================================================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SimuladorMultidiscoGUI()
    window.show()
    sys.exit(app.exec_())