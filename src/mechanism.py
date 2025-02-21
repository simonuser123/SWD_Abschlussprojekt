import math

class Joint:
    def __init__(self, joint_id, x=0.0, y=0.0, is_fixed=False, on_circular_path=False):
        self.joint_id = joint_id
        self.x = x
        self.y = y
        self.is_fixed = is_fixed
        self.on_circular_path = on_circular_path

    def set_position(self, x, y):
        self.x = x
        self.y = y

    def get_position(self):
        return (self.x, self.y)

    # Optional: visualize or print info
    def print_info(self):
        print(f"Joint {self.joint_id} at ({self.x}, {self.y})")

    
class Link:
    def __init__(self, joint_a, joint_b, length):
        self.joint_a = joint_a
        self.joint_b = joint_b
        self.length = length

    def get_current_length(self):
        dx = self.joint_b.x - self.joint_a.x
        dy = self.joint_b.y - self.joint_a.y
        return math.sqrt(dx*dx + dy*dy)
    
    def get_length_error(self):
        return self.get_current_length() - self.length
    
    # Optional: visualize or print info
    def print_info(self):
        print(f"Link between Joint {self.joint_a.joint_id} and Joint {self.joint_b.joint_id} with length {self.length}")

class Mechanism:
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
    def print_info(self):
        print(f"Mechanism with {len(self.joints)} joints and {len(self.links)} links")
        for joint in self.joints:
            joint.print_info()
        for link in self.links:
            link.print_info()
        print(f"Driven angle: {self.driven_angle}")
        print(f"Boundary conditions: {self.boundary_conditions}")

    def get_joint_by_id(self, joint_id):
        for joint in self.joints:
            if joint.joint_id == joint_id:
                return joint
        return None
    