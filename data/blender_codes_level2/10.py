import bpy
import math
from mathutils import Vector, Matrix

# Clear scene
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=True)

# Parameters from summary
span = 12.0
height = 2.0
bottom_z = 5.0
top_z = 7.0
panel_width = 2.0
num_panels = 6
chord_section = (0.2, 0.2)
web_section = (0.15, 0.15)
top_chord_length = panel_width
bottom_chord_length = panel_width
vertical_length = height
diagonal_length = 2.828427
x_positions = [-6.0, -4.0, -2.0, 0.0, 2.0, 4.0, 6.0]
bottom_joints = [(x, 0.0, bottom_z) for x in x_positions]
top_joints = [(x, 0.0, top_z) for x in x_positions]
total_force = 14715.0
num_top_nodes = 7
force_per_node = total_force / num_top_nodes
frames = 100
max_deflection_limit = 0.1
density = 7850.0

# Helper to create a beam between two points
def create_beam(name, start, end, section, is_passive=False):
    """Create a cuboid beam from start to end with given cross-section"""
    # Calculate center, length, and rotation
    start_vec = Vector(start)
    end_vec = Vector(end)
    direction = end_vec - start_vec
    length = direction.length
    center = (start_vec + end_vec) / 2
    
    # Create cube and scale
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=center)
    obj = bpy.context.active_object
    obj.name = name
    
    # Scale: cross-section in X/Y, length in Z
    obj.scale = (section[0]/2, section[1]/2, length/2)
    
    # Rotate to align with direction
    if length > 0:
        # Default cube local Z is up, rotate to match direction
        z_axis = Vector((0, 0, 1))
        rot_axis = z_axis.cross(direction.normalized())
        rot_angle = z_axis.angle(direction)
        if rot_axis.length > 0:
            obj.rotation_mode = 'AXIS_ANGLE'
            obj.rotation_axis_angle = (rot_angle, rot_axis.normalized())
    
    # Add rigid body
    bpy.ops.rigidbody.object_add()
    obj.rigid_body.type = 'PASSIVE' if is_passive else 'ACTIVE'
    obj.rigid_body.mass = density * (section[0] * section[1] * length)
    obj.rigid_body.collision_shape = 'BOX'
    obj.rigid_body.collision_margin = 0.001
    obj.rigid_body.linear_damping = 0.1
    obj.rigid_body.angular_damping = 0.1
    
    return obj

# Create passive supports at ends
create_beam("LeftSupport", (-6.0, -0.1, 4.9), (-6.0, 0.1, 5.1), (0.4, 0.4, 0.4), is_passive=True)
create_beam("RightSupport", (6.0, -0.1, 4.9), (6.0, 0.1, 5.1), (0.4, 0.4, 0.4), is_passive=True)

# Create bottom chord (6 segments)
bottom_objects = []
for i in range(num_panels):
    start = bottom_joints[i]
    end = bottom_joints[i+1]
    obj = create_beam(f"BottomChord_{i}", start, end, chord_section)
    bottom_objects.append(obj)

# Create top chord (6 segments)
top_objects = []
for i in range(num_panels):
    start = top_joints[i]
    end = top_joints[i+1]
    obj = create_beam(f"TopChord_{i}", start, end, chord_section)
    top_objects.append(obj)

# Create vertical members (5 members, excluding ends)
vertical_objects = []
for i in range(1, num_panels):  # Skip first and last (ends)
    start = bottom_joints[i]
    end = top_joints[i]
    obj = create_beam(f"Vertical_{i}", start, end, web_section)
    vertical_objects.append(obj)

# Create diagonal members (6 diagonals)
diagonal_objects = []
# Left side diagonals (3)
for i in range(3):
    if i % 2 == 0:  # From bottom to top
        start = bottom_joints[i*2]
        end = top_joints[i*2 + 2]
    else:  # From top to bottom
        start = top_joints[i*2 + 1]
        end = bottom_joints[i*2 + 3]
    obj = create_beam(f"Diagonal_L{i}", start, end, web_section)
    diagonal_objects.append(obj)

# Right side diagonals (3, symmetric)
for i in range(3):
    idx = 6 - i*2  # Mirror index
    if i % 2 == 0:  # From top to bottom
        start = top_joints[idx]
        end = bottom_joints[idx - 2]
    else:  # From bottom to top
        start = bottom_joints[idx - 1]
        end = top_joints[idx - 3]
    obj = create_beam(f"Diagonal_R{i}", start, end, web_section)
    diagonal_objects.append(obj)

# Create fixed constraints at all joints
def create_fixed_constraint(obj1, obj2, location):
    """Create fixed constraint between two objects at location"""
    # Create empty for constraint
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=location)
    empty = bpy.context.active_object
    empty.name = f"Constraint_{obj1.name}_{obj2.name}"
    
    # Add rigid body constraint
    bpy.ops.rigidbody.constraint_add()
    empty.rigid_body_constraint.type = 'FIXED'
    empty.rigid_body_constraint.object1 = obj1
    empty.rigid_body_constraint.object2 = obj2

# Create constraints at each joint
# Bottom chord joints
for i in range(len(bottom_joints)):
    loc = Vector(bottom_joints[i])
    # Find all objects connected to this joint
    connected = []
    for obj in bottom_objects:
        if Vector(obj.location).distance(loc) < 1.0:  # Rough check
            connected.append(obj)
    for obj in vertical_objects + diagonal_objects:
        if Vector(obj.location).distance(loc) < 1.0:
            connected.append(obj)
    
    # Create constraints between first object and others
    if len(connected) > 1:
        for j in range(1, len(connected)):
            create_fixed_constraint(connected[0], connected[j], loc)

# Top chord joints (with forces)
force_objects = []  # Track top chord objects for force application
for i in range(len(top_joints)):
    loc = Vector(top_joints[i])
    # Find connected objects
    connected = []
    for obj in top_objects:
        if Vector(obj.location).distance(loc) < 1.0:
            connected.append(obj)
            force_objects.append(obj)  # For force application
    for obj in vertical_objects + diagonal_objects:
        if Vector(obj.location).distance(loc) < 1.0:
            connected.append(obj)
    
    if len(connected) > 1:
        for j in range(1, len(connected)):
            create_fixed_constraint(connected[0], connected[j], loc)

# Apply downward forces to top chord nodes
# Forces applied to top chord segment objects at their centers
for obj in top_objects:
    # Add force field (downward)
    bpy.ops.object.effector_add(type='FORCE', location=obj.location)
    force = bpy.context.active_object
    force.name = f"Force_{obj.name}"
    force.field.strength = -force_per_node  # Negative for downward
    force.field.use_max_distance = True
    force.field.distance_max = 0.5  # Only affect nearby objects
    force.field.falloff_power = 0.0  # Constant within range
    
    # Parent to top chord object
    force.parent = obj
    force.matrix_parent_inverse = obj.matrix_world.inverted()

# Setup rigid body world
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 10
bpy.context.scene.frame_end = frames

# Keyframe initial state
for obj in bpy.data.objects:
    if obj.rigid_body:
        obj.keyframe_insert(data_path="location")
        obj.keyframe_insert(data_path="rotation_euler")

print("Howe Truss construction complete. Simulate with: bpy.ops.ptcache.bake_all()")
print(f"Expected max deflection limit: {max_deflection_limit}m")