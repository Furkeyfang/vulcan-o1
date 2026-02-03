import bpy
import mathutils

# Clear existing scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Extract parameters from summary
ground_size = (10.0, 10.0, 0.5)
ground_loc = (0.0, 0.0, -0.25)
support_dim = (0.5, 0.5, 2.0)
support_loc = (0.25, 0.0, 1.0)
deck_dim = (4.0, 1.0, 0.1)
deck_loc = (2.0, 0.0, 2.05)
load_dim = (0.2, 0.2, 0.2)
load_loc = (4.0, 0.0, 2.15)
load_mass = 500.0
simulation_frames = 100
simulation_substeps = 60
simulation_iterations = 10

# Create Ground Plane (immovable reference)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=ground_loc)
ground = bpy.context.active_object
ground.name = "Ground"
ground.scale = ground_size
bpy.ops.rigidbody.object_add()
ground.rigid_body.type = 'PASSIVE'
ground.rigid_body.collision_shape = 'BOX'

# Create Support Column
bpy.ops.mesh.primitive_cube_add(size=1.0, location=support_loc)
support = bpy.context.active_object
support.name = "Support_Column"
support.scale = support_dim
bpy.ops.rigidbody.object_add()
support.rigid_body.type = 'PASSIVE'
support.rigid_body.collision_shape = 'BOX'

# Create Ramp Deck
bpy.ops.mesh.primitive_cube_add(size=1.0, location=deck_loc)
deck = bpy.context.active_object
deck.name = "Ramp_Deck"
deck.scale = deck_dim
bpy.ops.rigidbody.object_add()
deck.rigid_body.type = 'PASSIVE'
deck.rigid_body.collision_shape = 'BOX'

# Create Load Cube
bpy.ops.mesh.primitive_cube_add(size=1.0, location=load_loc)
load = bpy.context.active_object
load.name = "Load_Cube"
load.scale = load_dim
bpy.ops.rigidbody.object_add()
load.rigid_body.type = 'ACTIVE'
load.rigid_body.mass = load_mass
load.rigid_body.collision_shape = 'BOX'

# Create Fixed Constraints
# Constraint 1: Ground to Support (at support base)
bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0.0, 0.0, 0.0))
constraint1 = bpy.context.active_object
constraint1.name = "Ground_Support_Constraint"
bpy.ops.rigidbody.constraint_add()
constraint1.rigid_body_constraint.type = 'FIXED'
constraint1.rigid_body_constraint.object1 = ground
constraint1.rigid_body_constraint.object2 = support

# Constraint 2: Support to Deck (at deck fixed end)
bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0.0, 0.0, 2.0))
constraint2 = bpy.context.active_object
constraint2.name = "Support_Deck_Constraint"
bpy.ops.rigidbody.constraint_add()
constraint2.rigid_body_constraint.type = 'FIXED'
constraint2.rigid_body_constraint.object1 = support
constraint2.rigid_body_constraint.object2 = deck

# Configure physics world for stable simulation
scene = bpy.context.scene
scene.rigidbody_world.substeps_per_frame = simulation_substeps
scene.rigidbody_world.solver_iterations = simulation_iterations
scene.rigidbody_world.time_scale = 1.0
scene.frame_end = simulation_frames

# Set initial positions as keyframes for verification
for obj in [ground, support, deck, load]:
    obj.keyframe_insert(data_path="location", frame=1)

# Run simulation
bpy.ops.ptcache.bake_all(bake=True)

# Verification: Check final positions match initial
print("Structural Verification Results:")
print(f"Ground displacement: {ground.location - mathutils.Vector(ground_loc)}")
print(f"Support displacement: {support.location - mathutils.Vector(support_loc)}")
print(f"Deck displacement: {deck.location - mathutils.Vector(deck_loc)}")
print("All structural components should show (0,0,0) displacement for stability.")