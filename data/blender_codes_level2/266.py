import bpy
import mathutils

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Parameters from summary
beam_len = 7.0
beam_wid = 0.5
beam_ht = 0.5
beam_left_ext = 2.0
beam_right_ext = 5.0
beam_center_x = 1.5
beam_center_z = 0.25
beam_loc = (1.5, 0.0, 0.25)

base_wid = 0.5
base_dep = 0.5
base_ht = 1.0
base_center_z = -0.5
base_loc = (0.0, 0.0, -0.5)

cw_size = 1.0
cw_mass = 600.0
cw_loc = (-2.5, 0.0, 1.0)

ground_size = 20.0
ground_loc = (0.0, 0.0, -1.05)

# Create ground plane (visual reference only)
bpy.ops.mesh.primitive_cube_add(size=1, location=ground_loc)
ground = bpy.context.active_object
ground.scale = (ground_size, ground_size, 0.1)
ground.name = "Ground"

# Create base support
bpy.ops.mesh.primitive_cube_add(size=1, location=base_loc)
base = bpy.context.active_object
base.scale = (base_wid, base_dep, base_ht)
base.name = "BaseSupport"
bpy.ops.rigidbody.object_add()
base.rigid_body.type = 'PASSIVE'

# Create main beam
bpy.ops.mesh.primitive_cube_add(size=1, location=beam_loc)
beam = bpy.context.active_object
beam.scale = (beam_len, beam_wid, beam_ht)
beam.name = "MainBeam"
bpy.ops.rigidbody.object_add()
beam.rigid_body.type = 'PASSIVE'

# Create counterweight
bpy.ops.mesh.primitive_cube_add(size=1, location=cw_loc)
counterweight = bpy.context.active_object
counterweight.scale = (cw_size, cw_size, cw_size)
counterweight.name = "Counterweight"
bpy.ops.rigidbody.object_add()
counterweight.rigid_body.type = 'ACTIVE'
counterweight.rigid_body.mass = cw_mass

# Create constraints
# 1. Base support to ground (bottom face fixation)
bpy.ops.object.select_all(action='DESELECT')
ground.select_set(True)
base.select_set(True)
bpy.context.view_layer.objects.active = base
bpy.ops.rigidbody.constraint_add()
constraint1 = bpy.context.active_object
constraint1.rigid_body_constraint.type = 'FIXED'
constraint1.name = "BaseToGround_Constraint"

# 2. Base support to beam (top face fixation)
bpy.ops.object.select_all(action='DESELECT')
base.select_set(True)
beam.select_set(True)
bpy.context.view_layer.objects.active = beam
bpy.ops.rigidbody.constraint_add()
constraint2 = bpy.context.active_object
constraint2.rigid_body_constraint.type = 'FIXED'
constraint2.name = "BaseToBeam_Constraint"

# 3. Beam to counterweight
bpy.ops.object.select_all(action='DESELECT')
beam.select_set(True)
counterweight.select_set(True)
bpy.context.view_layer.objects.active = counterweight
bpy.ops.rigidbody.constraint_add()
constraint3 = bpy.context.active_object
constraint3.rigid_body_constraint.type = 'FIXED'
constraint3.name = "BeamToCounterweight_Constraint"

# Position constraints at connection points (optional but clean)
constraint1.location = (0, 0, -1.0)  # Base bottom
constraint2.location = (0, 0, 0.0)   # Base top / beam bottom
constraint3.location = (-2.5, 0, 0.5) # Beam top at counterweight

# Set rigid body world settings
bpy.context.scene.rigidbody_world.enabled = True
bpy.context.scene.rigidbody_world.time_scale = 1.0
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 10
bpy.context.scene.gravity = (0, 0, -9.81)

# Finalize scene
bpy.ops.object.select_all(action='DESELECT')
print("Asymmetric cantilever beam with counterweight constructed successfully.")