import bpy
import math
from mathutils import Matrix, Vector

# Clear scene
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

# Define variables from summary
chassis_size = (3.0, 2.0, 0.6)
chassis_loc = (0.0, 0.0, 0.3)
wheel_radius = 1.0
wheel_depth = 0.4
front_wheel_loc = (-1.5, 0.0, 1.0)
rear_wheel_loc = (1.5, 0.0, 1.0)
pad_count = 20
pad_size = (0.3, 0.1, 0.05)
loop_length = 2 * 3.0 + 2 * math.pi * wheel_radius
pad_spacing_arc = loop_length / pad_count
straight_length = 3.0
wheel_circ_half = math.pi * wheel_radius
motor_velocity = 6.0

# Ensure rigid body world exists
if bpy.context.scene.rigidbody_world is None:
    bpy.ops.rigidbody.world_add()

# Helper to add rigid body
def add_rigidbody(obj, body_type='ACTIVE', mass=1.0):
    bpy.ops.rigidbody.object_add()
    obj.rigid_body.type = body_type
    obj.rigid_body.mass = mass
    obj.rigid_body.collision_shape = 'MESH'

# 1. Create chassis
bpy.ops.mesh.primitive_cube_add(size=1, location=chassis_loc)
chassis = bpy.context.active_object
chassis.scale = (chassis_size[0]/2, chassis_size[1]/2, chassis_size[2]/2)  # scale is half-size
chassis.name = "Chassis"
add_rigidbody(chassis, body_type='ACTIVE', mass=chassis_size[0]*chassis_size[1]*chassis_size[2]*100)  # density ~100

# 2. Create wheels
def create_wheel(name, location):
    bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=wheel_radius, depth=wheel_depth, location=location)
    wheel = bpy.context.active_object
    wheel.name = name
    wheel.rotation_euler = (0, math.pi/2, 0)  # orient cylinder axis along X
    add_rigidbody(wheel, body_type='ACTIVE', mass=math.pi*wheel_radius**2*wheel_depth*500)  # density ~500
    return wheel

front_wheel = create_wheel("FrontWheel", front_wheel_loc)
rear_wheel = create_wheel("RearWheel", rear_wheel_loc)

# 3. Add hinge constraints between chassis and wheels
def add_hinge(obj_a, obj_b, pivot, axis_type='LOCAL_X', use_motor=False, target_velocity=0):
    # Create empty at pivot
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=pivot)
    empty = bpy.context.active_object
    empty.name = f"Hinge_{obj_a.name}_{obj_b.name}"
    # Add rigid body constraint
    bpy.ops.rigidbody.constraint_add()
    con = bpy.context.active_object
    con.name = f"Constraint_{obj_a.name}_{obj_b.name}"
    con.rigid_body_constraint.type = 'HINGE'
    con.rigid_body_constraint.object1 = obj_a
    con.rigid_body_constraint.object2 = obj_b
    con.rigid_body_constraint.pivot_type = 'CUSTOM'
    con.rigid_body_constraint.use_override_solver_iterations = True
    con.rigid_body_constraint.solver_iterations = 50
    # Set pivot and axis in world coordinates
    con.location = pivot
    if axis_type == 'LOCAL_X':
        con.rotation_euler = (0, 0, 0)  # X axis of empty
    # Enable motor
    if use_motor:
        con.rigid_body_constraint.use_motor = True
        con.rigid_body_constraint.motor_angular_target_velocity = target_velocity
        con.rigid_body_constraint.motor_max_impulse = 1000.0
    # Parent empty to chassis for organization (optional)
    empty.parent = obj_a

# Hinge pivots at wheel centers
add_hinge(chassis, front_wheel, front_wheel_loc, use_motor=True, target_velocity=motor_velocity)
add_hinge(chassis, rear_wheel, rear_wheel_loc, use_motor=True, target_velocity=motor_velocity)

