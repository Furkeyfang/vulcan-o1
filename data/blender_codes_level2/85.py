import bpy
import mathutils

# Clear existing scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Extract parameters from summary
mast_dim = (0.3, 0.3, 8.0)
mast_loc = (0.0, 0.0, 4.0)
arm_dim = (1.2, 0.1, 0.1)
arm_loc = (0.6, 0.0, 8.0)
platform_dim = (0.2, 0.2, 0.05)
platform_loc = (1.2, 0.0, 8.075)
force_magnitude = 392.0
force_direction = (0.0, 0.0, -1.0)
hinge_pivot = (0.0, 0.0, 8.0)
ground_size = 5.0
ground_loc = (0.0, 0.0, -0.01)

# Create ground plane (static reference)
bpy.ops.mesh.primitive_plane_add(size=ground_size, location=ground_loc)
ground = bpy.context.active_object
ground.name = "Ground"
bpy.ops.rigidbody.object_add()
ground.rigid_body.type = 'PASSIVE'

# Create mast
bpy.ops.mesh.primitive_cube_add(size=1.0, location=mast_loc)
mast = bpy.context.active_object
mast.name = "Mast"
mast.scale = mast_dim
bpy.ops.rigidbody.object_add()
mast.rigid_body.type = 'PASSIVE'
mast.rigid_body.collision_shape = 'BOX'

# Create arm
bpy.ops.mesh.primitive_cube_add(size=1.0, location=arm_loc)
arm = bpy.context.active_object
arm.name = "Arm"
arm.scale = arm_dim
bpy.ops.rigidbody.object_add()
arm.rigid_body.type = 'ACTIVE'
arm.rigid_body.mass = 5.0  # Reasonable mass for arm
arm.rigid_body.collision_shape = 'BOX'

# Create platform
bpy.ops.mesh.primitive_cube_add(size=1.0, location=platform_loc)
platform = bpy.context.active_object
platform.name = "Platform"
platform.scale = platform_dim
bpy.ops.rigidbody.object_add()
platform.rigid_body.type = 'ACTIVE'
platform.rigid_body.mass = 40.0  # Load mass
platform.rigid_body.collision_shape = 'BOX'

# Create constraints
# 1. Fixed constraint: Mast to Ground (at mast base)
bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 0))
constraint_empty = bpy.context.active_object
constraint_empty.name = "Constraints"

bpy.ops.rigidbody.constraint_add()
constraint = bpy.context.active_object.rigid_body_constraint
constraint.type = 'FIXED'
constraint.object1 = ground
constraint.object2 = mast
constraint.disable_collisions = True

# 2. Hinge constraint: Mast to Arm (at mast top)
bpy.ops.object.empty_add(type='PLAIN_AXES', location=hinge_pivot)
hinge_empty = bpy.context.active_object
hinge_empty.name = "Hinge_Constraint"
hinge_empty.parent = mast  # Position relative to mast

bpy.ops.rigidbody.constraint_add()
hinge_constraint = bpy.context.active_object.rigid_body_constraint
hinge_constraint.type = 'HINGE'
hinge_constraint.object1 = mast
hinge_constraint.object2 = arm
hinge_constraint.pivot_x = hinge_pivot[0]
hinge_constraint.pivot_y = hinge_pivot[1]
hinge_constraint.pivot_z = hinge_pivot[2]
hinge_constraint.use_limit_z = True
hinge_constraint.limit_z_upper = math.radians(5)  # Small rotation limit
hinge_constraint.limit_z_lower = math.radians(-5)
hinge_constraint.disable_collisions = True

# 3. Fixed constraint: Arm to Platform
bpy.ops.object.empty_add(type='PLAIN_AXES', location=platform_loc)
platform_constraint_empty = bpy.context.active_object
platform_constraint_empty.name = "Platform_Constraint"
platform_constraint_empty.parent = arm

bpy.ops.rigidbody.constraint_add()
platform_constraint = bpy.context.active_object.rigid_body_constraint
platform_constraint.type = 'FIXED'
platform_constraint.object1 = arm
platform_constraint.object2 = platform
platform_constraint.disable_collisions = True

# Apply downward force to platform
bpy.ops.object.forcefield_add(type='FORCE')
force_field = bpy.context.active_object
force_field.name = "Load_Force"
force_field.location = platform_loc
force_field.field.strength = force_magnitude
force_field.field.direction = force_direction
force_field.field.use_max_distance = True
force_field.field.max_distance = 0.15  # Only affect platform
force_field.field.falloff_power = 0.0  # Constant force within range

# Link force field to platform
platform.field.new(type='FORCE')
platform.field_settings[0].field = force_field.field

# Configure simulation
bpy.context.scene.rigidbody_world.enabled = True
bpy.context.scene.rigidbody_world.time_scale = 1.0
bpy.context.scene.rigidbody_world.steps_per_second = 250
bpy.context.scene.rigidbody_world.solver_iterations = 50

# Set gravity
bpy.context.scene.gravity = (0.0, 0.0, -9.81)

print("Cantilever mast construction complete.")
print(f"Expected deflection limit: 0.1 m")
print(f"Applied force: {force_magnitude} N at platform center")