import bpy
import math

# Clear existing scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Extract parameters
L = 12.0
W = 4.0
T = 0.3
roof_z = 4.0
cw = 0.5
cd = 0.5
ch = 4.0
bl = 12.0
bw = 0.5
bd = 0.5
col_pos = [(-6.0, -2.0, 2.0), (-6.0, 2.0, 2.0), (6.0, -2.0, 2.0), (6.0, 2.0, 2.0)]
beam_pos = [(0.0, -2.0, 4.0), (0.0, 2.0, 4.0)]
mass = 900.0
g = 9.81
force_total = mass * g

# Create ground plane (passive)
bpy.ops.mesh.primitive_plane_add(size=20.0, location=(0, 0, 0))
ground = bpy.context.active_object
ground.name = "Ground"
bpy.ops.rigidbody.object_add()
ground.rigid_body.type = 'PASSIVE'

# Create columns
columns = []
for i, pos in enumerate(col_pos):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=pos)
    col = bpy.context.active_object
    col.name = f"Column_{i+1}"
    col.scale = (cw, cd, ch)
    bpy.ops.rigidbody.object_add()
    col.rigid_body.mass = 200.0  # Heavy columns for stability
    columns.append(col)

# Create beams
beams = []
for i, pos in enumerate(beam_pos):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=pos)
    beam = bpy.context.active_object
    beam.name = f"Beam_{i+1}"
    beam.scale = (bl, bw, bd)
    bpy.ops.rigidbody.object_add()
    beam.rigid_body.mass = 100.0
    beams.append(beam)

# Create roof panel
roof_loc = (0.0, 0.0, roof_z)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=roof_loc)
roof = bpy.context.active_object
roof.name = "Roof_Panel"
roof.scale = (L, W, T)
bpy.ops.rigidbody.object_add()
roof.rigid_body.mass = mass

# Add fixed constraints: columns to ground
for col in columns:
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(col.location.x, col.location.y, 0))
    constraint = bpy.context.active_object
    constraint.name = f"Fix_{col.name}_Ground"
    constraint.empty_display_size = 0.5
    bpy.ops.rigidbody.constraint_add()
    constraint.rigid_body_constraint.type = 'FIXED'
    constraint.rigid_body_constraint.object1 = ground
    constraint.rigid_body_constraint.object2 = col

# Add fixed constraints: columns to beams
# Column1 (-6,-2) → Beam1 (Y=-2)
bpy.ops.object.empty_add(type='PLAIN_AXES', location=(-6, -2, 4))
constraint = bpy.context.active_object
constraint.name = "Fix_Col1_Beam1"
constraint.empty_display_size = 0.5
bpy.ops.rigidbody.constraint_add()
constraint.rigid_body_constraint.type = 'FIXED'
constraint.rigid_body_constraint.object1 = columns[0]
constraint.rigid_body_constraint.object2 = beams[0]

# Column3 (6,-2) → Beam1 (Y=-2)
bpy.ops.object.empty_add(type='PLAIN_AXES', location=(6, -2, 4))
constraint = bpy.context.active_object
constraint.name = "Fix_Col3_Beam1"
constraint.empty_display_size = 0.5
bpy.ops.rigidbody.constraint_add()
constraint.rigid_body_constraint.type = 'FIXED'
constraint.rigid_body_constraint.object1 = columns[2]
constraint.rigid_body_constraint.object2 = beams[0]

# Column2 (-6,2) → Beam2 (Y=2)
bpy.ops.object.empty_add(type='PLAIN_AXES', location=(-6, 2, 4))
constraint = bpy.context.active_object
constraint.name = "Fix_Col2_Beam2"
constraint.empty_display_size = 0.5
bpy.ops.rigidbody.constraint_add()
constraint.rigid_body_constraint.type = 'FIXED'
constraint.rigid_body_constraint.object1 = columns[1]
constraint.rigid_body_constraint.object2 = beams[1]

# Column4 (6,2) → Beam2 (Y=2)
bpy.ops.object.empty_add(type='PLAIN_AXES', location=(6, 2, 4))
constraint = bpy.context.active_object
constraint.name = "Fix_Col4_Beam2"
constraint.empty_display_size = 0.5
bpy.ops.rigidbody.constraint_add()
constraint.rigid_body_constraint.type = 'FIXED'
constraint.rigid_body_constraint.object1 = columns[3]
constraint.rigid_body_constraint.object2 = beams[1]

# Add fixed constraints: roof to beams
bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, -2, roof_z))
constraint = bpy.context.active_object
constraint.name = "Fix_Roof_Beam1"
constraint.empty_display_size = 0.5
bpy.ops.rigidbody.constraint_add()
constraint.rigid_body_constraint.type = 'FIXED'
constraint.rigid_body_constraint.object1 = roof
constraint.rigid_body_constraint.object2 = beams[0]

bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 2, roof_z))
constraint = bpy.context.active_object
constraint.name = "Fix_Roof_Beam2"
constraint.empty_display_size = 0.5
bpy.ops.rigidbody.constraint_add()
constraint.rigid_body_constraint.type = 'FIXED'
constraint.rigid_body_constraint.object1 = roof
constraint.rigid_body_constraint.object2 = beams[1]

# Apply downward force to roof (uniform distribution approximated)
force_per_vertex = force_total / 8.0  # 8 vertices of roof
roof.rigid_body.use_gravity = True  # Gravity provides base load
# Additional force field for the 900kg load
bpy.ops.object.effector_add(type='FORCE', location=(0, 0, roof_z + 1))
force_field = bpy.context.active_object
force_field.name = "Load_Force"
force_field.field.strength = -force_total
force_field.field.distance_max = 2.0
force_field.field.falloff_power = 0.0

# Set up simulation parameters
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 10
bpy.context.scene.frame_end = 100

print(f"Structure built. Total load: {force_total:.1f}N")
print("Simulation ready - run for 100 frames to verify stability")