import bpy
import mathutils

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Physics setup
bpy.context.scene.use_gravity = True
bpy.context.scene.gravity = (0, 0, -9.81)
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 10

# Create ground plane (passive rigid body)
bpy.ops.mesh.primitive_plane_add(size=20.0, location=(0, 0, -3.0))
ground = bpy.context.active_object
bpy.ops.rigidbody.object_add()
ground.rigid_body.type = 'PASSIVE'
ground.name = "Ground"

# Create canopy cubes
cube_objects = []
for i, cx in enumerate([-2.0, 0.0, 2.0]):
    for j, cy in enumerate([-2.0, 0.0, 2.0]):
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(cx, cy, 0.25))
        cube = bpy.context.active_object
        cube.scale = (2.0, 2.0, 0.5)
        cube.name = f"CanopyCube_{i}_{j}"
        bpy.ops.rigidbody.object_add()
        cube.rigid_body.type = 'ACTIVE'
        cube.rigid_body.mass = 166.666667
        cube.rigid_body.collision_shape = 'BOX'
        cube.rigid_body.friction = 0.5
        cube.rigid_body.restitution = 0.1
        cube_objects.append(cube)

# Create pillars
pillar_objects = []
pillar_locs = [(-3.0, -3.0), (-3.0, 3.0), (3.0, -3.0), (3.0, 3.0)]
for idx, (px, py) in enumerate(pillar_locs):
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=32,
        radius=0.3,
        depth=3.0,
        location=(px, py, -1.5)
    )
    pillar = bpy.context.active_object
    pillar.name = f"Pillar_{idx}"
    bpy.ops.rigidbody.object_add()
    pillar.rigid_body.type = 'ACTIVE'
    pillar.rigid_body.mass = 100.0  # Additional pillar mass
    pillar.rigid_body.collision_shape = 'CYLINDER'
    pillar_objects.append(pillar)

# Add fixed constraints between adjacent cubes
for i, cube in enumerate(cube_objects):
    cx, cy, cz = cube.location
    # Find right neighbor
    for other in cube_objects:
        ox, oy, oz = other.location
        if abs(ox - cx - 2.0) < 0.1 and abs(oy - cy) < 0.1:  # Right neighbor
            bpy.ops.object.select_all(action='DESELECT')
            cube.select_set(True)
            other.select_set(True)
            bpy.context.view_layer.objects.active = cube
            bpy.ops.rigidbody.constraint_add()
            constraint = bpy.context.active_object
            constraint.rigid_body_constraint.type = 'FIXED'
            constraint.rigid_body_constraint.object1 = cube
            constraint.rigid_body_constraint.object2 = other
            constraint.rigid_body_constraint.use_breaking = True
            constraint.rigid_body_constraint.breaking_threshold = 1000.0
        # Find front neighbor
        if abs(oy - cy - 2.0) < 0.1 and abs(ox - cx) < 0.1:  # Front neighbor
            bpy.ops.object.select_all(action='DESELECT')
            cube.select_set(True)
            other.select_set(True)
            bpy.context.view_layer.objects.active = cube
            bpy.ops.rigidbody.constraint_add()
            constraint = bpy.context.active_object
            constraint.rigid_body_constraint.type = 'FIXED'
            constraint.rigid_body_constraint.object1 = cube
            constraint.rigid_body_constraint.object2 = other
            constraint.rigid_body_constraint.use_breaking = True
            constraint.rigid_body_constraint.breaking_threshold = 1000.0

# Connect pillars to corner cubes and ground
corner_cubes = [cube_objects[0], cube_objects[2], cube_objects[6], cube_objects[8]]  # Indices: (0,0), (0,2), (2,0), (2,2)
for pillar, corner_cube in zip(pillar_objects, corner_cubes):
    # Pillar to cube constraint
    bpy.ops.object.select_all(action='DESELECT')
    pillar.select_set(True)
    corner_cube.select_set(True)
    bpy.context.view_layer.objects.active = pillar
    bpy.ops.rigidbody.constraint_add()
    constraint = bpy.context.active_object
    constraint.location = (pillar.location.x, pillar.location.y, 0.0)  # Connection point
    constraint.rigid_body_constraint.type = 'FIXED'
    constraint.rigid_body_constraint.object1 = pillar
    constraint.rigid_body_constraint.object2 = corner_cube
    constraint.rigid_body_constraint.use_breaking = True
    constraint.rigid_body_constraint.breaking_threshold = 1000.0
    
    # Pillar to ground constraint
    bpy.ops.object.select_all(action='DESELECT')
    pillar.select_set(True)
    ground.select_set(True)
    bpy.context.view_layer.objects.active = pillar
    bpy.ops.rigidbody.constraint_add()
    constraint = bpy.context.active_object
    constraint.location = (pillar.location.x, pillar.location.y, -3.0)  # Base connection
    constraint.rigid_body_constraint.type = 'FIXED'
    constraint.rigid_body_constraint.object1 = pillar
    constraint.rigid_body_constraint.object2 = ground
    constraint.rigid_body_constraint.use_breaking = True
    constraint.rigid_body_constraint.breaking_threshold = 1000.0

# Set simulation length
bpy.context.scene.frame_end = 500

# Bake physics simulation (headless compatible)
bpy.ops.ptcache.bake_all(bake=True)