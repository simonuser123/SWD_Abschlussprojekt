import os
from tinydb import TinyDB, Query
from serializer import serializer
import math
import numpy as np

# +++++++++++++ Joint Class +++++++++++++
class Joint:
    db_connector = TinyDB(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database.json'),
                           storage=serializer).table('Joints')

    def __init__(self, name: str, x: float, y: float, is_fixed: bool = True, on_circular_path: bool = False):
        self.name = name
        self.x = x
        self.y = y
        self.is_fixed = is_fixed
        self.on_circular_path = on_circular_path

    def set_position(self, x, y):
        self.x = x
        self.y = y

    def get_position(self):
        return (self.x, self.y)

    def save(self):
        qr = Query()
        # Prüfe, ob das Gelenk bereits in der Datenbank existiert.
        result = self.db_connector.search(qr.name == self.name)
        if result:
            # Aktualisiere den bestehenden Datensatz
            self.db_connector.update(self.to_dict(), doc_ids=[result[0].doc_id])
        else:
            # Falls nicht vorhanden, neuen Datensatz einfügen
            self.db_connector.insert(self.to_dict())

    def to_dict(self):
        return {
            "name": self.name,
            "x": self.x,
            "y": self.y,
            "is_fixed": self.is_fixed,
            "on_circular_path": self.on_circular_path
        }
    
    @classmethod
    def find_all_joints(cls):
        result = cls.db_connector.all()
        if result:
            return [x["name"] for x in result if "name" in x]
        return None
    
    @classmethod
    def find_joints_info(cls):
        return cls.db_connector.all()
    
    @classmethod
    def find_by_name(cls, name):
        qr = Query()  
        result = cls.db_connector.search(qr.name == name)
        if result:
            data = result[0]
            return cls(data["name"], data["x"], data["y"], data["is_fixed"], data["on_circular_path"])
        return None
    
    def print_info(self):
        print(f"Joint {self.name} at ({self.x}, {self.y})")

    def __str__(self):
        return f"Joint {self.name} at ({self.x}, {self.y})"
    
    def __repr__(self):
        return f"Joint {self.name} at ({self.x}, {self.y})"

# +++++++++++++ Link Class +++++++++++++
class Link:
    db_connector = TinyDB(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database.json'),
                           storage=serializer).table('Links')

    def __init__(self, name: str, joint_a: Joint, joint_b: Joint, length = None):
        self.name = name
        self.joint_a = joint_a
        self.joint_b = joint_b
        self.length = length # Ziel-/Soll-Länge

    def initialize_self_lenght(self):
        self.length = self.get_current_length()

    def get_current_length(self):
        dx = self.joint_b.x - self.joint_a.x
        dy = self.joint_b.y - self.joint_a.y
        return math.sqrt(dx * dx + dy * dy)
    
    def get_length_error(self):
        return self.get_current_length() - self.length
    
    def save(self):
        qr = Query()
        result = self.db_connector.search(qr.name == self.name)
        if result:
            self.db_connector.update(self.to_dict(), doc_ids=[result[0].doc_id])
        else:
            self.db_connector.insert(self.to_dict())

    def to_dict(self):
        return {
            "name": self.name,
            "joint_a": self.joint_a.to_dict(),
            "joint_b": self.joint_b.to_dict(),
            "length": self.length
        }
    
    @classmethod
    def find_link_info(self):
        return self.db_connector.all()

    @classmethod
    def find_by_name(cls, name):
        qr = Query()  
        result = cls.db_connector.search(qr.name == name)
        if result:
            data = result[0]
            joint_a_i = Joint.find_by_name(data["joint_a"]["name"])
            joint_b_i = Joint.find_by_name(data["joint_b"]["name"])

            link = cls(data["name"], joint_a_i, joint_b_i)
            link.length = data["length"]
            return link
        return None
    
    @classmethod
    def find_links_by_mechanism(cls, mechanismName):
        qr = Query()
        result = cls.db_connector.search(qr.mechanism == mechanismName)
        return [data["name"] for data in result]
    
    def print_info(self):
        print(f"Link between Joint {self.joint_a.name} and Joint {self.joint_b.name} with length {self.length}")

    def __str__(self):
        return f"Link between Joint {self.joint_a.name} and Joint {self.joint_b.name} with length {self.length}"
    
    def __repr__(self):
        return f"Link between Joint {self.joint_a.name} and Joint {self.joint_b.name} with length {self.length}"

