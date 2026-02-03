import bpy
import math
import mathutils
from mathutils import Vector

# Clear scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Parameters from summary
tower_height = 30.0
base_width = 4.0
top_width = 2.0
vertical_member_length = 2.0
vertical_cross = 0.2
diagonal_length = 1.0  # Will be scaled
diagonal_cross = 0.2
bracing_levels = [5.0, 10.0, 15.0, 20.0, 25.0]
platform_dim = (1.0, 1.0, 0.5)
platform_loc_z = 30.25
platform_mass = 350.0
guy_wire_radius = 0.05
anchor_radius = 10.0
anchor_z = 0.0
num_vertical_segments = 15
num_corners = 4

# Helper function to create a cube with given dimensions and location
def create_cube(dim, location, name):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = (dim[0], dim[1], dim[2])
    bpy.ops.object.transform_apply(scale=True)
    return obj

# Helper function to create a cylinder between two points
def create_cylinder_between(point1, point2, radius, name):
    # Calculate center and rotation
    vec = point2 - point1
    center = (point1 + point2) / 2
    length = vec.length
    
    # Create cylinder
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=16,
        radius=radius,
        depth=length,
        location=center
    )
    obj = bpy.context.active_object
    obj.name = name
    
    # Rotate to align with vector
    if length > 0:
        # Default cylinder is along Z
        axis = Vector((0, 0, 1))
        rot_quat = axis.rotation_difference(vec.normalized())
        obj.rotation_euler = rot_quat.to_euler()
    
    return obj, length

# Helper function to add rigid body physics
def add_rigidbody(obj, body_type='ACTIVE', mass=1.0):
    bpy.context.view_layer.objects.active = obj
    bpy.ops.rigidbody.object_add()
    obj.rigid_body.type = body_type
    obj.rigid_body.mass = mass
    obj.rigid_body.collision_shape = 'BOX'

# Helper function to add fixed constraint between two objects
def add_fixed_constraint(obj1, obj2, name):
    bpy.context.view_layer.objects.active = obj1
    bpy.ops.rigidbody.constraint_add()
    constraint = obj1.rigid_body.constraints[-1]
    constraint.name = name
    constraint.type = 'FIXED'
    constraint.object2 = obj2

# Define corner indices: 0=front-right, 1=front-left, 2=back-left, 3=back-right
corner_signs = [(1, 1), (-1, 1), (-1, -1), (1, -1)]

# Function to get corner position at height z
def get_corner_pos(corner_idx, z):
    sign_x, sign_y = corner_signs[corner_idx]
    # Linear interpolation between base and top
    base_half = base_width / 2
    top_half = top_width / 2
    t = z / tower_height
    x = sign_x * (base_half * (1 - t) + top_half * t)
    y = sign_y * (base_half * (1 - t) + top_half * t)
    return Vector((x, y, z))

# Create vertical legs
vertical_members = []
for corner in range(num_corners):
    for seg in range(num_vertical_segments):
        z_start = seg * vertical_member_length
        z_end = (seg + 1) * vertical_member_length
        
        # Start and end points
        p1 = get_corner_pos(corner, z_start)
        p2 = get_corner_pos(corner, z_end)
        
        # Create member (will be rotated to align with vector)
        center = (p1 + p2) / 2
        vec = p2 - p1
        actual_length = vec.length
        
        # Create cube and scale
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=center)
        obj = bpy.context.active_object
        obj.name = f"Vertical_{corner}_{seg}"
        obj.scale = (vertical_cross, vertical_cross, actual_length)
        bpy.ops.object.transform_apply(scale=True)
        
        # Rotate to align with vector
        if actual_length > 0:
            axis = Vector((0, 0, 1))
            rot_quat = axis.rotation_difference(vec.normalized())
            obj.rotation_euler = rot_quat.to_euler()
        
        vertical_members.append(obj)

# Create diagonal bracing at each level
diagonal_members = []
for level_z in bracing_levels:
    # Get corner positions at this level
    corners = [get_corner_pos(i, level_z) for i in range(4)]
    
    # Diagonal 1: corner 0 to corner 2
    p1, p2 = corners[0], corners[2]
    vec = p2 - p1
    center = (p1 + p2) / 2
    actual_length = vec.length
    
    # Create cube and scale
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=center)
    obj1 = bpy.context.active_object
    obj1.name = f"Diagonal_0-2_{level_z}"
    obj1.scale = (diagonal_cross, diagonal_cross, actual_length)
    bpy.ops.object.transform_apply(scale=True)
    
    # Rotate
    if actual_length > 0:
        axis = Vector((0, 0, 1))
        rot_quat = axis.rotation_difference(vec.normalized())
        obj1.rotation_euler = rot_quat.to_euler()
    
    diagonal_members.append(obj1)
    
    # Diagonal 2: corner 1 to corner 3
    p1, p2 = corners[1], corners[3]
    vec = p2 - p1
    center = (p1 + p2) / 2
    actual_length = vec.length
    
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=center)
    obj2 = bpy.context.active_object
    obj2.name = f"Diagonal_1-3_{level_z}"
    obj2.scale = (diagonal_cross, diagonal_cross, actual_length)
    bpy.ops.object.transform_apply(scale=True)
    
    if actual_length > 0:
        axis = Vector((0, 0, 1))
        rot_quat = axis.rotation_difference(vec.normalized())
        obj2.rotation_euler = rot_quat.to_euler()
    
    diagonal_members.append(obj2)

