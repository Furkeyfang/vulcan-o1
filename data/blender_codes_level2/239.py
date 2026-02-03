import bpy
import mathutils

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Parameters from summary
cube_xy = 2.0
cube_z = 0.2
spacing = 0.0
grid_count = 5
roof_width = 10.0
roof_bottom_z = 5.0
steel_cube_mass = 80.0
skylight_xy = 2.0
skylight_z = 0.05
skylight_mass = 10.0
column_radius = 0.3
column_height = 5.0
ground_size = 20.0

# Compute steel cube centers
steel_cube_centers = []
for i in range(grid_count):
    for j in range(grid_count):
        x = -roof_width/2 + cube_xy/2 + i * cube_xy
        y = -roof_width/2 + cube_xy/2 + j * cube_xy
        z = roof_bottom_z + cube_z/2  # Center Z
        steel_cube_centers.append((x, y, z))

# Skylight centers (at four central intersections)
skylight_centers = [(1,1), (1,-1), (-1,1), (-1,-1)]

# Column centers (at roof corners)
column_centers = [
    (-roof_width/2, -roof_width/2, column_height/2),
    (-roof_width/2,  roof_width/2, column_height/2),
    ( roof_width/2, -roof_width/2, column_height/2),
    ( roof_width/2,  roof_width/2, column_height/2)
]

# Create ground plane
bpy.ops.mesh.primitive_plane_add(size=ground_size, location=(0,0,0))
ground = bpy.context.active_object
ground.name = "Ground"
bpy.ops.rigidbody.object_add()
ground.rigid_body.type = 'PASSIVE'

# Create steel cubes
steel_cubes = []
for center in steel_cube_centers:
    bpy.ops.mesh.primitive_cube_add(size=1, location=center)
    cube = bpy.context.active_object
    cube.scale = (cube_xy, cube_xy, cube_z)
    bpy.ops.rigidbody.object_add()
    cube.rigid_body.mass = steel_cube_mass
    steel_cubes.append(cube)

# Create skylights
skylights = []
for center in skylight_centers:
    x, y = center
    z = roof_bottom_z + cube_z - skylight_z/2  # Flush with top of steel cubes
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x, y, z))
    skylight = bpy.context.active_object
    skylight.scale = (skylight_xy, skylight_xy, skylight_z)
    # Assign transparent material (optional, for visualization)
    mat = bpy.data.materials.new(name="SkylightMaterial")
    mat.use_nodes = True
    mat.node_tree.nodes["Principled BSDF"].inputs['Base Color'].default_value = (0.8, 0.9, 1.0, 0.5)
    mat.blend_method = 'BLEND'
    skylight.data.materials.append(mat)
    bpy.ops.rigidbody.object_add()
    skylight.rigid_body.mass = skylight_mass
    skylights.append(skylight)

# Create columns
columns = []
for center in column_centers:
    bpy.ops.mesh.primitive_cylinder_add(radius=column_radius, depth=column_height, location=center)
    column = bpy.context.active_object
    column.rotation_euler = (0, 0, 0)  # Already aligned with Z
    bpy.ops.rigidbody.object_add()
    column.rigid_body.type = 'PASSIVE'
    columns.append(column)

# Function to add fixed constraint between two objects
def add_fixed_constraint(obj_a, obj_b):
    bpy.context.view_layer.objects.active = obj_a
    bpy.ops.rigidbody.constraint_add()
    constraint = obj_a.constraints[-1]
    constraint.type = 'FIXED'
    constraint.object1 = obj_a
    constraint.object2 = obj_b

# Connect steel cubes in grid (adjacent in X and Y directions)
cube_grid = {}
for idx, center in enumerate(steel_cube_centers):
    i = idx // grid_count
    j = idx % grid_count
    cube_grid[(i, j)] = steel_cubes[idx]

for i in range(grid_count):
    for j in range(grid_count):
        cube = cube_grid[(i, j)]
        # Right neighbor
        if i + 1 < grid_count:
            neighbor = cube_grid[(i+1, j)]
            add_fixed_constraint(cube, neighbor)
        # Above neighbor
        if j + 1 < grid_count:
            neighbor = cube_grid[(i, j+1)]
            add_fixed_constraint(cube, neighbor)

# Connect skylights to surrounding steel cubes
for skylight in skylights:
    x, y, z = skylight.location
    # Find surrounding steel cubes (centers at ±1 in X and Y)
    for dx in [-1, 1]:
        for dy in [-1, 1]:
            target_center = (x + dx, y + dy, roof_bottom_z + cube_z/2)
            # Find the steel cube at this center
            for cube in steel_cubes:
                if (mathutils.Vector(cube.location) - mathutils.Vector(target_center)).length < 0.001:
                    add_fixed_constraint(skylight, cube)
                    break

# Connect columns to ground and to corner steel cubes
corner_cube_centers = [(-4, -4), (-4, 4), (4, -4), (4, 4)]
for column, corner_center in zip(columns, corner_cube_centers):
    # Connect column to ground
    add_fixed_constraint(column, ground)
    # Connect column to corner steel cube
    for cube in steel_cubes:
        if abs(cube.location.x - corner_center[0]) < 0.001 and abs(cube.location.y - corner_center[1]) < 0.001:
            add_fixed_constraint(column, cube)
            break

# Set rigid body world settings (gravity)
bpy.context.scene.rigidbody_world.gravity.z = -9.81