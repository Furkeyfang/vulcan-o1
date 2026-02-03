import bpy
import mathutils

# Clear existing scene
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

# Extract variables from parameter summary
v_dim = (0.2, 0.2, 2.0)
v_loc = (0.0, 0.0, 1.0)
h_dim = (2.0, 0.2, 0.2)
h_loc = (1.0, 0.0, 2.1)
c_dim = (0.5, 0.5, 0.5)
c_loc = (1.0, 0.0, 2.45)
load_mass = 300.0
sim_frames = 100
constraint_loc = (0.0, 0.0, 2.0)

# Enable rigid body physics
bpy.context.scene.use_gravity = True
bpy.context.scene.gravity = (0, 0, -9.81)
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 10

# Create vertical arm
bpy.ops.mesh.primitive_cube_add(size=1, location=v_loc)
vertical_arm = bpy.context.active_object
vertical_arm.name = "Vertical_Arm"
vertical_arm.scale = v_dim
bpy.ops.rigidbody.object_add()
vertical_arm.rigid_body.type = 'PASSIVE'
vertical_arm.rigid_body.collision_shape = 'BOX'
vertical_arm.rigid_body.mass = 1000.0  # Large mass for stability

# Create horizontal arm
bpy.ops.mesh.primitive_cube_add(size=1, location=h_loc)
horizontal_arm = bpy.context.active_object
horizontal_arm.name = "Horizontal_Arm"
horizontal_arm.scale = h_dim
bpy.ops.rigidbody.object_add()
horizontal_arm.rigid_body.type = 'PASSIVE'
horizontal_arm.rigid_body.collision_shape = 'BOX'
horizontal_arm.rigid_body.mass = 1000.0

# Create fixed constraint between arms
bpy.ops.object.empty_add(type='PLAIN_AXES', location=constraint_loc)
constraint_empty = bpy.context.active_object
constraint_empty.name = "Fixed_Constraint"
bpy.ops.rigidbody.constraint_add()
constraint_empty.rigid_body_constraint.type = 'FIXED'
constraint_empty.rigid_body_constraint.object1 = vertical_arm
constraint_empty.rigid_body_constraint.object2 = horizontal_arm

# Create load cube
bpy.ops.mesh.primitive_cube_add(size=1, location=c_loc)
load_cube = bpy.context.active_object
load_cube.name = "Load_Cube"
load_cube.scale = c_dim
bpy.ops.rigidbody.object_add()
load_cube.rigid_body.type = 'ACTIVE'
load_cube.rigid_body.collision_shape = 'BOX'
load_cube.rigid_body.mass = load_mass
load_cube.rigid_body.friction = 0.5
load_cube.rigid_body.restitution = 0.1

# Set simulation frame range
bpy.context.scene.frame_start = 1
bpy.context.scene.frame_end = sim_frames

# Bake rigid body simulation
bpy.ops.ptcache.bake_all(bake=True)

print(f"L-bracket constructed with {load_mass}kg load")
print(f"Simulation baked for {sim_frames} frames")