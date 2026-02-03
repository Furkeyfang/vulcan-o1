import bpy
import mathutils

# Clear existing scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Parameters from summary
support_dim = (0.3, 0.3, 3.0)
support_center = (0.0, 0.0, 1.5)
canopy_dim = (2.5, 0.2, 0.1)
canopy_center = (1.25, 0.0, 3.05)
canopy_mass = 300.0
joint_position = (0.0, 0.0, 3.0)
frame_count = 100

# Create Support Beam (Vertical Column)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=support_center)
support = bpy.context.active_object
support.name = "Support_Beam"
support.scale = support_dim
bpy.ops.rigidbody.object_add()
support.rigid_body.type = 'PASSIVE'
support.rigid_body.collision_shape = 'BOX'
support.rigid_body.mass = 1.0  # Irrelevant for passive

# Create Canopy Beam (Horizontal Cantilever)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=canopy_center)
canopy = bpy.context.active_object
canopy.name = "Canopy_Beam"
canopy.scale = canopy_dim
bpy.ops.rigidbody.object_add()
canopy.rigid_body.type = 'ACTIVE'
canopy.rigid_body.collision_shape = 'BOX'
canopy.rigid_body.mass = canopy_mass
canopy.rigid_body.use_margin = True
canopy.rigid_body.collision_margin = 0.001

# Create Fixed Constraint at Connection Point
bpy.ops.object.empty_add(type='PLAIN_AXES', location=joint_position)
constraint_empty = bpy.context.active_object
constraint_empty.name = "Fixed_Constraint"
constraint_empty.empty_display_size = 0.1

bpy.ops.rigidbody.constraint_add()
constraint = constraint_empty.rigid_body_constraint
constraint.type = 'FIXED'
constraint.object1 = support
constraint.object2 = canopy

# Set up physics world
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 50
bpy.context.scene.frame_end = frame_count

# Ensure proper collision bounds
for obj in [support, canopy]:
    obj.display_type = 'SOLID'
    if obj.rigid_body:
        obj.rigid_body.use_deactivation = False

# Run simulation (headless compatible)
bpy.ops.ptcache.bake_all(bake=True)