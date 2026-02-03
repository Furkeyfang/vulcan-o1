import bpy
import math

# 1. Clear existing scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# 2. Define parameters from summary
chassis_dim = (3.0, 1.0, 0.3)
chassis_center = (0.0, 0.0, 0.5)
axle_radius = 0.05
axle_length = 1.2
axle1_center = (0.0, 0.0, 0.35)
axle2_center = (1.5, 0.0, 0.35)
wheel_radius = 0.5
wheel_depth = 0.2
wheel_y_offset = axle_length / 2.0  # = 0.6
ground_clearance = 0.05
motor_velocity = 2.5
simulation_frames = 300

# 3. Create chassis (cube)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=chassis_center)
chassis = bpy.context.active_object
chassis.scale = (chassis_dim[0]/2, chassis_dim[1]/2, chassis_dim[2]/2)  # Blender cube radius=1, so halve
chassis.name = "Chassis"
# Rigid body
bpy.ops.rigidbody.object_add()
chassis.rigid_body.type = 'ACTIVE'
chassis.rigid_body.collision_shape = 'BOX'

# 4. Create axles and wheels
axle_centers = [axle1_center, axle2_center]
axles = []
for i, center in enumerate(axle_centers):
    # Axle cylinder (aligned along Y)
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=axle_radius, depth=axle_length, location=center)
    axle = bpy.context.active_object
    axle.name = f"Axle_{i+1}"
    axle.rotation_euler = (math.pi/2, 0, 0)  # Rotate 90° around X to align with Y axis
    # Rigid body
    bpy.ops.rigidbody.object_add()
    axle.rigid_body.type = 'ACTIVE'
    axle.rigid_body.collision_shape = 'CYLINDER'
    axles.append(axle)
    
    # Create two wheels per axle
    for side in [-1, 1]:
        wheel_y = center[1] + side * wheel_y_offset
        wheel_loc = (center[0], wheel_y, center[2])
        bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=wheel_radius, depth=wheel_depth, location=wheel_loc)
        wheel = bpy.context.active_object
        wheel.name = f"Wheel_{i+1}_{'L' if side==-1 else 'R'}"
        wheel.rotation_euler = (0, math.pi/2, 0)  # Rotate 90° around Y to align with X axis (width)
        # Parent wheel to axle
        wheel.parent = axle
        # Rigid body (inherits from parent via compound shape)
        bpy.ops.rigidbody.object_add()
        wheel.rigid_body.type = 'ACTIVE'
        wheel.rigid_body.collision_shape = 'CYLINDER'

# 5. Create ground anchor (Empty at chassis base)
bpy.ops.object.empty_add(type='PLAIN_AXES', location=(chassis_center[0], chassis_center[1], 0))
ground_anchor = bpy.context.active_object
ground_anchor.name = "Ground_Anchor"
bpy.ops.rigidbody.object_add()
ground_anchor.rigid_body.type = 'PASSIVE'

# 6. Fixed constraint between chassis and ground
bpy.ops.object.select_all(action='DESELECT')
chassis.select_set(True)
ground_anchor.select_set(True)
bpy.context.view_layer.objects.active = chassis
bpy.ops.rigidbody.constraint_add()
constraint = chassis.rigid_body_constraints[-1]
constraint.type = 'FIXED'
constraint.object1 = chassis
constraint.object2 = ground_anchor

# 7. Hinge constraints between chassis and each axle (motorized)
for axle in axles:
    bpy.ops.object.select_all(action='DESELECT')
    chassis.select_set(True)
    axle.select_set(True)
    bpy.context.view_layer.objects.active = chassis
    bpy.ops.rigidbody.constraint_add()
    hinge = chassis.rigid_body_constraints[-1]
    hinge.type = 'HINGE'
    hinge.object1 = chassis
    hinge.object2 = axle
    hinge.use_limit_ang_z = True
    hinge.limit_ang_z_lower = 0
    hinge.limit_ang_z_upper = 0  # Lock other axes
    # Motor settings
    hinge.use_motor_ang_z = True
    hinge.motor_ang_z_vel = motor_velocity
    hinge.motor_ang_z_max_torque = 1000.0  # High torque to overcome inertia

# 8. Simulation settings
bpy.context.scene.frame_end = simulation_frames
bpy.context.scene.rigidbody_world.time_scale = 1.0
bpy.context.scene.rigidbody_world.substeps_per_frame = 10
bpy.context.scene.rigidbody_world.solver_iterations = 50

# 9. Bake simulation (headless compatible)
bpy.ops.ptcache.bake_all(bake=True)

# 10. Verify final position (after bake)
final_frame = simulation_frames
bpy.context.scene.frame_set(final_frame)
final_y = chassis.location.y
print(f"Robot final Y position: {final_y}")
if final_y > 12.0:
    print("SUCCESS: Robot exceeded 12 meters.")
else:
    print(f"FAILURE: Robot only reached {final_y} meters.")