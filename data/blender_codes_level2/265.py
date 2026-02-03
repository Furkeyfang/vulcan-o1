import bpy
import math
from mathutils import Vector, Matrix

# Clear existing scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Physics setup
bpy.context.scene.gravity = (0, 0, -gravity)
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 50

# Create ground plane
bpy.ops.mesh.primitive_plane_add(size=100, location=(0,0,0))
ground = bpy.context.active_object
ground.name = "Ground"
bpy.ops.rigidbody.object_add()
ground.rigid_body.type = 'PASSIVE'

# Helper function for fixed constraints
def add_fixed_constraint(obj1, obj2):
    bpy.ops.rigidbody.constraint_add()
    constraint = bpy.context.active_object
    constraint.name = f"Fixed_{obj1.name}_{obj2.name}"
    constraint.rigid_body_constraint.type = 'FIXED'
    constraint.rigid_body_constraint.object1 = obj1
    constraint.rigid_body_constraint.object2 = obj2

# Create lower deck
bpy.ops.mesh.primitive_cube_add(size=1, location=(0,0,lower_deck_z))
lower_deck = bpy.context.active_object
lower_deck.name = "Lower_Deck"
lower_deck.scale = (deck_length, deck_width, deck_thickness)
bpy.ops.rigidbody.object_add()
lower_deck.rigid_body.type = 'ACTIVE'
lower_deck.rigid_body.mass = lower_mass_kg
lower_deck.rigid_body.collision_shape = 'BOX'

# Create upper deck
bpy.ops.mesh.primitive_cube_add(size=1, location=(0,0,upper_deck_z))
upper_deck = bpy.context.active_object
upper_deck.name = "Upper_Deck"
upper_deck.scale = (deck_length, deck_width, deck_thickness)
bpy.ops.rigidbody.object_add()
upper_deck.rigid_body.type = 'ACTIVE'
upper_deck.rigid_body.mass = upper_mass_kg
upper_deck.rigid_body.collision_shape = 'BOX'

# Create columns (8 total: 4 ground-to-lower, 4 lower-to-upper)
column_locations = [
    (-column_x_offset, -column_y_offset),
    (-column_x_offset, column_y_offset),
    (column_x_offset, -column_y_offset),
    (column_x_offset, column_y_offset)
]

columns = []
for i, (x, y) in enumerate(column_locations):
    # Lower columns (ground to lower deck)
    z_lower = lower_deck_z - deck_thickness/2 - column_height/2
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x, y, z_lower))
    col_lower = bpy.context.active_object
    col_lower.name = f"Column_Lower_{i}"
    col_lower.scale = (column_width, column_depth, column_height)
    bpy.ops.rigidbody.object_add()
    col_lower.rigid_body.type = 'PASSIVE'
    col_lower.rigid_body.collision_shape = 'BOX'
    columns.append(col_lower)
    
    # Upper columns (lower deck to upper deck)
    z_upper = lower_deck_z + deck_thickness/2 + column_height/2
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x, y, z_upper))
    col_upper = bpy.context.active_object
    col_upper.name = f"Column_Upper_{i}"
    col_upper.scale = (column_width, column_depth, column_height)
    bpy.ops.rigidbody.object_add()
    col_upper.rigid_body.type = 'PASSIVE'
    col_upper.rigid_body.collision_shape = 'BOX'
    columns.append(col_upper)

# Create cross-bracing (2 diagonal beams)
# Diagonal between (-7.25,-1.25) and (7.25,1.25) at mid-height
start_point = Vector((-column_x_offset, -column_y_offset, lower_deck_z + deck_thickness/2 + column_height/2))
end_point = Vector((column_x_offset, column_y_offset, lower_deck_z + deck_thickness/2 + column_height/2))
direction = end_point - start_point
length = direction.length
center = (start_point + end_point) / 2

bpy.ops.mesh.primitive_cube_add(size=1, location=center)
cross1 = bpy.context.active_object
cross1.name = "Cross_Brace_1"
cross1.scale = (cross_beam_width, cross_beam_depth, cross_beam_length)

# Rotate to align with diagonal
cross1.rotation_euler = Vector((0,0,1)).rotation_difference(direction.normalized()).to_euler()
bpy.ops.rigidbody.object_add()
cross1.rigid_body.type = 'PASSIVE'
cross1.rigid_body.collision_shape = 'BOX'

# Second diagonal (opposite corners)
start_point2 = Vector((-column_x_offset, column_y_offset, lower_deck_z + deck_thickness/2 + column_height/2))
end_point2 = Vector((column_x_offset, -column_y_offset, lower_deck_z + deck_thickness/2 + column_height/2))
direction2 = end_point2 - start_point2
center2 = (start_point2 + end_point2) / 2

bpy.ops.mesh.primitive_cube_add(size=1, location=center2)
cross2 = bpy.context.active_object
cross2.name = "Cross_Brace_2"
cross2.scale = (cross_beam_width, cross_beam_depth, cross_beam_length)
cross2.rotation_euler = Vector((0,0,1)).rotation_difference(direction2.normalized()).to_euler()
bpy.ops.rigidbody.object_add()
cross2.rigid_body.type = 'PASSIVE'
cross2.rigid_body.collision_shape = 'BOX'

# Apply fixed constraints
# Lower deck to lower columns
for i in range(4):
    add_fixed_constraint(lower_deck, columns[i*2])
    add_fixed_constraint(columns[i*2], ground)  # Columns fixed to ground

# Upper deck to upper columns and lower columns
for i in range(4):
    add_fixed_constraint(upper_deck, columns[i*2 + 1])
    add_fixed_constraint(columns[i*2 + 1], columns[i*2])  # Column continuity

# Cross-bracing to columns
add_fixed_constraint(cross1, columns[0])  # (-,-) lower column
add_fixed_constraint(cross1, columns[3])  # (+,+) upper column
add_fixed_constraint(cross2, columns[1])  # (-,+) lower column
add_fixed_constraint(cross2, columns[2])  # (+,-) upper column

# Set simulation parameters
bpy.context.scene.frame_end = simulation_frames

# Run simulation
print("Starting physics simulation...")
bpy.ops.ptcache.bake_all(bake=True)

# Verification
bpy.context.scene.frame_set(simulation_frames)
lower_final = lower_deck.location.z
upper_final = upper_deck.location.z

lower_dev = abs(lower_final - lower_deck_z) / lower_deck_z
upper_dev = abs(upper_final - upper_deck_z) / upper_deck_z

print(f"Lower deck final Z: {lower_final:.3f}m (deviation: {lower_dev*100:.1f}%)")
print(f"Upper deck final Z: {upper_final:.3f}m (deviation: {upper_dev*100:.1f}%)")

if lower_dev < position_tolerance and upper_dev < position_tolerance:
    print("✓ Bridge passed structural integrity test")
else:
    print("✗ Bridge deformation exceeds 5% tolerance")