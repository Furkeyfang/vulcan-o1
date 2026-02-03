import bpy
import math
from mathutils import Vector, Matrix

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# ========== Parameters ==========
seg_count = 12
seg_size = 2.0
seg_mass = 6400.0  # Approx steel density 8000 kg/m³ * 8 m³
joint_count = seg_count - 1
brace_x = 0.5
brace_y = 0.5
brace_z = math.sqrt(8)  # 2.828...
brace_mass = 8000 * (brace_x * brace_y * brace_z)  # 5656.8 kg
load_size = 1.0
load_mass = 1800.0
load_z = 24.5  # Center of 1m cube placed on top (tower top at Z=24)
break_thresh = 1e6

# ========== Helper Functions ==========
def add_cube(name, location, scale, mass, passive=False):
    """Create a cube with rigid body physics."""
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = scale
    bpy.ops.rigidbody.object_add()
    obj.rigid_body.mass = mass
    if passive:
        obj.rigid_body.type = 'PASSIVE'
    else:
        obj.rigid_body.type = 'ACTIVE'
    return obj

def add_fixed_constraint(obj_a, obj_b, break_threshold):
    """Create a fixed constraint between two objects."""
    # Create empty object as constraint holder
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=obj_a.location)
    empty = bpy.context.active_object
    empty.name = f"Constraint_{obj_a.name}_{obj_a.name}"
    # Add rigid body constraint
    bpy.ops.rigidbody.constraint_add()
    con = empty.rigid_body_constraint
    con.type = 'FIXED'
    con.object1 = obj_a
    con.object2 = obj_b
    con.breaking_threshold = break_threshold
    return con

# ========== Build Tower Segments ==========
segments = []
for i in range(1, seg_count + 1):
    z_center = i * seg_size - seg_size/2  # i=1 => z=1
    seg = add_cube(
        name=f"Segment_{i:02d}",
        location=(0.0, 0.0, z_center),
        scale=(seg_size, seg_size, seg_size),
        mass=seg_mass,
        passive=(i == 1)  # Only base is passive
    )
    segments.append(seg)

# ========== Build Diagonal Braces ==========
braces = []
for joint in range(joint_count):  # 0..10
    lower_seg = segments[joint]
    upper_seg = segments[joint + 1]
    z_joint = (joint + 1) * seg_size  # Z coordinate of joint plane
    # Four corners: (+1,+1), (+1,-1), (-1,+1), (-1,-1) in segment-local coordinates
    for x_sign, y_sign in [(1,1), (1,-1), (-1,1), (-1,-1)]:
        # Start and end points of diagonal in world coordinates
        start = Vector((x_sign * seg_size/2, y_sign * seg_size/2, z_joint))
        end = Vector((-x_sign * seg_size/2, -y_sign * seg_size/2, z_joint + seg_size))
        # Brace center is midpoint
        center = (start + end) / 2
        # Direction vector and length
        dir_vec = end - start
        length = dir_vec.length
        # Rotation to align local Z with dir_vec
        # First rotate around global Z to point in correct XY direction
        xy_angle = math.atan2(dir_vec.y, dir_vec.x)
        # Then tilt down/up by angle between dir_vec and XY plane
        tilt_angle = math.asin(dir_vec.z / length)
        # Create brace cube
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=center)
        brace = bpy.context.active_object
        brace.name = f"Brace_J{joint+1:02d}_{x_sign}{y_sign}"
        # Scale: cross-section in X,Y, length in Z
        brace.scale = (brace_x, brace_y, length/2.0)  # Cube default size=2, so scale=length/2
        # Apply rotations
        brace.rotation_euler = (0.0, tilt_angle, xy_angle)
        # Add rigid body
        bpy.ops.rigidbody.object_add()
        brace.rigid_body.mass = brace_mass
        braces.append(brace)
        # Constraints to adjacent segments
        add_fixed_constraint(brace, lower_seg, break_thresh)
        add_fixed_constraint(brace, upper_seg, break_thresh)

# ========== Build Load Cube ==========
load_cube = add_cube(
    name="Load_Cube",
    location=(0.0, 0.0, load_z),
    scale=(load_size, load_size, load_size),
    mass=load_mass,
    passive=False
)
# Constrain load to top segment
add_fixed_constraint(load_cube, segments[-1], break_thresh)

# ========== Finalize Scene ==========
# Set gravity to Earth standard (negative Z)
bpy.context.scene.gravity = (0.0, 0.0, -9.81)
# Set simulation end frame
bpy.context.scene.frame_end = 500
# Ensure rigid body world is enabled
if not bpy.context.scene.rigidbody_world:
    bpy.ops.rigidbody.world_add()