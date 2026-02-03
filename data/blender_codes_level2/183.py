import bpy
import math

# 1. Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# 2. Define variables from summary
w = 2.0
d = 2.0
h = 30.0
mass = 9000.0
base_z = 0.0
center_z = h / 2.0
ground_sz = 50.0
col_margin = 0.04
sim_frames = 500
fps = 24

# 3. Set scene properties for simulation
scene = bpy.context.scene
scene.frame_end = sim_frames
scene.render.fps = fps
scene.rigidbody_world.steps_per_second = fps * 2  # 48 substeps for stability

# 4. Create ground plane (passive rigid body)
bpy.ops.mesh.primitive_plane_add(size=ground_sz, location=(0, 0, base_z))
ground = bpy.context.active_object
ground.name = "Ground"
bpy.ops.rigidbody.object_add()
ground.rigid_body.type = 'PASSIVE'
ground.rigid_body.collision_margin = col_margin

# 5. Create steel column (cube)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, center_z))
column = bpy.context.active_object
column.name = "Steel_Column"
column.scale = (w, d, h)  # Scale to actual dimensions
bpy.ops.rigidbody.object_add()
column.rigid_body.type = 'ACTIVE'
column.rigid_body.mass = mass
column.rigid_body.collision_shape = 'BOX'
column.rigid_body.collision_margin = col_margin
column.rigid_body.friction = 0.5
column.rigid_body.restitution = 0.1

# 6. Apply fixed constraint at base
# In Blender, constraints are added to the object and target the world (empty).
bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, base_z))
empty = bpy.context.active_object
empty.name = "Fixed_Constraint_Anchor"

bpy.ops.object.select_all(action='DESELECT')
column.select_set(True)
bpy.context.view_layer.objects.active = column
bpy.ops.rigidbody.constraint_add()
constraint = column.rigid_body_constraints[-1]
constraint.type = 'FIXED'
constraint.object1 = column
constraint.object2 = empty

# 7. Set up camera for verification view
bpy.ops.object.camera_add(location=(25, -25, 15))
cam = bpy.context.active_object
cam.data.lens = 50
cam.rotation_euler = (math.radians(63.4), 0, math.radians(45))
scene.camera = cam

# 8. Add light
bpy.ops.object.light_add(type='SUN', location=(50, -50, 100))
sun = bpy.context.active_object
sun.data.energy = 5.0

# 9. Set rigid body world gravity to default Earth (Z = -9.81 m/s²)
scene.rigidbody_world.gravity = (0, 0, -9.81)

# 10. Optional: Set up a quick render for visual verification
scene.render.image_settings.file_format = 'PNG'
scene.render.filepath = "/tmp/column_verification.png"
bpy.ops.render.render(write_still=True)