# +++++++++++++ Mechanism Class +++++++++++++
class Mechanism:
    db_connector = TinyDB(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database.json'),
                           storage=serializer).table('Mechanism')

    def __init__(self,name:str, joints=None, links=None, angle=0.0):
        self.name = name
        self.joints = joints if joints else []
        self.links = links if links else []
        self.driven_angle = angle
        self.boundary_conditions = []

    def set_driven_angle(self, angle):
        self.driven_angle = angle

    def add_joint(self, joint):
        self.joints.append(joint)

    def add_link(self, link):
        self.links.append(link)

    def add_boundary_condition(self, condition):
        self.boundary_conditions.append(condition)
    
    def print_info(self):
        print(f"Mechanism with {len(self.joints)} joints and {len(self.links)} links")
        for joint in self.joints:
            joint.print_info()
        for link in self.links:
            link.print_info()
        print(f"Driven angle: {self.driven_angle}")
        print(f"Boundary conditions: {self.boundary_conditions}")

    def get_joint_by_id(self, joint_id):
        # Hier vergleichen wir mit dem Attribut 'name'
        for joint in self.joints:
            if joint.name == joint_id:
                return joint
        return None
    
    def get_all_x(self) -> list:
        return [joint.x for joint in self.joints]
    
    def get_all_y(self) -> list:
        return [joint.y for joint in self.joints]
    
    def get_link(self):
        for link in self.links:
            return link
        return None 
    
    def compute_total_error(self):
        """Berechnet die Summe der quadrierten Fehler aller Links."""
        total_error = 0.0
        for link in self.links:
            # Stelle sicher, dass die Soll-Länge gesetzt ist
            if link.length is None:
                link.initialize_self_lenght()
            error = link.get_current_length() - link.length
            total_error += error ** 2
        return total_error

    def save(self):
        qr = Query()
        result = self.db_connector.search(qr.name == self.name)
        if result:
            result = self.db_connector.update(self.to_dict(), doc_ids=[result[0].doc_id])
        else:
            self.db_connector.insert(self.to_dict())

    def to_dict(self):
        joints_dict = [joint.to_dict() for joint in self.joints]
        links_dict = [link.to_dict() for link in self.links]   

        return {
            "name": self.name,
            "joints": joints_dict,
            "links": links_dict,    
            "driven_angle": self.driven_angle,
            "boundary_conditions": self.boundary_conditions
        }

    def validate(self):
        """
        Prüft, ob der Mechanismus valide ist.
        Gibt (True, "") zurück, wenn alles in Ordnung ist,
        ansonsten (False, "Fehlermeldung").
        """
        # 1) Mindestens ein fixiertes Gelenk
        fixed_joints = [j for j in self.joints if j.is_fixed]
        if len(fixed_joints) == 0:
            return False, "Keine fixierten Gelenke gefunden."
        
        # 2) Überprüfe, ob höchstens ein getriebenes Gelenk definiert ist
        driven_joints = [j for j in self.joints if j.on_circular_path]
        if len(driven_joints) > 1:
            return False, "Mehr als ein getriebenes Gelenk definiert."
        
        # 3) Prüfe, ob der Mechanismus zusammenhängend ist
        if not self._is_connected():
            return False, "Mechanismus ist nicht zusammenhängend."
        
        # 4) Freiheitsgrad-Check 
        n = len(self.joints)
        m_BC_stat = 2 * len(fixed_joints)  # Anzahl der statischen Randbedingungen
        m_BC_dyn = 2 if driven_joints else 0  # Anzahl der kinematischen Randbedingungen

        # Filtere den Link, der zwischen einem fixierten und einem getriebenen Gelenk besteht.
        constraint_links = [
            link for link in self.links 
            if not ((link.joint_a.is_fixed and link.joint_b.on_circular_path) or 
                    (link.joint_b.is_fixed and link.joint_a.on_circular_path))
        ]
        m = len(constraint_links)  # Anzahl der Links, die als Zwang gelten

        f = 2 * n - m_BC_stat - m_BC_dyn - m 
        if f != 0:
            return False, f"Mechanismus hat nicht den erwarteten Freiheitsgrad (F = {f})."

        # 5) Prüfe, ob alle Link-Längen gültig sind
        for link in self.links:
            if link.length is None or link.length <= 0:
                return False, f"Link {link.name} hat ungültige Länge."
        return True, ""

    def _is_connected(self):
        """
        Prüft, ob alle Gelenke im Mechanismus zusammenhängend sind.
        """
        # Erstelle eine Adjazenzliste: Knoten = Gelenk, Kanten = Verbindungen über Links
        adj = {joint.name: [] for joint in self.joints}
        for link in self.links:
            a = link.joint_a.name
            b = link.joint_b.name
            adj[a].append(b)
            adj[b].append(a)
        
        if not self.joints:
            return True  # Kein Gelenk => trivial zusammenhängend

        start = self.joints[0].name
        visited = set()
        queue = [start]
        
        while queue:
            current = queue.pop(0)
            if current not in visited:
                visited.add(current)
                for neighbor in adj[current]:
                    if neighbor not in visited:
                        queue.append(neighbor)
        
        return len(visited) == len(self.joints)

    @classmethod
    def find_all_mechs(cls):
        result = cls.db_connector.all()
        if result:
            return [x["name"] for x in result if "name" in x]
        return None
    
    @classmethod
    def find_joints_by_mechanism(cls, mechanismName):
        qr = Query()
        result = cls.db_connector.search(qr.name == mechanismName)
        if not result:
            return []
        
        # Korrektur: Hole die Joint-Daten direkt aus dem Mechanismus-Eintrag
        joint_data = result[0].get("joints", [])  # Direkter Zugriff auf "joints"
        
        joints = []
        for data in joint_data:
            joint = Joint(
                name=data['name'],
                x=data['x'],
                y=data['y'],
                is_fixed=data['is_fixed'],
                on_circular_path=data['on_circular_path']
            )
            joints.append(joint)
        return joints
    
    @classmethod
    def find_links_by_mechanism(cls, mechanismName):
        qr = Query()
        result = cls.db_connector.search(qr.name == mechanismName)
        if not result:
            return []

        # Lade die Joints des Mechanismus (bereits vorhanden)
        mechanism_joints = cls.find_joints_by_mechanism(mechanismName)
        # Erstelle ein Dictionary für schnellen Zugriff: {joint_name: joint_object}
        joint_dict = {joint.name: joint for joint in mechanism_joints}

        links = []
        for mech_entry in result:
            link_data = mech_entry.get("links", [])
            for link_info in link_data:
                # Hole die Joint-Instanzen aus dem Mechanismus (nicht neu erstellen!)
                joint_a = joint_dict.get(link_info["joint_a"]["name"])
                joint_b = joint_dict.get(link_info["joint_b"]["name"])

                if not joint_a or not joint_b:
                    continue  # Fehlerbehandlung optional
                
                link = Link(
                    name=link_info["name"],
                    joint_a=joint_a,
                    joint_b=joint_b,
                    length=link_info["length"]
                )
                links.append(link)
        return links
    
    @classmethod
    def find_driven_angle_by_mechanism(cls, mechanismName):
        """
        Sucht in der Datenbank den Mechanismus mit dem angegebenen Namen
        und gibt den gespeicherten driven_angle zurück.
        Falls kein Mechanismus gefunden wird, wird None zurückgegeben.
        """
        qr = Query()
        result = cls.db_connector.search(qr.name == mechanismName)
        if result:
            return result[0].get("driven_angle", None)
        return None


