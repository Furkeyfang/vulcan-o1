import bpy
import math
from mathutils import Vector

# Clear scene
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)

# Extract variables
H = 20.0
base_hw = 2.0
top_hw = 0.5
cross = 0.2
length = 1.0
n_seg = 20
plat_sz = 1.0
plat_thk = 0.2
steel_rho = 7850.0
plat_mass = 300.0
ground_sz = 30.0
frames = 100

# Helper: Create cube between two points
def create_member(p1, p2, name):
    # Calculate midpoint and direction
    mid = (p1 + p2) / 2
    dir_vec = p2 - p1
    dist = dir_vec.length
    
    # Create base cube (default 2×2×2)
    bpy.ops.mesh.primitive_cube_add(size=1, location=mid)
    obj = bpy.context.active_object
    obj.name = name
    
    # Scale: cross-section 0.2×0.2, length = dist
    scale_x = cross / 2.0  # 0.2 / 2 (since default cube is 2 units wide)
    scale_y = cross / 2.0
    scale_z = dist / 2.0   # desired length / 2
    obj.scale = (scale_x, scale_y, scale_z)
    
    # Rotate to align with direction vector
    if dir_vec.length > 0:
        # Default cube local Z is up
        up = Vector((0, 0, 1))
        rot_quat = up.rotation_difference(dir_vec.normalized())
        obj.rotation_mode = 'QUATERNION'
        obj.rotation_quaternion = rot_quat
    
    # Apply scale and rotation
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    return obj

# Create ground plane
bpy.ops.mesh.primitive_plane_add(size=ground_sz, location=(0,0,-0.1))
ground = bpy.context.active_object
ground.name = "Ground"
bpy.ops.rigidbody.object_add()
ground.rigid_body.type = 'PASSIVE'

# Create all structural members
members = []
# Four corners indices: 0=front-left, 1=front-right, 2=back-right, 3=back-left
corner_offsets = [(-1,-1), (1,-1), (1,1), (-1,1)]

# Store joint positions for constraint creation
joints = {}  # key: (corner_idx, level_z) -> list of member objects

for seg in range(n_seg):
    z_bot = seg * length
    z_top = (seg + 1) * length
    
    # Tapering interpolation
    taper_bot = base_hw - (base_hw - top_hw) * (z_bot / H)
    taper_top = base_hw - (base_hw - top_hw) * (z_top / H)
    
    # Create vertical members
    for c_idx, (dx, dy) in enumerate(corner_offsets):
        p1 = Vector((dx * taper_bot, dy * taper_bot, z_bot))
        p2 = Vector((dx * taper_top, dy * taper_top, z_top))
        vert = create_member(p1, p2, f"Vert_{c_idx}_{seg}")
        members.append(vert)
        
        # Register joints
        for z_val, point in [(z_bot, p1), (z_top, p2)]:
            key = (c_idx, round(z_val, 3))
            joints.setdefault(key, []).append(vert)
    
    # Create diagonal bracing for each face
    # Face definition: corners (0,1)=front, (1,2)=right, (2,3)=back, (3,0)=left
    faces = [(0,1), (1,2), (2,3), (3,0)]
    for f_idx, (c1, c2) in enumerate(faces):
        dx1, dy1 = corner_offsets[c1]
        dx2, dy2 = corner_offsets[c2]
        
        # Diagonal 1: c1_bottom to c2_top
        p1 = Vector((dx1 * taper_bot, dy1 * taper_bot, z_bot))
        p2 = Vector((dx2 * taper_top, dy2 * taper_top, z_top))
        diag1 = create_member(p1, p2, f"Diag1_{f_idx}_{seg}")
        members.append(diag1)
        
        # Diagonal 2: c2_bottom to c1_top
        p3 = Vector((dx2 * taper_bot, dy2 * taper_bot, z_bot))
        p4 = Vector((dx1 * taper_top, dy1 * taper_top, z_top))
        diag2 = create_member(p3, p4, f"Diag2_{f_idx}_{seg}")
        members.append(diag2)
        
        # Register joints for diagonals
        joints[(c1, round(z_bot, 3))].append(diag1)
        joints[(c2, round(z_top, 3))].append(diag1)
        joints[(c2, round(z_bot, 3))].append(diag2)
        joints[(c1, round(z_top, 3))].append(diag2)

# Create top platform
bpy.ops.mesh.primitive_cube_add(size=1, location=(0,0,H))
platform = bpy.context.active_object
platform.name = "Platform"
platform.scale = (plat_sz/2, plat_sz/2, plat_thk/2)
bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
members.append(platform)

# Register platform joints at top corners
for c_idx, (dx, dy) in enumerate(corner_offsets):
    key = (c_idx, round(H, 3))
    joints.setdefault(key, []).append(platform)

# Add rigid body physics to all members
for obj in members:
    bpy.ops.rigidbody.object_add()
    obj.rigid_body.type = 'ACTIVE'
    obj.rigid_body.collision_shape = 'BOX'
    obj.rigid_body.mass = steel_rho * (cross*cross*length)  # Volume × density
    obj.rigid_body.friction = 0.5
    obj.rigid_body.restitution = 0.1

# Override platform mass
platform.rigid_body.mass = plat_mass

# Create fixed constraints between connected members
constraint_count = 0
for (corner, z), obj_list in joints.items():
    if len(obj_list) < 2:
        continue
    
    # Use first object as anchor
    anchor = obj_list[0]
    for other in obj_list[1:]:
        # Create empty constraint object
        bpy.ops.object.empty_add(type='PLAIN_AXES', location=anchor.location)
        constraint = bpy.context.active_object
        constraint.name = f"Fixed_{constraint_count}"
        
        # Add rigid body constraint
        bpy.ops.rigidbody.constraint_add()
        constraint.rigid_body_constraint.type = 'FIXED'
        constraint.rigid_body_constraint.object1 = anchor
        constraint.rigid_body_constraint.object2 = other
        
        # Parent constraint to anchor for organization
        constraint.parent = anchor
        constraint.hide_viewport = True
        constraint.hide_render = True
        constraint_count += 1

# Create fixed constraints from base to ground
base_z = 0.0
for c_idx in range(4):
    key = (c_idx, round(base_z, 3))
    if key in joints:
        base_obj = joints[key][0]  # Any base member at this joint
        
        bpy.ops.object.empty_add(type='PLAIN_AXES', location=base_obj.location)
        constraint = bpy.context.active_object
        constraint.name = f"BaseAnchor_{c_idx}"
        
        bpy.ops.rigidbody.constraint_add()
        constraint.rigid_body_constraint.type = 'FIXED'
        constraint.rigid_body_constraint.object1 = ground
        constraint.rigid_body_constraint.object2 = base_obj
        
        constraint.parent = ground
        constraint.hide_viewport = True
        constraint.hide_render = True

# Configure simulation
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 50
bpy.context.scene.frame_end = frames

print(f"Tower built: {len(members)} members, {constraint_count} constraints")