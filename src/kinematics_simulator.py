import numpy as np
from scipy.optimize import least_squares
from mechanism import Mechanism, Joint, Link

class KinematicsSimulator:
    def __init__(self, mechanism: Mechanism):
        """
        Initialisiert den Simulator mit einem Mechanismus.
        Es werden alle Gelenke, die weder fix noch durch den Antrieb (on_circular_path)
        bestimmt sind, als optimierbare Variablen identifiziert.
        """
        self.mechanism = mechanism
        # Optimierbar sind jene Gelenke, die weder fix noch getrieben sind.
        self.free_joints = [joint for joint in self.mechanism.joints if (not joint.is_fixed) and (not joint.on_circular_path)]
        # Debug-Ausgabe
        print("[DEBUG] Gelenkattribute:")
        for joint in self.mechanism.joints:
            print(f"  - {joint.name}: is_fixed={joint.is_fixed}, on_circular_path={joint.on_circular_path}")
        print("[DEBUG] Freie Gelenke:", [j.name for j in self.free_joints])
        # Stelle sicher, dass alle Links ihre Soll-Länge (ursprüngliche Länge) initialisiert haben.
        for link in self.mechanism.links:                           
            if link.length is None:
                link.initialize_self_lenght()

    def update_driven_joint(self):
        """
        Aktualisiert die Position der Gelenke, die sich auf einer Kreisbahn bewegen sollen.
        Es wird angenommen, dass das getriebene Gelenk über einen Link mit einem fixen
        Gelenk (Zentrum) verbunden ist.
        """
        for joint in self.mechanism.joints:
            if joint.on_circular_path:
                for link in self.mechanism.links:
                    if link.joint_b.name == joint.name and link.joint_a.is_fixed:
                        center = link.joint_a
                        radius = link.length  
                        joint.x = center.x + radius * np.cos(self.mechanism.driven_angle)
                        joint.y = center.y + radius * np.sin(self.mechanism.driven_angle)
                        break
                    elif link.joint_a.name == joint.name and link.joint_b.is_fixed:
                        center = link.joint_b
                        radius = link.length
                        joint.x = center.x + radius * np.cos(self.mechanism.driven_angle)
                        joint.y = center.y + radius * np.sin(self.mechanism.driven_angle)
                        break

    def _compute_length_errors(self, params):
        """
        Berechnet den Fehlervektor für die Optimierung:
        - Für jeden Link wird die Differenz zwischen aktueller Länge und Soll-Länge berechnet.
        """
        # Aktualisiere die Positionen der freien Gelenke anhand des Parametervektors.

        for i, joint in enumerate(self.free_joints):
            joint.x = params[2 * i]
            joint.y = params[2 * i + 1]

        errors = []
        for link in self.mechanism.links:
            current_length = link.get_current_length()
            error = current_length - link.length
            errors.append(error)
            print(f"Link {link.name}: current length = {current_length}, target = {link.length}, error = {error}")
        return np.array(errors)

    
    def optimize(self):
        """
        Führt die Optimierung durch, um die freien Gelenkpositionen so anzupassen,
        dass die Summe der quadrierten Fehler (Differenz zwischen aktueller und Soll-Länge)
        minimiert wird.
        """
        # Zuerst wird die Position des getriebenen Gelenks (Gelenk 2) aktualisiert.
        self.update_driven_joint()
        
        # Erstelle den initialen Parametervektor für die freien Gelenke.
        init_params = []
        for joint in self.free_joints:
            init_params.extend([joint.x, joint.y])
        init_params = np.array(init_params)
        
        # Führe die Optimierung mit least_squares durch.
        result = least_squares(self._compute_length_errors, init_params)
        
        # Aktualisiere die freien Gelenke mit den optimierten Werten.
        optimized_params = result.x
        for i, joint in enumerate(self.free_joints):
            joint.x = optimized_params[2 * i]
            joint.y = optimized_params[2 * i + 1]
        
        return result

