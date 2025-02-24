import os
from tinydb import TinyDB, Query
from serializer import serializer
import math

class Joint:
    db_connector = TinyDB(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database.json'), storage=serializer).table('Joints')

    def __init__(self, name=str, x=float, y=float, is_fixed=True, on_circular_path=False): #    def __init__(self, joint_id, x=0.0, y=0.0, is_fixed=True, on_circular_path=False):
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
        # Check if the device already exists in the database
        result = self.db_connector.search(qr.name == self.name)
        if result:
            # Update the existing record with the current instance's data
            result = self.db_connector.update(self.to_dict(), doc_ids=[result[0].doc_id])
        else:
            # If the device doesn't exist, insert a new record
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
            result = [x["name"] for x in result if "name" in x]
            return result
        return None
    
    @classmethod
    def find_joints_info(self):
        return self.db_connector.all()
    
    @classmethod
    def find_by_name(cls, name):
        qr = Query()  
        result = cls.db_connector.search(qr.name == name)
        if result:
            data = result[0]
            return cls(data["name"], data["x"], data["y"], data["is_fixed"], data["on_circular_path"])
        return None

    

    # Optional: visualize or print info
    def print_info(self):
        print(f"Joint {self.name} at ({self.x}, {self.y})")

    
class Link:
    db_connector = TinyDB(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database.json'), storage=serializer).table('Links')

    def __init__(self, name=str, joint_a=Joint, joint_b=Joint):
        self.joint_a = joint_a
        self.joint_b = joint_b
        self.name =  name
        self.length = None

    def initialize_self_lenght(self):
        self.length = self.get_current_length()

    def get_current_length(self):
        dx = self.joint_b.x - self.joint_a.x
        dy = self.joint_b.y - self.joint_a.y
        return math.sqrt(dx*dx + dy*dy)
    
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
    
    # Optional: visualize or print info
    def print_info(self):
        print(f"Link between Joint {self.joint_a.joint_id} and Joint {self.joint_b.joint_id} with length {self.length}")

class Mechanism:
    db_connector = TinyDB(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database.json'), storage=serializer).table('Mechanism')

    def __init__(self, joints=None, links=None, angle=0.0):
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
    
    # Optional: visualize or print info
    # def print_info(self):
    #     print(f"Mechanism with {len(self.joints)} joints and {len(self.links)} links")
    #     for joint in self.joints:
    #         joint.print_info()
    #     for link in self.links:
    #         link.print_info()
    #     print(f"Driven angle: {self.driven_angle}")
    #     print(f"Boundary conditions: {self.boundary_conditions}")

    def get_joint_by_id(self, joint_id):
        for joint in self.joints:
            if joint.joint_id == joint_id:
                return joint
        return None
    
    def get_all_x(self) -> float:
        try:
            return [joint.x for joint in self.joints]
        except:
            return 0
    
    def get_all_y(self) -> float:
        try: 
            return [joint.y for joint in self.joints]
        except:
            return 0
    
    def get_link(self):
        for link in self.links:
            return link
        return None 

    
if __name__ == "__main__":
    g1= Joint(1,0,0)
    g2= Joint(2,0,10)
    g3= Joint(3,10,10)

    s1= Link("t",g1,g2)
    s1.save()
    s2= Link("g", g2,g3)

    m1= Mechanism([g1,g2,g3],[s1,s2])

    print(s1.get_current_length())
    print(m1.get_all_x())
    print(m1.get_link())
