import bpy
import mathutils

# Clear scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Parameters from summary
platform_depth = 2.0
platform_width = 3.0
platform_thickness = 0.3
cube_x = 1.0
cube_y = 1.0
cube_z = 0.3
num_x = 2
num_y = 3
railing_height = 1.0
front_railing_thickness = 0.05
side_railing_thickness = 0.05
front_railing_width = 3.0
side_railing_depth = 2.0
wall_size = (0.5, 4.0, 4.0)
wall_location = (-0.25, 0.0, 2.0)  # Wall center at X=-0.25 so its front face is at X=0
load_mass = 200.0
gravity = 9.81
total_force = load_mass * gravity
force_per_cube = total_force / (num_x * num_y)
simulation_steps = 100

# Create wall (passive rigid body)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=wall_location)
wall = bpy.context.active_object
wall.name = "Wall"
wall.scale = wall_size
bpy.ops.rigidbody.object_add()
wall.rigid_body.type = 'PASSIVE'

# Create platform cubes
platform_cubes = []
for i in range(num_x):
    for j in range(num_y):
        x = i * cube_x + cube_x / 2.0
        y = j * cube_y - (platform_width / 2.0) + cube_y / 2.0
        z = cube_z / 2.0  # Top of cube at Z=cube_z
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(x, y, z))
        cube = bpy.context.active_object
        cube.name = f"PlatformCube_{i}_{j}"
        cube.scale = (cube_x, cube_y, cube_z)
        bpy.ops.rigidbody.object_add()
        cube.rigid_body.type = 'ACTIVE'
        cube.rigid_body.mass = 720.0  # Density of concrete ~2400 kg/m³ * volume (1*1*0.3)
        platform_cubes.append(cube)

# Create front railing
front_x = platform_depth - front_railing_thickness / 2.0
front_z = platform_thickness + railing_height / 2.0
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(front_x, 0.0, front_z))
front_railing = bpy.context.active_object
front_railing.name = "FrontRailing"
front_railing.scale = (front_railing_thickness, front_railing_width, railing_height)
front_railing.active_material = bpy.data.materials.new(name="Glass")
front_railing.active_material.diffuse_color = (0.8, 0.9, 1.0, 0.5)  # Semi-transparent blue
bpy.ops.rigidbody.object_add()
front_railing.rigid_body.type = 'ACTIVE'
front_railing.rigid_body.mass = 12.5  # Glass density ~2500 kg/m³ * volume (0.05*3*1)

# Create left side railing
left_y = -platform_width / 2.0 + side_railing_thickness / 2.0
side_x = platform_depth / 2.0
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(side_x, left_y, front_z))
left_railing = bpy.context.active_object
left_railing.name = "LeftRailing"
left_railing.scale = (side_railing_depth, side_railing_thickness, railing_height)
left_railing.active_material = front_railing.active_material.copy()
bpy.ops.rigidbody.object_add()
left_railing.rigid_body.type = 'ACTIVE'
left_railing.rigid_body.mass = 12.5

# Create right side railing
right_y = platform_width / 2.0 - side_railing_thickness / 2.0
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(side_x, right_y, front_z))
right_railing = bpy.context.active_object
right_railing.name = "RightRailing"
right_railing.scale = (side_railing_depth, side_railing_thickness, railing_height)
right_railing.active_material = front_railing.active_material.copy()
bpy.ops.rigidbody.object_add()
right_railing.rigid_body.type = 'ACTIVE'
right_railing.rigid_body.mass = 12.5

# Function to add fixed constraint between two objects
def add_fixed_constraint(obj_a, obj_b):
    bpy.ops.rigidbody.constraint_add()
    constraint = bpy.context.active_object
    constraint.name = f"Fixed_{obj_a.name}_{obj_b.name}"
    constraint.rigid_body_constraint.type = 'FIXED'
    constraint.rigid_body_constraint.object1 = obj_a
    constraint.rigid_body_constraint.object2 = obj_b

# Add constraints between wall and inner platform cubes (i=0)
inner_cubes = [cube for cube in platform_cubes if cube.location.x == 0.5]  # i=0 -> x=0.5
for cube in inner_cubes:
    add_fixed_constraint(wall, cube)

# Add constraints between adjacent platform cubes
for i in range(num_x):
    for j in range(num_y):
        idx = i * num_y + j
        cube = platform_cubes[idx]
        # Right neighbor (next i)
        if i + 1 < num_x:
            neighbor = platform_cubes[(i + 1) * num_y + j]
            add_fixed_constraint(cube, neighbor)
        # Above neighbor (next j)
        if j + 1 < num_y:
            neighbor = platform_cubes[i * num_y + (j + 1)]
            add_fixed_constraint(cube, neighbor)

# Attach front railing to outer platform cubes (i=1)
outer_cubes = [cube for cube in platform_cubes if cube.location.x == 1.5]  # i=1 -> x=1.5
for cube in outer_cubes:
    add_fixed_constraint(cube, front_railing)

# Attach side railings to side platform cubes
left_side_cubes = [cube for cube in platform_cubes if abs(cube.location.y - (-1.0)) < 0.01]  # j=0 -> y=-1.0
right_side_cubes = [cube for cube in platform_cubes if abs(cube.location.y - 1.0) < 0.01]   # j=2 -> y=1.0
for cube in left_side_cubes:
    add_fixed_constraint(cube, left_railing)
for cube in right_side_cubes:
    add_fixed_constraint(cube, right_railing)

# Apply distributed load as downward forces on each platform cube
for cube in platform_cubes:
    # Add a force field (downward) at each cube's center
    bpy.ops.object.effector_add(type='FORCE', location=cube.location)
    force = bpy.context.active_object
    force.name = f"Force_{cube.name}"
    force.field.strength = -force_per_cube  # Negative for downward
    force.field.use_max_distance = True
    force.field.distance_max = 0.1  # Only affect nearby objects (the cube itself)

# Set gravity
bpy.context.scene.use_gravity = True
bpy.context.scene.gravity = (0.0, 0.0, -gravity)

# Run simulation briefly to verify stability
bpy.context.scene.frame_end = simulation_steps
bpy.ops.ptcache.bake_all(bake=True)

# Verification: Check that all objects have not moved significantly
print("Simulation complete. Checking final positions...")
for obj in platform_cubes + [front_railing, left_railing, right_railing]:
    initial_loc = obj.matrix_world.translation.copy()
    obj.keyframe_insert(data_path="location", frame=1)
    obj.keyframe_insert(data_path="location", frame=simulation_steps)
    final_loc = obj.matrix_world.translation
    displacement = (final_loc - initial_loc).length
    if displacement > 0.001:
        print(f"Warning: {obj.name} moved by {displacement:.6f} m")
    else:
        print(f"{obj.name} stable (displacement {displacement:.6f} m)")

# Overhang verification
outermost_cube = max(platform_cubes, key=lambda c: c.location.x)
overhang = outermost_cube.location.x + cube_x / 2.0  # Outer edge X coordinate
print(f"Overhang from wall (X=0): {overhang:.2f} meters")