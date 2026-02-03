import bpy
import mathutils

# Clear existing scene
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

# Parameters from summary
col_sz = (0.5, 0.5, 3.0)
col_loc = (0.0, 0.0, 1.5)
beam_sz = (3.5, 0.5, 0.5)
beam_loc = (1.75, 0.0, 3.25)
load_sz = (0.8, 0.8, 0.8)
load_loc = (3.5, 0.0, 3.9)
anchor_loc = (0.0, 0.0, 0.0)
hinge_piv = (0.0, 0.0, 3.0)
load_mass = 400.0
beam_mass = 100.0
hinge_stiff = 500000.0
hinge_damp = 10000.0
sim_frames = 100

# Enable rigid body physics
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 50

# 1. Create anchor (invisible reference)
bpy.ops.object.empty_add(type='PLAIN_AXES', location=anchor_loc)
anchor = bpy.context.active_object
anchor.name = "Anchor"
bpy.ops.rigidbody.object_add()
anchor.rigid_body.type = 'PASSIVE'
anchor.rigid_body.collision_shape = 'BOX'
anchor.hide_render = True
anchor.hide_viewport = True

# 2. Create vertical column
bpy.ops.mesh.primitive_cube_add(size=1, location=col_loc)
column = bpy.context.active_object
column.name = "Column"
column.scale = col_sz
bpy.ops.rigidbody.object_add()
column.rigid_body.type = 'PASSIVE'
column.rigid_body.collision_shape = 'BOX'
column.rigid_body.mass = 1000  # Heavy base

# Fixed constraint: Column to Anchor
bpy.ops.object.empty_add(type='PLAIN_AXES', location=anchor_loc)
const_fixed = bpy.context.active_object
const_fixed.name = "Fixed_Constraint"
const_fixed.empty_display_size = 0.3
bpy.ops.rigidbody.constraint_add()
const_fixed.rigid_body_constraint.type = 'FIXED'
const_fixed.rigid_body_constraint.object1 = anchor
const_fixed.rigid_body_constraint.object2 = column

# 3. Create horizontal beam
bpy.ops.mesh.primitive_cube_add(size=1, location=beam_loc)
beam = bpy.context.active_object
beam.name = "Beam"
beam.scale = beam_sz
bpy.ops.rigidbody.object_add()
beam.rigid_body.type = 'ACTIVE'
beam.rigid_body.collision_shape = 'BOX'
beam.rigid_body.mass = beam_mass

# Hinge constraint: Column to Beam
bpy.ops.object.empty_add(type='PLAIN_AXES', location=hinge_piv)
hinge = bpy.context.active_object
hinge.name = "Hinge_Constraint"
hinge.empty_display_size = 0.4
bpy.ops.rigidbody.constraint_add()
hinge.rigid_body_constraint.type = 'HINGE'
hinge.rigid_body_constraint.object1 = column
hinge.rigid_body_constraint.object2 = beam
hinge.rigid_body_constraint.use_limit_ang_z = True
hinge.rigid_body_constraint.limit_ang_z_lower = -math.radians(5)
hinge.rigid_body_constraint.limit_ang_z_upper = math.radians(5)
hinge.rigid_body_constraint.use_spring_ang_z = True
hinge.rigid_body_constraint.spring_stiffness_ang_z = hinge_stiff
hinge.rigid_body_constraint.spring_damping_ang_z = hinge_damp

# 4. Create load block
bpy.ops.mesh.primitive_cube_add(size=1, location=load_loc)
load = bpy.context.active_object
load.name = "Load"
load.scale = load_sz
bpy.ops.rigidbody.object_add()
load.rigid_body.type = 'ACTIVE'
load.rigid_body.collision_shape = 'BOX'
load.rigid_body.mass = load_mass

# Fixed constraint: Beam to Load
bpy.ops.object.empty_add(type='PLAIN_AXES', location=load_loc)
const_load = bpy.context.active_object
const_load.name = "Load_Constraint"
const_load.empty_display_size = 0.3
bpy.ops.rigidbody.constraint_add()
const_load.rigid_body_constraint.type = 'FIXED'
const_load.rigid_body_constraint.object1 = beam
const_load.rigid_body_constraint.object2 = load

# 5. Set simulation parameters
bpy.context.scene.frame_end = sim_frames
bpy.context.scene.rigidbody_world.enabled = True

# 6. Run simulation (headless)
print("Running cantilever simulation...")
initial_z = load_loc[2]
for frame in range(sim_frames + 1):
    bpy.context.scene.frame_set(frame)
    # In headless mode, we'd typically export data or compute metrics
    # For verification, we could check load.z here
    if frame == sim_frames:
        final_z = load.matrix_world.translation.z
        deflection = initial_z - final_z
        print(f"Frame {frame}: Load Z = {final_z:.3f}m, Deflection = {deflection:.3f}m")
        if abs(deflection) < 0.1:
            print("SUCCESS: Deflection < 0.1m")
        else:
            print("WARNING: Deflection exceeds 0.1m limit")