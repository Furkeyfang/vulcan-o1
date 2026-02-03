import bpy
import mathutils

# Clear existing scene
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

# Extract parameters
seg_len = 2.0
seg_wid = 0.5
seg_hgt = 0.5
base_loc = (0.0, 0.0, 0.25)
moving_loc = (2.0, 0.0, 0.25)
joint_pt = (1.0, 0.0, 0.25)
hinge_axis = (0.0, 0.0, 1.0)
motor_vel = 1.0

# Create first segment (base)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=base_loc)
base_seg = bpy.context.active_object
base_seg.name = "BaseSegment"
base_seg.scale = (seg_len/2, seg_wid/2, seg_hgt/2)  # Scale from unit cube
bpy.ops.rigidbody.object_add()
base_seg.rigid_body.type = 'PASSIVE'
base_seg.rigid_body.collision_shape = 'BOX'
base_seg.rigid_body.use_margin = True
base_seg.rigid_body.collision_margin = 0.001

# Create second segment (moving)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=moving_loc)
moving_seg = bpy.context.active_object
moving_seg.name = "MovingSegment"
moving_seg.scale = (seg_len/2, seg_wid/2, seg_hgt/2)
bpy.ops.rigidbody.object_add()
moving_seg.rigid_body.type = 'ACTIVE'
moving_seg.rigid_body.collision_shape = 'BOX'
moving_seg.rigid_body.use_margin = True
moving_seg.rigid_body.collision_margin = 0.001

# Create hinge constraint at joint point
# Set 3D cursor to joint location (acceptable in headless)
bpy.context.scene.cursor.location = joint_pt

# Create empty for constraint
bpy.ops.object.empty_add(type='PLAIN_AXES', location=joint_pt)
constraint_empty = bpy.context.active_object
constraint_empty.name = "HingeConstraint"

# Add rigid body constraint to empty
bpy.ops.rigidbody.constraint_add()
constraint = constraint_empty.rigid_body_constraint
constraint.type = 'HINGE'

# Link objects to constraint
constraint.object1 = base_seg
constraint.object2 = moving_seg

# Configure hinge properties
constraint.pivot_type = 'CENTER'
constraint.use_limit_ang_z = False  # Allow unlimited rotation
constraint.use_motor_ang_z = True
constraint.motor_ang_z_velocity = motor_vel
constraint.motor_ang_z_max_torque = 100.0  # High torque for reliable motion

# Set hinge axis (Z-axis for rotation in XY plane)
constraint.axis = hinge_axis

# Optional: Set simulation frame range for verification
bpy.context.scene.frame_end = 100

print("Articulated steering joint created successfully.")
print(f"Motor angular velocity: {motor_vel} rad/s")
print(f"Expected rotation in 100 frames: {motor_vel * 100/60:.1f} rad = {math.degrees(motor_vel * 100/60):.1f}°")