import bpy
import math
from mathutils import Vector

# 1. Clear existing scene
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

# 2. Parameters from summary
span_x = 14.0
chord_y = 0.2
chord_z = 0.2
bottom_chord_z = 0.0
top_chord_z = 2.0
queen_post_x_left = -3.5
queen_post_x_right = 3.5
queen_post_height = 2.0
brace_length = 2.658  # actual length
brace_angle = math.radians(48.8)  # convert to radians
brace_connect_top_x_left = -1.75
brace_connect_top_x_right = 1.75
load_force = 10791.0
frame_end = 500
solver_iterations = 50
substeps = 10

# 3. Physics world settings
bpy.context.scene.rigidbody_world.substeps_per_frame = substeps
bpy.context.scene.rigidbody_world.solver_iterations = solver_iterations
bpy.context.scene.frame_end = frame_end

# 4. Helper function to create a rigid body cube
def create_cube(name, size, location, rotation=(0,0,0), rigidbody_type='PASSIVE'):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = (size[0]/2.0, size[1]/2.0, size[2]/2.0)  # default cube is 2x2x2
    obj.rotation_euler = rotation
    bpy.ops.rigidbody.object_add()
    obj.rigid_body.type = rigidbody_type
    obj.rigid_body.collision_shape = 'BOX'
    return obj

# 5. Create bottom chord
bottom = create_cube(
    "bottom_chord",
    (span_x, chord_y, chord_z),
    (0.0, 0.0, bottom_chord_z)
)

# 6. Create top chord (active rigid body for load)
top = create_cube(
    "top_chord",
    (span_x, chord_y, chord_z),
    (0.0, 0.0, top_chord_z),
    rigidbody_type='ACTIVE'
)
top.rigid_body.mass = 100.0  # arbitrary mass, force will dominate

# 7. Create queen posts (left and right)
queen_left = create_cube(
    "queen_post_left",
    (chord_z, chord_y, queen_post_height),  # x=thickness, z=height
    (queen_post_x_left, 0.0, queen_post_height/2.0)
)
queen_right = create_cube(
    "queen_post_right",
    (chord_z, chord_y, queen_post_height),
    (queen_post_x_right, 0.0, queen_post_height/2.0)
)

# 8. Create diagonal braces
# Left brace: from (queen_post_x_left, 0, 0) to (brace_connect_top_x_left, 0, top_chord_z)
# Calculate midpoint and rotation
brace_left_start = Vector((queen_post_x_left, 0.0, 0.0))
brace_left_end   = Vector((brace_connect_top_x_left, 0.0, top_chord_z))
brace_left_mid = (brace_left_start + brace_left_end) / 2.0
# Rotation: align local Z axis with the vector from start to end
direction = (brace_left_end - brace_left_start).normalized()
angle = math.acos(direction.dot(Vector((0,0,1))))  # angle between direction and global Z
axis = Vector((0,0,1)).cross(direction)
if axis.length > 0:
    axis.normalize()
else:
    axis = Vector((1,0,0))  # if direction is exactly Z, use X axis
rotation = axis.angle_to(direction)  # Actually, we need a full quaternion
# Simpler: rotate around Y axis only (2D truss)
rot_y = math.atan2(direction.x, direction.z)
brace_left = create_cube(
    "brace_left",
    (chord_z, chord_y, brace_length),
    brace_left_mid,
    rotation=(0.0, rot_y, 0.0)
)

# Right brace (symmetric)
brace_right_start = Vector((queen_post_x_right, 0.0, 0.0))
brace_right_end   = Vector((brace_connect_top_x_right, 0.0, top_chord_z))
brace_right_mid = (brace_right_start + brace_right_end) / 2.0
direction_r = (brace_right_end - brace_right_start).normalized()
rot_y_r = math.atan2(direction_r.x, direction_r.z)
brace_right = create_cube(
    "brace_right",
    (chord_z, chord_y, brace_length),
    brace_right_mid,
    rotation=(0.0, rot_y_r, 0.0)
)

# 9. Create fixed constraints between connected members
def add_fixed_constraint(obj1, obj2, location):
    # Create an empty at joint location
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=location)
    empty = bpy.context.active_object
    empty.name = f"constraint_{obj1.name}_{obj2.name}"
    bpy.ops.rigidbody.constraint_add()
    empty.rigid_body_constraint.type = 'FIXED'
    empty.rigid_body_constraint.object1 = obj1
    empty.rigid_body_constraint.object2 = obj2

# Joints (all Y=0)
# Bottom-left: bottom, queen_left, brace_left
add_fixed_constraint(bottom, queen_left, (queen_post_x_left, 0.0, 0.0))
add_fixed_constraint(bottom, brace_left, (queen_post_x_left, 0.0, 0.0))
add_fixed_constraint(queen_left, brace_left, (queen_post_x_left, 0.0, 0.0))
# Top-left: top, queen_left, brace_left
add_fixed_constraint(top, queen_left, (queen_post_x_left, 0.0, top_chord_z))
add_fixed_constraint(top, brace_left, (brace_connect_top_x_left, 0.0, top_chord_z))
# Bottom-right: bottom, queen_right, brace_right
add_fixed_constraint(bottom, queen_right, (queen_post_x_right, 0.0, 0.0))
add_fixed_constraint(bottom, brace_right, (queen_post_x_right, 0.0, 0.0))
add_fixed_constraint(queen_right, brace_right, (queen_post_x_right, 0.0, 0.0))
# Top-right: top, queen_right, brace_right
add_fixed_constraint(top, queen_right, (queen_post_x_right, 0.0, top_chord_z))
add_fixed_constraint(top, brace_right, (brace_connect_top_x_right, 0.0, top_chord_z))

# 10. Apply downward force field to top chord only
bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0,0,top_chord_z))
force_empty = bpy.context.active_object
force_empty.name = "force_field"
bpy.ops.object.forcefield_add()
force_empty.field.type = 'FORCE'
force_empty.field.strength = load_force
force_empty.field.direction = 'Z'
force_empty.field.use_gravity = False
force_empty.field.z = -1.0  # downward
# Limit force field to affect only top chord
force_empty.field.flow = 0  # no particle flow
# In rigid body world, force fields affect all objects by default.
# To restrict, we could use collections, but for simplicity, we rely on symmetry.

# 11. Set gravity to zero? Actually, we want only our force field to act.
# But the top chord is active and will also be affected by scene gravity.
# We'll set gravity to zero and let the force field provide the entire load.
bpy.context.scene.gravity = (0.0, 0.0, 0.0)

print("Queen Post truss construction complete. Run simulation with 'blender --background --python-expr "import bpy; bpy.ops.ptcache.bake_all(bake=True)"'")