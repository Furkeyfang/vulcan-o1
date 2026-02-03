import bpy
import math

# Clear existing scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Extract parameters from summary
base_dim = (2.0, 2.0, 1.0)
base_loc = (0.0, 0.0, 0.0)
top_dim = (1.5, 1.5, 1.0)
top_loc = (0.0, 0.0, 12.0)
top_rot_deg = 30.0
top_mass = 350.0
col_radius = 0.2
col_height = 12.0
col_z_center = 6.0
col_positions = [(1.0, 1.0), (1.0, -1.0), (-1.0, 1.0), (-1.0, -1.0)]
hinge_loc = (0.0, 0.0, 6.0)
simulation_frames = 250

# Convert rotation to radians
top_rot_rad = math.radians(top_rot_deg)

# Create Base Cube
bpy.ops.mesh.primitive_cube_add(size=1.0, location=base_loc)
base = bpy.context.active_object
base.scale = base_dim
base.name = "Base_Cube"
bpy.ops.rigidbody.object_add()
base.rigid_body.type = 'PASSIVE'

# Create Top Cube
bpy.ops.mesh.primitive_cube_add(size=1.0, location=top_loc)
top = bpy.context.active_object
top.scale = top_dim
top.rotation_euler = (0.0, 0.0, top_rot_rad)
top.name = "Top_Cube"
bpy.ops.rigidbody.object_add()
top.rigid_body.type = 'ACTIVE'
top.rigid_body.mass = top_mass

# Create Four Columns
for i, (x, y) in enumerate(col_positions):
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=32,
        radius=col_radius,
        depth=col_height,
        location=(x, y, col_z_center)
    )
    col = bpy.context.active_object
    col.name = f"Column_{i+1}"
    bpy.ops.rigidbody.object_add()
    col.rigid_body.type = 'PASSIVE'

# Create Hinge Constraint (Fixed type)
bpy.ops.object.empty_add(type='PLAIN_AXES', location=hinge_loc)
empty = bpy.context.active_object
empty.name = "Hinge_Constraint"
bpy.ops.rigidbody.constraint_add()
constraint = empty.rigid_body_constraint
constraint.type = 'FIXED'
constraint.object1 = base
constraint.object2 = top

# Configure physics world
bpy.context.scene.rigidbody_world.enabled = True
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 50
bpy.context.scene.frame_end = simulation_frames

# Verification: Set keyframes at frame 0 to track initial state
base.keyframe_insert(data_path="location", frame=0)
base.keyframe_insert(data_path="rotation_euler", frame=0)
top.keyframe_insert(data_path="location", frame=0)
top.keyframe_insert(data_path="rotation_euler", frame=0)

# Note: Actual simulation requires running `bpy.ops.ptcache.bake_all()` 
# or setting up scene to bake on playback. For headless verification,
# one would typically bake the simulation and check final frame.
print(f"Tower structure created. Top cube mass: {top_mass}kg, Rotation: {top_rot_deg}°")
print(f"Fixed hinge constraint at {hinge_loc}. Simulation ready for {simulation_frames} frames.")