if __name__ == "__main__":
    # --- Schritt 1: Definition der Gelenke (Joint) ---
    # Gelenk 1: Fixer Ankerpunkt (Gestell)
    joint1 = Joint("1", x=-30.0, y=0.0, is_fixed=True)
    
    # Gelenk 2: Getrieben – bewegt sich auf einer Kreisbahn um Gelenk 1.
    # Hier wird on_circular_path=True gesetzt, damit wird seine Position über den Drehwinkel bestimmt.
    # Als Startwert nehmen wir (-25.0, 10.0) an.
    joint2 = Joint("2", x=-25.0, y=10.0, is_fixed=False, on_circular_path=True)
    
    # Gelenk 3: Frei beweglich, verbunden mit Gelenk 2 (Koppelglied).
    joint3 = Joint("3", x=10.0, y=35.0, is_fixed=False)
    
    # Gelenk 4: Fix, verbunden mit Gelenk 3 (Ausgangsglied).
    joint4 = Joint("4", x=0.0, y=0.0, is_fixed=True)
    
    # --- Schritt 2: Definition der Glieder (Link) ---
    # link1: Von Gelenk 1 zu Gelenk 2 – definiert den Radius der Kreisbahn für Gelenk 2.
    link1 = Link("link1", joint1, joint2)
    # link2: Von Gelenk 2 zu Gelenk 3 – Koppelglied.
    link2 = Link("link2", joint2, joint3)
    # link3: Von Gelenk 3 zu Gelenk 4 – Ausgangsglied.
    link3 = Link("link3", joint3, joint4)
    # link4: Ground-Link zwischen Gelenk 4 und Gelenk 1 – schließt den Viergelenkzyklus.
    link4 = Link("link4", joint4, joint1)
    
    # --- Schritt 3: Mechanismus erstellen und Antriebswinkel setzen ---
    # Zuerst wird der Mechanismus mit dem Anfangswinkel erstellt. 
    # Dabei werden die Soll-Längen (Referenz) aus der Anfangskonfiguration ermittelt.
    mech = Mechanism("mech", joints=[joint1, joint2, joint3, joint4],
                     links=[link1, link2, link3, link4],
                     angle=np.arctan(10/5))  # Anfangswinkel, z. B. ca. 63,43° in Radiant.
    
    # Berechne und gebe die Linklängen aus der Anfangskonfiguration (Soll-Längen) aus.
    print("Link-Längen in der Anfangskonfiguration (Soll-Längen):")
    for link in mech.links:
        if link.length is None:
            link.initialize_self_lenght()
        print(f"{link.name}: {link.get_current_length():.4f}")
    print()
    
    # Ausgabe des Mechanismus vor Optimierung.
    print("=== Vor der Optimierung ===")
    mech.print_info()
    print(f"Gesamter quadratischer Fehler: {mech.compute_total_error():.4f}\n")
    
    # --- Schritt 4: Änderung des Antriebswinkels (θ) ---
    new_theta = np.arctan(10/5) + np.deg2rad(10)  # Erhöhung des Winkels um 10°
    mech.driven_angle = new_theta
    
    # Erstelle einen Simulator, der zunächst nur das getriebene Gelenk aktualisiert.
    simulator = KinematicsSimulator(mech)
    simulator.update_driven_joint()
    
    print("=== Nach Erhöhung von θ ===")
    print("Neue Position des getriebenen Gelenks (Gelenk 2):")
    print(f"[{joint2.x:.2f}, {joint2.y:.2f}]")
    print()
    
    # Berechne und gebe die aktuellen Linklängen (nach Änderung von θ) aus.
    print("Aktuelle Link-Längen nach Änderung von θ:")
    for link in mech.links:
        current_length = link.get_current_length()
        print(f"{link.name}: {current_length:.4f}")
    print()
    
    # Vergleiche die aktuellen Linklängen mit den Soll-Längen.
    print("Fehlervektor (aktuelle Länge - Soll-Länge):")
    for link in mech.links:
        error = link.get_current_length() - link.length
        print(f"{link.name}: Fehler = {error:.4f}")
    print()
    
    # --- Schritt 5: Optimierung der freien Gelenkposition (hier: Gelenk 3) ---
    # Ziel: Durch Optimierung (unter Anpassung der freien Gelenke) soll der Fehler minimiert werden,
    # sodass die Linklängen wieder den Soll-Werten entsprechen.
    result = simulator.optimize()
    
    print("=== Nach der Optimierung ===")
    mech.print_info()
    print(f"Gesamter quadratischer Fehler: {mech.compute_total_error():.4f}\n")
    print("Optimierungsresultat:")
    print(result)
