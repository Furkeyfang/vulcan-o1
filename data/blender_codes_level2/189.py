import bpy
import math

# Clear scene
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

# Extract parameters
seg_r = 0.2
seg_h = 1.0
seg_n = 13
total_h = 13.0
plat_dim = (1.5, 1.5, 0.3)
plat_z = 13.15
plat_mass = 200.0
force_mag = 1962.0
force_loc = (0.0, 0.0, plat_z)
force_dir = (0.0, 0.0, -1.0)
steel_density = 7850.0
seg_mass = math.pi * seg_r**2 * seg_h * steel_density

# Create cylindrical segments
segments = []
for i in range(seg_n):
    z_center = (i + 0.5) * seg_h  # i from 0 to 12
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=32,
        radius=seg_r,
        depth=seg_h,
        location=(0.0, 0.0, z_center)
    )
    seg = bpy.context.active_object
    seg.name = f"Segment_{i+1:02d}"
    
    # Rigid body
    bpy.ops.rigidbody.object_add()
    if i == 0:
        seg.rigid_body.type = 'PASSIVE'  # Fixed base
    else:
        seg.rigid_body.type = 'ACTIVE'
        seg.rigid_body.mass = seg_mass
    seg.rigid_body.collision_shape = 'CONVEX_HULL'
    segments.append(seg)

# Create platform
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, 0.0, plat_z))
platform = bpy.context.active_object
platform.name = "Observation_Platform"
platform.scale = plat_dim
bpy.ops.rigidbody.object_add()
platform.rigid_body.type = 'ACTIVE'
platform.rigid_body.mass = plat_mass
platform.rigid_body.collision_shape = 'BOX'

# Create fixed constraints between segments
for i in range(len(segments) - 1):
    parent = segments[i]
    child = segments[i + 1]
    
    # Create constraint empty
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=parent.location)
    const_obj = bpy.context.active_object
    const_obj.name = f"Fixed_{i+1:02d}"
    const_obj.empty_display_size = 0.3
    
    # Add constraint
    bpy.ops.rigidbody.constraint_add()
    const_obj.rigid_body_constraint.type = 'FIXED'
    const_obj.rigid_body_constraint.object1 = parent
    const_obj.rigid_body_constraint.object2 = child

# Constraint between top segment and platform
top_seg = segments[-1]
bpy.ops.object.empty_add(type='PLAIN_AXES', location=top_seg.location)
const_obj = bpy.context.active_object
const_obj.name = "Constraint_Platform"
const_obj.empty_display_size = 0.3
bpy.ops.rigidbody.constraint_add()
const_obj.rigid_body_constraint.type = 'FIXED'
const_obj.rigid_body_constraint.object1 = top_seg
const_obj.rigid_body_constraint.object2 = platform

# Apply downward force as a force field at platform location
bpy.ops.object.effector_add(type='FORCE', location=force_loc)
force_field = bpy.context.active_object
force_field.name = "Load_Force"
force_field.field.strength = force_mag
force_field.field.direction = 'Z'
force_field.field.use_gravity = False
force_field.field.falloff_power = 0  # Uniform
force_field.field.distance_max = 0.01  # Only affect nearby objects
force_field.field.flow = 0  # Force only, no flow

# Link force field to platform for precise application
# (Alternative: parent to platform, but we'll use location constraint)
platform.location = force_loc  # Ensure alignment

# Set up rigid body world for stability
bpy.context.scene.rigidbody_world.enabled = True
bpy.context.scene.rigidbody_world.steps_per_second = 120
bpy.context.scene.rigidbody_world.solver_iterations = 50
bpy.context.scene.rigidbody_world.constraint_solver_iterations = 10

# Set simulation duration
bpy.context.scene.frame_end = 500

# Verify initial positions
print(f"Platform initial Z: {platform.location.z}")
print(f"Total mast height: {total_h}")
print(f"Segment mass: {seg_mass:.1f} kg")
print(f"Platform mass: {plat_mass} kg")