import csv
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import tempfile, os, io
from tinydb import Query
from mechanism import Mechanism, Joint, Link
from kinematics_simulator import KinematicsSimulator
from solid import *
from solid.utils import * 

def load_mechanism_from_db(mechanismName):
    # Lade alle Gelenke für den Mechanismus
    joints = Mechanism.find_joints_by_mechanism(mechanismName)
    #print(f"[DEBUG] Geladene Gelenke für '{mechanismName}':")
    for joint in joints:
        print(f"  - {joint}")

    # Lade alle Links für den Mechanismus
    links = Mechanism.find_links_by_mechanism(mechanismName)
    #print(f"[DEBUG] Geladene Links für '{mechanismName}':")
    for link in links:
        print(f"  - {link}")
    
    for link in links:
        if link.length is None:
            link.initialize_self_lenght()

    # Lade den gespeicherten driven_angle
    driven_angle = Mechanism.find_driven_angle_by_mechanism(mechanismName)
    #print(f"[DEBUG] Geladener driven_angle für '{mechanismName}': {driven_angle}")

    # Erzeuge und gib den Mechanismus zurück
    return Mechanism(name=mechanismName, joints=joints, links=links, angle=driven_angle)


class SimulationManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(SimulationManager, cls).__new__(cls)
        return cls._instance

    def __init__(self, mechanismName:str ):
        # Statt FourBarLinkage.create_default() laden wir den Mechanismus aus der DB.
        #self.mechanism = FourBarLinkage.create_default()  # Statische Fabrikmethode, siehe unten
        self.mechanism = Mechanism.find_mech_by_name(mechanismName)
        print(f"Debug Mechanism: {self.mechanism.joints}")
        #for joint in self.mechanism.joints:
        #    print(f"Joint {joint.name}: is_fixed={joint.is_fixed}, on_circular_path={joint.on_circular_path}, initial pos=({joint.x}, {joint.y
        self.simulator = KinematicsSimulator(self.mechanism)
        print("...KinematicsSimulator erstellt!")  # Debug
        self.trajectories = {joint.name: [] for joint in self.mechanism.joints}


    def simulate_over_360(self, num_steps=36):
        """
        Berechnet die Kinematik für Winkel im Bereich von driven_angle bis driven_angle + 360°.
        Dabei werden die Trajektorien für alle Gelenke neu aufgebaut.
        """
        # Trajektorien zurücksetzen
        self.trajectories = {joint.name: [] for joint in self.mechanism.joints}

        # Starte mit dem aktuellen driven_angle als Ausgangswert
        initial_angle = self.mechanism.driven_angle
        angles = np.linspace(initial_angle, initial_angle + 2 * np.pi, num_steps)

        for theta in angles:
            self.mechanism.driven_angle = theta
            # Aktualisiere das getriebene Gelenk
            self.simulator.update_driven_joint()
            # Optimiere die freien Gelenke
            self.simulator.optimize()
            # Speichere die aktuelle Position aller Gelenke
            for joint in self.mechanism.joints:
                self.trajectories[joint.name].append((joint.x, joint.y))
            # (Optional) Debug: Überprüfe, ob sich die Positionen ändern
            # print(f"Angle: {theta:.2f}, Positions: {[ (j.name, j.x, j.y) for j in self.mechanism.joints ]}")
        #print("[DEBUG] Trajoktorieren", self.trajectories)
        return angles

    def create_animation(self):
        """
        Erzeugt eine GIF-Animation, in der in jedem Frame der aktuelle Mechanismus dargestellt wird.
        Die globalen Achsen werden dynamisch anhand aller gespeicherten Trajektorien berechnet.
        Die Animation wird in einer temporären Datei gespeichert und anschließend in einen BytesIO-Puffer geladen.
        """
        n_frames = len(next(iter(self.trajectories.values())))

        # Berechne globale Achsen-Grenzen aus allen Trajektorien
        all_x = []
        all_y = []
        for traj in self.trajectories.values():
            for (x, y) in traj:
                all_x.append(x)
                all_y.append(y)
        margin = 10  # Zusätzlicher Rand
        x_min, x_max = min(all_x) - margin, max(all_x) + margin
        y_min, y_max = min(all_y) - margin, max(all_y) + margin

        fig, ax = plt.subplots(figsize=(10, 10))

        def update(frame):
            ax.clear()
            # Zeichne für jeden Link eine Linie zwischen den verbundenen Gelenken
            for link in self.mechanism.links:
                pos_a = self.trajectories[link.joint_a.name][frame]
                pos_b = self.trajectories[link.joint_b.name][frame]
                ax.plot([pos_a[0], pos_b[0]], [pos_a[1], pos_b[1]], 'ko-', lw=2)
            # Zeichne die bisherige Trajektorie für jedes Gelenk
            for joint_name, positions in self.trajectories.items():
                xs = [p[0] for p in positions[:frame+1]]
                ys = [p[1] for p in positions[:frame+1]]
                ax.plot(xs, ys, '-', label=f"Trajectory {joint_name}")
            ax.set_xlim(x_min, x_max)
            ax.set_ylim(y_min, y_max)
            ax.set_title(f"Frame {frame+1}/{n_frames}")
            ax.legend(loc='upper right')
            ax.grid(True)

        ani = animation.FuncAnimation(fig, update, frames=n_frames, repeat=False)

        import tempfile, os, io
        with tempfile.NamedTemporaryFile(suffix=".gif", delete=False) as tmp:
            temp_filename = tmp.name
        ani.save(temp_filename, writer='pillow', fps=30)
        with open(temp_filename, "rb") as f:
            buf = io.BytesIO(f.read())
        os.remove(temp_filename)
        return buf

    def export_trajectories_to_csv(self):
        try:
            if not self.trajectories:
                return b""  # Leere Bytes statt None

            # Prüfe, ob Trajektorien vorhanden sind
            if not any(len(traj) > 0 for traj in self.trajectories.values()):
                return b""

            # Generiere CSV-Daten
            output_str = io.StringIO()
            writer = csv.writer(output_str)

            # Header
            header = ["Frame"]
            joint_names = list(self.trajectories.keys())
            for name in joint_names:
                header.extend([f"{name}_x", f"{name}_y"])
            writer.writerow(header)

            # Daten
            num_frames = len(next(iter(self.trajectories.values())))
            for i in range(num_frames):
                row = [i]
                for name in joint_names:
                    x, y = self.trajectories[name][i]
                    row.extend([float(x), float(y)])
                writer.writerow(row)

            # Konvertiere zu Bytes
            return output_str.getvalue().encode("utf-8")

        except Exception as e:
            print(f"Fehler beim CSV-Export: {e}")
            return b""  
        

    def calculate_forward_velocity(self, crank_rpm, point):
        """
        Berechnet die Vorwärtsgeschwindigkeit basierend auf der Kurbeldrehzahl
        und der gespeicherten Trajektorien-Daten.
        """
        if not self.trajectories:
            return 0.0, 0.0, 0.0  # Geschwindigkeit, Schrittlänge, Schritthöhe
        #print(f"Trajectories {self.trajectories}")
        x_positions = [pos[0] for pos in self.trajectories[point]]
        y_positions = [pos[1] for pos in self.trajectories[point]]
        #print(f"Positions for joint '{point}': x={x_positions}, y={y_positions}")

        # Berechne Schrittparameter
        step_length = max(x_positions) - min(x_positions)

        # Berechne effektive Geschwindigkeit
        steps_per_revolution = len(x_positions)
        #print(f"Steps per revolution: {steps_per_revolution}")
        effective_velocity = (crank_rpm/60)/steps_per_revolution * step_length  # m/s
    
        return round(effective_velocity, 4), round(step_length, 4), steps_per_revolution
    
    def export_configuration_to_scad(self, filename):
        """
        Exportiert die Ausgangskonfiguration des Mechanismus als flache Stäbe
        mit Löchern an beiden Enden und Bolzen (als Gelenke).
        Die Links werden abwechselnd leicht in Z-Richtung versetzt, damit sie sich nicht im Weg sind.
        Dabei wird sichergestellt, dass die Bolzenlöcher exakt mit den Gelenkpositionen übereinstimmen.
        """

        components = []

        # Parameter für die flachen Links und Bolzen
        link_thickness = 4       # Dicke des flachen Stabs
        link_width = 10          # Breite des flachen Stabs
        bolt_diameter = 6        # Durchmesser der Bolzen (Gelenke)
        bolt_height = 8        # Höhe der Bolzen
        z_offset_value = 2       # Versatz in Z-Richtung für abwechselnde Positionierung

        # Links erstellen: Jeder Link wird als rechteckiger Stab mit Löchern an den Enden erzeugt.
        for i, link in enumerate(self.mechanism.links):
            # Bestimme Start- und Endpunkt (gerundet)
            start = [round(link.joint_a.x, 3), round(link.joint_a.y, 3)]
            end = [round(link.joint_b.x, 3), round(link.joint_b.y, 3)]
            dx = end[0] - start[0]
            dy = end[1] - start[1]
            actual_length = round(np.hypot(dx, dy), 3)
            # Wir erweitern um 12 Einheiten (6 an jedem Ende) für die Bolzenlöcher:
            total_length = round(actual_length + 12, 3)

            # Winkel in Bogenmaß und Grad (gerundet)
            angle_rad = np.arctan2(dy, dx)
            angle_deg = round(np.degrees(angle_rad), 3)

            # Alternierende Z-Verschiebung
            z_offset = z_offset_value if i % 2 == 0 else -z_offset_value

            # Erstelle den flachen Stab (Link) als Cube, der von 0 bis total_length in X geht.
            link_body = cube([total_length, link_width, link_thickness])

            # Löcher an beiden Enden – in der lokalen Mitte der Breite und Z-Mitte.
            # Positionen: x=6 und x=total_length-6
            hole_start = translate([6, link_width/2, link_thickness/2])(
                cylinder(r=bolt_diameter/2, h=link_thickness+2, center=True)
            )
            hole_end = translate([total_length - 6, link_width/2, link_thickness/2])(
                cylinder(r=bolt_diameter/2, h=link_thickness+2, center=True)
            )

            # Subtrahiere die Löcher vom Stab
            link_with_holes = difference()(link_body, hole_start, hole_end)

            # Damit der Bolzen am linken Ende (lokal x=6, y=link_width/2) exakt bei start liegt,
            # verschieben wir den Link zunächst um 6 Einheiten in X (lokal):
            offset_x = 6 * np.cos(angle_rad)
            offset_y = 6 * np.sin(angle_rad)
            # Zusätzlich: Versatz um link_width/2 in der lokalen Y-Richtung
            # Rotiere [0, link_width/2] in den globalen Raum:
            extra_offset_x = - np.sin(angle_rad) * (link_width/2)
            extra_offset_y =   np.cos(angle_rad) * (link_width/2)
            translation_vector = [
                round(start[0] - offset_x - extra_offset_x, 3),
                round(start[1] - offset_y - extra_offset_y, 3),
                round(z_offset, 3)
            ]

            # Drehe den Link (um angle_deg) und setze ihn an die korrekte globale Position.
            link_transformed = translate(translation_vector)(
                rotate([0, 0, angle_deg])(link_with_holes)
            )

            components.append(link_transformed)

        # Erstelle Bolzen (Gelenke) als Zylinder an den Gelenkpositionen (gerundet)
        for joint in self.mechanism.joints:
            bolt = translate([round(joint.x, 3), round(joint.y, 3), 2])(
                cylinder(r=bolt_diameter/2, h=bolt_height, center=True)
            )
            components.append(bolt)

        # Vereine alle Komponenten und exportiere das Modell
        final_model = union()(*components)
        scad_render_to_file(final_model, filename)
        print(f"Ausgangskonfiguration nach {filename} exportiert.")
