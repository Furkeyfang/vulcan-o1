import bpy
import mathutils
from math import radians

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Variables from parameter summary
beam_dim = (0.3, 0.3, 2.5)
beam_rot_x = radians(-90)  # -90 degrees
beam_loc = (0.0, 1.25, 0.15)
platform_dim = (2.5, 1.5, 0.1)
platform_loc = (0.0, 2.5, 0.15)
load_dim = (0.5, 0.5, 0.5)
load_mass = 350.0
load_loc = (0.0, 2.5, 0.45)
wall_anchor_loc = (0.0, 0.0, 0.0)
simulation_frames = 500

# Enable rigid body world
if bpy.context.scene.rigidbody_world is None:
    bpy.ops.rigidbody.world_add()
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 10

# Create Wall Anchor (invisible empty)
bpy.ops.object.empty_add(type='PLAIN_AXES', location=wall_anchor_loc)
wall_anchor = bpy.context.active_object
wall_anchor.name = "WallAnchor"
bpy.ops.rigidbody.object_add(type='PASSIVE')
wall_anchor.rigid_body.collision_shape = 'MESH'

# Create Cantilever Beam
bpy.ops.mesh.primitive_cube_add(size=1.0, location=beam_loc)
beam = bpy.context.active_object
beam.name = "Beam"
beam.scale = beam_dim
beam.rotation_euler = (beam_rot_x, 0.0, 0.0)
bpy.ops.rigidbody.object_add(type='PASSIVE')
beam.rigid_body.collision_shape = 'CONVEX_HULL'

# Create Platform
bpy.ops.mesh.primitive_cube_add(size=1.0, location=platform_loc)
platform = bpy.context.active_object
platform.name = "Platform"
platform.scale = platform_dim
bpy.ops.rigidbody.object_add(type='PASSIVE')
platform.rigid_body.collision_shape = 'CONVEX_HULL'

# Create Load Cube
bpy.ops.mesh.primitive_cube_add(size=1.0, location=load_loc)
load = bpy.context.active_object
load.name = "Load"
load.scale = load_dim
bpy.ops.rigidbody.object_add(type='ACTIVE')
load.rigid_body.mass = load_mass
load.rigid_body.collision_shape = 'BOX'

# Create Constraints
# 1. Beam fixed to wall anchor
bpy.ops.object.empty_add(type='ARROWS', location=(0,0,0))
constraint1 = bpy.context.active_object
constraint1.name = "BeamToWall_Constraint"
bpy.ops.rigidbody.constraint_add()
constraint1.rigid_body_constraint.type = 'FIXED'
constraint1.rigid_body_constraint.object1 = wall_anchor
constraint1.rigid_body_constraint.object2 = beam

# 2. Platform fixed to beam
bpy.ops.object.empty_add(type='ARROWS', location=platform_loc)
constraint2 = bpy.context.active_object
constraint2.name = "PlatformToBeam_Constraint"
bpy.ops.rigidbody.constraint_add()
constraint2.rigid_body_constraint.type = 'FIXED'
constraint2.rigid_body_constraint.object1 = beam
constraint2.rigid_body_constraint.object2 = platform

# Set simulation length
bpy.context.scene.frame_end = simulation_frames

# Bake physics simulation (headless compatible)
bpy.ops.ptcache.bake_all(bake=True)