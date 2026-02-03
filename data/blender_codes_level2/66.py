import bpy
import math
from mathutils import Matrix

# Clear existing scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Parameters from summary
span = 9.0
truss_height = 1.5
truss_width = 0.5
chord_cs = 0.1
num_triangles = 6
num_nodes = 7
node_spacing = span / num_triangles
diag_length = node_spacing / math.cos(math.radians(60))
diag_angle = math.radians(60)
support_x = [-span/2, span/2]
load_force = 600.0 * 9.81
density = 7850.0

# Calculate node positions
bottom_nodes = [( -span/2 + i*node_spacing, 0.0, 0.0) for i in range(num_nodes)]
top_nodes =    [( -span/2 + i*node_spacing, 0.0, truss_height) for i in range(num_nodes)]

# Function to create rigid body member
def create_member(name, location, scale, rotation=None, passive=False):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location)
    member = bpy.context.active_object
    member.name = name
    member.scale = scale
    
    if rotation:
        member.rotation_euler = rotation
    
    # Add rigid body
    bpy.ops.rigidbody.object_add()
    member.rigid_body.type = 'PASSIVE' if passive else 'ACTIVE'
    member.rigid_body.collision_shape = 'BOX'
    member.rigid_body.mass = scale[0] * scale[1] * scale[2] * density
    
    return member

# Create support nodes (passive rigid bodies)
supports = []
for i, x in enumerate(support_x):
    supp = create_member(
        f"Support_{i}",
        (x, 0.0, -0.25),  # Slightly below bottom chord
        (0.2, truss_width, 0.5),
        passive=True
    )
    supports.append(supp)

# Create bottom chord members
bottom_chords = []
for i in range(num_nodes - 1):
    x_center = (bottom_nodes[i][0] + bottom_nodes[i+1][0]) / 2
    chord = create_member(
        f"Bottom_Chord_{i}",
        (x_center, 0.0, 0.0),
        (node_spacing, truss_width, chord_cs)
    )
    bottom_chords.append(chord)

# Create top chord members
top_chords = []
for i in range(num_nodes - 1):
    x_center = (top_nodes[i][0] + top_nodes[i+1][0]) / 2
    chord = create_member(
        f"Top_Chord_{i}",
        (x_center, 0.0, truss_height),
        (node_spacing, truss_width, chord_cs)
    )
    top_chords.append(chord)

# Create diagonal members (Warren pattern)
diagonals = []
for i in range(num_triangles):
    if i % 2 == 0:  # Ascending diagonal
        start = bottom_nodes[i]
        end = top_nodes[i+1]
    else:  # Descending diagonal
        start = top_nodes[i]
        end = bottom_nodes[i+1]
    
    # Center position
    center_x = (start[0] + end[0]) / 2
    center_z = (start[2] + end[2]) / 2
    
    # Rotation angle
    dx = end[0] - start[0]
    dz = end[2] - start[2]
    angle = math.atan2(dz, dx)
    
    diag = create_member(
        f"Diagonal_{i}",
        (center_x, 0.0, center_z),
        (diag_length, truss_width, chord_cs),
        rotation=(0.0, 0.0, angle)
    )
    diagonals.append(diag)

# Create fixed constraints between connected members
def create_fixed_constraint(obj1, obj2):
    # Select and activate objects
    bpy.ops.object.select_all(action='DESELECT')
    obj1.select_set(True)
    obj2.select_set(True)
    bpy.context.view_layer.objects.active = obj1
    
    # Add constraint
    bpy.ops.rigidbody.constraint_add()
    constraint = bpy.context.active_object
    constraint.name = f"Fix_{obj1.name}_{obj2.name}"
    constraint.rigid_body_constraint.type = 'FIXED'
    constraint.rigid_body_constraint.object1 = obj1
    constraint.rigid_body_constraint.object2 = obj2

# Connect chords at nodes (simplified - connect adjacent chord segments)
for i in range(len(bottom_chords) - 1):
    create_fixed_constraint(bottom_chords[i], bottom_chords[i+1])
for i in range(len(top_chords) - 1):
    create_fixed_constraint(top_chords[i], top_chords[i+1])

# Connect diagonals to chords at their endpoints
for i, diag in enumerate(diagonals):
    if i % 2 == 0:  # Ascending: bottom[i] to top[i+1]
        create_fixed_constraint(diag, bottom_chords[i])
        create_fixed_constraint(diag, top_chords[i])
    else:  # Descending: top[i] to bottom[i+1]
        create_fixed_constraint(diag, top_chords[i])
        create_fixed_constraint(diag, bottom_chords[i])

# Connect end chords to supports
create_fixed_constraint(bottom_chords[0], supports[0])
create_fixed_constraint(bottom_chords[-1], supports[1])

# Apply downward force at center top node
# Create force field localized at center
bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, truss_height))
force_empty = bpy.context.active_object
force_empty.name = "Load_Force"

bpy.ops.object.forcefield_add()
force_field = bpy.context.active_object
force_field.field.type = 'FORCE'
force_field.field.strength = -load_force  # Negative for downward
force_field.field.use_max_distance = True
force_field.field.distance_max = 0.5  # Affect only nearby objects
force_field.field.falloff_power = 2.0

# Link force field to empty
force_field.parent = force_empty
force_field.matrix_parent_inverse = force_empty.matrix_world.inverted()

# Setup physics world
bpy.context.scene.use_gravity = True
bpy.context.scene.gravity = (0, 0, -9.81)
bpy.context.scene.rigidbody_world.steps_per_second = 250
bpy.context.scene.rigidbody_world.solver_iterations = 50

print("Warren truss bridge constructed with fixed joints.")
print(f"Design load: {600}kg ({load_force:.1f}N) at center span.")
print(f"Supports at X = {support_x}")