# Create top platform
platform = create_cube(
    platform_dim,
    (0.0, 0.0, platform_loc_z),
    "TopPlatform"
)

# Create ground anchors (passive cubes)
anchors = []
anchor_points = [
    (anchor_radius, anchor_radius, anchor_z),
    (-anchor_radius, anchor_radius, anchor_z),
    (-anchor_radius, -anchor_radius, anchor_z),
    (anchor_radius, -anchor_radius, anchor_z)
]

for i, pos in enumerate(anchor_points):
    anchor = create_cube(
        (0.5, 0.5, 0.5),
        pos,
        f"Anchor_{i}"
    )
    anchors.append(anchor)

# Create guy-wires
guy_wires = []
platform_corners = [
    (0.5, 0.5, platform_loc_z),
    (-0.5, 0.5, platform_loc_z),
    (-0.5, -0.5, platform_loc_z),
    (0.5, -0.5, platform_loc_z)
]

for i in range(4):
    start = Vector(platform_corners[i])
    end = Vector(anchor_points[i])
    
    wire, wire_length = create_cylinder_between(
        start, end, guy_wire_radius, f"GuyWire_{i}"
    )
    guy_wires.append(wire)
    print(f"Guy wire {i} length: {wire_length:.2f}m")

# Add rigid body physics
for obj in vertical_members + diagonal_members:
    add_rigidbody(obj, 'ACTIVE', mass=50.0)  # Steel members ~50kg each

add_rigidbody(platform, 'ACTIVE', mass=platform_mass)

for anchor in anchors:
    add_rigidbody(anchor, 'PASSIVE', mass=1000.0)

for wire in guy_wires:
    add_rigidbody(wire, 'ACTIVE', mass=10.0)  # Cable mass

# Add fixed constraints between vertical segments in each leg
for corner in range(num_corners):
    for seg in range(num_vertical_segments - 1):
        idx1 = corner * num_vertical_segments + seg
        idx2 = corner * num_vertical_segments + seg + 1
        add_fixed_constraint(
            vertical_members[idx1],
            vertical_members[idx2],
            f"Fixed_Vertical_{corner}_{seg}"
        )

# Add fixed constraints between diagonals and nearest verticals
# This is simplified - in reality each diagonal connects to 2 verticals at same level
# We'll connect to the vertical segment that contains the level point
for level_idx, level_z in enumerate(bracing_levels):
    # Find vertical segments at this height for each corner
    for corner in range(4):
        seg_index = int(level_z // vertical_member_length)
        if seg_index >= num_vertical_segments:
            seg_index = num_vertical_segments - 1
        
        vert_idx = corner * num_vertical_segments + seg_index
        # Connect to both diagonals at this level
        diag1_idx = level_idx * 2
        diag2_idx = level_idx * 2 + 1
        
        # Check if diagonal connects to this corner
        corners_for_diag1 = [0, 2]
        corners_for_diag2 = [1, 3]
        
        if corner in corners_for_diag1:
            add_fixed_constraint(
                vertical_members[vert_idx],
                diagonal_members[diag1_idx],
                f"Fixed_Diag1_Corner{corner}_L{level_z}"
            )
        
        if corner in corners_for_diag2:
            add_fixed_constraint(
                vertical_members[vert_idx],
                diagonal_members[diag2_idx],
                f"Fixed_Diag2_Corner{corner}_L{level_z}"
            )

# Connect top platform to top vertical segments
for corner in range(4):
    top_vert_idx = corner * num_vertical_segments + (num_vertical_segments - 1)
    add_fixed_constraint(
        platform,
        vertical_members[top_vert_idx],
        f"Fixed_Platform_Corner{corner}"
    )

# Connect guy-wires to platform and anchors
for i in range(4):
    # Wire to platform
    add_fixed_constraint(
        guy_wires[i],
        platform,
        f"Fixed_Wire{i}_Platform"
    )
    
    # Wire to anchor
    add_fixed_constraint(
        guy_wires[i],
        anchors[i],
        f"Fixed_Wire{i}_Anchor"
    )

print("Tower construction complete. Total objects:", len(bpy.data.objects))
print("Platform mass set to:", platform.rigid_body.mass, "kg")