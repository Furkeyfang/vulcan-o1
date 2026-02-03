import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Parameters from summary
radius = 0.5
height = 2.0
base_loc = (0.0, 2.0, 5.0)
center_loc = (0.0, 2.0, 6.0)  # Because cylinder origin is at its center
rotation_rad = math.radians(120.0)  # Convert 120 degrees to radians

# Create cylinder primitive (default origin at center)
bpy.ops.mesh.primitive_cylinder_add(
    vertices=32,
    radius=radius,
    depth=height,
    location=center_loc
)
cylinder = bpy.context.active_object
cylinder.name = "Target_Cylinder"

# Apply rotation about Z-axis
cylinder.rotation_euler = (0, 0, rotation_rad)

# Verify location: the base should now be at (0,2,5)
# Note: After rotation, the base is still at the same height relative to the center.
# Since we rotated about Z, the base plane remains perpendicular to Z, so the base location is unchanged.

# Optional: Add a passive rigid body if physics is needed later (not required by task)
# bpy.ops.rigidbody.object_add()
# cylinder.rigid_body.type = 'PASSIVE'

# For clarity, print the location and rotation
print(f"Cylinder created at world location: {cylinder.location}")
print(f"Cylinder rotation (radians): {cylinder.rotation_euler}")