import bpy
import math
from mathutils import Vector, Matrix

# Clear scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Parameters from summary
L = 3.0
H = 1.0
D = 0.5
cs = 0.1
bs = 0.1
diag_len = math.sqrt(1.5**2 + 1**2)
diag_angle = math.atan(1/1.5)  # radians

top_center = (1.5, 0.0, 1.0)
bot_center = (1.5, 0.0, 0.0)

joints = {
    'A': (0.0, 0.0, 0.0),
    'B': (1.5, 0.0, 0.0),
    'C': (3.0, 0.0, 0.0),
    'D': (0.0, 0.0, 1.0),
    'E': (1.5, 0.0, 1.0),
    'F': (3.0, 0.0, 1.0)
}

force_N = 2452.5
frames = 250

# Setup rigid body world
bpy.context.scene.rigidbody_world.substeps_per_frame = 5
bpy.context.scene.rigidbody_world.solver_iterations = 10
bpy.context.scene.frame_end = frames

# 1. Ground base (passive)
bpy.ops.mesh.primitive_cube_add(size=1, location=(1.5, 0, -0.5))
ground = bpy.context.active_object
ground.scale = (L + 1.0, 2.0, 0.5)
bpy.ops.rigidbody.object_add()
ground.rigid_body.type = 'PASSIVE'

# 2. Bottom chord (passive, fixed to ground via constraints later)
bpy.ops.mesh.primitive_cube_add(size=1, location=bot_center)
bot_chord = bpy.context.active_object
bot_chord.scale = (L, cs, cs)
bpy.ops.rigidbody.object_add()
bot_chord.rigid_body.type = 'PASSIVE'

# 3. Top chord (active, will receive load)
bpy.ops.mesh.primitive_cube_add(size=1, location=top_center)
top_chord = bpy.context.active_object
top_chord.scale = (L, cs, cs)
bpy.ops.rigidbody.object_add()
top_chord.rigid_body.type = 'ACTIVE'
top_chord.rigid_body.mass = 50  # approximate mass for top chord itself

# 4. Diagonals (active)
diagonals = []
# Diagonal A->E (from bottom left to top middle)
bpy.ops.mesh.primitive_cube_add(size=1, location=(0.75, 0.1, 0.5))
diag1 = bpy.context.active_object
diag1.scale = (diag_len, bs, bs)
diag1.rotation_euler = (0, diag_angle, 0)  # rotate around Y
bpy.ops.rigidbody.object_add()
diag1.rigid_body.type = 'ACTIVE'
diag1.rigid_body.mass = 5
diagonals.append(diag1)

# Diagonal B->D (from bottom middle to top left)
bpy.ops.mesh.primitive_cube_add(size=1, location=(0.75, -0.1, 0.5))
diag2 = bpy.context.active_object
diag2.scale = (diag_len, bs, bs)
diag2.rotation_euler = (0, -diag_angle, 0)
bpy.ops.rigidbody.object_add()
diag2.rigid_body.type = 'ACTIVE'
diag2.rigid_body.mass = 5
diagonals.append(diag2)

# Diagonal B->F (from bottom middle to top right)
bpy.ops.mesh.primitive_cube_add(size=1, location=(2.25, 0.1, 0.5))
diag3 = bpy.context.active_object
diag3.scale = (diag_len, bs, bs)
diag3.rotation_euler = (0, -diag_angle, 0)  # symmetric to diag2
bpy.ops.rigidbody.object_add()
diag3.rigid_body.type = 'ACTIVE'
diag3.rigid_body.mass = 5
diagonals.append(diag3)

# Diagonal C->E (from bottom right to top middle)
bpy.ops.mesh.primitive_cube_add(size=1, location=(2.25, -0.1, 0.5))
diag4 = bpy.context.active_object
diag4.scale = (diag_len, bs, bs)
diag4.rotation_euler = (0, diag_angle, 0)  # symmetric to diag1
bpy.ops.rigidbody.object_add()
diag4.rigid_body.type = 'ACTIVE'
diag4.rigid_body.mass = 5
diagonals.append(diag4)

# 5. Fixed constraints at joints
def add_fixed_constraint(obj1, obj2, location):
    """Create a fixed rigid body constraint at given world location."""
    # Create empty for constraint
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=location)
    const_obj = bpy.context.active_object
    const_obj.empty_display_size = 0.2
    # Add constraint
    bpy.ops.rigidbody.constraint_add()
    const = const_obj.rigid_body_constraint
    const.type = 'FIXED'
    const.object1 = obj1
    const.object2 = obj2

# Bottom chord to ground at ends A and C
add_fixed_constraint(bot_chord, ground, joints['A'])
add_fixed_constraint(bot_chord, ground, joints['C'])

# Bottom chord to diagonals at A, B, C
add_fixed_constraint(bot_chord, diag1, joints['A'])  # A connects to diag1
add_fixed_constraint(bot_chord, diag2, joints['B'])  # B connects to diag2
add_fixed_constraint(bot_chord, diag3, joints['B'])  # B also connects to diag3
add_fixed_constraint(bot_chord, diag4, joints['C'])  # C connects to diag4

# Top chord to diagonals at D, E, F
add_fixed_constraint(top_chord, diag2, joints['D'])  # D connects to diag2
add_fixed_constraint(top_chord, diag1, joints['E'])  # E connects to diag1
add_fixed_constraint(top_chord, diag4, joints['E'])  # E also connects to diag4
add_fixed_constraint(top_chord, diag3, joints['F'])  # F connects to diag3

# 6. Apply downward force to top chord (uniform distribution)
# Create a force field affecting only top chord
bpy.ops.object.effector_add(type='FORCE', location=(1.5, 0, 1.5))
force = bpy.context.active_object
force.field.strength = -force_N  # Negative Z
force.field.falloff_power = 0  # Uniform
force.field.distance_max = 2.0
force.field.use_max_distance = True
# Limit to top chord via collection (headless workaround)
bpy.ops.object.select_all(action='DESELECT')
top_chord.select_set(True)
bpy.ops.object.move_to_collection(collection_index=0, is_new=True, new_collection_name='ForceTarget')
force.field.collection = bpy.data.collections['ForceTarget']

# 7. Set simulation bake (optional for verification)
bpy.context.scene.rigidbody_world.point_cache.frame_start = 1
bpy.context.scene.rigidbody_world.point_cache.frame_end = frames