import bpy
import mathutils

# Clear existing scene
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

# Extract parameters
pier_dim = (0.5, 0.5, 3.0)
pier_center = (0.0, 0.0, 1.5)
beam_dim = (5.0, 0.5, 0.5)
beam_center = (2.5, 0.0, 3.25)
load_dim = (0.5, 0.5, 0.5)
load_center = (5.0, 0.0, 3.75)
load_mass = 600.0
beam_density = 2400.0
beam_volume = beam_dim[0] * beam_dim[1] * beam_dim[2]
beam_mass = beam_volume * beam_density
constraint_anchor = (0.0, 0.0, 3.0)
simulation_frames = 100

# Configure physics world
bpy.context.scene.use_gravity = True
bpy.context.scene.gravity = (0.0, 0.0, -9.81)
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 50

# Create pier (vertical column)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=pier_center)
pier = bpy.context.active_object
pier.name = "Pier"
pier.scale = pier_dim
bpy.ops.rigidbody.object_add()
pier.rigid_body.type = 'PASSIVE'
pier.rigid_body.collision_shape = 'BOX'
pier.rigid_body.collision_margin = 0.001

# Create cantilever beam
bpy.ops.mesh.primitive_cube_add(size=1.0, location=beam_center)
beam = bpy.context.active_object
beam.name = "Beam"
beam.scale = beam_dim
bpy.ops.rigidbody.object_add()
beam.rigid_body.type = 'ACTIVE'
beam.rigid_body.mass = beam_mass
beam.rigid_body.collision_shape = 'BOX'
beam.rigid_body.collision_margin = 0.01

# Create load cube
bpy.ops.mesh.primitive_cube_add(size=1.0, location=load_center)
load = bpy.context.active_object
load.name = "Load"
load.scale = load_dim
bpy.ops.rigidbody.object_add()
load.rigid_body.type = 'ACTIVE'
load.rigid_body.mass = load_mass
load.rigid_body.collision_shape = 'BOX'
load.rigid_body.collision_margin = 0.001

# Create FIXED constraint between pier and beam
bpy.ops.object.empty_add(type='PLAIN_AXES', location=constraint_anchor)
constraint_empty = bpy.context.active_object
constraint_empty.name = "Fixed_Constraint"
bpy.ops.rigidbody.constraint_add()
constraint = constraint_empty.rigid_body_constraint
constraint.type = 'FIXED'
constraint.object1 = pier
constraint.object2 = beam

# Parent constraint to beam for cleaner hierarchy
constraint_empty.parent = beam

# Set simulation length
bpy.context.scene.frame_end = simulation_frames

# Optional: Bake physics for headless verification
# Note: In headless mode, this would be run separately
# bpy.ops.ptcache.bake_all(bake=True)

print(f"Structure created:")
print(f"  Pier mass: {pier.rigid_body.mass:.1f} kg (static)")
print(f"  Beam mass: {beam.rigid_body.mass:.1f} kg")
print(f"  Load mass: {load.rigid_body.mass:.1f} kg")
print(f"  Total moment at connection: {(load_mass * 9.81 * 5.0 + beam_mass * 9.81 * 2.5):.0f} Nm")