# 4. Create track pads
def position_on_loop(t):  # t from 0 to 1
    # t * loop_length = arc length from start (top midpoint between wheels)
    # Path: start at top middle (0,0,1.0+pad_size[2]/2), go +Z direction? Actually track wraps around wheels.
    # Let's define loop: start at top front (front_wheel top), go rearward along top straight, around rear wheel, forward along bottom, around front wheel.
    # Parameterization:
    # 0-0.5: top straight + rear semicircle
    # 0.5-1.0: bottom straight + front semicircle
    # But easier: compute directly from arc length s = t * loop_length
    s = t * loop_length
    if s < straight_length:  # top straight from front to rear
        x = front_wheel_loc[0] + s  # from -1.5 to 1.5
        z = wheel_radius + pad_size[2]/2  # top of wheel + half pad thickness
        tangent = Vector((1,0,0))
    elif s < straight_length + wheel_circ_half:  # rear wheel semicircle (top to bottom)
        angle = (s - straight_length) / wheel_radius  # rad from 0 to π
        x = rear_wheel_loc[0] + wheel_radius * math.sin(angle)  # offset from wheel center
        z = wheel_radius * math.cos(angle) + pad_size[2]/2
        tangent = Vector((math.cos(angle), 0, -math.sin(angle)))
    elif s < 2*straight_length + wheel_circ_half:  # bottom straight from rear to front
        s_local = s - (straight_length + wheel_circ_half)
        x = rear_wheel_loc[0] - s_local  # from 1.5 to -1.5
        z = -wheel_radius + pad_size[2]/2  # bottom of wheel
        tangent = Vector((-1,0,0))
    else:  # front wheel semicircle (bottom to top)
        angle = (s - (2*straight_length + wheel_circ_half)) / wheel_radius + math.pi  # from π to 2π
        x = front_wheel_loc[0] + wheel_radius * math.sin(angle)
        z = wheel_radius * math.cos(angle) + pad_size[2]/2
        tangent = Vector((math.cos(angle), 0, -math.sin(angle)))
    return Vector((x, 0.0, z)), tangent

pads = []
for i in range(pad_count):
    t = i / pad_count
    pos, tangent = position_on_loop(t)
    # Create pad
    bpy.ops.mesh.primitive_cube_add(size=1, location=pos)
    pad = bpy.context.active_object
    pad.name = f"TrackPad_{i:02d}"
    pad.scale = (pad_size[0]/2, pad_size[1]/2, pad_size[2]/2)
    # Orient pad: length along tangent, width along Y, thickness perpendicular to loop plane
    normal = Vector((0,1,0))
    binormal = tangent.cross(normal).normalized()
    # Correct orientation matrix
    mat = Matrix([tangent, normal, binormal]).transposed().to_4x4()
    mat.translation = pos
    pad.matrix_world = mat
    add_rigidbody(pad, body_type='ACTIVE', mass=pad_size[0]*pad_size[1]*pad_size[2]*800)
    pads.append(pad)

# 5. Connect pads with fixed constraints (and close loop)
def add_fixed_constraint(obj_a, obj_b):
    # Create empty at midpoint
    mid = (obj_a.location + obj_b.location) / 2
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=mid)
    empty = bpy.context.active_object
    empty.name = f"Fixed_{obj_a.name}_{obj_b.name}"
    bpy.ops.rigidbody.constraint_add()
    con = bpy.context.active_object
    con.name = f"Constraint_{obj_a.name}_{obj_b.name}"
    con.rigid_body_constraint.type = 'FIXED'
    con.rigid_body_constraint.object1 = obj_a
    con.rigid_body_constraint.object2 = obj_b
    con.rigid_body_constraint.pivot_type = 'CUSTOM'
    con.rigid_body_constraint.use_override_solver_iterations = True
    con.rigid_body_constraint.solver_iterations = 50
    con.location = mid
    # Parent empty to one of the pads
    empty.parent = obj_a

for i in range(pad_count-1):
    add_fixed_constraint(pads[i], pads[i+1])
# Close loop
add_fixed_constraint(pads[-1], pads[0])

# 6. Adjust rigid body settings for stability
rb_world = bpy.context.scene.rigidbody_world
rb_world.steps_per_second = 60
rb_world.solver_iterations = 50
rb_world.use_split_impulse = True

# 7. Set initial keyframe for chassis location at frame 1
chassis.keyframe_insert(data_path="location", frame=1)

# 8. Set simulation end frame
bpy.context.scene.frame_end = 300

print("Tracked robot assembly complete. Motors activated with velocity", motor_velocity, "rad/s.")
print("Simulation will run for 300 frames.")