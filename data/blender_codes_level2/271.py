import bpy
import mathutils

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Extract parameters from summary
beam_cs = 0.5
beam_z = 0.5
gap_start = -1.0
gap_end = 1.0
left_center_x = -3.0
left_length = 4.0
right_center_x = 3.0
right_length = 4.0
support_x = -2.0
support_base_z = 0.0
support_height = 2.0
support_center_z = 1.0
cube_size = 0.5
cube_x = 5.0
cube_z = 0.5
cube_mass = 700.0
constraint_x = -2.0
constraint_z = 0.5

# Create Left Cantilever Arm
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(left_center_x, 0, beam_z))
left_arm = bpy.context.active_object
left_arm.name = "Left_Cantilever_Arm"
left_arm.scale = (left_length, beam_cs, beam_cs)
bpy.ops.rigidbody.object_add()
left_arm.rigid_body.type = 'PASSIVE'
left_arm.rigid_body.mass = 1000  # Approximate based on volume

# Create Right Cantilever Arm
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(right_center_x, 0, beam_z))
right_arm = bpy.context.active_object
right_arm.name = "Right_Cantilever_Arm"
right_arm.scale = (right_length, beam_cs, beam_cs)
bpy.ops.rigidbody.object_add()
right_arm.rigid_body.type = 'ACTIVE'
right_arm.rigid_body.mass = 1000

# Create Central Support Column
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(support_x, 0, support_center_z))
support = bpy.context.active_object
support.name = "Central_Support_Column"
support.scale = (beam_cs, beam_cs, support_height)
bpy.ops.rigidbody.object_add()
support.rigid_body.type = 'PASSIVE'
support.rigid_body.mass = 500

# Create Fixed Constraint between Left Arm and Support
# First create empty for constraint pivot
bpy.ops.object.empty_add(type='PLAIN_AXES', location=(constraint_x, 0, constraint_z))
constraint_empty = bpy.context.active_object
constraint_empty.name = "Constraint_Pivot"

# Create constraint object
bpy.ops.rigidbody.constraint_add()
constraint = bpy.context.active_object
constraint.name = "Fixed_Constraint"
constraint.empty = constraint_empty
constraint.rigid_body_constraint.type = 'FIXED'
constraint.rigid_body_constraint.object1 = left_arm
constraint.rigid_body_constraint.object2 = support

# Create Tip Load Cube
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(cube_x, 0, cube_z))
cube = bpy.context.active_object
cube.name = "Tip_Load_Cube"
cube.scale = (cube_size, cube_size, cube_size)
bpy.ops.rigidbody.object_add()
cube.rigid_body.type = 'ACTIVE'
cube.rigid_body.mass = cube_mass

# Set up physics world
bpy.context.scene.rigidbody_world.enabled = True
bpy.context.scene.rigidbody_world.time_scale = 1.0
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 50

# Set gravity (standard Earth gravity)
bpy.context.scene.gravity = mathutils.Vector((0.0, 0.0, -9.81))

# Set frame range for simulation
bpy.context.scene.frame_start = 1
bpy.context.scene.frame_end = 100

# Bake simulation (headless compatible)
bpy.ops.ptcache.bake_all(bake=True)

print("Cantilever bridge construction complete. Simulation baked for 100 frames.")