import bpy
import math

# 1. Clear existing scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# 2. Define all parameters from summary
top_beam_length = 4.0
top_beam_width = 0.5
top_beam_height = 0.5
top_beam_z = 4.0
top_beam_mass = 4000.0
force_magnitude = 39240.0
slanted_beam_size = (0.5, 0.5, 5.0)
right_base_x = 5.0
left_base_x = -5.0
right_top_x = 2.0
left_top_x = -2.0
ground_size = (20.0, 20.0, 1.0)
ground_z = -0.5
right_beam_angle = -0.6435
left_beam_angle = 0.6435
simulation_frames = 100
gravity_z = -9.81

# 3. Set up physics world
bpy.context.scene.rigidbody_world.gravity.z = gravity_z
bpy.context.scene.frame_end = simulation_frames

# 4. Create ground plane (passive rigid body)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, ground_z))
ground = bpy.context.active_object
ground.name = "Ground"
ground.scale = (ground_size[0], ground_size[1], ground_size[2])
bpy.ops.rigidbody.object_add()
ground.rigid_body.type = 'PASSIVE'
ground.rigid_body.collision_shape = 'BOX'

# 5. Create top beam
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, top_beam_z))
top_beam = bpy.context.active_object
top_beam.name = "TopBeam"
top_beam.scale = (top_beam_length, top_beam_width, top_beam_height)
bpy.ops.rigidbody.object_add()
top_beam.rigid_body.mass = top_beam_mass
top_beam.rigid_body.collision_shape = 'BOX'

# 6. Create right slanted beam
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(right_base_x, 0, 0))
right_beam = bpy.context.active_object
right_beam.name = "RightBeam"
right_beam.scale = slanted_beam_size
right_beam.rotation_euler = (0, right_beam_angle, 0)
bpy.ops.rigidbody.object_add()
right_beam.rigid_body.collision_shape = 'BOX'

# 7. Create left slanted beam
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(left_base_x, 0, 0))
left_beam = bpy.context.active_object
left_beam.name = "LeftBeam"
left_beam.scale = slanted_beam_size
left_beam.rotation_euler = (0, left_beam_angle, 0)
bpy.ops.rigidbody.object_add()
left_beam.rigid_body.collision_shape = 'BOX'

# 8. Apply fixed constraints (simulating rigid joints)

# Right beam to ground (base joint)
bpy.context.view_layer.objects.active = right_beam
bpy.ops.rigidbody.constraint_add()
right_ground_constraint = bpy.context.active_object
right_ground_constraint.name = "RightBaseConstraint"
constraint = right_beam.constraints["RigidBodyConstraint"]
constraint.type = 'FIXED'
constraint.object2 = ground

# Right beam to top beam (top joint)
bpy.context.view_layer.objects.active = right_beam
bpy.ops.rigidbody.constraint_add()
right_top_constraint = bpy.context.active_object
right_top_constraint.name = "RightTopConstraint"
constraint = right_beam.constraints["RigidBodyConstraint"]
constraint.type = 'FIXED'
constraint.object2 = top_beam
# Set constraint location at beam top (local Z = 5.0/2 = 2.5 since scale 5.0)
constraint.location = (0, 0, 2.5)

# Left beam to ground (base joint)
bpy.context.view_layer.objects.active = left_beam
bpy.ops.rigidbody.constraint_add()
left_ground_constraint = bpy.context.active_object
left_ground_constraint.name = "LeftBaseConstraint"
constraint = left_beam.constraints["RigidBodyConstraint"]
constraint.type = 'FIXED'
constraint.object2 = ground

# Left beam to top beam (top joint)
bpy.context.view_layer.objects.active = left_beam
bpy.ops.rigidbody.constraint_add()
left_top_constraint = bpy.context.active_object
left_top_constraint.name = "LeftTopConstraint"
constraint = left_beam.constraints["RigidBodyConstraint"]
constraint.type = 'FIXED'
constraint.object2 = top_beam
constraint.location = (0, 0, 2.5)

# 9. Apply downward force to top beam (simulating tank load)
# Create force field (downward gravity-like force)
bpy.ops.object.effector_add(type='FORCE', location=(0, 0, top_beam_z + 1))
force_field = bpy.context.active_object
force_field.name = "TankLoadForce"
force_field.field.strength = -force_magnitude  # Negative for downward
force_field.field.falloff_power = 0  # Uniform force
force_field.field.distance_max = 2.0  # Affect only top beam region

# Link force field to top beam via parenting
force_field.parent = top_beam
force_field.matrix_parent_inverse = top_beam.matrix_world.inverted()

# 10. Bake simulation for verification
bpy.context.scene.rigidbody_world.point_cache.frame_end = simulation_frames
bpy.ops.ptcache.bake_all(bake=True)