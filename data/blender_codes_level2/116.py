import bpy
import mathutils

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Parameters from summary
wall_dim = (0.5, 3.0, 4.0)
wall_loc = (0.0, 1.5, 2.0)
balcony_dim = (3.0, 2.0, 0.3)
balcony_loc = (0.0, 4.0, 4.15)
cube_dim = (0.5, 0.5, 0.5)
cube_loc = (0.0, 5.5, 4.55)
cube_mass = 200.0
sim_frames = 100

# Ensure rigid body world exists
if bpy.context.scene.rigidbody_world is None:
    bpy.ops.rigidbody.world_add()

# 1. Create Support Wall (Passive)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=wall_loc)
wall = bpy.context.active_object
wall.name = "SupportWall"
wall.scale = wall_dim
bpy.ops.rigidbody.object_add()
wall.rigid_body.type = 'PASSIVE'

# 2. Create Balcony Platform (Active)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=balcony_loc)
balcony = bpy.context.active_object
balcony.name = "BalconyPlatform"
balcony.scale = balcony_dim
bpy.ops.rigidbody.object_add()
balcony.rigid_body.type = 'ACTIVE'

# 3. Create Load Cube (Active)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=cube_loc)
cube = bpy.context.active_object
cube.name = "LoadCube"
cube.scale = cube_dim
bpy.ops.rigidbody.object_add()
cube.rigid_body.type = 'ACTIVE'
cube.rigid_body.mass = cube_mass

# 4. Add Fixed Constraints
# Constraint: Wall -> Balcony
bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0.0, 3.0, 4.0))  # Junction point
con1 = bpy.context.active_object
con1.name = "Fixed_Wall_Balcony"
bpy.ops.rigidbody.constraint_add()
con1.rigid_body_constraint.type = 'FIXED'
con1.rigid_body_constraint.object1 = wall
con1.rigid_body_constraint.object2 = balcony

# Constraint: Balcony -> Cube
bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0.0, 5.0, 4.3))  # Cube's near edge
con2 = bpy.context.active_object
con2.name = "Fixed_Balcony_Cube"
bpy.ops.rigidbody.constraint_add()
con2.rigid_body_constraint.type = 'FIXED'
con2.rigid_body_constraint.object1 = balcony
con2.rigid_body_constraint.object2 = cube

# 5. Set up simulation
bpy.context.scene.frame_end = sim_frames
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 50  # Higher for stability

# 6. Run simulation (headless)
for frame in range(sim_frames + 1):
    bpy.context.scene.frame_set(frame)
    # Optional: print positions for verification
    if frame % 20 == 0:
        print(f"Frame {frame}: Cube at {cube.location}")

print("Simulation setup complete. Structure should remain stable.")