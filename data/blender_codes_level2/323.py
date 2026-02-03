import bpy
import mathutils

# Clear existing scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Define variables from parameter summary
deck_length = 14.0
deck_width = 4.0
deck_thickness = 0.5
deck_center = (7.0, 0.0, 0.5)

parapet_length = 14.0
parapet_thickness = 0.2
parapet_height = 1.0
loaded_parapet_y = 1.9
unloaded_parapet_y = -1.9
parapet_center_z = 1.25

cube_size = 0.2
cube_mass = 30.0
num_cubes = 10
cube_spacing = 1.4
cube_start_x = 0.7
cube_y = 2.1
cube_z = 1.85

anchor1_x = 0.0
anchor2_x = 14.0
anchor_y = 0.0
anchor_z = 0.0
anchor_size = 0.5

# Create Bridge Deck
bpy.ops.mesh.primitive_cube_add(size=1.0, location=deck_center)
deck = bpy.context.active_object
deck.scale = (deck_length, deck_width, deck_thickness)
deck.name = "Bridge_Deck"
bpy.ops.rigidbody.object_add()
deck.rigid_body.type = 'PASSIVE'
deck.rigid_body.collision_shape = 'BOX'

# Create Ground Anchors (Fixed to World)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(anchor1_x, anchor_y, anchor_z))
anchor1 = bpy.context.active_object
anchor1.scale = (anchor_size, anchor_size, anchor_size)
anchor1.name = "Ground_Anchor1"
bpy.ops.rigidbody.object_add()
anchor1.rigid_body.type = 'PASSIVE'

bpy.ops.mesh.primitive_cube_add(size=1.0, location=(anchor2_x, anchor_y, anchor_z))
anchor2 = bpy.context.active_object
anchor2.scale = (anchor_size, anchor_size, anchor_size)
anchor2.name = "Ground_Anchor2"
bpy.ops.rigidbody.object_add()
anchor2.rigid_body.type = 'PASSIVE'

# Create Loaded Parapet
bpy.ops.mesh.primitive_cube_add(
    size=1.0,
    location=(deck_center[0], loaded_parapet_y, parapet_center_z)
)
loaded_parapet = bpy.context.active_object
loaded_parapet.scale = (parapet_length, parapet_thickness, parapet_height)
loaded_parapet.name = "Loaded_Parapet"
bpy.ops.rigidbody.object_add()
loaded_parapet.rigid_body.type = 'PASSIVE'
loaded_parapet.rigid_body.collision_shape = 'BOX'

# Create Unloaded Parapet
bpy.ops.mesh.primitive_cube_add(
    size=1.0,
    location=(deck_center[0], unloaded_parapet_y, parapet_center_z)
)
unloaded_parapet = bpy.context.active_object
unloaded_parapet.scale = (parapet_length, parapet_thickness, parapet_height)
unloaded_parapet.name = "Unloaded_Parapet"
bpy.ops.rigidbody.object_add()
unloaded_parapet.rigid_body.type = 'PASSIVE'
unloaded_parapet.rigid_body.collision_shape = 'BOX'

# Create Load Cubes
for i in range(num_cubes):
    cube_x = cube_start_x + i * cube_spacing
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(cube_x, cube_y, cube_z))
    cube = bpy.context.active_object
    cube.scale = (cube_size, cube_size, cube_size)
    cube.name = f"Load_Cube_{i+1}"
    bpy.ops.rigidbody.object_add()
    cube.rigid_body.type = 'ACTIVE'
    cube.rigid_body.mass = cube_mass
    cube.rigid_body.collision_shape = 'BOX'

# Create Fixed Constraints
def create_fixed_constraint(obj_a, obj_b):
    bpy.ops.rigidbody.constraint_add()
    constraint = bpy.context.active_object
    constraint.empty_display_type = 'ARROWS'
    constraint.name = f"Fixed_{obj_a.name}_to_{obj_b.name}"
    constraint.rigid_body_constraint.type = 'FIXED'
    constraint.rigid_body_constraint.object1 = obj_a
    constraint.rigid_body_constraint.object2 = obj_b
    constraint.location = (0, 0, 0)

# Deck to Ground Anchors
create_fixed_constraint(anchor1, deck)
create_fixed_constraint(anchor2, deck)

# Parapets to Deck
create_fixed_constraint(deck, loaded_parapet)
create_fixed_constraint(deck, unloaded_parapet)

# Load Cubes to Loaded Parapet
for i in range(num_cubes):
    cube = bpy.data.objects.get(f"Load_Cube_{i+1}")
    if cube:
        create_fixed_constraint(loaded_parapet, cube)

# Setup Physics World
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 50
bpy.context.scene.frame_end = 100

# Verification: Run simulation (headless compatible)
print("Bridge construction complete. Simulation ready for 100 frames.")