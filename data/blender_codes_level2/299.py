import bpy
import mathutils

# Clear existing scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Extract parameters
slab_dim = (6.0, 3.0, 0.3)
overhang = 3.5
column_radius = 0.3
column_height = 3.0
slab_center = (0.5, 0.0, 3.15)
column_center = (0.0, 0.0, 1.5)
total_force = 4414.5
slab_volume = 5.4
force_density = 817.5
sim_frames = 100

# Create Column (Cylinder)
bpy.ops.mesh.primitive_cylinder_add(
    radius=column_radius,
    depth=column_height,
    location=column_center
)
column = bpy.context.active_object
column.name = "Column"
bpy.ops.rigidbody.object_add()
column.rigid_body.type = 'PASSIVE'

# Create Slab (Cube)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=slab_center)
slab = bpy.context.active_object
slab.name = "Slab"
slab.scale = slab_dim
bpy.ops.rigidbody.object_add()
slab.rigid_body.type = 'ACTIVE'
slab.rigid_body.mass = 0.1  # Arbitrary small mass since force field drives loading

# Create Fixed Constraint between Column and Slab
bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 3.0))
constraint_empty = bpy.context.active_object
constraint_empty.name = "Fixed_Constraint"
bpy.ops.rigidbody.constraint_add()
constraint = constraint_empty.rigid_body_constraint
constraint.type = 'FIXED'
constraint.object1 = column
constraint.object2 = slab

# Apply Distributed Load as Force Field
bpy.ops.object.effector_add(type='FORCE', location=(0, 0, 3.30))
force_field = bpy.context.active_object
force_field.name = "Distributed_Load"
force_field.field.strength = -force_density  # Negative Z direction
force_field.field.distance_max = 0.001  # Limit influence to very close proximity
force_field.field.falloff_power = 0
force_field.field.use_max_distance = True

# Parent force field to slab to move with it
force_field.parent = slab

# Set up simulation parameters
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 50
bpy.context.scene.frame_end = sim_frames

# Run simulation (headless will execute frames automatically)
# Note: In headless mode, we rely on background rendering or physics update
# For pure simulation without UI, we can step through frames:
for frame in range(1, sim_frames + 1):
    bpy.context.scene.frame_set(frame)
    # Optionally update scene for physics evaluation
    bpy.context.scene.update()