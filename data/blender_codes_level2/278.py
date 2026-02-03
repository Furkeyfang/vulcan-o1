import bpy
import mathutils

# Clear scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Physics setup
bpy.context.scene.gravity = (0, 0, -9.81)
bpy.context.scene.rigidbody_world.steps_per_second = 250
bpy.context.scene.rigidbody_world.solver_iterations = 50

# Parameters
levels = 4
platform_dim = (5.0, 2.0, 0.1)
beam_dim = (0.5, 0.5, 3.0)
overhang_offset = 2.5
back_edge_y = -1.0
platform_mass = 200.0
beam_mass = 0.0

# Pre-calculated coordinates from spatial layout
beam_centers = [
    (0.0, back_edge_y, 1.5),
    (2.5, back_edge_y, 4.5),
    (5.0, back_edge_y, 7.5),
    (7.5, back_edge_y, 10.5)
]
platform_centers = [
    (0.0, 0.0, 0.0),
    (2.5, 0.0, 3.0),
    (5.0, 0.0, 6.0),
    (7.5, 0.0, 9.0)
]

# Helper function to create fixed constraint
def create_fixed_constraint(obj1, obj2):
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=obj1.location)
    empty = bpy.context.active_object
    empty.empty_display_size = 0.5
    bpy.ops.rigidbody.constraint_add()
    constraint = empty.rigid_body_constraint
    constraint.type = 'FIXED'
    constraint.object1 = obj1
    constraint.object2 = obj2

# Create structure
prev_beam = None
for i in range(levels):
    # Create platform
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=platform_centers[i])
    platform = bpy.context.active_object
    platform.name = f"Platform_{i+1}"
    platform.scale = platform_dim
    bpy.ops.rigidbody.object_add()
    platform.rigid_body.type = 'ACTIVE'
    platform.rigid_body.mass = platform_mass
    platform.rigid_body.collision_shape = 'BOX'
    
    # Create beam
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=beam_centers[i])
    beam = bpy.context.active_object
    beam.name = f"Beam_{i+1}"
    beam.scale = beam_dim
    bpy.ops.rigidbody.object_add()
    
    if i == 0:
        # Base beam fixed to ground
        beam.rigid_body.type = 'PASSIVE'
    else:
        beam.rigid_body.type = 'ACTIVE'
        beam.rigid_body.mass = beam_mass
        # Constrain to previous beam
        create_fixed_constraint(beam, prev_beam)
    
    beam.rigid_body.collision_shape = 'BOX'
    
    # Constrain platform to its beam
    create_fixed_constraint(platform, beam)
    
    prev_beam = beam

# Verify final platform position
final_platform = bpy.data.objects.get("Platform_4")
if final_platform:
    print(f"Final platform location: {final_platform.location}")
    expected = mathutils.Vector((7.5, 0.0, 9.0))
    if (final_platform.location - expected).length < 0.01:
        print("✓ Top platform positioned correctly")
    else:
        print("✗ Position mismatch")