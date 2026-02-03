import bpy
import math

# ====================
# PARAMETERS FROM SUMMARY
# ====================
spine_radius = 0.5
spine_height = 15.0
step_count = 30
step_length = 1.0
step_width = 0.3
step_thickness = 0.05
step_mass = 100.0
vertical_spacing = 0.5
z_start = 0.5
angular_increment = 12.0  # degrees
gravity = 9.8
simulation_frames = 500

# Derived
angular_increment_rad = math.radians(angular_increment)
radial_offset = spine_radius + step_length / 2.0  # Step center from spine center

# ====================
# SCENE SETUP
# ====================
# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Set gravity
bpy.context.scene.gravity = (0, 0, -gravity)

# ====================
# CENTRAL SPINE
# ====================
bpy.ops.mesh.primitive_cylinder_add(
    vertices=32,
    radius=spine_radius,
    depth=spine_height,
    location=(0, 0, 0)
)
spine = bpy.context.active_object
spine.name = "Central_Spine"
# Rigid body: static
bpy.ops.rigidbody.object_add()
spine.rigid_body.type = 'PASSIVE'
spine.rigid_body.collision_shape = 'MESH'

# ====================
# HELICAL STEPS
# ====================
steps = []
for i in range(step_count):
    # Calculate position and rotation
    angle = i * angular_increment_rad
    x = radial_offset * math.cos(angle)
    y = radial_offset * math.sin(angle)
    z = z_start + i * vertical_spacing
    
    # Create step (cube)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(x, y, z))
    step = bpy.context.active_object
    step.name = f"Step_{i+1:02d}"
    
    # Scale to step dimensions (length=X, width=Y, thickness=Z)
    step.scale = (step_length, step_width, step_thickness)
    
    # Rotate to align length radially
    step.rotation_euler = (0, 0, angle)
    
    # Rigid body: dynamic with mass
    bpy.ops.rigidbody.object_add()
    step.rigid_body.mass = step_mass
    step.rigid_body.collision_shape = 'BOX'
    
    steps.append(step)

# ====================
# FIXED CONSTRAINTS
# ====================
for i, step in enumerate(steps):
    angle = i * angular_increment_rad
    # Constraint location at spine surface, same height as step
    constraint_z = z_start + i * vertical_spacing
    constraint_x = spine_radius * math.cos(angle)
    constraint_y = spine_radius * math.sin(angle)
    
    # Create empty for constraint (parent of world)
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(constraint_x, constraint_y, constraint_z))
    constraint = bpy.context.active_object
    constraint.name = f"Constraint_Step_{i+1:02d}"
    
    # Add rigid body constraint
    bpy.ops.rigidbody.constraint_add()
    constraint.rigid_body_constraint.type = 'FIXED'
    constraint.rigid_body_constraint.object1 = spine
    constraint.rigid_body_constraint.object2 = step

# ====================
# SIMULATION SETUP
# ====================
bpy.context.scene.frame_end = simulation_frames
bpy.context.scene.rigidbody_world.substeps_per_frame = 10
bpy.context.scene.rigidbody_world.solver_iterations = 50

# Optional: Bake simulation for verification
# bpy.ops.ptcache.bake_all(bake=True)

print(f"Helical stair tower built with {step_count} steps.")