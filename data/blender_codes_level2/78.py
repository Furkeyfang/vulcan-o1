import bpy
import mathutils

# Clear scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Physics setup
bpy.context.scene.use_gravity = True
bpy.context.scene.gravity = (0, 0, -9.81)
bpy.context.scene.rigidbody_world.substeps_per_frame = 10
bpy.context.scene.rigidbody_world.solver_iterations = 10

# Parameters from summary
col_w = 0.5
col_d = 0.5
col_h = 3.0
col_loc = (0.0, 0.0, 1.5)

beam_l = 3.0
beam_w = 0.3
beam_d = 0.3
beam_loc = (1.5, 0.0, 3.15)

panel_l = 1.0
panel_w = 1.0
panel_t = 0.1
panel_loc = (3.0, 0.0, 3.35)

force_vec = mathutils.Vector((0.0, 0.0, -1765.2))
sim_frames = 100

# Create vertical support column
bpy.ops.mesh.primitive_cube_add(size=1.0, location=col_loc)
column = bpy.context.active_object
column.name = "Column"
column.scale = (col_w, col_d, col_h)
bpy.ops.rigidbody.object_add()
column.rigid_body.type = 'PASSIVE'
column.rigid_body.collision_shape = 'BOX'

# Create horizontal cantilever beam
bpy.ops.mesh.primitive_cube_add(size=1.0, location=beam_loc)
beam = bpy.context.active_object
beam.name = "Beam"
beam.scale = (beam_l, beam_w, beam_d)
bpy.ops.rigidbody.object_add()
beam.rigid_body.type = 'ACTIVE'
beam.rigid_body.mass = 100.0  # Approx steel beam
beam.rigid_body.collision_shape = 'BOX'

# Create solar panel cube
bpy.ops.mesh.primitive_cube_add(size=1.0, location=panel_loc)
panel = bpy.context.active_object
panel.name = "Panel"
panel.scale = (panel_l, panel_w, panel_t)
bpy.ops.rigidbody.object_add()
panel.rigid_body.type = 'ACTIVE'
panel.rigid_body.mass = 180.0  # 180 kg load
panel.rigid_body.collision_shape = 'BOX'

# Create fixed constraint: Column to Ground (World)
bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0,0,0))
empty = bpy.context.active_object
empty.name = "Ground_Anchor"

bpy.ops.rigidbody.constraint_add()
constraint1 = bpy.context.active_object
constraint1.name = "Column_Anchor"
constraint1.rigid_body_constraint.type = 'FIXED'
constraint1.rigid_body_constraint.object1 = column

# Create fixed constraint: Column to Beam
bpy.ops.rigidbody.constraint_add()
constraint2 = bpy.context.active_object
constraint2.name = "Column_Beam_Joint"
constraint2.rigid_body_constraint.type = 'FIXED'
constraint2.rigid_body_constraint.object1 = column
constraint2.rigid_body_constraint.object2 = beam
constraint2.location = (0, 0, 3.0)  # Junction point

# Create fixed constraint: Beam to Panel
bpy.ops.rigidbody.constraint_add()
constraint3 = bpy.context.active_object
constraint3.name = "Beam_Panel_Joint"
constraint3.rigid_body_constraint.type = 'FIXED'
constraint3.rigid_body_constraint.object1 = beam
constraint3.rigid_body_constraint.object2 = panel
constraint3.location = (3.0, 0, 3.15)  # End of beam

# Apply downward force to panel
panel.rigid_body.use_gravity = True
bpy.ops.object.forcefield_add(type='FORCE', location=panel_loc)
force_field = bpy.context.active_object
force_field.name = "Load_Force"
force_field.field.strength = 1765.2
force_field.field.direction = 'Z'
force_field.field.use_gravity_falloff = False
force_field.field.use_max_distance = True
force_field.field.distance_max = 0.05
force_field.field.falloff_power = 0.0

# Link force field to panel
panel.field.new(type='FORCE')
panel.field[0].field = force_field.field

# Set simulation range
bpy.context.scene.frame_end = sim_frames

# Bake physics simulation
bpy.ops.ptcache.bake_all(bake=True)