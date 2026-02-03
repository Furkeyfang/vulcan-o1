import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Extract parameters
col_dim = (0.3, 0.3, 2.0)
col_loc = (0.0, 0.0, 1.0)

beam_dim = (2.5, 0.3, 0.3)
beam_loc = (1.25, 0.0, 2.15)

brace_dim = (0.2, 0.2, 2.2)
brace_start = (0.0, 0.0, 0.0)
brace_end = (2.5, 0.0, 2.15)

plate_dim = (0.5, 0.5, 0.1)
plate_loc = (2.5, 0.0, 2.35)

load_mass = 200.0

# Create Support Column
bpy.ops.mesh.primitive_cube_add(size=1, location=col_loc)
column = bpy.context.active_object
column.name = "SupportColumn"
column.scale = (col_dim[0], col_dim[1], col_dim[2])
bpy.ops.rigidbody.object_add()
column.rigid_body.type = 'PASSIVE'

# Create Main Beam
bpy.ops.mesh.primitive_cube_add(size=1, location=beam_loc)
beam = bpy.context.active_object
beam.name = "MainBeam"
beam.scale = (beam_dim[0], beam_dim[1], beam_dim[2])
bpy.ops.rigidbody.object_add()
beam.rigid_body.type = 'ACTIVE'

# Create Diagonal Brace (requires scaling and rotation)
# Calculate actual brace vector and length
import math
brace_vec = (brace_end[0] - brace_start[0], 
             brace_end[1] - brace_start[1], 
             brace_end[2] - brace_start[2])
brace_length = math.sqrt(brace_vec[0]**2 + brace_vec[1]**2 + brace_vec[2]**2)
brace_mid = ((brace_start[0] + brace_end[0])/2,
             (brace_start[1] + brace_end[1])/2,
             (brace_start[2] + brace_end[2])/2)

# Scale factor: actual length / nominal length
scale_z = brace_length / brace_dim[2]

# Rotation: align Z-axis with brace vector
# Calculate rotation angle around Y-axis (since brace is in XZ plane)
angle_y = math.atan2(brace_vec[0], brace_vec[2])

bpy.ops.mesh.primitive_cube_add(size=1, location=brace_mid)
brace = bpy.context.active_object
brace.name = "DiagonalBrace"
brace.scale = (brace_dim[0], brace_dim[1], scale_z)
brace.rotation_euler = (0.0, angle_y, 0.0)
bpy.ops.rigidbody.object_add()
brace.rigid_body.type = 'ACTIVE'

# Create Load Plate
bpy.ops.mesh.primitive_cube_add(size=1, location=plate_loc)
plate = bpy.context.active_object
plate.name = "LoadPlate"
plate.scale = (plate_dim[0], plate_dim[1], plate_dim[2])
bpy.ops.rigidbody.object_add()
plate.rigid_body.type = 'ACTIVE'
plate.rigid_body.mass = load_mass

# Create Fixed Constraints (using empties as constraint objects)
def create_fixed_constraint(name, location, obj1, obj2):
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=location)
    constraint_empty = bpy.context.active_object
    constraint_empty.name = name
    bpy.ops.rigidbody.constraint_add()
    constraint = constraint_empty.rigid_body_constraint
    constraint.type = 'FIXED'
    constraint.object1 = obj1
    constraint.object2 = obj2

# Column-Beam junction (at column top, beam start)
create_fixed_constraint("ColBeam_Constraint", (0.0, 0.0, 2.0), column, beam)

# Column-Brace junction (at column base)
create_fixed_constraint("ColBrace_Constraint", brace_start, column, brace)

# Beam-Brace junction (at beam outer end)
create_fixed_constraint("BeamBrace_Constraint", brace_end, beam, brace)

# Set gravity to realistic Earth value (default is 9.8 m/s²)
bpy.context.scene.use_gravity = True
bpy.context.scene.gravity = (0.0, 0.0, -9.81)

# Enable rigid body simulation
bpy.context.scene.rigidbody_world.enabled = True

print("Cantilever safety net support arm constructed successfully.")
print(f"Load: {load_mass} kg at position {plate_loc}")