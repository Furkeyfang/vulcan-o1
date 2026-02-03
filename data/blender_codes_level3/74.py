import bpy
import mathutils

# Clear existing scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Parameters from summary
base_dim = (3.0, 3.0, 0.5)
base_loc = (0.0, 0.0, 0.0)
tube_rad = 0.2
tube_ht = 2.0
tube_loc = (0.0, 0.0, 1.25)
sphere_rad = 0.15
sphere_loc = (0.0, 0.0, 2.1)
target_loc = (10.0, 0.0, 0.0)
hinge_axis = (0.0, 0.0, 1.0)
motor_vel = 25.0

# Create base platform
bpy.ops.mesh.primitive_cube_add(size=1.0, location=base_loc)
base = bpy.context.active_object
base.name = "BasePlatform"
base.scale = base_dim
bpy.ops.rigidbody.object_add()
base.rigid_body.type = 'PASSIVE'

# Create launch tube (cylinder)
bpy.ops.mesh.primitive_cylinder_add(
    vertices=32,
    radius=tube_rad,
    depth=tube_ht,
    location=tube_loc
)
tube = bpy.context.active_object
tube.name = "LaunchTube"
bpy.ops.rigidbody.object_add()
tube.rigid_body.type = 'PASSIVE'

# Create projectile sphere
bpy.ops.mesh.primitive_uv_sphere_add(
    segments=16,
    ring_count=8,
    radius=sphere_rad,
    location=sphere_loc
)
projectile = bpy.context.active_object
projectile.name = "Projectile"
bpy.ops.rigidbody.object_add()
projectile.rigid_body.type = 'ACTIVE'
projectile.rigid_body.mass = 1.0
projectile.rigid_body.collision_shape = 'SPHERE'

# Add Fixed Constraint between Base and Tube
bpy.context.view_layer.objects.active = base
bpy.ops.rigidbody.constraint_add()
constraint_fixed = base.rigid_body_constraint
constraint_fixed.type = 'FIXED'
constraint_fixed.object1 = base
constraint_fixed.object2 = tube

# Add Hinge Constraint between Tube and Projectile
bpy.context.view_layer.objects.active = tube
bpy.ops.rigidbody.constraint_add()
constraint_hinge = tube.rigid_body_constraint
constraint_hinge.type = 'HINGE'
constraint_hinge.object1 = tube
constraint_hinge.object2 = projectile
constraint_hinge.use_limit_z = False
constraint_hinge.use_motor_z = True
constraint_hinge.motor_velocity_z = motor_vel
constraint_hinge.motor_max_impulse_z = 100.0  # Sufficient torque

# Set world physics
bpy.context.scene.use_gravity = True
bpy.context.scene.gravity = mathutils.Vector((0.0, 0.0, -9.81))
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 10

# Add ground plane for reference
bpy.ops.mesh.primitive_plane_add(size=20.0, location=(5.0, 0.0, -0.1))
ground = bpy.context.active_object
ground.name = "Ground"
bpy.ops.rigidbody.object_add()
ground.rigid_body.type = 'PASSIVE'

# Add target marker (visual only)
bpy.ops.mesh.primitive_cylinder_add(
    vertices=8,
    radius=0.5,
    depth=0.1,
    location=target_loc
)
target = bpy.context.active_object
target.name = "Target"
target.rigid_body.type = 'PASSIVE'