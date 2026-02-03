import bpy
import mathutils

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Extract parameters
H = 8.0
W = 0.5
D = 0.5
col_mass = 15700.0
col_damp_lin = 0.99
col_damp_ang = 0.99
load_mass = 7000.0
load_sz = 0.4
col_z = 4.0
load_z = 8.2
frames = 100
max_disp = 0.01

# Create column (steel cube)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, 0.0, col_z))
column = bpy.context.active_object
column.name = "Steel_Column"
column.scale = (W, D, H)  # Scale to desired dimensions

# Add rigid body physics to column
bpy.ops.rigidbody.object_add()
column.rigid_body.type = 'ACTIVE'
column.rigid_body.mass = col_mass
column.rigid_body.linear_damping = col_damp_lin
column.rigid_body.angular_damping = col_damp_ang
column.rigid_body.collision_shape = 'BOX'
column.rigid_body.friction = 0.5
column.rigid_body.restitution = 0.1

# Create fixed constraint at base
bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0.0, 0.0, 0.0))
constraint_empty = bpy.context.active_object
constraint_empty.name = "Base_Fixed_Constraint"

# Add rigid body constraint
bpy.ops.rigidbody.constraint_add()
constraint = bpy.context.active_object
constraint.rigid_body_constraint.type = 'FIXED'
constraint.rigid_body_constraint.object1 = column
# Leave object2 as None to constrain to world

# Set constraint location at column base (in column's local space)
constraint.location = (0.0, 0.0, 0.0)  # World origin
constraint.rotation_euler = (0.0, 0.0, 0.0)

# Parent constraint to column for proper transformation
constraint.parent = column
constraint.matrix_parent_inverse = column.matrix_world.inverted()

# Create load (7000 kg cube)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, 0.0, load_z))
load = bpy.context.active_object
load.name = "7000kg_Load"
load.scale = (load_sz, load_sz, load_sz)

# Add rigid body to load
bpy.ops.rigidbody.object_add()
load.rigid_body.type = 'ACTIVE'
load.rigid_body.mass = load_mass
load.rigid_body.linear_damping = 0.95
load.rigid_body.angular_damping = 0.95
load.rigid_body.collision_shape = 'BOX'

# Configure physics world for stability
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 50
bpy.context.scene.rigidbody_world.use_split_impulse = True
bpy.context.scene.frame_end = frames

# Verification setup: Add custom property to track displacement
column["max_displacement"] = 0.0
column["initial_location"] = column.location.copy()

# Function to check displacement (would be called during simulation)
def check_displacement(obj, frame):
    displacement = (obj.location - obj["initial_location"]).length
    if displacement > obj["max_displacement"]:
        obj["max_displacement"] = displacement
    if displacement > max_disp:
        print(f"Frame {frame}: Displacement {displacement:.4f} exceeds limit!")

# Note: In a complete implementation, you would bake simulation and check each frame
# For headless data generation, we set up the scene for later simulation
print(f"Column setup complete. Mass: {col_mass} kg, Load: {load_mass} kg")
print(f"Simulation will run for {frames} frames with displacement limit: {max_disp} m")