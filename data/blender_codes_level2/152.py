import bpy

# Clear scene
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

# Parameters
ground_size = 10.0
mast_scale = (0.5, 0.5, 18.0)
mast_center = (0.0, 0.0, 9.0)
lamp_scale = (0.8, 0.8, 0.2)
lamp_center = (0.0, 0.0, 18.1)
lamp_mass = 120.0
simulation_frames = 100
solver_iterations = 10
steps_per_second = 60

# Create ground (passive rigid body)
bpy.ops.mesh.primitive_plane_add(size=ground_size, location=(0,0,0))
ground = bpy.context.active_object
ground.name = "Ground"
bpy.ops.rigidbody.object_add()
ground.rigid_body.type = 'PASSIVE'

# Create mast (active rigid body)
bpy.ops.mesh.primitive_cube_add(size=1, location=mast_center)
mast = bpy.context.active_object
mast.name = "Mast"
mast.scale = mast_scale
bpy.ops.rigidbody.object_add()
mast.rigid_body.type = 'ACTIVE'
# Mast mass is left default (1.0 kg) since constraints will hold it

# Create lamp (active rigid body with specified mass)
bpy.ops.mesh.primitive_cube_add(size=1, location=lamp_center)
lamp = bpy.context.active_object
lamp.name = "Lamp"
lamp.scale = lamp_scale
bpy.ops.rigidbody.object_add()
lamp.rigid_body.type = 'ACTIVE'
lamp.rigid_body.mass = lamp_mass

# Add FIXED constraint between mast and ground at base
bpy.ops.object.select_all(action='DESELECT')
mast.select_set(True)
bpy.context.view_layer.objects.active = mast
bpy.ops.rigidbody.constraint_add()
constraint_mast = mast.rigid_body_constraints[-1]
constraint_mast.type = 'FIXED'
constraint_mast.object1 = mast
constraint_mast.object2 = ground

# Add FIXED constraint between lamp and mast at top
bpy.ops.object.select_all(action='DESELECT')
lamp.select_set(True)
bpy.context.view_layer.objects.active = lamp
bpy.ops.rigidbody.constraint_add()
constraint_lamp = lamp.rigid_body_constraints[-1]
constraint_lamp.type = 'FIXED'
constraint_lamp.object1 = lamp
constraint_lamp.object2 = mast

# Configure rigid body world
scene = bpy.context.scene
scene.rigidbody_world.steps_per_second = steps_per_second
scene.rigidbody_world.solver_iterations = solver_iterations
scene.frame_start = 1
scene.frame_end = simulation_frames

# Bake simulation (headless compatible)
bpy.ops.ptcache.bake_all(bake=True)

# Verify stability at frame 100
scene.frame_set(simulation_frames)
mast_final = mast.matrix_world.translation
lamp_final = lamp.matrix_world.translation
tolerance = 1e-4
mast_stable = (mast_final - mast_center).length < tolerance
lamp_stable = (lamp_final - lamp_center).length < tolerance

if mast_stable and lamp_stable:
    print("SUCCESS: Mast and lamp remained stable over 100 frames.")
else:
    print(f"WARNING: Movement detected. Mast delta: {mast_final - mast_center}, Lamp delta: {lamp_final - lamp_center}")