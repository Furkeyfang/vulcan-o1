import bpy
import mathutils

# Clear scene
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

# Parameters from summary
mast_height = 25.0
grid_spacing = 1.0
vert_dim = (0.2, 0.2, 1.0)
horiz_dim = (0.2, 0.2, 0.5)
corner_off = 0.5

antenna_dim = (0.5, 0.5, 0.5)
antenna_mass = 220.0
antenna_z = 25.25

# Build mast as single mesh
verts = []
edges = []
faces = []

# Helper to add beam between two points
def add_beam(p1, p2, dim, verts, edges):
    start_idx = len(verts)
    # Create local box vertices for beam oriented along Z
    sx, sy, sz = dim[0]/2, dim[1]/2, dim[2]/2
    local_verts = [
        (-sx, -sy, -sz), (-sx, sy, -sz), (sx, sy, -sz), (sx, -sy, -sz),
        (-sx, -sy, sz), (-sx, sy, sz), (sx, sy, sz), (sx, -sy, sz)
    ]
    # Transform to align with direction vector
    direction = (mathutils.Vector(p2) - mathutils.Vector(p1)).normalized()
    if direction.length == 0:
        return
    # Find rotation to align local Z with direction
    local_z = mathutils.Vector((0,0,1))
    rot_quat = local_z.rotation_difference(direction)
    center = (mathutils.Vector(p1) + mathutils.Vector(p2)) / 2
    for v in local_verts:
        tv = rot_quat @ mathutils.Vector(v) + center
        verts.append(tv[:])
    # Box edges (12 edges)
    box_edges = [(0,1),(1,2),(2,3),(3,0),(4,5),(5,6),(6,7),(7,4),(0,4),(1,5),(2,6),(3,7)]
    edges.extend([(start_idx + e[0], start_idx + e[1]) for e in box_edges])

# Generate vertical beams (4 columns, 25 segments each)
corner_points = [(-corner_off, -corner_off), (-corner_off, corner_off),
                 (corner_off, -corner_off), (corner_off, corner_off)]
for cx, cy in corner_points:
    for i in range(int(mast_height)):
        z1 = i * grid_spacing
        z2 = z1 + grid_spacing
        add_beam((cx, cy, z1), (cx, cy, z2), vert_dim, verts, edges)

# Generate horizontal beams (24 levels, 4 sides per level)
for level in range(int(mast_height)):  # levels at integer Z
    z = level + 0.5  # center of horizontal beam
    # Side 1: between (-0.5,-0.5) and (0.5,-0.5)
    add_beam((-corner_off, -corner_off, z), (corner_off, -corner_off, z), horiz_dim, verts, edges)
    # Side 2: between (-0.5,0.5) and (0.5,0.5)
    add_beam((-corner_off, corner_off, z), (corner_off, corner_off, z), horiz_dim, verts, edges)
    # Side 3: between (-0.5,-0.5) and (-0.5,0.5)
    add_beam((-corner_off, -corner_off, z), (-corner_off, corner_off, z), horiz_dim, verts, edges)
    # Side 4: between (0.5,-0.5) and (0.5,0.5)
    add_beam((corner_off, -corner_off, z), (corner_off, corner_off, z), horiz_dim, verts, edges)

# Create mast object
mesh = bpy.data.meshes.new("MastMesh")
mesh.from_pydata(verts, edges, faces)
mast = bpy.data.objects.new("Mast", mesh)
bpy.context.collection.objects.link(mast)

# Add rigid body to mast
bpy.ops.object.select_all(action='DESELECT')
mast.select_set(True)
bpy.context.view_layer.objects.active = mast
bpy.ops.rigidbody.object_add()
mast.rigid_body.type = 'PASSIVE'

# Create antenna
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0,0,antenna_z))
antenna = bpy.context.active_object
antenna.scale = antenna_dim
bpy.ops.rigidbody.object_add()
antenna.rigid_body.mass = antenna_mass
antenna.rigid_body.type = 'ACTIVE'

# Add fixed constraint between antenna and mast
bpy.ops.object.select_all(action='DESELECT')
antenna.select_set(True)
mast.select_set(True)
bpy.context.view_layer.objects.active = antenna
bpy.ops.rigidbody.constraint_add()
constraint = antenna.rigid_body_constraints[0]
constraint.type = 'FIXED'
constraint.object1 = antenna
constraint.object2 = mast

# Position constraint at top center
constraint.pivot_x = 0.0
constraint.pivot_y = 0.0
constraint.pivot_z = mast_height

# Ensure all transforms are applied
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)