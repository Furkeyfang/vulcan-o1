import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Enable rigid body physics
if bpy.context.scene.rigidbody_world is None:
    bpy.ops.rigidbody.world_add()
bpy.context.scene.rigidbody_world.enabled = True

# Parameters from summary
col_radius = 0.5
col_height = 4.0
col_loc = (0.0, 0.0, 2.0)

beam_dim = (3.0, 0.5, 0.5)
beam_loc = (1.5, 0.0, 4.25)

platform_dim = (3.0, 2.0, 0.1)
platform_loc = (1.5, 0.0, 4.55)

load_dim = (0.5, 0.5, 0.5)
load_mass = 300.0
load_loc = (3.0, 0.0, 4.85)

steel_density = 7850.0

# 1. Create GROUND (large passive plane)
bpy.ops.mesh.primitive_plane_add(size=20.0, location=(0,0,-0.1))
ground = bpy.context.active_object
ground.name = "Ground"
ground.scale = (10, 10, 1)
bpy.ops.rigidbody.object_add()
ground.rigid_body.type = 'PASSIVE'

# 2. Create COLUMN (vertical support)
bpy.ops.mesh.primitive_cylinder_add(
    vertices=32,
    radius=col_radius,
    depth=col_height,
    location=col_loc
)
column = bpy.context.active_object
column.name = "Column"
bpy.ops.rigidbody.object_add()
column.rigid_body.type = 'PASSIVE'
column.rigid_body.mass = steel_density * (math.pi * col_radius**2 * col_height)

# 3. Create BEAM (horizontal cantilever)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=beam_loc)
beam = bpy.context.active_object
beam.name = "Beam"
beam.scale = (beam_dim[0]/2, beam_dim[1]/2, beam_dim[2]/2)
bpy.ops.rigidbody.object_add()
beam.rigid_body.type = 'PASSIVE'
beam.rigid_body.mass = steel_density * (beam_dim[0] * beam_dim[1] * beam_dim[2])

# 4. Create PLATFORM
bpy.ops.mesh.primitive_cube_add(size=1.0, location=platform_loc)
platform = bpy.context.active_object
platform.name = "Platform"
platform.scale = (platform_dim[0]/2, platform_dim[1]/2, platform_dim[2]/2)
bpy.ops.rigidbody.object_add()
platform.rigid_body.type = 'PASSIVE'
platform.rigid_body.mass = steel_density * (platform_dim[0] * platform_dim[1] * platform_dim[2])

# 5. Create LOAD
bpy.ops.mesh.primitive_cube_add(size=1.0, location=load_loc)
load = bpy.context.active_object
load.name = "Load"
load.scale = (load_dim[0]/2, load_dim[1]/2, load_dim[2]/2)
bpy.ops.rigidbody.object_add()
load.rigid_body.type = 'ACTIVE'
load.rigid_body.mass = load_mass

# 6. Create FIXED CONSTRAINTS
def add_fixed_constraint(obj1, obj2, name):
    """Create fixed constraint between two objects"""
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=obj1.location)
    constraint = bpy.context.active_object
    constraint.name = name
    bpy.ops.rigidbody.constraint_add()
    constraint.rigid_body_constraint.type = 'FIXED'
    constraint.rigid_body_constraint.object1 = obj1
    constraint.rigid_body_constraint.object2 = obj2

# Column to Beam constraint
add_fixed_constraint(column, beam, "Column_Beam_Constraint")

# Beam to Platform constraint  
add_fixed_constraint(beam, platform, "Beam_Platform_Constraint")

# Platform to Load constraint
add_fixed_constraint(platform, load, "Platform_Load_Constraint")

print("Cantilever museum exhibit created successfully")
print(f"Projection distance: {load_loc[0]} m")
print(f"Load mass: {load_mass} kg")