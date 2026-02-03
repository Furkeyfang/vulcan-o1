import bpy
import math
from mathutils import Matrix

# Clear scene
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

# Define variables from summary
chassis_dim = (3.0, 1.5, 0.4)
chassis_loc = (0.0, 0.0, 0.0)
wheel_radius = 0.4
wheel_depth = 0.2
front_left_wheel_loc = (1.5, 0.85, 0.2)
front_right_wheel_loc = (1.5, -0.85, 0.2)
rear_left_wheel_loc = (-1.5, 0.85, 0.2)
rear_right_wheel_loc = (-1.5, -0.85, 0.2)
track_seg_dim = (0.8, 0.2, 0.1)
track_top_z = 0.65
track_bottom_z = -0.25
track_front_x = 1.5
track_rear_x = -1.5
track_left_y = 0.85
track_right_y = -0.85
motor_velocity = 4.0
ramp_length = 20.0
ramp_width = 4.0
ramp_thickness = 0.2
ramp_angle = 30.0

# Helper function to add hinge constraint between two objects
def add_hinge(obj1, obj2, axis='X', use_motor=False, target_velocity=0.0):
    # Create empty for constraint
    bpy.ops.object.empty_add(type='PLAIN_AXES')
    constraint_empty = bpy.context.active_object
    constraint_empty.name = f"Hinge_{obj1.name}_{obj2.name}"
    constraint_empty.location = ((obj1.location.x + obj2.location.x) / 2,
                                 (obj1.location.y + obj2.location.y) / 2,
                                 (obj1.location.z + obj2.location.z) / 2)
    # Add rigid body constraint
    bpy.ops.rigidbody.constraint_add()
    constraint = constraint_empty.rigid_body_constraint
    constraint.type = 'HINGE'
    constraint.object1 = obj1
    constraint.object2 = obj2
    # Set axis
    if axis == 'X':
        constraint.use_limits_ang_x = False
    elif axis == 'Y':
        constraint.use_limits_ang_y = False
    elif axis == 'Z':
        constraint.use_limits_ang_z = False
    # Motor settings
    if use_motor:
        constraint.use_motor_ang = True
        constraint.motor_ang_target_velocity = target_velocity
        constraint.motor_ang_max_impulse = 10.0

# Create chassis
bpy.ops.mesh.primitive_cube_add(size=1, location=chassis_loc)
chassis = bpy.context.active_object
chassis.name = "Chassis"
chassis.scale = (chassis_dim[0]/2, chassis_dim[1]/2, chassis_dim[2]/2)  # Scale from center
bpy.ops.rigidbody.object_add()
chassis.rigid_body.type = 'PASSIVE'

# Function to create wheel
def create_wheel(name, location):
    bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=wheel_radius, depth=wheel_depth, location=location)
    wheel = bpy.context.active_object
    wheel.name = name
    wheel.rotation_euler = (0, 0, math.pi/2)  # Orient cylinder axis along Y
    bpy.ops.rigidbody.object_add()
    wheel.rigid_body.type = 'ACTIVE'
    wheel.rigid_body.collision_shape = 'CYLINDER'
    return wheel

# Create wheels
wheels = {
    "front_left": create_wheel("Wheel_FL", front_left_wheel_loc),
    "front_right": create_wheel("Wheel_FR", front_right_wheel_loc),
    "rear_left": create_wheel("Wheel_RL", rear_left_wheel_loc),
    "rear_right": create_wheel("Wheel_RR", rear_right_wheel_loc)
}

# Add wheel hinges to chassis (motor on front wheels)
for side in ['front_left', 'front_right']:
    add_hinge(chassis, wheels[side], axis='X', use_motor=True, target_velocity=motor_velocity)
for side in ['rear_left', 'rear_right']:
    add_hinge(chassis, wheels[side], axis='X', use_motor=False)

