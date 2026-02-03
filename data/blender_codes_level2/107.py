import bpy
import mathutils

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Extract parameters from summary
col_size = (0.5, 0.5, 2.0)
col_loc = (0.0, 0.0, 1.0)
beam_size = (3.0, 0.2, 0.2)
beam_loc = (1.5, 0.0, 2.0)
plat_size = (0.5, 0.5, 0.1)
plat_loc = (3.0, 0.0, 2.0)
load_mass = 100.0
sim_frames = 100

# Enable rigid body physics
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 10

# 1. Create vertical support column
bpy.ops.mesh.primitive_cube_add(size=1.0, location=col_loc)
column = bpy.context.active_object
column.name = "Column"
column.scale = col_size
bpy.ops.rigidbody.object_add()
column.rigid_body.type = 'PASSIVE'
column.rigid_body.collision_shape = 'BOX'
column.rigid_body.mass = 1000.0  # Heavy base mass

# 2. Create main beam
bpy.ops.mesh.primitive_cube_add(size=1.0, location=beam_loc)
beam = bpy.context.active_object
beam.name = "MainBeam"
beam.scale = beam_size
bpy.ops.rigidbody.object_add()
beam.rigid_body.type = 'PASSIVE'
beam.rigid_body.collision_shape = 'BOX'
beam.rigid_body.mass = 50.0  # Beam mass

# 3. Create camera platform
bpy.ops.mesh.primitive_cube_add(size=1.0, location=plat_loc)
platform = bpy.context.active_object
platform.name = "CameraPlatform"
platform.scale = plat_size
bpy.ops.rigidbody.object_add()
platform.rigid_body.type = 'ACTIVE'
platform.rigid_body.collision_shape = 'BOX'
platform.rigid_body.mass = load_mass

# 4. Create fixed constraints
# Column to World (simulated by making column passive with heavy mass)
# Beam to Column constraint
beam.select_set(True)
bpy.context.view_layer.objects.active = beam
bpy.ops.rigidbody.constraint_add()
beam_constraint = beam.rigid_body_constraints[-1]
beam_constraint.type = 'FIXED'
# Set constraint location at beam start (0,0,2)
constraint_loc = mathutils.Matrix.Translation((0.0, 0.0, 0.0))
beam_constraint.object1 = column
beam_constraint.disable_collisions = True

# Platform to Beam constraint
platform.select_set(True)
bpy.context.view_layer.objects.active = platform
bpy.ops.rigidbody.constraint_add()
plat_constraint = platform.rigid_body_constraints[-1]
plat_constraint.type = 'FIXED'
plat_constraint.object1 = beam
plat_constraint.disable_collisions = True

# 5. Set simulation parameters
bpy.context.scene.frame_end = sim_frames
bpy.context.scene.rigidbody_world.enabled = True
bpy.context.scene.rigidbody_world.collection = bpy.context.scene.collection

# 6. Optional: Add ground plane for visual reference (not needed for physics)
bpy.ops.mesh.primitive_plane_add(size=10.0, location=(0,0,-0.1))
ground = bpy.context.active_object
ground.name = "Ground"
bpy.ops.rigidbody.object_add()
ground.rigid_body.type = 'PASSIVE'

print("Cantilever camera arm created. Run simulation for", sim_frames, "frames.")