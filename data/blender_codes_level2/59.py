import bpy
import math
from mathutils import Vector

# Clear existing objects
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

# Define variables from parameter summary
span_x = 4.0
width_y = 2.0
height_z = 1.0
chord_section = 0.1
brace_section = 0.1
chord_length = 4.0
brace_length_vert = 1.0
brace_length_diag = 1.414
num_panels = 4
panel_length = span_x / num_panels
truss_y_positions = [-1.0, 1.0]
platform_size = (2.0, 2.0, 0.1)
platform_mass = 600.0
support_x = [-2.0, 2.0]
support_y = [-1.0, 1.0]
support_z = 0.0
top_joints_x = [-2.0, -1.0, 0.0, 1.0, 2.0]
bottom_joints_x = [-2.0, -1.0, 0.0, 1.0, 2.0]
joint_z_top = 1.0
joint_z_bottom = 0.0

# Function to create a structural member
def create_member(name, location, scale, rotation=(0,0,0)):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = scale
    if rotation != (0,0,0):
        obj.rotation_euler = rotation
    return obj

# Create support blocks at truss ends
supports = []
for sx in support_x:
    for sy in support_y:
        sup_name = f"Support_{sx}_{sy}"
        create_member(sup_name, (sx, sy, 0.05), (0.2, 0.2, 0.1))
        sup = bpy.context.active_object
        bpy.ops.rigidbody.object_add()
        sup.rigid_body.type = 'PASSIVE'
        supports.append(sup)

# Build two parallel trusses
for truss_idx, truss_y in enumerate(truss_y_positions):
    truss_prefix = f"Truss{truss_idx+1}"
    
    # Create top chord (horizontal member)
    top_chord = create_member(
        f"{truss_prefix}_TopChord",
        (0, truss_y, joint_z_top),
        (chord_length/2, chord_section/2, chord_section/2)
    )
    bpy.ops.rigidbody.object_add()
    top_chord.rigid_body.type = 'PASSIVE'
    
    # Create bottom chord
    bottom_chord = create_member(
        f"{truss_prefix}_BottomChord",
        (0, truss_y, joint_z_bottom),
        (chord_length/2, chord_section/2, chord_section/2)
    )
    bpy.ops.rigidbody.object_add()
    bottom_chord.rigid_body.type = 'PASSIVE'
    
    # Create vertical braces at panel points
    verticals = []
    for i, joint_x in enumerate(bottom_joints_x[1:-1]):  # Skip ends
        vert_name = f"{truss_prefix}_Vertical_{i+1}"
        vert = create_member(
            vert_name,
            (joint_x, truss_y, 0.5),
            (brace_section/2, brace_section/2, brace_length_vert/2)
        )
        bpy.ops.rigidbody.object_add()
        vert.rigid_body.type = 'PASSIVE'
        verticals.append(vert)
    
    # Create diagonal braces (Warren pattern)
    diagonals = []
    for i in range(num_panels):
        # Start point for diagonal
        start_x = bottom_joints_x[i] if i % 2 == 0 else top_joints_x[i]
        start_z = joint_z_bottom if i % 2 == 0 else joint_z_top
        
        # End point for diagonal
        end_x = top_joints_x[i+1] if i % 2 == 0 else bottom_joints_x[i+1]
        end_z = joint_z_top if i % 2 == 0 else joint_z_bottom
        
        # Center position
        center_x = (start_x + end_x) / 2
        center_z = (start_z + end_z) / 2
        
        # Rotation angle (45° for unit square diagonals)
        angle = math.radians(45)
        rotation = (0, -angle if i % 2 == 0 else angle, 0)
        
        diag_name = f"{truss_prefix}_Diagonal_{i+1}"
        diag = create_member(
            diag_name,
            (center_x, truss_y, center_z),
            (brace_length_diag/2, brace_section/2, brace_section/2),
            rotation
        )
        bpy.ops.rigidbody.object_add()
        diag.rigid_body.type = 'PASSIVE'
        diagonals.append(diag)

# Create central platform
platform = create_member(
    "CentralPlatform",
    (0, 0, 1.05),
    (platform_size[0]/2, platform_size[1]/2, platform_size[2]/2)
)
bpy.ops.rigidbody.object_add()
platform.rigid_body.type = 'ACTIVE'
platform.rigid_body.mass = platform_mass

# Create fixed constraints between connected members
def add_fixed_constraint(obj_a, obj_b):
    # Create empty object as constraint parent
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=obj_a.location)
    empty = bpy.context.active_object
    empty.name = f"Constraint_{obj_a.name}_{obj_a.name}"
    
    # Add rigid body constraint
    bpy.ops.rigidbody.constraint_add()
    constraint = empty.rigid_body_constraint
    constraint.type = 'FIXED'
    
    # Link objects
    constraint.object1 = obj_a
    constraint.object2 = obj_b

# Connect truss members (simplified - in practice would connect all joints)
# For demonstration, connect bottom chord to supports
for sup in supports:
    # Find adjacent bottom chord
    for obj in bpy.data.objects:
        if "BottomChord" in obj.name and abs(obj.location.y - sup.location.y) < 0.1:
            add_fixed_constraint(sup, obj)

# Set up physics world
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 50

# Set simulation end frame
bpy.context.scene.frame_end = 100

print("Warren Truss platform construction complete. Simulation ready for 100 frames.")