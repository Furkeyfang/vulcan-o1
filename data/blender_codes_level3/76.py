import bpy
import math

# Clear existing scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Extract parameters from summary
base_dim = (2.0, 2.0, 0.3)
base_loc = (0.0, 0.0, 0.0)
support_dim = (0.2, 0.2, 1.5)
support_loc = (0.0, 0.0, 1.05)
launcher_dim = (1.5, 0.2, 0.2)
launcher_loc = (0.75, 0.0, 1.8)
projectile_radius = 0.1
projectile_depth = 0.3
projectile_loc = (1.65, 0.0, 1.8)
hinge_pivot_support_local = (0.0, 0.0, 0.75)
hinge_pivot_launcher_local = (-0.75, 0.0, 0.0)
fixed_pivot_launcher_local = (0.75, 0.0, 0.0)
fixed_pivot_projectile_local = (-0.15, 0.0, 0.0)
motor_angular_velocity = 20.0
constraint_breaking_threshold = 10.0

# Create base platform
bpy.ops.mesh.primitive_cube_add(size=1.0, location=base_loc)
base = bpy.context.active_object
base.scale = base_dim
bpy.ops.rigidbody.object_add()
base.rigid_body.type = 'PASSIVE'

# Create vertical support arm
bpy.ops.mesh.primitive_cube_add(size=1.0, location=support_loc)
support = bpy.context.active_object
support.scale = support_dim
bpy.ops.rigidbody.object_add()
support.rigid_body.type = 'PASSIVE'

# Create launcher arm
bpy.ops.mesh.primitive_cube_add(size=1.0, location=launcher_loc)
launcher = bpy.context.active_object
launcher.scale = launcher_dim
bpy.ops.rigidbody.object_add()
launcher.rigid_body.type = 'ACTIVE'

# Create projectile (cylinder oriented along X)
bpy.ops.mesh.primitive_cylinder_add(
    radius=projectile_radius,
    depth=projectile_depth,
    location=projectile_loc,
    rotation=(0, math.pi/2, 0)
)
projectile = bpy.context.active_object
bpy.ops.rigidbody.object_add()
projectile.rigid_body.type = 'ACTIVE'

# Fixed constraint between base and support
support.select_set(True)
base.select_set(True)
bpy.context.view_layer.objects.active = support
bpy.ops.rigidbody.constraint_add()
constraint_base_support = support.rigid_body_constraints[-1]
constraint_base_support.type = 'FIXED'

# Hinge constraint between support and launcher (with motor)
launcher.select_set(True)
support.select_set(True)
bpy.context.view_layer.objects.active = launcher
bpy.ops.rigidbody.constraint_add()
constraint_hinge = launcher.rigid_body_constraints[-1]
constraint_hinge.type = 'HINGE'
constraint_hinge.pivot_type = 'CUSTOM'
constraint_hinge.use_limits = False
constraint_hinge.use_motor = True
constraint_hinge.motor_angular_velocity = motor_angular_velocity
# Set pivots in local coordinates
constraint_hinge.object1 = support
constraint_hinge.object2 = launcher
constraint_hinge.pivot_x = hinge_pivot_launcher_local[0]
constraint_hinge.pivot_y = hinge_pivot_launcher_local[1]
constraint_hinge.pivot_z = hinge_pivot_launcher_local[2]
constraint_hinge.pivot_x_1 = hinge_pivot_support_local[0]
constraint_hinge.pivot_y_1 = hinge_pivot_support_local[1]
constraint_hinge.pivot_z_1 = hinge_pivot_support_local[2]

# Fixed constraint between launcher and projectile (breakable)
projectile.select_set(True)
launcher.select_set(True)
bpy.context.view_layer.objects.active = projectile
bpy.ops.rigidbody.constraint_add()
constraint_fixed = projectile.rigid_body_constraints[-1]
constraint_fixed.type = 'FIXED'
constraint_fixed.pivot_type = 'CUSTOM'
constraint_fixed.breaking_threshold = constraint_breaking_threshold
# Set pivots
constraint_fixed.object1 = launcher
constraint_fixed.object2 = projectile
constraint_fixed.pivot_x = fixed_pivot_projectile_local[0]
constraint_fixed.pivot_y = fixed_pivot_projectile_local[1]
constraint_fixed.pivot_z = fixed_pivot_projectile_local[2]
constraint_fixed.pivot_x_1 = fixed_pivot_launcher_local[0]
constraint_fixed.pivot_y_1 = fixed_pivot_launcher_local[1]
constraint_fixed.pivot_z_1 = fixed_pivot_launcher_local[2]

# Ensure all objects are visible in render and have collision
for obj in [base, support, launcher, projectile]:
    obj.visible_camera = True
    obj.visible_diffuse = True
    obj.visible_glossy = True
    obj.visible_transmission = True
    obj.visible_volume_scatter = True
    obj.visible_shadow = True

print("Side-arm launcher mechanism created successfully.")