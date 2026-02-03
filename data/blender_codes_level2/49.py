import bpy
import math
from mathutils import Vector

# Clear scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Parameters from summary
H = 6.0
W = 8.0
cross = 0.2
v_len = 1.0
h_len = 1.0
d_len = 1.414
load_mass = 600.0
base_z = 0.0
top_z = H
left_x = -W/2
right_x = W/2
mid_x_vals = [-3.0, -1.0, 1.0, 3.0]
mid_z = H/2
load_pos = (0.0, 0.0, top_z)
const_offset = 0.01

# Function to create a member
def create_member(name, loc, rot_euler, scale):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=loc)
    obj = bpy.context.active_object
    obj.name = name
    obj.rotation_euler = rot_euler
    obj.scale = scale
    bpy.ops.rigidbody.object_add()
    return obj

# Joint positions (X, Z, Y=0)
joints = {
    'A1': (left_x, 0, base_z), 'A2': (left_x+2, 0, base_z), 'A3': (0.0, 0, base_z),
    'A4': (right_x-2, 0, base_z), 'A5': (right_x, 0, base_z),
    'B1': (left_x, 0, top_z), 'B2': (left_x+2, 0, top_z), 'B3': (0.0, 0, top_z),
    'B4': (right_x-2, 0, top_z), 'B5': (right_x, 0, top_z),
    'C1': (left_x+1, 0, mid_z), 'C2': (left_x+3, 0, mid_z),
    'C3': (right_x-3, 0, mid_z), 'C4': (right_x-1, 0, mid_z)
}

# Create bottom horizontals (passive)
for i in range(4):
    x1, z1 = joints[f'A{i+1}'][0], joints[f'A{i+1}'][2]
    x2, z2 = joints[f'A{i+2}'][0], joints[f'A{i+2}'][2]
    cx, cz = (x1 + x2)/2, (z1 + z2)/2
    length = abs(x2 - x1)
    create_member(f'bottom_horiz_{i}', (cx, 0, cz), (0,0,0), (length, cross, cross))
    bpy.context.active_object.rigid_body.type = 'PASSIVE'

# Create top horizontals (active)
for i in range(4):
    x1, z1 = joints[f'B{i+1}'][0], joints[f'B{i+1}'][2]
    x2, z2 = joints[f'B{i+2}'][0], joints[f'B{i+2}'][2]
    cx, cz = (x1 + x2)/2, (z1 + z2)/2
    length = abs(x2 - x1)
    create_member(f'top_horiz_{i}', (cx, 0, cz), (0,0,0), (length, cross, cross))

# Create verticals
verts = [('A1','B1'), ('A2','B2'), ('A3','B3'), ('A4','B4'), ('A5','B5')]
for i, (bot, top) in enumerate(verts):
    x1, z1 = joints[bot][0], joints[bot][2]
    x2, z2 = joints[top][0], joints[top][2]
    cx, cz = (x1 + x2)/2, (z1 + z2)/2
    create_member(f'vert_{i}', (cx, 0, cz), (0,0,0), (cross, cross, H))

# Create diagonals (Howe pattern: left side slope down to right, right side slope down to left)
diags = [
    ('A1','C1'), ('C1','B2'), ('A2','C2'), ('C2','B3'),
    ('B3','C3'), ('C3','A4'), ('B4','C4'), ('C4','A5')
]
for i, (j1, j2) in enumerate(diags):
    x1, z1 = joints[j1][0], joints[j1][2]
    x2, z2 = joints[j2][0], joints[j2][2]
    cx, cz = (x1 + x2)/2, (z1 + z2)/2
    length = math.hypot(x2-x1, z2-z1)
    angle = math.atan2(z2-z1, x2-x1)
    create_member(f'diag_{i}', (cx, 0, cz), (0, -angle, 0), (length, cross, cross))

# Create fixed constraints at each joint
for j_name, (jx, jy, jz) in joints.items():
    # Find all objects whose bounds include this joint (within tolerance)
    nearby = []
    for obj in bpy.data.objects:
        if obj.type == 'MESH' and obj.name.startswith(('bottom','top','vert','diag')):
            # Simple center-distance check (crude but works for this layout)
            center = Vector(obj.matrix_world @ Vector((0,0,0)))
            if (Vector((jx, jy, jz)) - center).length < 1.0:
                nearby.append(obj)
    
    if len(nearby) >= 2:
        # Create constraint between first object and all others
        for k in range(1, len(nearby)):
            # Create empty at joint for constraint
            bpy.ops.object.empty_add(type='PLAIN_AXES', location=(jx, jy+const_offset, jz))
            empty = bpy.context.active_object
            empty.name = f'const_{j_name}_{k}'
            bpy.ops.rigidbody.constraint_add()
            const = empty.rigid_body_constraint
            const.type = 'FIXED'
            const.object1 = nearby[0]
            const.object2 = nearby[k]

# Reinforce top central joint (B3) with extra mass
for obj in bpy.data.objects:
    if obj.type == 'MESH' and 'vert_2' in obj.name or 'top_horiz_2' in obj.name or 'diag_3' in obj.name or 'diag_4' in obj.name:
        obj.rigid_body.mass *= 2.0

# Add load at top center
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.3, location=load_pos)
load = bpy.context.active_object
load.name = 'load'
bpy.ops.rigidbody.object_add()
load.rigid_body.mass = load_mass
# Fix load to top central joint members
for obj in bpy.data.objects:
    if obj.type == 'MESH' and ('vert_2' in obj.name or 'top_horiz_2' in obj.name):
        bpy.ops.object.empty_add(type='PLAIN_AXES', location=(load_pos[0], const_offset, load_pos[2]))
        empty = bpy.context.active_object
        empty.name = f'load_const_to_{obj.name}'
        bpy.ops.rigidbody.constraint_add()
        const = empty.rigid_body_constraint
        const.type = 'FIXED'
        const.object1 = load
        const.object2 = obj

# Set gravity and simulation settings
bpy.context.scene.gravity = (0, 0, -9.81)
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 50
bpy.context.scene.frame_end = 100