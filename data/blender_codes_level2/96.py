import bpy

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Extract variables from parameter summary
col_size = (0.5, 0.5, 2.0)
col_loc = (0.0, 0.0, 1.0)
beam_size = (4.0, 0.5, 0.5)
beam_loc = (2.0, 0.0, 2.25)
plat_size = (4.0, 1.0, 0.1)
plat_loc = (2.0, 0.0, 2.55)
cube_sz = 0.5
cube_mass = 500.0
cube_loc = (3.75, 0.0, 2.85)
sim_frames = 100

# 1. Create Vertical Column (Anchor)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=col_loc)
column = bpy.context.active_object
column.name = "Column"
column.scale = col_size
bpy.ops.rigidbody.object_add()
column.rigid_body.type = 'PASSIVE'

# 2. Create Horizontal Support Beam
bpy.ops.mesh.primitive_cube_add(size=1.0, location=beam_loc)
beam = bpy.context.active_object
beam.name = "SupportBeam"
beam.scale = beam_size
bpy.ops.rigidbody.object_add()
beam.rigid_body.mass = beam.scale.x * beam.scale.y * beam.scale.z * 1000  # Approx density 1000 kg/m³

# 3. Create Conveyor Platform
bpy.ops.mesh.primitive_cube_add(size=1.0, location=plat_loc)
platform = bpy.context.active_object
platform.name = "ConveyorPlatform"
platform.scale = plat_size
bpy.ops.rigidbody.object_add()
platform.rigid_body.mass = platform.scale.x * platform.scale.y * platform.scale.z * 1000

# 4. Create Load Cube
bpy.ops.mesh.primitive_cube_add(size=1.0, location=cube_loc)
load_cube = bpy.context.active_object
load_cube.name = "LoadCube"
load_cube.scale = (cube_sz, cube_sz, cube_sz)
bpy.ops.rigidbody.object_add()
load_cube.rigid_body.mass = cube_mass

# 5. Create Fixed Constraints (Rigid Joints)
# Column <-> Beam
bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0.0, 0.0, 2.0))
empty1 = bpy.context.active_object
empty1.name = "Fix_Column_Beam"
bpy.ops.rigidbody.constraint_add()
empty1.rigid_body_constraint.type = 'FIXED'
empty1.rigid_body_constraint.object1 = column
empty1.rigid_body_constraint.object2 = beam

# Beam <-> Platform
bpy.ops.object.empty_add(type='PLAIN_AXES', location=beam_loc)
empty2 = bpy.context.active_object
empty2.name = "Fix_Beam_Platform"
bpy.ops.rigidbody.constraint_add()
empty2.rigid_body_constraint.type = 'FIXED'
empty2.rigid_body_constraint.object2 = beam
empty2.rigid_body_constraint.object1 = platform

# 6. Configure Physics World
bpy.context.scene.frame_end = sim_frames
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 50

# 7. Optional: Set collision margins for stability
for obj in [column, beam, platform, load_cube]:
    if obj.rigid_body:
        obj.rigid_body.collision_margin = 0.01