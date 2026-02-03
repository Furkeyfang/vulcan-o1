import bpy
import mathutils

# Clear scene
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

# Variables from summary
bracket_dim = (0.2, 0.2, 0.1)
bracket_loc = (0.0, 0.0, 0.05)
beam_dim = (1.5, 0.2, 0.1)
beam_loc = (0.75, 0.1, 0.05)
load_point = (1.5, 0.1, 0.05)
load_force_magnitude = 981.0
constraint_breaking_threshold = 10000.0
ground_size = (10.0, 10.0, 0.1)
ground_loc = (0.0, 0.0, -0.05)
beam_mass = 20.0
sim_frames = 100

# Ensure rigid body world exists
if bpy.context.scene.rigidbody_world is None:
    bpy.ops.rigidbody.world_add()
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.frame_end = sim_frames

# Create Ground Plane (Passive)
bpy.ops.mesh.primitive_plane_add(size=1, location=ground_loc)
ground = bpy.context.active_object
ground.scale = ground_size
bpy.ops.rigidbody.object_add()
ground.rigid_body.type = 'PASSIVE'
ground.name = "Ground"

# Create Wall Bracket (Passive)
bpy.ops.mesh.primitive_cube_add(size=1, location=bracket_loc)
bracket = bpy.context.active_object
bracket.scale = bracket_dim
bpy.ops.rigidbody.object_add()
bracket.rigid_body.type = 'PASSIVE'
bracket.name = "WallBracket"

# Create Main Beam (Active)
bpy.ops.mesh.primitive_cube_add(size=1, location=beam_loc)
beam = bpy.context.active_object
beam.scale = beam_dim
bpy.ops.rigidbody.object_add()
beam.rigid_body.type = 'ACTIVE'
beam.rigid_body.mass = beam_mass
beam.name = "MainBeam"

# Fixed Constraint: Ground -> Bracket
bpy.ops.object.empty_add(type='PLAIN_AXES', location=bracket_loc)
constraint_empty1 = bpy.context.active_object
constraint_empty1.name = "Constraint_Ground_Bracket"
bpy.ops.rigidbody.constraint_add()
constraint1 = constraint_empty1.rigid_body_constraint
constraint1.type = 'FIXED'
constraint1.object1 = ground
constraint1.object2 = bracket
constraint1.breaking_threshold = constraint_breaking_threshold

# Fixed Constraint: Bracket -> Beam
bpy.ops.object.empty_add(type='PLAIN_AXES', location=bracket_loc)
constraint_empty2 = bpy.context.active_object
constraint_empty2.name = "Constraint_Bracket_Beam"
bpy.ops.rigidbody.constraint_add()
constraint2 = constraint_empty2.rigid_body_constraint
constraint2.type = 'FIXED'
constraint2.object1 = bracket
constraint2.object2 = beam
constraint2.breaking_threshold = constraint_breaking_threshold

# Create Force Field for Load (applied at free end, downward)
bpy.ops.object.effector_add(type='FORCE', location=load_point)
force_field = bpy.context.active_object
force_field.name = "LoadForceField"
force_field.field.strength = -load_force_magnitude  # Negative Z = downward
force_field.field.falloff_power = 0  # Uniform in range
force_field.field.distance_max = 0.2  # Affect only nearby objects
# Limit force field to affect only the beam
force_field.field.use_absorption = False
# Create a collection for the beam and assign force field to it
beam_collection = bpy.data.collections.new("BeamCollection")
bpy.context.scene.collection.children.link(beam_collection)
beam_collection.objects.link(beam)
force_field.field.collection = beam_collection
# Keyframe force strength to ramp up slowly (0 at frame 1, full at frame 10)
force_field.field.strength = 0
force_field.keyframe_insert(data_path="field.strength", frame=1)
force_field.field.strength = -load_force_magnitude
force_field.keyframe_insert(data_path="field.strength", frame=10)

# Set up visualization (optional, for headless rendering)
bpy.context.scene.render.engine = 'BLENDER_EEVEE'
bpy.context.scene.frame_set(1)

# Verification: The simulation will run when Blender is executed with --render-frame or --render-animation
# In headless mode, we can run the simulation with bpy.ops.ptcache.bake_all() but that requires UI context.
# Instead, we rely on the user to run the simulation via command line.
# We'll at least ensure the rigid body world is set to cache the simulation.
bpy.context.scene.rigidbody_world.point_cache.frame_start = 1
bpy.context.scene.rigidbody_world.point_cache.frame_end = sim_frames

print("Cantilever shelf system created. Run simulation for", sim_frames, "frames.")