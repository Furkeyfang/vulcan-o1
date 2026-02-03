import bpy
import mathutils

# Clear existing scene
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

# Parameters from summary
deck_dim = (12.0, 3.0, 0.5)
deck_loc = (0.0, 0.0, 0.75)
col_radius = 0.5
col_height = 2.0
col_left_loc = (-5.0, 0.0, 0.25)
col_right_loc = (5.0, 0.0, 0.25)
cube_dim = (1.0, 1.0, 1.0)
cube_mass = 700.0
cube_loc = (0.0, 1.0, 1.5)
frame_end = 100

# Enable rigid body physics
if bpy.context.scene.rigidbody_world is None:
    bpy.ops.rigidbody.world_add()

# Create Deck
bpy.ops.mesh.primitive_cube_add(size=1, location=deck_loc)
deck = bpy.context.active_object
deck.name = "BridgeDeck"
deck.scale = deck_dim
bpy.ops.rigidbody.object_add()
deck.rigid_body.type = 'PASSIVE'
deck.rigid_body.collision_shape = 'BOX'

# Create Left Column
bpy.ops.mesh.primitive_cylinder_add(
    vertices=32,
    radius=col_radius,
    depth=col_height,
    location=col_left_loc
)
col_left = bpy.context.active_object
col_left.name = "LeftColumn"
col_left.rotation_euler = (0, 0, 0)  # Ensure vertical orientation
bpy.ops.rigidbody.object_add()
col_left.rigid_body.type = 'PASSIVE'
col_left.rigid_body.collision_shape = 'CYLINDER'

# Create Right Column
bpy.ops.mesh.primitive_cylinder_add(
    vertices=32,
    radius=col_radius,
    depth=col_height,
    location=col_right_loc
)
col_right = bpy.context.active_object
col_right.name = "RightColumn"
col_right.rotation_euler = (0, 0, 0)
bpy.ops.rigidbody.object_add()
col_right.rigid_body.type = 'PASSIVE'
col_right.rigid_body.collision_shape = 'CYLINDER'

# Create Fixed Constraints
def add_fixed_constraint(obj1, obj2, name):
    # Create empty for constraint
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=obj1.location)
    constraint = bpy.context.active_object
    constraint.name = name
    bpy.ops.rigidbody.constraint_add()
    rb_constraint = constraint.rigid_body_constraint
    rb_constraint.type = 'FIXED'
    rb_constraint.object1 = obj1
    rb_constraint.object2 = obj2

add_fixed_constraint(deck, col_left, "Deck_LeftColumn_Fixed")
add_fixed_constraint(deck, col_right, "Deck_RightColumn_Fixed")

# Create Live Load Cube
bpy.ops.mesh.primitive_cube_add(size=1, location=cube_loc)
cube = bpy.context.active_object
cube.name = "LiveLoad"
cube.scale = cube_dim
bpy.ops.rigidbody.object_add()
cube.rigid_body.type = 'ACTIVE'
cube.rigid_body.mass = cube_mass
cube.rigid_body.collision_shape = 'BOX'

# Set simulation frames
bpy.context.scene.frame_end = frame_end

# Optional: Bake physics for verification (commented for headless)
# bpy.ops.ptcache.bake_all(bake=True)

print("Bridge construction complete. Simulation ready for 100 frames.")