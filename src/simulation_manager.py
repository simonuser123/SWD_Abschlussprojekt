import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
from mechanism import FourBarLinkage  
from kinematics_simulator import KinematicsSimulator
import matplotlib.animation as animation
import tempfile, os, io

class SimulationManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(SimulationManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        # Hier wird der Mechanismus einmalig erstellt.
        # Zum Beispiel ein Viergelenkgetriebe:
        self.mechanism = FourBarLinkage.create_default()  # Statische Fabrikmethode, siehe unten
        self.simulator = KinematicsSimulator(self.mechanism)
        # Speichert die Bahnkurven der Gelenke als Dictionary {joint_name: [Positionen]}
        self.trajectories = {joint.name: [] for joint in self.mechanism.joints}

    def simulate_over_360(self, num_steps=360):
        """
        Berechnet die Kinematik für Winkel im Bereich von 0 bis 360°.
        """
        angles = np.linspace(0, 2 * np.pi, num_steps)
        for theta in angles:
            self.mechanism.driven_angle = theta
            # Aktualisiere das getriebene Gelenk
            self.simulator.update_driven_joint()
            # Optimiere (hier werden nur die freien Gelenke angepasst, z. B. Gelenk 3)
            self.simulator.optimize()
            # Speichere die Positionen aller Gelenke
            for joint in self.mechanism.joints:
                self.trajectories[joint.name].append((joint.x, joint.y))
        return angles

    def create_animation(self):
        """
        Erzeugt eine GIF-Animation, in der in jedem Frame der aktuelle Mechanismus (Verbindungen und Trajektorien)
        dargestellt wird. Dabei wird die Animation zuerst in einer temporären Datei gespeichert und dann in einen
        BytesIO-Puffer geladen.
        """
    
        n_frames = len(next(iter(self.trajectories.values())))
        fig, ax = plt.subplots(figsize=(8, 6))
        
        def update(frame):
            ax.clear()
            # Zeichne für jeden Link eine Linie zwischen den aktuell verbundenen Gelenken
            for link in self.mechanism.links:
                pos_a = self.trajectories[link.joint_a.name][frame]
                pos_b = self.trajectories[link.joint_b.name][frame]
                ax.plot([pos_a[0], pos_b[0]], [pos_a[1], pos_b[1]], 'ko-', lw=2)
            # Zeichne die Trajektorie bis zum aktuellen Frame für jedes Gelenk
            for joint_name, positions in self.trajectories.items():
                xs = [p[0] for p in positions[:frame+1]]
                ys = [p[1] for p in positions[:frame+1]]
                ax.plot(xs, ys, '--', label=f"Trajectory {joint_name}")
            ax.set_xlim(-100, 100)
            ax.set_ylim(-100, 100)
            ax.set_title(f"Frame {frame+1}/{n_frames}")
            ax.legend(loc='upper right')
            ax.grid(True)
        
        ani = animation.FuncAnimation(fig, update, frames=n_frames, repeat=False)
        
        # Verwende eine temporäre Datei, um die Animation zu speichern
        with tempfile.NamedTemporaryFile(suffix=".gif", delete=False) as tmp:
            temp_filename = tmp.name
    
        ani.save(temp_filename, writer='pillow', fps=10)
        
        # Lese den Inhalt der temporären Datei in einen BytesIO-Puffer ein
        with open(temp_filename, "rb") as f:
            buf = io.BytesIO(f.read())
        os.remove(temp_filename)
        return buf

