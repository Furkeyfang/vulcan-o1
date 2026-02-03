import bpy
import mathutils

# Clear existing scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Extract parameters from summary
plate_dim = (1.5, 0.3, 0.05)
plate_loc = (0.0, 0.0, 0.025)
arm_dim = (1.2, 0.2, 0.05)
arm_loc = (0.6, 0.0, 0.075)
platform_dim = (0.8, 0.6, 0.05)
platform_loc = (1.2, 0.0, 0.125)
load_mass_kg = 120.0
simulation_frames = 100
constraint_margin = 0.001
damping_factor = 0.5
collision_margin = 0.04

# Function to create a cube with physics
def create_cube(name, dimensions, location, rigidbody_type='ACTIVE', mass=1.0):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = (dimensions[0]/2, dimensions[1]/2, dimensions[2]/2)  # Cube size=2, so scale by half-dim
    bpy.ops.rigidbody.object_add()
    obj.rigid_body.type = rigidbody_type
    obj.rigid_body.mass = mass
    obj.rigid_body.linear_damping = damping_factor
    obj.rigid_body.angular_damping = damping_factor
    obj.rigid_body.collision_margin = collision_margin
    return obj

# Create mounting plate (passive, fixed to wall)
plate = create_cube("MountingPlate", plate_dim, plate_loc, 'PASSIVE', 100.0)  # Heavy but passive

# Create arm (active, will be constrained to plate)
arm = create_cube("Arm", arm_dim, arm_loc, 'ACTIVE', 20.0)  # Moderate mass

# Create load platform (active with 120kg load)
platform = create_cube("Platform", platform_dim, platform_loc, 'ACTIVE', load_mass_kg)

# Create fixed constraint between plate and arm
# Position constraint at interface: midpoint between plate front and arm back
bpy.ops.object.empty_add(type='PLAIN_AXES', location=(constraint_margin, 0, plate_loc[2]))
constraint_empty = bpy.context.active_object
constraint_empty.name = "Plate_Arm_Constraint"

bpy.ops.rigidbody.constraint_add()
constraint = constraint_empty.rigid_body_constraint
constraint.type = 'FIXED'
constraint.object1 = plate
constraint.object2 = arm
# Position constraint at the interface
interface_x = plate_dim[0]/2  # Right edge of plate (assuming arm extends right)
constraint_empty.location = (interface_x - constraint_margin, 0, plate_loc[2])

# Create fixed constraint between arm and platform
bpy.ops.object.empty_add(type='PLAIN_AXES', location=(arm_loc[0] + arm_dim[0]/2, 0, arm_loc[2]))
constraint_empty2 = bpy.context.active_object
constraint_empty2.name = "Arm_Platform_Constraint"

bpy.ops.rigidbody.constraint_add()
constraint2 = constraint_empty2.rigid_body_constraint
constraint2.type = 'FIXED'
constraint2.object1 = arm
constraint2.object2 = platform
# Position at arm's distal end
constraint_empty2.location = (arm_loc[0] + arm_dim[0]/2 - constraint_margin, 0, arm_loc[2])

# Set up physics world
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 50
bpy.context.scene.frame_end = simulation_frames

# Keyframe initial positions to ensure constraints are established
plate.keyframe_insert(data_path="location", frame=1)
arm.keyframe_insert(data_path="location", frame=1)
platform.keyframe_insert(data_path="location", frame=1)

# Verification: Run simulation (in background this would execute automatically)
# Note: In headless mode, physics sim runs when rendering or via bpy.ops.ptcache.bake()
print("Equipment rack constructed. Simulation ready for 100 frames.")