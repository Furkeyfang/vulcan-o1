import bpy
import mathutils

# Clear existing scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Parameters from summary
wall_dim = (5.0, 0.3, 3.0)
wall_loc = (0.0, 0.0, 0.0)
platform_dim = (3.0, 2.0, 0.2)
wall_face_x = 0.15
platform_loc = (1.65, 0.0, 0.1)
beam_dim = (0.3, 0.3, 3.0)
beam_loc = (1.65, 0.0, -0.15)
cube_dim = (0.5, 0.5, 0.5)
cube_loc = (3.15, 0.0, 0.45)
cube_mass = 150.0
simulation_frames = 100

# Enable rigid body physics
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 10

# 1. Create fixed wall
bpy.ops.mesh.primitive_cube_add(size=1, location=wall_loc)
wall = bpy.context.active_object
wall.scale = wall_dim
bpy.ops.rigidbody.object_add()
wall.rigid_body.type = 'PASSIVE'
wall.rigid_body.collision_shape = 'MESH'

# 2. Create balcony platform
bpy.ops.mesh.primitive_cube_add(size=1, location=platform_loc)
platform = bpy.context.active_object
platform.scale = platform_dim
bpy.ops.rigidbody.object_add()
platform.rigid_body.type = 'ACTIVE'
platform.rigid_body.mass = 50  # Estimated platform mass
platform.rigid_body.collision_shape = 'MESH'

# 3. Create support beam
bpy.ops.mesh.primitive_cube_add(size=1, location=beam_loc)
beam = bpy.context.active_object
beam.scale = beam_dim
bpy.ops.rigidbody.object_add()
beam.rigid_body.type = 'ACTIVE'
beam.rigid_body.mass = 20  # Estimated beam mass
beam.rigid_body.collision_shape = 'MESH'

# 4. Create load cube
bpy.ops.mesh.primitive_cube_add(size=1, location=cube_loc)
cube = bpy.context.active_object
cube.scale = cube_dim
bpy.ops.rigidbody.object_add()
cube.rigid_body.type = 'ACTIVE'
cube.rigid_body.mass = cube_mass
cube.rigid_body.collision_shape = 'BOX'

# 5. Create fixed constraints (headless compatible)
def add_fixed_constraint(obj1, obj2, name):
    # Create empty for constraint
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0,0,0))
    empty = bpy.context.active_object
    empty.name = name
    
    # Add rigid body constraint
    bpy.ops.rigidbody.constraint_add()
    rb_constraint = empty.rigid_body_constraint
    rb_constraint.type = 'FIXED'
    rb_constraint.object1 = obj1
    rb_constraint.object2 = obj2

# Bond platform to wall
add_fixed_constraint(wall, platform, "Wall_Platform_Constraint")
# Bond beam to wall
add_fixed_constraint(wall, beam, "Wall_Beam_Constraint")
# Bond beam to platform
add_fixed_constraint(beam, platform, "Beam_Platform_Constraint")

# 6. Set simulation length
bpy.context.scene.frame_end = simulation_frames

# 7. Run physics simulation (headless)
bpy.ops.ptcache.bake_all(bake=True)