import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Parameters from summary
deck_dim = (16.0, 4.0, 0.5)
deck_center = (0.0, 0.0, 0.5)
support_dim = (1.0, 1.0, 8.0)
left_support_loc = (-8.0, 0.0, -1.1181)
left_support_rot = (0.0, math.radians(70.0), 0.0)  # 70° to radians
right_support_loc = (8.0, 0.0, -1.1181)
right_support_rot = (0.0, math.radians(-70.0), 0.0)  # -70° to radians
load_dim = (2.0, 2.0, 1.0)
load_center = (0.0, 0.0, 1.5)
load_mass = 1100.0

# Create Bridge Deck
bpy.ops.mesh.primitive_cube_add(size=1.0, location=deck_center)
deck = bpy.context.active_object
deck.name = "BridgeDeck"
deck.scale = deck_dim
bpy.ops.rigidbody.object_add()
deck.rigid_body.type = 'PASSIVE'

# Create Left Support
bpy.ops.mesh.primitive_cube_add(size=1.0, location=left_support_loc)
left_support = bpy.context.active_object
left_support.name = "LeftSupport"
left_support.scale = support_dim
left_support.rotation_euler = left_support_rot
bpy.ops.rigidbody.object_add()
left_support.rigid_body.type = 'PASSIVE'

# Create Right Support
bpy.ops.mesh.primitive_cube_add(size=1.0, location=right_support_loc)
right_support = bpy.context.active_object
right_support.name = "RightSupport"
right_support.scale = support_dim
right_support.rotation_euler = right_support_rot
bpy.ops.rigidbody.object_add()
right_support.rigid_body.type = 'PASSIVE'

# Create Load Block
bpy.ops.mesh.primitive_cube_add(size=1.0, location=load_center)
load = bpy.context.active_object
load.name = "LoadBlock"
load.scale = load_dim
bpy.ops.rigidbody.object_add()
load.rigid_body.type = 'ACTIVE'
load.rigid_body.mass = load_mass

# Create Fixed Constraints
def add_fixed_constraint(obj1, obj2):
    """Create a fixed rigid body constraint between two objects"""
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0,0,0))
    empty = bpy.context.active_object
    empty.name = f"Fixed_{obj1.name}_to_{obj2.name}"
    bpy.ops.rigidbody.constraint_add()
    constraint = empty.rigid_body_constraint
    constraint.type = 'FIXED'
    constraint.object1 = obj1
    constraint.object2 = obj2

# Attach supports to deck
add_fixed_constraint(left_support, deck)
add_fixed_constraint(right_support, deck)

# Attach load to deck
add_fixed_constraint(load, deck)

# Set up physics world (gravity)
if bpy.context.scene.rigidbody_world is None:
    bpy.ops.rigidbody.world_add()
bpy.context.scene.rigidbody_world.enabled = True
bpy.context.scene.rigidbody_world.substeps_per_frame = 10
bpy.context.scene.rigidbody_world.solver_iterations = 50

# Ensure proper collision shapes
for obj in [deck, left_support, right_support, load]:
    obj.rigid_body.collision_shape = 'BOX'
    obj.rigid_body.friction = 0.5
    obj.rigid_body.restitution = 0.1

print("Bridge assembly complete with fixed constraints.")