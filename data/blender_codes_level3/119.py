import bpy
import math

# Clear existing scene
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)

# Extract parameters from summary
base_dim = (3.0, 3.0, 0.5)
base_loc = (0.0, 0.0, 0.25)
column_dim = (0.5, 0.5, 4.0)
column_loc = (0.0, 0.0, 2.5)
boom_dim = (4.0, 0.5, 0.5)
boom_loc = (2.0, 0.0, 4.75)
platform_dim = (2.0, 2.0, 0.2)
platform_loc = (4.0, 0.0, 4.4)
hinge_axis = (0.0, 0.0, 1.0)
target_velocity = 0.3 * math.pi  # rad/s
simulation_frames = 100

# Ensure rigid body world exists
if bpy.context.scene.rigidbody_world is None:
    bpy.ops.rigidbody.world_add()

# Helper function to create a rigid body object
def create_rb_object(name, dim, loc, scale_factors, rb_type='PASSIVE', mesh_type='CUBE'):
    if mesh_type == 'CUBE':
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=loc)
    elif mesh_type == 'SPHERE':
        bpy.ops.mesh.primitive_uv_sphere_add(radius=1.0, location=loc)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = (dim[0] * scale_factors[0], 
                 dim[1] * scale_factors[1], 
                 dim[2] * scale_factors[2])
    bpy.ops.rigidbody.object_add()
    obj.rigid_body.type = rb_type
    obj.rigid_body.collision_shape = 'BOX'
    return obj

# Create base platform
base = create_rb_object("Base", base_dim, base_loc, (0.5, 0.5, 0.5), 'PASSIVE', 'CUBE')
base.rigid_body.collision_shape = 'BOX'

# Create vertical column
column = create_rb_object("Column", column_dim, column_loc, (0.5, 0.5, 0.5), 'PASSIVE', 'CUBE')
column.rigid_body.collision_shape = 'BOX'

# Create boom arm
boom = create_rb_object("Boom", boom_dim, boom_loc, (0.5, 0.5, 0.5), 'PASSIVE', 'CUBE')
boom.rigid_body.collision_shape = 'BOX'

# Create rotating platform (active rigid body)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=platform_loc)
platform = bpy.context.active_object
platform.name = "RotatingPlatform"
platform.scale = (platform_dim[0] * 0.5, platform_dim[1] * 0.5, platform_dim[2] * 0.5)
bpy.ops.rigidbody.object_add()
platform.rigid_body.type = 'ACTIVE'
platform.rigid_body.collision_shape = 'BOX'

# Add fixed constraint between base and world (empty second object = world)
bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0,0,0))
world_empty = bpy.context.active_object
world_empty.name = "WorldAnchor"

def add_fixed_constraint(obj1, obj2=None):
    bpy.context.view_layer.objects.active = obj1
    bpy.ops.rigidbody.constraint_add()
    con = obj1.rigid_body_constraints[-1]
    con.type = 'FIXED'
    if obj2:
        con.object2 = obj2

# Bond base to world (fixed)
add_fixed_constraint(base, world_empty)
# Bond column to base
add_fixed_constraint(column, base)
# Bond boom to column
add_fixed_constraint(boom, column)

# Add hinge constraint between boom and rotating platform
bpy.context.view_layer.objects.active = boom
bpy.ops.rigidbody.constraint_add()
hinge = boom.rigid_body_constraints[-1]
hinge.type = 'HINGE'
hinge.object2 = platform
hinge.use_limit_z = False
hinge.use_motor_z = True
hinge.motor_velocity_z = target_velocity
hinge.motor_max_impulse_z = 1000.0  # Sufficient torque

# Set simulation frames
bpy.context.scene.frame_end = simulation_frames

# Optional: Set initial rotation of platform to 0 (already at default)
platform.rotation_euler = (0.0, 0.0, 0.0)

# Ensure proper collision margins (optional)
for obj in [base, column, boom, platform]:
    obj.rigid_body.collision_margin = 0.04

print("Crane assembly complete. Rotating platform will rotate at", target_velocity, "rad/s.")