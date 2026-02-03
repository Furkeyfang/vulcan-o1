import bpy
import math
from mathutils import Vector

# Clear scene
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

# Parameters from summary
base = 6.0
w = 0.1
h = 0.1
vh = 3.0
mh = 1.5
apex_h = 3.0
apex_pos = Vector((0.0, 0.0, 3.0))
force = 8825.985
density = 7850.0

# Helper: create beam between two points
def create_beam(p1, p2, name):
    # Calculate midpoint, length, and direction
    mid = (p1 + p2) / 2
    length = (p1 - p2).length
    dir_vec = (p2 - p1).normalized()
    
    # Create cube and scale to beam dimensions
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=mid)
    beam = bpy.context.active_object
    beam.name = name
    beam.scale = (w, h, length / 2.0)  # Cube default size 2, so half-length
    
    # Rotate to align with direction vector (default cube aligns with Z)
    # Find rotation difference between +Z and dir_vec
    up = Vector((0, 0, 1))
    axis = up.cross(dir_vec)
    angle = up.angle(dir_vec)
    if axis.length > 0:
        beam.rotation_mode = 'AXIS_ANGLE'
        beam.rotation_axis_angle = (angle, axis.normalized())
    
    # Add rigid body
    bpy.ops.rigidbody.object_add()
    beam.rigid_body.mass = density * (w * h * length)
    beam.rigid_body.collision_shape = 'BOX'
    return beam

# Base square beams
base_corners = [
    Vector((-base/2, -base/2, 0)),
    Vector(( base/2, -base/2, 0)),
    Vector(( base/2,  base/2, 0)),
    Vector((-base/2,  base/2, 0))
]
base_beams = []
for i in range(4):
    p1 = base_corners[i]
    p2 = base_corners[(i+1)%4]
    beam = create_beam(p1, p2, f"BaseBeam{i+1}")
    beam.rigid_body.type = 'PASSIVE'  # Fixed foundation
    base_beams.append(beam)

# Vertical supports
vertical_beams = []
for i, corner in enumerate(base_corners):
    top = corner + Vector((0, 0, vh))
    beam = create_beam(corner, top, f"Vertical{i+1}")
    beam.rigid_body.type = 'ACTIVE'
    vertical_beams.append(beam)

# Diagonal beams to apex
diag_beams = []
for i, corner in enumerate(base_corners):
    top = corner + Vector((0, 0, vh))
    beam = create_beam(top, apex_pos, f"Diagonal{i+1}")
    beam.rigid_body.type = 'ACTIVE'
    diag_beams.append(beam)

# Mid-height horizontal ring
mid_corners = [c + Vector((0, 0, mh)) for c in base_corners]
mid_beams = []
for i in range(4):
    p1 = mid_corners[i]
    p2 = mid_corners[(i+1)%4]
    beam = create_beam(p1, p2, f"MidBeam{i+1}")
    beam.rigid_body.type = 'ACTIVE'
    mid_beams.append(beam)

# Cross-bracing diagonals (X-bracing in each vertical face)
brace_beams = []
face_indices = [(0,1), (1,2), (2,3), (3,0)]  # Base corners for each face
for i, (a, b) in enumerate(face_indices):
    # Two diagonals per face
    p1 = base_corners[a]
    p2 = base_corners[b] + Vector((0, 0, mh))
    beam1 = create_beam(p1, p2, f"Brace{i+1}A")
    beam1.rigid_body.type = 'ACTIVE'
    brace_beams.append(beam1)
    
    p3 = base_corners[b]
    p4 = base_corners[a] + Vector((0, 0, mh))
    beam2 = create_beam(p3, p4, f"Brace{i+1}B")
    beam2.rigid_body.type = 'ACTIVE'
    brace_beams.append(beam2)

# Create apex node (small cube for force application)
bpy.ops.mesh.primitive_cube_add(size=0.2, location=apex_pos)
apex = bpy.context.active_object
apex.name = "ApexNode"
bpy.ops.rigidbody.object_add()
apex.rigid_body.mass = 1.0  # Small mass, force will dominate

# Apply downward force (using rigid body force field)
bpy.ops.object.effector_add(type='FORCE', location=apex_pos)
force_field = bpy.context.active_object
force_field.field.strength = -force
force_field.field.use_max_distance = True
force_field.field.distance_max = 0.3
force_field.field.falloff_power = 0

# Create fixed constraints at intersections
# Base corners: base beam + vertical
for i in range(4):
    bpy.ops.object.select_all(action='DESELECT')
    base_beams[i].select_set(True)
    vertical_beams[i].select_set(True)
    bpy.context.view_layer.objects.active = vertical_beams[i]
    bpy.ops.rigidbody.connect()

# Mid-height: vertical + mid beam
for i in range(4):
    bpy.ops.object.select_all(action='DESELECT')
    vertical_beams[i].select_set(True)
    mid_beams[i].select_set(True)
    bpy.context.view_layer.objects.active = vertical_beams[i]
    bpy.ops.rigidbody.connect()

# Apex: diagonal + apex node
for diag in diag_beams:
    bpy.ops.object.select_all(action='DESELECT')
    diag.select_set(True)
    apex.select_set(True)
    bpy.context.view_layer.objects.active = diag
    bpy.ops.rigidbody.connect()

# Cross-bracing connections (at base and mid-height)
# Each brace connects to vertical at mid-height and base at corner
# Since we already have constraints at base corners and mid-height,
# additional constraints ensure full rigidity
all_beams = base_beams + vertical_beams + diag_beams + mid_beams + brace_beams
for i in range(0, len(all_beams), 2):
    if i+1 < len(all_beams):
        bpy.ops.object.select_all(action='DESELECT')
        all_beams[i].select_set(True)
        all_beams[i+1].select_set(True)
        bpy.context.view_layer.objects.active = all_beams[i]
        bpy.ops.rigidbody.connect()

# Set up rigid body world for stability
bpy.context.scene.rigidbody_world.enabled = True
bpy.context.scene.rigidbody_world.steps_per_second = 100
bpy.context.scene.rigidbody_world.solver_iterations = 50

# Ensure base is fixed
for beam in base_beams:
    beam.rigid_body.type = 'PASSIVE'