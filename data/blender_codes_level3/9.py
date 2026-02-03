import bpy
import math

# Clear scene
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

# Parameters from summary
L = 3.0
chassis_thickness = 0.3
chassis_center = (0.0, 0.0, 0.15)
wheel_radius = 0.4
wheel_depth = 0.25
motor_velocity = 3.0

R = L / math.sqrt(3.0)
vertex_angles = [math.pi/2, 7*math.pi/6, 11*math.pi/6]
vertex_positions = []
for angle in vertex_angles:
    x = R * math.cos(angle)
    y = R * math.sin(angle)
    vertex_positions.append((x, y, 0.0))

wheel_z = -wheel_radius
wheel_rotation = (0.0, math.pi/2, 0.0)  # 90° around Y to align cylinder axis with X

# Create Ground Plane
bpy.ops.mesh.primitive_plane_add(size=20.0, location=(0.0, 0.0, -1.0))
ground = bpy.context.active_object
bpy.ops.rigidbody.object_add()
ground.rigid_body.type = 'PASSIVE'

# Create Chassis (Triangular Prism)
# Define vertices for bottom and top triangles
verts = []
for v in vertex_positions:
    verts.append(v)  # bottom
for v in vertex_positions:
    verts.append((v[0], v[1], v[2] + chassis_thickness))  # top

# Define faces (3 side quads, bottom triangle, top triangle)
faces = [
    (0, 1, 4, 3),  # side 0-1
    (1, 2, 5, 4),  # side 1-2
    (2, 0, 3, 5),  # side 2-0
    (0, 2, 1),     # bottom triangle
    (3, 4, 5)      # top triangle
]

mesh = bpy.data.meshes.new("Chassis_Mesh")
mesh.from_pydata(verts, [], faces)
obj = bpy.data.objects.new("Chassis", mesh)
bpy.context.collection.objects.link(obj)
bpy.context.view_layer.objects.active = obj
obj.select_set(True)
obj.location = chassis_center

# Set origin to geometry center (0,0,0) in local coordinates
bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
obj.location = chassis_center  # reapply after origin set

# Add rigid body to chassis
bpy.ops.rigidbody.object_add()
obj.rigid_body.type = 'ACTIVE'

# Create Wheels
wheel_objects = []
for i, vertex in enumerate(vertex_positions):
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=32,
        radius=wheel_radius,
        depth=wheel_depth,
        location=(vertex[0], vertex[1], wheel_z),
        rotation=wheel_rotation
    )
    wheel = bpy.context.active_object
    wheel.name = f"Wheel_{i}"
    bpy.ops.rigidbody.object_add()
    wheel.rigid_body.type = 'ACTIVE'
    wheel_objects.append(wheel)

# Create Hinge Constraints
for wheel in wheel_objects:
    # Create empty for constraint (optional, but hinge needs two objects)
    # We'll add constraint directly from wheel to chassis
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=wheel.location)
    empty = bpy.context.active_object
    empty.name = f"Hinge_Pivot_{wheel.name}"
    
    # Add constraint to wheel
    bpy.ops.rigidbody.constraint_add()
    constraint = wheel.rigid_body_constraints[-1]
    constraint.type = 'HINGE'
    constraint.object1 = bpy.data.objects["Chassis"]
    constraint.object2 = wheel
    constraint.pivot_type = 'ACTIVE'
    # Set axis to world X (1,0,0)
    constraint.use_limits_x = False
    constraint.limit_angle_max_x = 0.0
    constraint.limit_angle_min_x = 0.0
    constraint.use_limit_x = False
    # Enable motor
    constraint.use_motor_x = True
    constraint.motor_velocity_x = motor_velocity
    constraint.motor_max_torque_x = 10.0  # sufficient torque
    
    # Keyframe motor enable at frame 1
    constraint.keyframe_insert(data_path="use_motor_x", frame=1)

# Set scene frames for simulation
scene = bpy.context.scene
scene.frame_end = 300
scene.rigidbody_world.steps_per_second = 60
scene.rigidbody_world.solver_iterations = 10

# Ensure proper collision shapes
bpy.data.objects["Chassis"].rigid_body.collision_shape = 'MESH'
for wheel in wheel_objects:
    wheel.rigid_body.collision_shape = 'CYLINDER'
    wheel.rigid_body.use_margin = True
    wheel.rigid_body.collision_margin = 0.0

# Set initial linear velocity to zero (optional)
bpy.data.objects["Chassis"].rigid_body.linear_velocity = (0.0, 0.0, 0.0)
for wheel in wheel_objects:
    wheel.rigid_body.linear_velocity = (0.0, 0.0, 0.0)