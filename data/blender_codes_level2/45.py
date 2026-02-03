import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Parameters from summary
span = 6.0
truss_depth = 1.0
member_cross_section = 0.2
top_chord_z = 3.0
bottom_chord_z = 2.0

top_chord_dim = (span, member_cross_section, member_cross_section)
bottom_chord_dim = (span, member_cross_section, member_cross_section)
vertical_dim = (member_cross_section, member_cross_section, truss_depth)
diagonal_length = 3.1622776601683795
diagonal_dim = (diagonal_length, member_cross_section, member_cross_section)

top_chord_pos = (span/2, 0.0, top_chord_z)
bottom_chord_pos = (span/2, 0.0, bottom_chord_z)

vertical_positions = [
    (0.0, 0.0, 2.5),
    (span/2, 0.0, 2.5),
    (span, 0.0, 2.5)
]

diagonal_centers = [
    (1.5, 0.0, 2.5),
    (4.5, 0.0, 2.5)
]

diagonal_angles = [
    -0.3217505543966422,  # atan2(-1, 3)
    -2.819842099193151    # atan2(-1, -3)
]

top_chord_mass = 800.0

# Create materials for visualization (optional)
def create_material(name, color):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    principled = nodes.get("Principled BSDF")
    if principled:
        principled.inputs[0].default_value = color
    return mat

steel_gray = (0.6, 0.6, 0.7, 1.0)
load_blue = (0.3, 0.5, 0.8, 1.0)

steel_mat = create_material("Steel", steel_gray)
load_mat = create_material("Load", load_blue)

# Function to create rigid body member
def create_member(name, location, dimensions, rotation=(0,0,0), mat=None, body_type='PASSIVE', mass=1.0):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = (dimensions[0]/2, dimensions[1]/2, dimensions[2]/2)  # Cube size=1, so scale by half dimensions
    
    # Apply rotation
    obj.rotation_euler = rotation
    
    # Add material
    if mat:
        obj.data.materials.append(mat)
    
    # Add rigid body
    bpy.ops.rigidbody.object_add()
    obj.rigid_body.type = body_type
    if body_type == 'ACTIVE':
        obj.rigid_body.mass = mass
        obj.rigid_body.collision_shape = 'BOX'
    else:
        obj.rigid_body.collision_shape = 'BOX'
    
    return obj

# Create structural members
print("Creating Howe Truss Structure...")

# Top chord (active with load mass)
top_chord = create_member(
    "TopChord", 
    top_chord_pos, 
    top_chord_dim, 
    mat=load_mat,
    body_type='ACTIVE', 
    mass=top_chord_mass
)

# Bottom chord
bottom_chord = create_member(
    "BottomChord", 
    bottom_chord_pos, 
    bottom_chord_dim, 
    mat=steel_mat
)

# Vertical members
verticals = []
for i, pos in enumerate(vertical_positions):
    vert = create_member(
        f"Vertical_{i}", 
        pos, 
        vertical_dim, 
        mat=steel_mat
    )
    verticals.append(vert)

# Diagonal members
diagonals = []
for i, (center, angle) in enumerate(zip(diagonal_centers, diagonal_angles)):
    diag = create_member(
        f"Diagonal_{i}", 
        center, 
        diagonal_dim, 
        rotation=(0, angle, 0),
        mat=steel_mat
    )
    diagonals.append(diag)

# Create fixed constraints at joints
print("Creating fixed constraints...")

def create_fixed_constraint(obj1, obj2, location):
    # Create empty for constraint
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=location)
    empty = bpy.context.active_object
    empty.name = f"Constraint_{obj1.name}_{obj2.name}"
    empty.empty_display_size = 0.3
    
    # Add rigid body constraint
    bpy.ops.rigidbody.constraint_add()
    empty.rigid_body_constraint.type = 'FIXED'
    empty.rigid_body_constraint.object1 = obj1
    empty.rigid_body_constraint.object2 = obj2

# Joint A (0,0,3): Top chord, Vertical1, Diagonal1
create_fixed_constraint(top_chord, verticals[0], (0,0,3))
create_fixed_constraint(top_chord, diagonals[0], (0,0,3))

# Joint B (0,0,2): Bottom chord, Vertical1
create_fixed_constraint(bottom_chord, verticals[0], (0,0,2))

# Joint C (3,0,3): Top chord, Vertical2
create_fixed_constraint(top_chord, verticals[1], (3,0,3))

# Joint D (3,0,2): Bottom chord, Vertical2, Diagonal1, Diagonal2
create_fixed_constraint(bottom_chord, verticals[1], (3,0,2))
create_fixed_constraint(bottom_chord, diagonals[0], (3,0,2))
create_fixed_constraint(bottom_chord, diagonals[1], (3,0,2))

# Joint E (6,0,3): Top chord, Vertical3, Diagonal2
create_fixed_constraint(top_chord, verticals[2], (6,0,3))
create_fixed_constraint(top_chord, diagonals[1], (6,0,3))

# Joint F (6,0,2): Bottom chord, Vertical3
create_fixed_constraint(bottom_chord, verticals[2], (6,0,2))

# Verify structure
print(f"Howe Truss created with {len(verticals)} verticals and {len(diagonals)} diagonals")
print(f"Top chord mass: {top_chord_mass} kg, Force: {top_chord_mass * 9.81:.1f} N")

# Set up scene for physics
bpy.context.scene.frame_end = 250  # Simulation duration
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 50

print("Howe Truss loading dock canopy ready for simulation.")