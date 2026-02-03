import bpy
import mathutils

# Clear existing objects
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

# Extract parameters from summary
tower_dim = (2.0, 2.0, 14.0)
tower_loc = (0.0, 0.0, 7.0)
platform_dim = (3.0, 3.0, 0.5)
platform_loc = (0.0, 0.0, 14.25)
load_mass = 200.0

# Create main tower (vertical rectangular prism)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=tower_loc)
tower = bpy.context.active_object
tower.name = "Signal_Tower"
tower.scale = tower_dim
# Set as passive rigid body (immovable)
bpy.ops.rigidbody.object_add()
tower.rigid_body.type = 'PASSIVE'
tower.rigid_body.collision_shape = 'BOX'

# Create platform at top
bpy.ops.mesh.primitive_cube_add(size=1.0, location=platform_loc)
platform = bpy.context.active_object
platform.name = "Load_Platform"
platform.scale = platform_dim
# Set as active rigid body with specified mass
bpy.ops.rigidbody.object_add()
platform.rigid_body.type = 'ACTIVE'
platform.rigid_body.mass = load_mass
platform.rigid_body.collision_shape = 'BOX'

# Create fixed constraint between platform and tower
# Constraints must be added to an object (here platform) then targeted to tower
bpy.ops.rigidbody.constraint_add()
constraint = bpy.context.active_object
constraint.name = "Fixed_Attachment"
constraint.rigid_body_constraint.type = 'FIXED'
constraint.rigid_body_constraint.object1 = platform
constraint.rigid_body_constraint.object2 = tower
# Position constraint at the interface (top of tower)
constraint.location = (0.0, 0.0, 14.0)

# Ensure rigid body world exists and set gravity (default -9.81 Z)
if bpy.context.scene.rigidbody_world is None:
    bpy.ops.rigidbody.world_add()