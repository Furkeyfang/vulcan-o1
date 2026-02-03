import bpy
import math

# Clear scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Extract parameters
col_h = 7.0
col_w = 1.0
arm_len = 4.0
arm_w = 0.5
arm_d = 0.5
load_sz = 0.5
load_mass = 400.0
steel_den = 7850.0
ground_sz = 10.0
col_base = (0.0, 0.0, 3.5)
arm_center = (2.0, 0.0, 7.0)
load_center = (4.0, 0.0, 7.0)
hinge_stiff = 10000.0
hinge_damp = 1000.0
sim_frames = 100
max_sag = 0.1

# Enable rigid body physics
bpy.context.scene.rigidbody_world.enabled = True

# Create ground plane
bpy.ops.mesh.primitive_plane_add(size=ground_sz, location=(0,0,0))
ground = bpy.context.active_object
ground.name = "Ground"
bpy.ops.rigidbody.object_add()
ground.rigid_body.type = 'PASSIVE'
ground.rigid_body.collision_shape = 'MESH'

# Create column (vertical)
bpy.ops.mesh.primitive_cube_add(size=1, location=col_base)
column = bpy.context.active_object
column.name = "Column"
column.scale = (col_w, col_w, col_h)
bpy.ops.rigidbody.object_add()
column.rigid_body.type = 'PASSIVE'
column.rigid_body.collision_shape = 'BOX'

# Create arm (horizontal)
bpy.ops.mesh.primitive_cube_add(size=1, location=arm_center)
arm = bpy.context.active_object
arm.name = "Arm"
arm.scale = (arm_len, arm_w, arm_d)
# Calculate arm mass: volume * density
arm_volume = arm_len * arm_w * arm_d
arm_mass = arm_volume * steel_den
bpy.ops.rigidbody.object_add()
arm.rigid_body.type = 'ACTIVE'
arm.rigid_body.mass = arm_mass
arm.rigid_body.collision_shape = 'BOX'

# Create load block
bpy.ops.mesh.primitive_cube_add(size=1, location=load_center)
load = bpy.context.active_object
load.name = "Load"
load.scale = (load_sz, load_sz, load_sz)
bpy.ops.rigidbody.object_add()
load.rigid_body.type = 'ACTIVE'
load.rigid_body.mass = load_mass
load.rigid_body.collision_shape = 'BOX'

# Add constraints
# 1. Fixed constraint between ground and column
bpy.ops.object.select_all(action='DESELECT')
ground.select_set(True)
column.select_set(True)
bpy.context.view_layer.objects.active = ground
bpy.ops.rigidbody.connect_add(type='FIXED')
fixed_con = bpy.context.active_object
fixed_con.name = "Ground_Column_Fixed"
fixed_con.rigid_body_constraint.object1 = ground
fixed_con.rigid_body_constraint.object2 = column
fixed_con.location = (0, 0, 0)

# 2. Hinge constraint between column and arm (Y-axis rotation)
bpy.ops.object.select_all(action='DESELECT')
column.select_set(True)
arm.select_set(True)
bpy.context.view_layer.objects.active = column
bpy.ops.rigidbody.connect_add(type='HINGE')
hinge_con = bpy.context.active_object
hinge_con.name = "Column_Arm_Hinge"
hinge_con.rigid_body_constraint.object1 = column
hinge_con.rigid_body_constraint.object2 = arm
hinge_con.location = (0, 0, 7)  # Top of column
# Configure hinge for stiffness (limit rotation)
hinge_con.rigid_body_constraint.use_limit_ang_z = True
hinge_con.rigid_body_constraint.limit_ang_z_lower = -0.01  # Small tolerance
hinge_con.rigid_body_constraint.limit_ang_z_upper = 0.01
hinge_con.rigid_body_constraint.use_spring_ang_z = True
hinge_con.rigid_body_constraint.spring_stiffness_ang_z = hinge_stiff
hinge_con.rigid_body_constraint.spring_damping_ang_z = hinge_damp

# 3. Fixed constraint between arm and load
bpy.ops.object.select_all(action='DESELECT')
arm.select_set(True)
load.select_set(True)
bpy.context.view_layer.objects.active = arm
bpy.ops.rigidbody.connect_add(type='FIXED')
load_con = bpy.context.active_object
load_con.name = "Arm_Load_Fixed"
load_con.rigid_body_constraint.object1 = arm
load_con.rigid_body_constraint.object2 = load
load_con.location = (4, 0, 7)  # End of arm

# Set simulation parameters
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 50
bpy.context.scene.rigidbody_world.use_split_impulse = True

# Bake simulation for verification
bpy.context.scene.frame_end = sim_frames
print("Crane constructed. Simulation ready for 100 frames.")
print(f"Arm mass: {arm_mass:.1f} kg (steel)")
print(f"Load mass: {load_mass} kg")
print(f"Expected bending moment: {load_mass * 9.81 * arm_len:.0f} Nm")
print(f"Hinge stiffness: {hinge_stiff} Nm/rad")
print("To verify sag < 0.1m, run: blender --background --python verify_sag.py")