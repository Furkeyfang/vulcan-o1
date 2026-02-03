import bpy
import mathutils

# Clear existing objects
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

# Parameters from summary
base_dim = (4.0, 2.0, 0.5)
base_center = (0.0, 0.0, 0.25)

support_dim = (0.2, 0.2, 2.0)
support1_center = (1.0, 0.5, 1.5)
support2_center = (3.0, 0.5, 1.5)

arm_dim = (0.2, 0.2, 3.0)
arm1_center = (2.5, 0.5, 2.5)
arm2_center = (4.5, 0.5, 2.5)

hinge1_point = (1.0, 0.5, 2.5)
hinge2_point = (3.0, 0.5, 2.5)

proj_dim = (0.2, 0.2, 0.2)
proj1_center = (4.0, 0.5, 2.5)
proj2_center = (6.0, 0.5, 2.5)

motor_velocity = 5.0
total_frames = 100

# Enable rigid body world
bpy.ops.rigidbody.world_add()

# 1. Base Platform
bpy.ops.mesh.primitive_cube_add(size=1.0, location=base_center)
base = bpy.context.active_object
base.name = "Base"
base.scale = base_dim
bpy.ops.rigidbody.object_add()
base.rigid_body.type = 'PASSIVE'

# 2. Vertical Support 1
bpy.ops.mesh.primitive_cube_add(size=1.0, location=support1_center)
support1 = bpy.context.active_object
support1.name = "Support1"
support1.scale = support_dim
bpy.ops.rigidbody.object_add()
support1.rigid_body.type = 'PASSIVE'

# 3. Vertical Support 2
bpy.ops.mesh.primitive_cube_add(size=1.0, location=support2_center)
support2 = bpy.context.active_object
support2.name = "Support2"
support2.scale = support_dim
bpy.ops.rigidbody.object_add()
support2.rigid_body.type = 'PASSIVE'

# 4. Throwing Arm 1
bpy.ops.mesh.primitive_cube_add(size=1.0, location=arm1_center)
arm1 = bpy.context.active_object
arm1.name = "Arm1"
arm1.scale = (3.0, 0.2, 0.2)  # Long dimension along X
bpy.ops.rigidbody.object_add()
arm1.rigid_body.type = 'ACTIVE'

# 5. Throwing Arm 2
bpy.ops.mesh.primitive_cube_add(size=1.0, location=arm2_center)
arm2 = bpy.context.active_object
arm2.name = "Arm2"
arm2.scale = (3.0, 0.2, 0.2)
bpy.ops.rigidbody.object_add()
arm2.rigid_body.type = 'ACTIVE'

# 6. Projectile 1
bpy.ops.mesh.primitive_cube_add(size=1.0, location=proj1_center)
proj1 = bpy.context.active_object
proj1.name = "Projectile1"
proj1.scale = proj_dim
bpy.ops.rigidbody.object_add()
proj1.rigid_body.type = 'ACTIVE'

# 7. Projectile 2
bpy.ops.mesh.primitive_cube_add(size=1.0, location=proj2_center)
proj2 = bpy.context.active_object
proj2.name = "Projectile2"
proj2.scale = proj_dim
bpy.ops.rigidbody.object_add()
proj2.rigid_body.type = 'ACTIVE'

# 8. Hinge Constraints (Motorized)
def add_motor_hinge(obj_a, obj_b, hinge_point, axis=(0,1,0)):
    """Create hinge constraint between two objects with motor"""
    # Create empty at hinge point for constraint reference
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=hinge_point)
    empty = bpy.context.active_object
    empty.name = f"Hinge_{obj_a.name}_{obj_b.name}"
    
    # Add constraint to first object (support)
    bpy.context.view_layer.objects.active = obj_a
    bpy.ops.rigidbody.constraint_add()
    constraint = obj_a.rigid_body.constraints[-1]
    constraint.type = 'HINGE'
    constraint.object1 = obj_a
    constraint.object2 = obj_b
    constraint.use_limit = False
    constraint.use_motor = True
    constraint.motor_velocity = motor_velocity
    constraint.motor_max_torque = 1000.0  # High torque for quick acceleration
    
    # Set pivot in local coordinates
    # For support: pivot is at top center relative to its center
    local_pivot_support = hinge_point - obj_a.location
    # Convert to object's scaled local space (since object scale applied)
    local_pivot_support.x /= obj_a.scale.x
    local_pivot_support.y /= obj_a.scale.y
    local_pivot_support.z /= obj_a.scale.z
    
    # For arm: pivot is at left end (negative X direction)
    local_pivot_arm = hinge_point - obj_b.location
    local_pivot_arm.x /= obj_b.scale.x
    local_pivot_arm.y /= obj_b.scale.y
    local_pivot_arm.z /= obj_b.scale.z
    
    constraint.pivot_type = 'LOCAL'
    constraint.pivot_x = local_pivot_support.x
    constraint.pivot_y = local_pivot_support.y
    constraint.pivot_z = local_pivot_support.z
    
    constraint.axis = axis
    
    # Clean up empty
    bpy.ops.object.select_all(action='DESELECT')
    empty.select_set(True)
    bpy.ops.object.delete()

# Add hinges
add_motor_hinge(support1, arm1, mathutils.Vector(hinge1_point))
add_motor_hinge(support2, arm2, mathutils.Vector(hinge2_point))

# 9. Simulation settings
scene = bpy.context.scene
scene.frame_end = total_frames
scene.rigidbody_world.enabled = True
scene.rigidbody_world.time_scale = 1.0
scene.rigidbody_world.steps_per_second = 60
scene.rigidbody_world.solver_iterations = 50

print(f"Dual-arm catapult created. Simulation will run for {total_frames} frames.")
print(f"Projectiles must travel >12m from start. Initial positions: {proj1_center}, {proj2_center}")