import bpy
import mathutils
from mathutils import Vector

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Parameters from summary
leg_cross = 0.5
leg_len_nom = 9.0
base_pts = [(-2, -2, 0), (2, -2, 0), (-2, 2, 0), (2, 2, 0)]
apex = Vector((0.0, 0.0, 9.0))
platform_size = 1.0
platform_mass = 150.0
sim_frames = 100
gravity = -9.81

# Setup rigid body world
if bpy.context.scene.rigidbody_world is None:
    bpy.ops.rigidbody.world_add()
bpy.context.scene.rigidbody_world.gravity = (0, 0, gravity)
bpy.context.scene.frame_end = sim_frames

# Create ground plane
bpy.ops.mesh.primitive_plane_add(size=20, location=(0,0,0))
ground = bpy.context.active_object
bpy.ops.rigidbody.object_add()
ground.rigid_body.type = 'PASSIVE'

# Function to create a leg from base point to apex
def create_leg(base_vec, apex_vec, cross_section, nominal_len):
    """Create a rotated/scaled cube leg between base and apex"""
    base = Vector(base_vec)
    apex = Vector(apex_vec)
    leg_vec = apex - base
    length = leg_vec.length
    mid = base + leg_vec / 2
    
    # Create cube at origin
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0,0,0))
    leg = bpy.context.active_object
    
    # Scale to cross-section and nominal length
    leg.scale = (cross_section, cross_section, nominal_len)
    bpy.ops.object.transform_apply(scale=True)
    
    # Move to midpoint and rotate to align with leg_vec
    leg.location = mid
    # Calculate rotation to align local Z (0,0,1) with leg_vec
    z_axis = Vector((0, 0, 1))
    rot_quat = z_axis.rotation_difference(leg_vec.normalized())
    leg.rotation_mode = 'QUATERNION'
    leg.rotation_quaternion = rot_quat
    
    # Scale in local Z to actual length
    # After initial rotation, local Z is aligned with leg_vec
    scale_factor = length / nominal_len
    # Apply scale only in local Z direction
    leg.scale = (1, 1, scale_factor)
    bpy.ops.object.transform_apply(scale=True)
    
    # Add rigid body
    bpy.ops.rigidbody.object_add()
    leg.rigid_body.collision_shape = 'BOX'
    leg.rigid_body.mass = 50.0  # Estimated mass for 0.5×0.5×9.434m leg
    
    return leg, base, apex

# Create four legs
legs = []
for base_pt in base_pts:
    leg_obj, base_conn, apex_conn = create_leg(base_pt, apex, leg_cross, leg_len_nom)
    legs.append((leg_obj, base_conn, apex_conn))

# Create platform cube at apex
bpy.ops.mesh.primitive_cube_add(size=platform_size, location=apex)
platform = bpy.context.active_object
bpy.ops.rigidbody.object_add()
platform.rigid_body.mass = platform_mass
platform.rigid_body.collision_shape = 'BOX'

# Function to add fixed constraint between two objects at world location
def add_fixed_constraint(obj_a, obj_b, pivot_world):
    """Create fixed constraint between obj_a and obj_b at pivot point"""
    # Create empty for constraint
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=pivot_world)
    empty = bpy.context.active_object
    empty.name = f"Constraint_{obj_a.name}_{obj_b.name}"
    
    # Add rigid body constraint
    bpy.ops.rigidbody.constraint_add()
    constraint = empty.rigid_body_constraint
    constraint.type = 'FIXED'
    constraint.object1 = obj_a
    constraint.object2 = obj_b
    # Set pivot in world coordinates (empty location already at pivot)
    constraint.use_breaking = True
    constraint.breaking_threshold = 10000.0  # High threshold for rigid connection

# Add constraints for each leg
for leg_obj, base_conn, apex_conn in legs:
    # Leg to ground constraint at base
    add_fixed_constraint(leg_obj, ground, base_conn)
    # Leg to platform constraint at apex
    add_fixed_constraint(leg_obj, platform, apex_conn)

# Set up scene for simulation
bpy.context.scene.frame_set(1)
bpy.ops.ptcache.bake_all(bake=True)

print("Tower construction complete. Simulating 100 frames...")