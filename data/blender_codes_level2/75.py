import bpy
import mathutils

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Parameters from summary
post_width_x = 0.5
post_width_y = 0.5
post_height = 5.0
post_loc = (0.0, 0.0, 2.5)

beam_width_x = 0.3
beam_width_y = 0.3
beam_length = 1.0
beam_loc = (0.0, 0.75, 4.85)

plate_width_x = 0.4
plate_width_y = 0.4
plate_thickness = 0.1
plate_loc = (0.0, 1.45, 4.65)

plate_mass = 60.0
simulation_frames = 100
gravity_z = -9.81

# Ensure rigid body world exists
if bpy.context.scene.rigidbody_world is None:
    bpy.ops.rigidbody.world_add()
bpy.context.scene.rigidbody_world.gravity = (0, 0, gravity_z)
bpy.context.scene.rigidbody_world.substeps_per_frame = 10
bpy.context.scene.rigidbody_world.solver_iterations = 50

# 1. Create Support Post (vertical column)
bpy.ops.mesh.primitive_cube_add(size=2.0, location=post_loc)
post = bpy.context.active_object
post.name = "SupportPost"
post.scale = (post_width_x/2.0, post_width_y/2.0, post_height/2.0)
bpy.ops.rigidbody.object_add()
post.rigid_body.type = 'PASSIVE'
post.rigid_body.collision_shape = 'BOX'
post.rigid_body.mass = 1000.0  # Heavy base

# 2. Create Overhang Beam (horizontal)
bpy.ops.mesh.primitive_cube_add(size=2.0, location=beam_loc)
beam = bpy.context.active_object
beam.name = "OverhangBeam"
beam.scale = (beam_width_x/2.0, beam_length/2.0, beam_width_y/2.0)
bpy.ops.rigidbody.object_add()
beam.rigid_body.type = 'ACTIVE'
beam.rigid_body.collision_shape = 'BOX'
beam.rigid_body.mass = 50.0  # Estimated steel beam mass

# 3. Create Load Plate (sign)
bpy.ops.mesh.primitive_cube_add(size=2.0, location=plate_loc)
plate = bpy.context.active_object
plate.name = "LoadPlate"
plate.scale = (plate_width_x/2.0, plate_width_y/2.0, plate_thickness/2.0)
bpy.ops.rigidbody.object_add()
plate.rigid_body.type = 'ACTIVE'
plate.rigid_body.collision_shape = 'BOX'
plate.rigid_body.mass = plate_mass

# 4. Create Fixed Constraints (welded joints)
# Beam to Post constraint
beam.select_set(True)
post.select_set(True)
bpy.context.view_layer.objects.active = beam
bpy.ops.rigidbody.constraint_add()
constraint1 = beam.rigid_body_constraints[-1]
constraint1.type = 'FIXED'
constraint1.object1 = beam
constraint1.object2 = post

# Plate to Beam constraint
plate.select_set(True)
beam.select_set(True)
bpy.context.view_layer.objects.active = plate
bpy.ops.rigidbody.constraint_add()
constraint2 = plate.rigid_body_constraints[-1]
constraint2.type = 'FIXED'
constraint2.object1 = plate
constraint2.object2 = beam

# 5. Set simulation length
bpy.context.scene.frame_end = simulation_frames

# 6. Optional: Bake simulation for verification
bpy.ops.ptcache.bake_all(bake=True)

print("Cantilever structure created. Simulation ready.")