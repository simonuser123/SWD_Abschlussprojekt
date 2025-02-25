import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import tempfile, os, io

from tinydb import Query
from mechanism import Mechanism, Joint, Link
from kinematics_simulator import KinematicsSimulator

def load_mechanism_from_db(mechanismName):
    # Lade die Gelenke und Links
    joint_names = Joint.find_joints_by_mechanism(mechanismName)
    joints = []
    if joint_names:
        for name in joint_names:
            joint = Joint.find_by_name(name)
            if joint:
                joints.append(joint)
    if not joints:
        print(f"Error: no Joints in {mechanismName}")
        return None

    link_data = Link.find_links_by_mechanism(mechanismName)
    links = []
    for item in link_data:
        joint_a = Joint.find_by_name(item["joint_a"]["name"])
        joint_b = Joint.find_by_name(item["joint_b"]["name"])
        if joint_a and joint_b:
            link = Link(item["name"], joint_a, joint_b)
            link.length = item["length"]
            links.append(link)

    if not links:
        print(f"Error: No links in mechanism {mechanismName}")
        return None

    # Rückgabe des Mechanismus
    return Mechanism(joints=joints, links=links, angle=0.0)


class SimulationManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(SimulationManager, cls).__new__(cls)
        return cls._instance

    def __init__(self, mechanismName:str ):
        # Statt FourBarLinkage.create_default() laden wir den Mechanismus aus der DB.
        self.mechanism = load_mechanism_from_db(mechanismName)
        self.simulator = KinematicsSimulator(self.mechanism)
        # Speichert die Bahnkurven der Gelenke als Dictionary {joint_name: [Positionen]}
       # self.trajectories = {joint.name: [] for joint in self.mechanism.joints}            ---------

    def simulate_over_360(self, num_steps=360):
        """
        Berechnet die Kinematik für Winkel im Bereich von 0 bis 360°.
        """
        angles = np.linspace(0, 2 * np.pi, num_steps)
        for theta in angles:
            self.mechanism.driven_angle = theta
            self.simulator.update_driven_joint()
            self.simulator.optimize()
            # Speichere die Positionen aller Gelenke
            for joint in self.mechanism.joints:
                self.trajectories[joint.name].append((joint.x, joint.y))
        return angles

    def create_animation(self):
        """
        Erzeugt eine GIF-Animation, in der in jedem Frame der aktuelle Mechanismus dargestellt wird.
        Die Animation wird in einer temporären Datei gespeichert und anschließend in einen BytesIO-Puffer geladen.
        """
        n_frames = len(next(iter(self.trajectories.values())))
        fig, ax = plt.subplots(figsize=(8, 6))
        
        def update(frame):
            ax.clear()
            for link in self.mechanism.links:
                pos_a = self.trajectories[link.joint_a.name][frame]
                pos_b = self.trajectories[link.joint_b.name][frame]
                ax.plot([pos_a[0], pos_b[0]], [pos_a[1], pos_b[1]], 'ko-', lw=2)
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
        
        with tempfile.NamedTemporaryFile(suffix=".gif", delete=False) as tmp:
            temp_filename = tmp.name
        ani.save(temp_filename, writer='pillow', fps=10)
        with open(temp_filename, "rb") as f:
            buf = io.BytesIO(f.read())
        os.remove(temp_filename)
        return buf
