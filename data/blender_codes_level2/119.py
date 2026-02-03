import bpy
import mathutils

# Clear existing scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Extract parameters from summary
pole_dim = (0.5, 0.5, 7.0)
pole_loc = (0.0, 0.0, 3.5)
arm_dim = (3.0, 0.3, 0.3)
arm_loc = (1.5, 0.0, 7.15)
cube_sz = 0.5
load_mass = 220.0
load_loc = (3.25, 0.0, 7.15)

# Set gravity direction (Z-down)
if bpy.context.scene.rigidbody_world:
    bpy.context.scene.rigidbody_world.gravity = mathutils.Vector((0, 0, -9.81))

# 1. Create Vertical Pole
bpy.ops.mesh.primitive_cube_add(size=1.0, location=pole_loc)
pole = bpy.context.active_object
pole.name = "Pole"
pole.scale = pole_dim
bpy.ops.rigidbody.object_add()
pole.rigid_body.type = 'PASSIVE'
pole.rigid_body.collision_shape = 'BOX'

# 2. Create Horizontal Arm
bpy.ops.mesh.primitive_cube_add(size=1.0, location=arm_loc)
arm = bpy.context.active_object
arm.name = "Arm"
arm.scale = arm_dim
bpy.ops.rigidbody.object_add()
arm.rigid_body.type = 'PASSIVE'
arm.rigid_body.collision_shape = 'BOX'

# 3. Create Load Cube
bpy.ops.mesh.primitive_cube_add(size=1.0, location=load_loc)
load = bpy.context.active_object
load.name = "Load"
load.scale = (cube_sz, cube_sz, cube_sz)
bpy.ops.rigidbody.object_add()
load.rigid_body.type = 'ACTIVE'
load.rigid_body.mass = load_mass
load.rigid_body.collision_shape = 'BOX'

# 4. Create Fixed Constraint: Pole -> Arm
bpy.context.view_layer.objects.active = arm
bpy.ops.rigidbody.constraint_add()
con1 = arm.constraints["RigidBodyConstraint"]
con1.type = 'FIXED'
con1.object1 = pole
con1.object2 = arm

# 5. Create Fixed Constraint: Arm -> Load
bpy.context.view_layer.objects.active = load
bpy.ops.rigidbody.constraint_add()
con2 = load.constraints["RigidBodyConstraint"]
con2.type = 'FIXED'
con2.object1 = arm
con2.object2 = load

# Ensure all transforms are applied
for obj in [pole, arm, load]:
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

print("Cantilever signage structure created successfully.")