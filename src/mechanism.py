import os
from tinydb import TinyDB, Query
from serializer import serializer
import math
import numpy as np

# +++++++++++++ Joint Class +++++++++++++
class Joint:
    ''' Create a Joint/ Point'''
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
    
    @classmethod
    def find_joints_by_mechanism(cls, mechanismName):
        qr = Query()
        result = cls.db_connector.search(qr.mechanism == mechanismName)
        jointslist = []
        if result:
            for joint in result:
                jointInfo = Joint.find_by_name(joint)
                # joint_info = {
                #     "name": data["name"],
                #     "x": data["x"],
                #     "y": data["y"],
                #     "is_fixed": data["is_fixed"],
                #     "on_circular_path": data["on_circular_path"]
                # }
                jointslist.append(jointInfo)

        return jointslist



    def print_info(self):
        print(f"Joint {self.name} at ({self.x}, {self.y})")

# +++++++++++++ Link Class +++++++++++++
class Link:
    db_connector = TinyDB(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database.json'),
                           storage=serializer).table('Links')

    def __init__(self, name: str, joint_a: Joint, joint_b: Joint):
        self.name = name
        self.joint_a = joint_a
        self.joint_b = joint_b
        self.length = None  # Ziel-/Soll-Länge

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

    # Optional: visualize or print info
    def print_info(self):
        print(f"Link between Joint {self.joint_a.name} and Joint {self.joint_b.name} with length {self.length}")

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
    @classmethod
    def find_all_mechs(cls):
        result = cls.db_connector.all()
        if result:
            return [x["name"] for x in result if "name" in x]
        return None


if __name__ == "__main__":
    # Beispiel zur Überprüfung
    # g1 = Joint("1", 0, 0)
    # g2 = Joint("2", 0, 10)
    # g3 = Joint("3", 10, 10)

    # s1 = Link("t", g1, g2)
    # s1.save()
    # s2 = Link("g", g2, g3)

    # m1 = Mechanism([g1, g2, g3], [s1, s2])

    # print("Aktuelle Länge von s1:", s1.get_current_length())
    # print("x-Koordinaten aller Gelenke:", m1.get_all_x())
    # print("Erster Link:", m1.get_link())
    #print(Mechanism.find_all_mechs())
    pass