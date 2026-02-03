import bpy
from mathutils import Matrix, Vector
import math

# Clear existing scene
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

# Extract parameters
platform_dim = Vector((6.0, 4.0, 0.5))
platform_loc = Vector((0.0, 0.0, 4.0))
mast_radius = 0.3
mast_height = 5.0
mast_loc = Vector((0.0, -2.0, 6.75))
boom_dim = Vector((8.0, 0.5, 0.5))
boom_loc = Vector((4.0, -2.0, 9.25))
load_size = 0.8
load_mass = 500.0
load_loc = Vector((8.0, -2.0, 0.0))
boom_hinge_pivot = Vector((0.0, -2.0, 9.25))
boom_hinge_axis = Vector((0.0, 0.0, 1.0))
load_hinge_pivot = Vector((8.0, -2.0, 9.25))
load_hinge_axis = Vector((0.0, 1.0, 0.0))
boom_motor_velocity = 1.0
load_motor_velocity = 0.5

# Create platform (passive rigid body)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=platform_loc)
platform = bpy.context.active_object
platform.scale = platform_dim
bpy.ops.rigidbody.object_add()
platform.rigid_body.type = 'PASSIVE'

# Create mast (active rigid body)
bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=mast_radius, depth=mast_height, location=mast_loc)
mast = bpy.context.active_object
bpy.ops.rigidbody.object_add()
mast.rigid_body.type = 'ACTIVE'
# Adjust mass if needed, but default is fine

# Fixed constraint between platform and mast
bpy.ops.object.select_all(action='DESELECT')
platform.select_set(True)
mast.select_set(True)
bpy.context.view_layer.objects.active = platform
bpy.ops.rigidbody.connect_add(type='FIXED')

# Create boom (active rigid body)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=boom_loc)
boom = bpy.context.active_object
boom.scale = boom_dim
bpy.ops.rigidbody.object_add()
boom.rigid_body.type = 'ACTIVE'

# Hinge constraint between mast and boom (horizontal rotation)
# Create an empty object for the constraint
bpy.ops.object.empty_add(type='PLAIN_AXES', location=boom_hinge_pivot)
hinge1 = bpy.context.active_object
hinge1.name = "Hinge_Boom"
bpy.ops.rigidbody.constraint_add(type='HINGE')
constraint1 = hinge1.rigid_body_constraint
constraint1.object1 = mast
constraint1.object2 = boom
# Align empty's Z-axis with world Z (hinge axis)
hinge1.rotation_euler = (0.0, 0.0, 0.0)
constraint1.use_motor = True
constraint1.motor_target_velocity = boom_motor_velocity

# Create load (active rigid body with mass)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=load_loc)
load = bpy.context.active_object
load.scale = (load_size, load_size, load_size)
bpy.ops.rigidbody.object_add()
load.rigid_body.type = 'ACTIVE'
load.rigid_body.mass = load_mass

# Hinge constraint between boom and load (vertical swing)
bpy.ops.object.empty_add(type='PLAIN_AXES', location=load_hinge_pivot)
hinge2 = bpy.context.active_object
hinge2.name = "Hinge_Load"
bpy.ops.rigidbody.constraint_add(type='HINGE')
constraint2 = hinge2.rigid_body_constraint
constraint2.object1 = boom
constraint2.object2 = load
# Rotate empty so its Z-axis aligns with world Y (hinge axis)
hinge2.rotation_euler = (math.pi/2, 0.0, 0.0)
constraint2.use_motor = True
constraint2.motor_target_velocity = load_motor_velocity

# Set world gravity to default (already -9.81 in Z)
rb_world = bpy.context.scene.rigidbody_world
if rb_world:
    rb_world.gravity = (0.0, 0.0, -9.81)

# Optional: Set simulation end frame to 300 for verification
bpy.context.scene.frame_end = 300