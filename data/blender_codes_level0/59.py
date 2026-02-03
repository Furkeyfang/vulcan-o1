import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create cylinder with specified parameters
bpy.ops.mesh.primitive_cylinder_add(
    vertices=32,
    radius=1.3,
    depth=2.7,
    location=(4.0, 1.0, 5.0),
    rotation=(0.610865, 0.0, 0.0)  # 35° in radians about X-axis
)

# Get reference to created cylinder
cylinder = bpy.context.active_object
cylinder.name = "Target_Cylinder"

# Apply smooth shading for better visual representation
bpy.ops.object.shade_smooth()

# Optional: Add subdivision surface modifier for higher mesh resolution
subdiv = cylinder.modifiers.new(name="Subdivision", type='SUBSURF')
subdiv.levels = 2
subdiv.render_levels = 2

# Update scene
bpy.context.view_layer.update()