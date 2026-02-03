import bpy
import mathutils

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Extract parameters from summary
shaft_height = 18.0
base_length = 4.0
column_width = 0.5
column_depth = 0.5
column_height = 18.0
beam_length = 4.0
beam_width = 4.0
beam_thickness = 0.5
load_size = 1.0
load_mass = 1000.0
column_offset = 1.75
column_z_center = 9.0
bottom_beam_z = 0.25
top_beam_z = 17.75
load_z = 18.5

# Create vertical columns
column_locations = [
    (column_offset, column_offset, column_z_center),
    (column_offset, -column_offset, column_z_center),
    (-column_offset, column_offset, column_z_center),
    (-column_offset, -column_offset, column_z_center)
]

columns = []
for i, loc in enumerate(column_locations):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=loc)
    col = bpy.context.active_object
    col.name = f"Column_{i+1}"
    col.scale = (column_width, column_depth, column_height)
    bpy.ops.rigidbody.object_add()
    col.rigid_body.type = 'PASSIVE'
    col.rigid_body.collision_shape = 'BOX'
    columns.append(col)

# Create bottom beam
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, bottom_beam_z))
bottom_beam = bpy.context.active_object
bottom_beam.name = "Bottom_Beam"
bottom_beam.scale = (beam_length, beam_width, beam_thickness)
bpy.ops.rigidbody.object_add()
bottom_beam.rigid_body.type = 'PASSIVE'
bottom_beam.rigid_body.collision_shape = 'BOX'

# Create top beam
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, top_beam_z))
top_beam = bpy.context.active_object
top_beam.name = "Top_Beam"
top_beam.scale = (beam_length, beam_width, beam_thickness)
bpy.ops.rigidbody.object_add()
top_beam.rigid_body.type = 'PASSIVE'
top_beam.rigid_body.collision_shape = 'BOX'

# Create load
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, load_z))
load = bpy.context.active_object
load.name = "Load"
load.scale = (load_size, load_size, load_size)
bpy.ops.rigidbody.object_add()
load.rigid_body.type = 'ACTIVE'
load.rigid_body.mass = load_mass
load.rigid_body.collision_shape = 'BOX'

# Add fixed constraints for structural connections
for col in columns:
    # Connect column to bottom beam
    constraint = col.constraints.new(type='FIXED')
    constraint.target = bottom_beam
    # Connect column to top beam
    constraint = col.constraints.new(type='FIXED')
    constraint.target = top_beam

# Connect load to top beam
constraint = load.constraints.new(type='FIXED')
constraint.target = top_beam

# Set up physics simulation
bpy.context.scene.frame_end = 100
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 50

# Verification: Bake simulation and check final position
print("Simulating 100 frames...")
bpy.ops.rigidbody.bake_to_keyframes(frame_start=1, frame_end=100)
bpy.context.scene.frame_set(100)
final_z = load.location.z
print(f"Load final Z-position: {final_z:.3f}m")
print(f"Target Z: {load_z:.3f}m")
print(f"Deviation: {abs(final_z - load_z):.3f}m")