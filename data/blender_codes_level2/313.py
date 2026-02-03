import bpy

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Parameters
column_size = (1.0, 1.0, 5.0)
column_center = (0.0, 0.0, 2.5)

deck_size = (6.0, 3.0, 0.2)
lower_deck_center = (0.5, 0.0, 2.5)
upper_deck_center = (0.5, 0.0, 4.5)

cube_size = (0.5, 0.5, 0.5)
cube_mass = 250.0
lower_cube_center = (2.0, 0.0, 2.85)  # Adjusted to sit on deck
upper_cube_center = (2.0, 0.0, 4.85)

# Create Column
bpy.ops.mesh.primitive_cube_add(size=1, location=column_center)
column = bpy.context.active_object
column.scale = column_size
bpy.ops.rigidbody.object_add()
column.rigid_body.type = 'PASSIVE'
column.name = "Column"

# Create Lower Deck
bpy.ops.mesh.primitive_cube_add(size=1, location=lower_deck_center)
lower_deck = bpy.context.active_object
lower_deck.scale = deck_size
bpy.ops.rigidbody.object_add()
lower_deck.rigid_body.type = 'ACTIVE'
lower_deck.name = "Lower_Deck"

# Create Upper Deck
bpy.ops.mesh.primitive_cube_add(size=1, location=upper_deck_center)
upper_deck = bpy.context.active_object
upper_deck.scale = deck_size
bpy.ops.rigidbody.object_add()
upper_deck.rigid_body.type = 'ACTIVE'
upper_deck.name = "Upper_Deck"

# Create Load Cubes
bpy.ops.mesh.primitive_cube_add(size=1, location=lower_cube_center)
lower_cube = bpy.context.active_object
lower_cube.scale = cube_size
bpy.ops.rigidbody.object_add()
lower_cube.rigid_body.mass = cube_mass
lower_cube.name = "Lower_Load"

bpy.ops.mesh.primitive_cube_add(size=1, location=upper_cube_center)
upper_cube = bpy.context.active_object
upper_cube.scale = cube_size
bpy.ops.rigidbody.object_add()
upper_cube.rigid_body.mass = cube_mass
upper_cube.name = "Upper_Load"

# Add Fixed Constraints between Column and Decks
def add_fixed_constraint(obj_a, obj_b):
    bpy.context.view_layer.objects.active = obj_a
    bpy.ops.rigidbody.constraint_add()
    constraint = obj_a.constraints[-1]
    constraint.type = 'FIXED'
    constraint.object1 = obj_a
    constraint.object2 = obj_b

add_fixed_constraint(column, lower_deck)
add_fixed_constraint(column, upper_deck)

# Set up physics world (default gravity -9.81 m/s^2 along Z)
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 10
bpy.context.scene.frame_end = 100

# Optional: Set collision margins (default is 0.04)
for obj in bpy.data.objects:
    if obj.rigid_body:
        obj.rigid_body.collision_margin = 0.04

print("Double-deck cantilever platform created. Run simulation with frame range 1-100.")