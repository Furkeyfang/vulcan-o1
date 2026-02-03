import bpy
import mathutils

# ========== CLEAR SCENE ==========
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

# ========== PARAMETERS ==========
# Column
col_width = 0.3
col_depth = 0.3
col_height = 3.0
col_center = (0.0, 0.0, 1.5)

# Beam
beam_length = 4.0
beam_height = 0.2
beam_width = 0.2
beam_center = (2.0, 0.0, 3.0)

# Platform
plat_width = 0.5
plat_depth = 0.5
plat_thickness = 0.1
plat_center = (4.0, 0.0, 2.95)

# Force
force_magnitude = -882.9
force_location = (4.0, 0.0, 2.95)

# Simulation
total_frames = 100
deflection_tolerance = 0.05
solver_iterations = 50
substeps = 5
constraint_stiffness = 1000.0

# ========== RIGID BODY WORLD SETUP ==========
bpy.context.scene.rigidbody_world.point_cache.frame_start = 1
bpy.context.scene.rigidbody_world.point_cache.frame_end = total_frames
bpy.context.scene.rigidbody_world.solver_iterations = solver_iterations
bpy.context.scene.rigidbody_world.substeps_per_frame = substeps
bpy.context.scene.rigidbody_world.time_scale = 1.0

# ========== CREATE COLUMN ==========
bpy.ops.mesh.primitive_cube_add(size=1.0, location=col_center)
column = bpy.context.active_object
column.name = "Column"
column.scale = (col_width, col_depth, col_height)
bpy.ops.rigidbody.object_add()
column.rigid_body.type = 'PASSIVE'
column.rigid_body.collision_shape = 'BOX'
column.rigid_body.mass = 100.0  # Heavy base

# ========== CREATE BEAM ==========
bpy.ops.mesh.primitive_cube_add(size=1.0, location=beam_center)
beam = bpy.context.active_object
beam.name = "Beam"
beam.scale = (beam_length, beam_width, beam_height)
bpy.ops.rigidbody.object_add()
beam.rigid_body.type = 'ACTIVE'
beam.rigid_body.collision_shape = 'BOX'
beam.rigid_body.mass = 10.0

# ========== CREATE PLATFORM ==========
bpy.ops.mesh.primitive_cube_add(size=1.0, location=plat_center)
platform = bpy.context.active_object
platform.name = "Platform"
platform.scale = (plat_width, plat_depth, plat_thickness)
bpy.ops.rigidbody.object_add()
platform.rigid_body.type = 'ACTIVE'
platform.rigid_body.collision_shape = 'BOX'
platform.rigid_body.mass = 5.0

# ========== CREATE FIXED CONSTRAINTS ==========
# Constraint: Column to Beam (at column top)
bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0.0, 0.0, 3.0))
constraint1 = bpy.context.active_object
constraint1.name = "Constraint_Column_Beam"
bpy.ops.rigidbody.constraint_add()
constraint1.rigid_body_constraint.type = 'FIXED'
constraint1.rigid_body_constraint.object1 = column
constraint1.rigid_body_constraint.object2 = beam
constraint1.rigid_body_constraint.use_breaking = False
constraint1.rigid_body_constraint.breaking_threshold = 10000.0

# Constraint: Beam to Platform (at beam free end)
bpy.ops.object.empty_add(type='PLAIN_AXES', location=(4.0, 0.0, 3.0))
constraint2 = bpy.context.active_object
constraint2.name = "Constraint_Beam_Platform"
bpy.ops.rigidbody.constraint_add()
constraint2.rigid_body_constraint.type = 'FIXED'
constraint2.rigid_body_constraint.object1 = beam
constraint2.rigid_body_constraint.object2 = platform
constraint2.rigid_body_constraint.use_breaking = False
constraint2.rigid_body_constraint.breaking_threshold = 10000.0

# ========== APPLY FORCE FIELD ==========
# Create force field at platform center
bpy.ops.object.empty_add(type='PLAIN_AXES', location=force_location)
force_field = bpy.context.active_object
force_field.name = "Force_Field"
bpy.ops.object.forcefield_add()
force_field.field.type = 'FORCE'
force_field.field.strength = force_magnitude
force_field.field.use_max_distance = False
force_field.field.falloff_power = 0.0

# Link force field only to platform collection
platform_collection = bpy.data.collections.new("PlatformCollection")
bpy.context.scene.collection.children.link(platform_collection)
platform_collection.objects.link(platform)
force_field.field.apply_only_to = 'COLLECTION'
force_field.field.collection = platform_collection

# ========== ANIMATE FORCE (ramp up) ==========
# Force starts at 0, reaches full magnitude at frame 10
force_field.field.keyframe_insert(data_path="strength", frame=1)
force_field.field.strength = 0.0
force_field.field.keyframe_insert(data_path="strength", frame=1)
force_field.field.strength = force_magnitude
force_field.field.keyframe_insert(data_path="strength", frame=10)

# ========== DEFLECTION MONITORING ==========
# Store initial platform Z position
initial_z = platform.location.z

# Insert keyframes for rigid body simulation
bpy.context.scene.frame_set(1)
bpy.ops.rigidbody.bake_to_keyframes(frame_start=1, frame_end=total_frames)

# Check final deflection
bpy.context.scene.frame_set(total_frames)
final_z = platform.location.z
deflection = abs(final_z - initial_z)

print(f"Initial platform Z: {initial_z:.4f} m")
print(f"Final platform Z: {final_z:.4f} m")
print(f"Vertical deflection: {deflection:.4f} m")
print(f"Tolerance: {deflection_tolerance} m")
print(f"Pass: {deflection <= deflection_tolerance}")

# ========== SCENE SETTINGS ==========
bpy.context.scene.frame_end = total_frames
bpy.context.scene.render.fps = 24