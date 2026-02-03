import bpy

# Clear existing scene
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

# Extract parameters
ground_size = 10.0
ground_loc = (0.0, 0.0, 0.0)
column_dim = (0.5, 0.5, 2.0)
column_loc = (0.0, 0.0, 1.0)
beam_dim = (4.0, 0.3, 0.3)
beam_loc = (2.0, 0.0, 2.0)
tank_dim = (1.0, 1.0, 1.0)
tank_loc = (4.0, 0.0, 2.65)
tank_mass = 700.0
simulation_frames = 100

# Create ground plane (passive rigid body)
bpy.ops.mesh.primitive_plane_add(size=ground_size, location=ground_loc)
ground = bpy.context.active_object
ground.name = "Ground"
bpy.ops.rigidbody.object_add()
ground.rigid_body.type = 'PASSIVE'
ground.rigid_body.collision_shape = 'MESH'

# Create vertical support column
bpy.ops.mesh.primitive_cube_add(size=1, location=column_loc)
column = bpy.context.active_object
column.name = "SupportColumn"
column.scale = column_dim
bpy.ops.rigidbody.object_add()
column.rigid_body.type = 'PASSIVE'
column.rigid_body.collision_shape = 'BOX'

# Create cantilever beam
bpy.ops.mesh.primitive_cube_add(size=1, location=beam_loc)
beam = bpy.context.active_object
beam.name = "CantileverBeam"
beam.scale = beam_dim
bpy.ops.rigidbody.object_add()
beam.rigid_body.type = 'PASSIVE'
beam.rigid_body.collision_shape = 'BOX'

# Create water tank
bpy.ops.mesh.primitive_cube_add(size=1, location=tank_loc)
tank = bpy.context.active_object
tank.name = "WaterTank"
tank.scale = tank_dim
bpy.ops.rigidbody.object_add()
tank.rigid_body.type = 'ACTIVE'
tank.rigid_body.mass = tank_mass
tank.rigid_body.collision_shape = 'BOX'

# Create fixed constraints
def add_fixed_constraint(obj1, obj2):
    # Create empty for constraint
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0,0,0))
    constraint_obj = bpy.context.active_object
    constraint_obj.name = f"Fixed_{obj1.name}_{obj2.name}"
    bpy.ops.rigidbody.constraint_add()
    constraint = constraint_obj.rigid_body_constraint
    constraint.type = 'FIXED'
    constraint.object1 = obj1
    constraint.object2 = obj2

# Bond column to ground
add_fixed_constraint(ground, column)
# Bond beam to column
add_fixed_constraint(column, beam)
# Bond tank to beam
add_fixed_constraint(beam, tank)

# Configure simulation
scene = bpy.context.scene
scene.frame_end = simulation_frames
scene.rigidbody_world.enabled = True
scene.rigidbody_world.time_scale = 1.0
scene.rigidbody_world.steps_per_second = 60
scene.rigidbody_world.solver_iterations = 50

# Set collision margins (improve stability)
for obj in [ground, column, beam, tank]:
    if obj.rigid_body:
        obj.rigid_body.use_margin = True
        obj.rigid_body.collision_margin = 0.001

print("Cantilever assembly complete. Simulate with rigid body physics.")