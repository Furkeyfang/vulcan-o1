import bpy
import mathutils

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Extract parameters from summary
col_h = 9.0
outer_w = 1.0
outer_d = 1.0
wall_t = 0.1
inner_w = outer_w - 2 * wall_t  # 0.8
inner_d = outer_d - 2 * wall_t  # 0.8
col_center_z = col_h / 2  # 4.5
load_mass = 4000
gravity = 9.81
force_n = load_mass * gravity  # 39240
sim_frames = 100
base_loc = (0.0, 0.0, 0.0)
top_center = (0.0, 0.0, col_h)

# Create outer column shell
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, col_center_z))
outer_col = bpy.context.active_object
outer_col.name = "Outer_Column"
outer_col.scale = (outer_w, outer_d, col_h)

# Create inner void (will be subtracted)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, col_center_z))
inner_void = bpy.context.active_object
inner_void.name = "Inner_Void"
inner_void.scale = (inner_w, inner_d, col_h)

# Apply boolean modifier to create hollow column
bool_mod = outer_col.modifiers.new(name="HollowBool", type='BOOLEAN')
bool_mod.object = inner_void
bool_mod.operation = 'DIFFERENCE'

# Apply modifier and clean up
bpy.context.view_layer.objects.active = outer_col
bpy.ops.object.modifier_apply(modifier="HollowBool")

# Delete inner void object
bpy.ops.object.select_all(action='DESELECT')
inner_void.select_set(True)
bpy.ops.object.delete()

# Select and prepare column for physics
outer_col.select_set(True)
bpy.context.view_layer.objects.active = outer_col

# Enable rigid body physics (passive/static)
bpy.ops.rigidbody.object_add()
outer_col.rigid_body.type = 'PASSIVE'
outer_col.rigid_body.collision_shape = 'MESH'

# Create force application indicator (small cube at top)
bpy.ops.mesh.primitive_cube_add(size=0.2, location=top_center)
force_indicator = bpy.context.active_object
force_indicator.name = "Load_Indicator"

# Apply downward force using force field
bpy.ops.object.forcefield_add(type='FORCE')
force_field = bpy.context.active_object
force_field.name = "Downward_Force"
force_field.location = top_center
force_field.field.strength = -force_n  # Negative for downward
force_field.field.falloff_power = 0  # Constant force
force_field.field.use_max_distance = True
force_field.field.distance_max = 0.5  # Only affects nearby objects

# Set up rigid body world
bpy.context.scene.rigidbody_world.enabled = True
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 10
bpy.context.scene.frame_end = sim_frames

# Create foundation plane (visual reference)
bpy.ops.mesh.primitive_plane_add(size=5.0, location=base_loc)
foundation = bpy.context.active_object
foundation.name = "Foundation"

# Set up simulation keyframes
bpy.context.scene.frame_set(1)
bpy.context.scene.frame_set(sim_frames)

print(f"Column design complete. Hollow rectangular section: {outer_w}x{outer_d}m, height: {col_h}m")
print(f"Wall thickness: {wall_t}m, Load: {load_mass}kg ({force_n:.0f}N)")
print(f"Simulation will run for {sim_frames} frames")