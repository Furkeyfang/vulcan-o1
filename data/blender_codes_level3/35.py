import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Extract parameters
p_size = (6.0, 4.0, 0.5)
p_loc = (0.0, 0.0, 0.25)
w_rad = 0.6
w_dep = 0.3
w_positions = [(-2.85, 1.85, -0.6), (-2.85, -1.85, -0.6),
               (2.85, 1.85, -0.6), (2.85, -1.85, -0.6)]
w_rot = (0.0, math.pi/2, 0.0)  # 90° around Y
motor_vel = 4.0

# Create chassis platform
bpy.ops.mesh.primitive_cube_add(size=1.0, location=p_loc)
chassis = bpy.context.active_object
chassis.name = "Chassis"
chassis.scale = (p_size[0]/2, p_size[1]/2, p_size[2]/2)  # Blender cube size=2
bpy.ops.rigidbody.object_add()
chassis.rigid_body.type = 'ACTIVE'
chassis.rigid_body.mass = 20.0  # Reasonable mass for platform

# Create wheels
wheel_objects = []
for i, w_pos in enumerate(w_positions):
    # Create cylinder (default: radius=1, depth=2)
    bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=1.0, depth=2.0, location=w_pos)
    wheel = bpy.context.active_object
    wheel.name = f"Wheel_{i+1}"
    wheel.rotation_euler = w_rot
    wheel.scale = (w_rad, w_rad, w_dep/2.0)  # Scale depth from 2.0 to w_dep
    
    # Add rigid body
    bpy.ops.rigidbody.object_add()
    wheel.rigid_body.type = 'ACTIVE'
    wheel.rigid_body.mass = 2.0  # Wheel mass
    
    wheel_objects.append(wheel)

# Create hinge constraints for each wheel
for wheel in wheel_objects:
    # Create empty object as constraint anchor
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=wheel.location)
    constraint_empty = bpy.context.active_object
    constraint_empty.name = f"Hinge_{wheel.name}"
    constraint_empty.empty_display_size = 0.5
    
    # Add rigid body constraint
    bpy.ops.rigidbody.constraint_add()
    constraint = constraint_empty.rigid_body_constraint
    constraint.type = 'HINGE'
    constraint.object1 = chassis
    constraint.object2 = wheel
    
    # Set constraint axis to local X (for wheel rotation)
    constraint.use_override_solver_iterations = True
    constraint.solver_iterations = 10
    
    # Enable motor
    constraint.use_motor = True
    constraint.motor_type = 'VELOCITY'
    constraint.motor_velocity = motor_vel
    constraint.motor_max_impulse = 100.0  # Sufficient torque

# Set world gravity (default -9.81 Z is fine)
bpy.context.scene.use_gravity = True

# Optional: Add ground plane
bpy.ops.mesh.primitive_plane_add(size=50.0, location=(0,0,-0.01))
ground = bpy.context.active_object
bpy.ops.rigidbody.object_add()
ground.rigid_body.type = 'PASSIVE'

print("Rover assembly complete with 4 motorized wheels.")