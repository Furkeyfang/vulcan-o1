import bpy
import mathutils

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# ========== PARAMETERS (from summary) ==========
column_size = (0.5, 0.5, 2.0)
column_loc = (0.0, 0.0, 1.0)
arm_size = (5.0, 0.5, 0.5)
arm_loc = (2.5, 0.0, 2.25)
platform_size = (1.0, 1.0, 0.2)
platform_loc = (5.0, 0.0, 1.9)

load_mass_kg = 700.0
gravity = 9.81
force_magnitude = load_mass_kg * gravity
constraint_breaking_threshold = 10000.0

ground_size = 20.0
ground_loc = (0.0, 0.0, 0.0)

# ========== CREATE GROUND PLANE ==========
bpy.ops.mesh.primitive_plane_add(size=ground_size, location=ground_loc)
ground = bpy.context.active_object
ground.name = "Ground"
bpy.ops.rigidbody.object_add()
ground.rigid_body.type = 'PASSIVE'
ground.rigid_body.collision_shape = 'MESH'

# ========== CREATE VERTICAL SUPPORT COLUMN ==========
bpy.ops.mesh.primitive_cube_add(size=1.0, location=column_loc)
column = bpy.context.active_object
column.name = "Column"
column.scale = column_size
bpy.ops.rigidbody.object_add()
column.rigid_body.type = 'PASSIVE'
column.rigid_body.collision_shape = 'BOX'

# ========== CREATE HORIZONTAL ARM BEAM ==========
bpy.ops.mesh.primitive_cube_add(size=1.0, location=arm_loc)
arm = bpy.context.active_object
arm.name = "Arm"
arm.scale = arm_size
bpy.ops.rigidbody.object_add()
arm.rigid_body.type = 'PASSIVE'
arm.rigid_body.collision_shape = 'BOX'

# ========== CREATE LOAD PLATFORM ==========
bpy.ops.mesh.primitive_cube_add(size=1.0, location=platform_loc)
platform = bpy.context.active_object
platform.name = "Platform"
platform.scale = platform_size
bpy.ops.rigidbody.object_add()
platform.rigid_body.type = 'ACTIVE'
platform.rigid_body.mass = load_mass_kg
platform.rigid_body.collision_shape = 'BOX'

# ========== CREATE FIXED CONSTRAINTS ==========
# Constraint 1: Ground ↔ Column Base
bpy.ops.rigidbody.constraint_add()
con1 = bpy.context.active_object
con1.name = "Constraint_Ground_Column"
con1.rigid_body_constraint.type = 'FIXED'
con1.rigid_body_constraint.object1 = ground
con1.rigid_body_constraint.object2 = column
con1.location = (0, 0, 0)  # Base of column
con1.rigid_body_constraint.breaking_threshold = constraint_breaking_threshold

# Constraint 2: Column Top ↔ Arm (at attachment point)
bpy.ops.rigidbody.constraint_add()
con2 = bpy.context.active_object
con2.name = "Constraint_Column_Arm"
con2.rigid_body_constraint.type = 'FIXED'
con2.rigid_body_constraint.object1 = column
con2.rigid_body_constraint.object2 = arm
con2.location = (0, 0, 2.0)  # Top of column / start of arm
con2.rigid_body_constraint.breaking_threshold = constraint_breaking_threshold

# Constraint 3: Arm Free End ↔ Platform
bpy.ops.rigidbody.constraint_add()
con3 = bpy.context.active_object
con3.name = "Constraint_Arm_Platform"
con3.rigid_body_constraint.type = 'FIXED'
con3.rigid_body_constraint.object1 = arm
con3.rigid_body_constraint.object2 = platform
con3.location = (5.0, 0, 2.0)  # Free end of arm / top of platform
con3.rigid_body_constraint.breaking_threshold = constraint_breaking_threshold

# ========== APPLY DOWNWARD FORCE FIELD ==========
# Create a force field (gravity-like) localized at the platform
bpy.ops.object.effector_add(type='FORCE', location=platform_loc)
force = bpy.context.active_object
force.name = "Load_Force"
force.field.type = 'FORCE'
force.field.strength = -force_magnitude  # Negative = downward
force.field.use_max_distance = True
force.field.max_distance = 0.5  # Only affect objects within 0.5m
force.field.falloff_power = 0  # Constant force within range

# Link force field to platform (parent it so it moves with platform)
force.parent = platform

# ========== SETUP PHYSICS WORLD ==========
# Ensure rigid body world exists and gravity is standard
if bpy.context.scene.rigidbody_world is None:
    bpy.ops.rigidbody.world_add()
bpy.context.scene.rigidbody_world.gravity.z = -gravity

print("Cantilever formwork arm assembly complete.")
print(f"Applied force: {force_magnitude:.1f} N downward on platform.")