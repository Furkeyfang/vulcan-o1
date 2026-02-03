import bpy
import math

# Clear existing objects (optional, but good practice for clean scene)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create cylinder with specified dimensions
bpy.ops.mesh.primitive_cylinder_add(
    vertices=32,  # Default resolution
    radius=2.5,
    depth=1.5,    # Blender uses 'depth' for cylinder height
    location=(5.0, 5.0, -5.0),
    rotation=(0.0, math.radians(90.0), 0.0)  # Convert 90° to radians for Y-rotation
)

# Get reference to the created cylinder
cylinder = bpy.context.active_object
cylinder.name = "TargetCylinder"

# Optional: Add material for better visibility
material = bpy.data.materials.new(name="CylinderMaterial")
material.diffuse_color = (0.8, 0.2, 0.2, 1.0)  # Red color
cylinder.data.materials.append(material)

# Optional: Adjust 3D view to see the cylinder at negative Z
for area in bpy.context.screen.areas:
    if area.type == 'VIEW_3D':
        for space in area.spaces:
            if space.type == 'VIEW_3D':
                space.region_3d.view_location = (5.0, 5.0, 0.0)  # Center view
                space.region_3d.view_distance = 15.0  # Zoom out
                break