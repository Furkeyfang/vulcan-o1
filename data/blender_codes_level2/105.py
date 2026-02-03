import bpy
import mathutils

# Clear existing scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Extract parameters from summary
col_dim = (0.5, 0.5, 2.0)
col_loc = (0.0, 0.0, 1.0)
beam_dim = (4.5, 0.3, 0.3)
beam_loc = (2.25, 0.0, 2.15)
plat_dim = (0.8, 0.8, 0.1)
plat_loc = (4.5, 0.0, 2.35)
load_mass = 550.0
steel_density = 7850.0
sim_frames = 100
gravity = -9.81

# Calculate volumes for mass assignment
col_vol = col_dim[0] * col_dim[1] * col_dim[2]
beam_vol = beam_dim[0] * beam_dim[1] * beam_dim[2]
plat_vol = plat_dim[0] * plat_dim[1] * plat_dim[2]

# Enable rigid body physics
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 10
bpy.context.scene.rigidbody_world.gravity.z = gravity

# 1. Create Vertical Support Column
bpy.ops.mesh.primitive_cube_add(size=1.0, location=col_loc)
column = bpy.context.active_object
column.name = "Support_Column"
column.scale = col_dim
bpy.ops.rigidbody.object_add()
column.rigid_body.type = 'PASSIVE'
column.rigid_body.collision_shape = 'BOX'
column.rigid_body.mass = col_vol * steel_density  # Heavy foundation

# 2. Create Main Beam
bpy.ops.mesh.primitive_cube_add(size=1.0, location=beam_loc)
beam = bpy.context.active_object
beam.name = "Main_Beam"
beam.scale = beam_dim
bpy.ops.rigidbody.object_add()
beam.rigid_body.type = 'ACTIVE'
beam.rigid_body.collision_shape = 'BOX'
beam.rigid_body.mass = beam_vol * steel_density

# 3. Create Load Platform
bpy.ops.mesh.primitive_cube_add(size=1.0, location=plat_loc)
platform = bpy.context.active_object
platform.name = "Load_Platform"
platform.scale = plat_dim
bpy.ops.rigidbody.object_add()
platform.rigid_body.type = 'ACTIVE'
platform.rigid_body.collision_shape = 'BOX'
platform.rigid_body.mass = load_mass  # Primary load mass

# 4. Create Fixed Constraints
# Beam-to-Column constraint
bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0.0, 0.0, 2.0))
constraint1 = bpy.context.active_object
constraint1.name = "Beam_Column_Fixed"
bpy.ops.rigidbody.constraint_add()
constraint1.rigid_body_constraint.type = 'FIXED'
constraint1.rigid_body_constraint.object1 = column
constraint1.rigid_body_constraint.object2 = beam

# Platform-to-Beam constraint
bpy.ops.object.empty_add(type='PLAIN_AXES', location=(4.5, 0.0, 2.15))
constraint2 = bpy.context.active_object
constraint2.name = "Beam_Platform_Fixed"
bpy.ops.rigidbody.constraint_add()
constraint2.rigid_body_constraint.type = 'FIXED'
constraint2.rigid_body_constraint.object1 = beam
constraint2.rigid_body_constraint.object2 = platform

# 5. Set simulation parameters
bpy.context.scene.frame_end = sim_frames

# Optional: Add visualization material for clarity
mat = bpy.data.materials.new(name="Steel_Gray")
mat.diffuse_color = (0.6, 0.6, 0.7, 1.0)
column.data.materials.append(mat)
beam.data.materials.append(mat)

plat_mat = bpy.data.materials.new(name="Load_Red")
plat_mat.diffuse_color = (0.8, 0.2, 0.1, 1.0)
platform.data.materials.append(plat_mat)

print(f"Cantilever boom setup complete. Simulation ready for {sim_frames} frames.")
print(f"Column mass: {column.rigid_body.mass:.1f} kg")
print(f"Beam mass: {beam.rigid_body.mass:.1f} kg")
print(f"Platform load: {platform.rigid_body.mass:.1f} kg")