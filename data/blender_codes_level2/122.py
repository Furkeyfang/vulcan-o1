import bpy
import math

# Clear scene
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

# Parameters from summary
base_dim = (1.0, 1.0, 1.0)
base_loc = (0.0, 0.0, 0.5)
boom_dim = (5.0, 0.3, 0.3)
boom_loc = (2.5, 0.0, 1.15)
platform_radius = 0.5
platform_depth = 0.1
platform_loc = (5.0, 0.0, 1.15)
steel_density = 7850.0
load_mass = 350.0
hinge_pivot = (0.0, 0.0, 1.0)
force_magnitude = 3433.5
simulation_frames = 100

# 1. Create Fixed Base
bpy.ops.mesh.primitive_cube_add(size=1, location=base_loc)
base = bpy.context.active_object
base.name = "Base"
base.scale = base_dim
bpy.ops.rigidbody.object_add()
base.rigid_body.type = 'PASSIVE'
base.rigid_body.collision_shape = 'BOX'

# 2. Create Boom Arm
bpy.ops.mesh.primitive_cube_add(size=1, location=boom_loc)
boom = bpy.context.active_object
boom.name = "Boom"
boom.scale = boom_dim
bpy.ops.rigidbody.object_add()
boom.rigid_body.type = 'ACTIVE'
boom.rigid_body.collision_shape = 'BOX'
# Calculate mass from steel density (volume = 5*0.3*0.3 = 0.45 m³)
boom.rigid_body.mass = steel_density * (boom_dim[0] * boom_dim[1] * boom_dim[2])

# 3. Create Inspection Platform
bpy.ops.mesh.primitive_cylinder_add(
    vertices=32,
    radius=platform_radius,
    depth=platform_depth,
    location=platform_loc
)
platform = bpy.context.active_object
platform.name = "Platform"
bpy.ops.rigidbody.object_add()
platform.rigid_body.type = 'ACTIVE'
platform.rigid_body.collision_shape = 'CYLINDER'
platform.rigid_body.mass = load_mass

# 4. Add Hinge Constraint (Base ↔ Boom)
bpy.ops.object.empty_add(type='PLAIN_AXES', location=hinge_pivot)
hinge = bpy.context.active_object
hinge.name = "Hinge_Constraint"
bpy.ops.rigidbody.constraint_add()
hinge.rigid_body_constraint.type = 'HINGE'
hinge.rigid_body_constraint.object1 = base
hinge.rigid_body_constraint.object2 = boom
# Align hinge axis to global Y
hinge.rigid_body_constraint.use_limit_ang_z = True
hinge.rigid_body_constraint.limit_ang_z_lower = -math.radians(30)
hinge.rigid_body_constraint.limit_ang_z_upper = math.radians(30)

# 5. Add Fixed Constraint (Boom ↔ Platform)
bpy.ops.object.empty_add(type='PLAIN_AXES', location=platform_loc)
fixed = bpy.context.active_object
fixed.name = "Fixed_Constraint"
bpy.ops.rigidbody.constraint_add()
fixed.rigid_body_constraint.type = 'FIXED'
fixed.rigid_body_constraint.object1 = boom
fixed.rigid_body_constraint.object2 = platform

# 6. Apply Downward Force
# Create force field (point gravity) at platform center
bpy.ops.object.effector_add(type='FORCE', location=platform_loc)
force = bpy.context.active_object
force.name = "Load_Force"
force.field.type = 'FORCE'
force.field.strength = -force_magnitude  # Negative Z direction
force.field.use_gravity = False
force.field.falloff_power = 0  # Constant force

# 7. Configure Simulation
bpy.context.scene.frame_end = simulation_frames
bpy.context.scene.rigidbody_world.steps_per_second = 250
bpy.context.scene.rigidbody_world.solver_iterations = 50

# Optional: Bake simulation for headless verification
# bpy.ops.ptcache.bake_all(bake=True)