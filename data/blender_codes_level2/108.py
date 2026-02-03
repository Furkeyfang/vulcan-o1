import bpy
import mathutils

# Clear existing scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Parameters from summary
mast_segments = 8
cube_size = 1.0
mast_height = 8.0
arm_length = 4.0
arm_height = 1.0
arm_width = 1.0
load_size = 0.5
load_mass = 650.0
arm_center_x = 2.0
arm_center_z = 8.0
load_center_x = 4.0
load_center_z = 8.0
ground_size = 20.0
ground_thickness = 0.5
hinge_motor_velocity = 0.0

# Enable rigid body physics
bpy.context.scene.use_gravity = True
bpy.context.scene.gravity = (0, 0, -9.81)

# Create ground plane
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, -ground_thickness/2))
ground = bpy.context.active_object
ground.name = "Ground"
ground.scale = (ground_size, ground_size, ground_thickness)
bpy.ops.rigidbody.object_add()
ground.rigid_body.type = 'PASSIVE'

# Create mast segments with fixed constraints
mast_objects = []
for i in range(mast_segments):
    z_pos = i * cube_size + cube_size/2
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, z_pos))
    cube = bpy.context.active_object
    cube.name = f"Mast_Segment_{i+1}"
    cube.scale = (cube_size, cube_size, cube_size)
    
    # Add rigid body - only base is passive, others active but constrained
    bpy.ops.rigidbody.object_add()
    if i == 0:
        cube.rigid_body.type = 'PASSIVE'  # Base fixed to ground
    else:
        cube.rigid_body.type = 'ACTIVE'
        cube.rigid_body.mass = cube_size**3 * 1000  # Density ~1000 kg/m³
        
    mast_objects.append(cube)
    
    # Add fixed constraints between consecutive segments
    if i > 0:
        bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, z_pos - cube_size/2))
        constraint_empty = bpy.context.active_object
        constraint_empty.name = f"Fixed_Constraint_{i}"
        
        bpy.ops.rigidbody.constraint_add()
        constraint = constraint_empty.rigid_body_constraint
        constraint.type = 'FIXED'
        constraint.object1 = mast_objects[i-1]
        constraint.object2 = mast_objects[i]

# Create arm
bpy.ops.mesh.primitive_cube_add(size=1, location=(arm_center_x, 0, arm_center_z))
arm = bpy.context.active_object
arm.name = "Arm"
arm.scale = (arm_length, arm_width, arm_height)
bpy.ops.rigidbody.object_add()
arm.rigid_body.type = 'ACTIVE'
arm.rigid_body.mass = arm_length * arm_width * arm_height * 1000  # Steel density

# Create load
bpy.ops.mesh.primitive_cube_add(size=1, location=(load_center_x, 0, load_center_z))
load = bpy.context.active_object
load.name = "Load"
load.scale = (load_size, load_size, load_size)
bpy.ops.rigidbody.object_add()
load.rigid_body.type = 'ACTIVE'
load.rigid_body.mass = load_mass

# Add hinge constraint between top mast segment and arm
bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, arm_center_z))
hinge_empty = bpy.context.active_object
hinge_empty.name = "Arm_Hinge"

bpy.ops.rigidbody.constraint_add()
hinge_constraint = hinge_empty.rigid_body_constraint
hinge_constraint.type = 'HINGE'
hinge_constraint.object1 = mast_objects[-1]  # Top mast segment
hinge_constraint.object2 = arm
hinge_constraint.use_limit_z = True
hinge_constraint.limit_z_lower = -1.57  # -90 degrees
hinge_constraint.limit_z_upper = 1.57   # +90 degrees
hinge_constraint.use_motor_z = True
hinge_constraint.motor_velocity_z = hinge_motor_velocity
hinge_constraint.motor_max_impulse_z = 10000  # High torque for static hold

# Add fixed constraint between arm and load
bpy.ops.object.empty_add(type='PLAIN_AXES', location=(load_center_x, 0, load_center_z))
load_constraint_empty = bpy.context.active_object
load_constraint_empty.name = "Load_Constraint"

bpy.ops.rigidbody.constraint_add()
load_constraint = load_constraint_empty.rigid_body_constraint
load_constraint.type = 'FIXED'
load_constraint.object1 = arm
load_constraint.object2 = load

# Set simulation parameters for stability
bpy.context.scene.rigidbody_world.steps_per_second = 250
bpy.context.scene.rigidbody_world.solver_iterations = 50
bpy.context.scene.frame_end = 100

# Ensure proper collision shapes
for obj in [ground] + mast_objects + [arm, load]:
    if hasattr(obj, 'rigid_body'):
        obj.rigid_body.collision_shape = 'BOX'
        obj.rigid_body.collision_margin = 0.001

print("Cantilever crane construction complete. Ready for 100-frame stability test.")