class FourBarLinkage(Mechanism):
    """
    Eine spezialisierte Mechanism-Klasse, die eine
    Standard-Viergelenkkette erzeugt.
    Gelenk 1: Fix
    Gelenk 2: Getrieben (auf Kreisbahn)
    Gelenk 3: frei
    Gelenk 4: Fix
    Zusätzlich wird ein 'Ground-Link' eingefügt, um
    die Kette zu schließen (4 Links).
    """
    @staticmethod
    def create_default():
        # Gelenk 1: fix
        joint1 = Joint("1", x=-30.0, y=0.0, is_fixed=True)
        # Gelenk 2: getrieben (auf Kreisbahn um Gelenk 1)
        joint2 = Joint("2", x=-25.0, y=10.0, is_fixed=False, on_circular_path=True)
        # Gelenk 3: frei
        joint3 = Joint("3", x=10.0, y=35.0, is_fixed=False)
        # Gelenk 4: fix
        joint4 = Joint("4", x=0.0, y=0.0, is_fixed=True)

        # Vier Links: 1→2, 2→3, 3→4, 4→1
        link1 = Link("link1", joint1, joint2)
        link2 = Link("link2", joint2, joint3)
        link3 = Link("link3", joint3, joint4)
        link4 = Link("link4", joint4, joint1)

        # Soll-Längen anhand der aktuellen Positionen initialisieren
        for link in [link1, link2, link3, link4]:
            link.initialize_self_lenght()

        # Mechanismus mit Name, Joints, Links und Anfangswinkel (z.B. arctan(10/5) ≈ 63.43°)
        return FourBarLinkage(
            name="Viergelenkkette",
            joints=[joint1, joint2, joint3, joint4],
            links=[link1, link2, link3, link4],
            angle=np.arctan(10/5)
        )


if __name__ == "__main__":
    # Beispiel zur Überprüfung
    # g1 = Joint("1", 0, 0)
    # g2 = Joint("2", 0, 10)
    # g3 = Joint("3", 10, 10)

    # s1 = Link("t", g1, g2)
    # s1.save()
    # s2 = Link("g", g2, g3)

    # joint1 = Joint("1", x=-30.0, y=0.0, is_fixed=True)
    #joint2 = Joint("2", x=0.0, y=0.0, on_circular_path=True)

    #print(joint1)
    #print(joint2)
    print(Mechanism.find_joints_by_mechanism("Viergelenkkette"))
    print(Mechanism.find_links_by_mechanism("Viergelenkkette"))

    