import bpy
import math

# Clear existing scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=True)

# Create unit cube at origin
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, 0.0, 0.0))
cube = bpy.context.active_object
cube.name = "RotatedCube"

# Apply 30° rotation around X-axis
rotation_rad = math.radians(30.0)
cube.rotation_euler = (rotation_rad, 0.0, 0.0)

# Update mesh data to apply transformation
bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)

# Set visual properties for clarity
mat = bpy.data.materials.new(name="CubeMaterial")
mat.diffuse_color = (0.8, 0.2, 0.2, 1.0)  # Red color
cube.data.materials.append(mat)

# Set up viewport for visualization
for area in bpy.context.screen.areas:
    if area.type == 'VIEW_3D':
        area.spaces[0].region_3d.view_location = (0, 0, 0)
        area.spaces[0].region_3d.view_distance = 5
        area.spaces[0].region_3d.view_rotation.rotate(math.radians(45), math.radians(45), 0)
        break

print(f"Cube created at {cube.location}")
print(f"Cube rotation (degrees): {math.degrees(cube.rotation_euler.x):.1f}, {math.degrees(cube.rotation_euler.y):.1f}, {math.degrees(cube.rotation_euler.z):.1f}")