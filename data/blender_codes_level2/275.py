import bpy
import mathutils

# Clear existing scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Extract parameters from summary
beam_length = 20.0
beam_width = 0.5
beam_height = 0.5
beam_z = 10.0

strut_x_positions = [-7.5, -2.5, 2.5, 7.5]
strut_y = 0.0
strut_top_z = 10.0
strut_bottom_z = 0.0
strut_cross_section = 0.3

platform_length = 18.0
platform_width = 4.0
platform_thickness = 0.5
platform_z = 0.0

total_load_kg = 800.0
gravity = 9.81
total_force_newton = total_load_kg * gravity

density_steel = 7850.0
frames_to_simulate = 100
constraint_breaking_threshold = 10000.0

# Enable rigid body physics
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 10

# 1. Create main beam (passive)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, 0.0, beam_z))
beam = bpy.context.active_object
beam.name = "MainBeam"
beam.scale = (beam_length, beam_width, beam_height)
beam.rigid_body = beam.rigid_body or beam.rigidbody_add()
beam.rigid_body.type = 'PASSIVE'
beam.rigid_body.mass = density_steel * (beam_length * beam_width * beam_height)
beam.rigid_body.collision_shape = 'BOX'

# 2. Create four vertical struts (active)
struts = []
for i, x in enumerate(strut_x_positions):
    # Strut center position (half-height from top attachment)
    strut_center_z = (strut_top_z + strut_bottom_z) / 2.0
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(x, strut_y, strut_center_z))
    strut = bpy.context.active_object
    strut.name = f"Strut_{i}"
    # Scale: cross-section XY, height Z
    strut.scale = (strut_cross_section, strut_cross_section, (strut_top_z - strut_bottom_z) / 2.0)
    strut.rigid_body = strut.rigid_body or strut.rigidbody_add()
    strut.rigid_body.type = 'ACTIVE'
    strut.rigid_body.mass = density_steel * (strut_cross_section**2 * (strut_top_z - strut_bottom_z))
    strut.rigid_body.collision_shape = 'BOX'
    struts.append(strut)

# 3. Create platform (active)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, 0.0, platform_z))
platform = bpy.context.active_object
platform.name = "Platform"
platform.scale = (platform_length, platform_width, platform_thickness)
platform.rigid_body = platform.rigid_body or platform.rigidbody_add()
platform.rigid_body.type = 'ACTIVE'
platform.rigid_body.mass = total_load_kg  # Mass represents the applied load
platform.rigid_body.collision_shape = 'BOX'

# 4. Create fixed constraints between beam and struts (top connections)
for strut in struts:
    # Create constraint empty at top connection point
    top_loc = (strut.location.x, strut_y, strut_top_z)
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=top_loc)
    constraint = bpy.context.active_object
    constraint.name = f"Constraint_Beam_Strut_{strut.name}"
    constraint.rigid_body_constraint = constraint.rigid_body_constraint or constraint.rigidbody_constraint_add()
    constraint.rigid_body_constraint.type = 'FIXED'
    constraint.rigid_body_constraint.object1 = beam
    constraint.rigid_body_constraint.object2 = strut
    constraint.rigid_body_constraint.breaking_threshold = constraint_breaking_threshold

# 5. Create fixed constraints between struts and platform (bottom connections)
for strut in struts:
    bottom_loc = (strut.location.x, strut_y, strut_bottom_z)
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=bottom_loc)
    constraint = bpy.context.active_object
    constraint.name = f"Constraint_Strut_Platform_{strut.name}"
    constraint.rigid_body_constraint = constraint.rigid_body_constraint or constraint.rigidbody_constraint_add()
    constraint.rigid_body_constraint.type = 'FIXED'
    constraint.rigid_body_constraint.object1 = strut
    constraint.rigid_body_constraint.object2 = platform
    constraint.rigid_body_constraint.breaking_threshold = constraint_breaking_threshold

# 6. Apply downward force to platform (simulate distributed load)
# In headless mode, we apply constant force via rigid body settings
platform.rigid_body.use_gravity = True
# The mass already represents the load, gravity will apply appropriate force

# 7. Set simulation length
bpy.context.scene.frame_end = frames_to_simulate

# 8. Bake simulation (headless compatible)
bpy.ops.rigidbody.bake_to_keyframes(frame_start=1, frame_end=frames_to_simulate)

print("Suspension roof structure created with fixed constraints and load applied.")