# Function to create track segment
def create_track_segment(name, location, scale, rotation=(0,0,0)):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    seg = bpy.context.active_object
    seg.name = name
    seg.scale = scale
    seg.rotation_euler = rotation
    bpy.ops.rigidbody.object_add()
    seg.rigid_body.type = 'ACTIVE'
    seg.rigid_body.mass = 0.5  # Lightweight
    return seg

# Create track assemblies per side
sides = [("left", track_left_y), ("right", track_right_y)]
track_segments = {}
for side_name, side_y in sides:
    # Top segment
    top = create_track_segment(f"Track_{side_name}_top",
                               (0, side_y, track_top_z),
                               (track_seg_dim[0]/2, track_seg_dim[1]/2, track_seg_dim[2]/2))
    # Bottom segment
    bottom = create_track_segment(f"Track_{side_name}_bottom",
                                  (0, side_y, track_bottom_z),
                                  (track_seg_dim[0]/2, track_seg_dim[1]/2, track_seg_dim[2]/2))
    # Front vertical segment (rotated)
    front = create_track_segment(f"Track_{side_name}_front",
                                 (track_front_x, side_y, 0.2),
                                 (track_seg_dim[2]/2, track_seg_dim[1]/2, track_seg_dim[0]/2),
                                 rotation=(0, math.pi/2, 0))
    # Rear vertical segment
    rear = create_track_segment(f"Track_{side_name}_rear",
                                (track_rear_x, side_y, 0.2),
                                (track_seg_dim[2]/2, track_seg_dim[1]/2, track_seg_dim[0]/2),
                                rotation=(0, math.pi/2, 0))
    track_segments[side_name] = [top, bottom, front, rear]
    
    # Connect segments into loop with hinges (axis depends on orientation)
    # Top-left to front (hinge axis Y)
    add_hinge(top, front, axis='Y', use_motor=False)
    # Front to bottom (hinge axis Z)
    add_hinge(front, bottom, axis='Z', use_motor=False)
    # Bottom to rear (hinge axis Y)
    add_hinge(bottom, rear, axis='Y', use_motor=False)
    # Rear to top (hinge axis Z)
    add_hinge(rear, top, axis='Z', use_motor=False)
    
    # Connect front segment to front wheel (axis X)
    front_wheel = wheels[f"front_{side_name}"] if side_name == "left" else wheels["front_right"]
    add_hinge(front_wheel, front, axis='X', use_motor=False)
    # Connect rear segment to rear wheel
    rear_wheel = wheels[f"rear_{side_name}"] if side_name == "left" else wheels["rear_right"]
    add_hinge(rear_wheel, rear, axis='X', use_motor=False)

# Create ramp (inclined plane)
bpy.ops.mesh.primitive_cube_add(size=1, location=(0,0,0))
ramp = bpy.context.active_object
ramp.name = "Ramp"
ramp.scale = (ramp_length/2, ramp_width/2, ramp_thickness/2)
ramp.rotation_euler = (0, math.radians(ramp_angle), 0)
# Position ramp so its surface starts at (0,0,0)
# After rotation around Y, the bottom edge at -x should be at Z=0
# The cube's local origin is at center; after scaling, the front face is at x = -length/2
# Rotate around Y by +30° moves that front face downward.
# To have that face at Z=0, we shift the ramp up by (length/2)*sin(30°) in Z and forward by (length/2)*(1-cos(30°)) in X?
# Simpler: Place the ramp such that the front bottom corner is at (0,0,0).
# The cube's front-bottom corner in local coordinates is (-length/2, -width/2, -thickness/2).
# After rotation, we want that corner at world (0,0,0). So set ramp location accordingly.
ramp.location = (ramp_length/2 * math.cos(math.radians(ramp_angle)),
                 0,
                 ramp_length/2 * math.sin(math.radians(ramp_angle)))
bpy.ops.rigidbody.object_add()
ramp.rigid_body.type = 'PASSIVE'

# Set world gravity (optional, default is -9.81 Z)
bpy.context.scene.gravity = (0, 0, -9.81)
# Set simulation end frame
bpy.context.scene.frame_end = 500

print("Crawler robot and ramp created. Simulation ready.")