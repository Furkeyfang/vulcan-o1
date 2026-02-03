import bpy
import mathutils
from math import sqrt, atan2, acos

# Clear scene
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

# Define variables from parameter summary
canopy_dim = (14.0, 6.0, 0.3)
canopy_center = (0.0, 0.0, 4.0)
pillar_short_pos = (-5.0, 0.0, 0.0)
pillar_short_height = 3.0
pillar_short_radius = 0.2
pillar_tall_pos = (5.0, 0.0, 0.0)
pillar_tall_height = 5.0
pillar_tall_radius = 0.2
cable_radius = 0.1
cable_length_short = 5.0
cable_length_tall = 7.0
canopy_corners = [
    (-7.0, 3.0, 4.0),
    (-7.0, -3.0, 4.0),
    (7.0, 3.0, 4.0),
    (7.0, -3.0, 4.0)
]
pillar_tops = [
    (-5.0, 0.0, 3.0),   # for left front
    (-5.0, 0.0, 3.0),   # for left back
    (5.0, 0.0, 5.0),    # for right front
    (5.0, 0.0, 5.0)     # for right back
]
load_dim = (1.0, 1.0, 1.0)
load_mass = 600.0
load_center = (0.0, 0.0, 4.65)

# Function to create a cylinder between two points with given radius and length
def create_cable_between_points(start, end, radius, length, name):
    # Calculate direction vector
    dir_vec = mathutils.Vector(end) - mathutils.Vector(start)
    # Midpoint for location
    mid = (mathutils.Vector(start) + mathutils.Vector(end)) / 2
    # Create cylinder aligned with local Z
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=16,
        radius=radius,
        depth=length,
        location=mid
    )
    cable = bpy.context.active_object
    cable.name = name
    # Rotate cylinder to align with direction vector
    up = mathutils.Vector((0, 0, 1))
    rot = up.rotation_difference(dir_vec)
    cable.rotation_euler = rot.to_euler()
    return cable

# Create canopy platform
bpy.ops.mesh.primitive_cube_add(size=1, location=canopy_center)
canopy = bpy.context.active_object
canopy.name = "Canopy"
canopy.scale = canopy_dim
bpy.ops.rigidbody.object_add()
canopy.rigid_body.type = 'ACTIVE'
canopy.rigid_body.mass = 12600  # approximate mass from volume * density (500 kg/m³)

# Create pillars
# Short pillar
bpy.ops.mesh.primitive_cylinder_add(
    vertices=16,
    radius=pillar_short_radius,
    depth=pillar_short_height,
    location=(
        pillar_short_pos[0],
        pillar_short_pos[1],
        pillar_short_pos[2] + pillar_short_height / 2
    )
)
pillar_short = bpy.context.active_object
pillar_short.name = "Pillar_Short"
bpy.ops.rigidbody.object_add()
pillar_short.rigid_body.type = 'PASSIVE'

# Tall pillar
bpy.ops.mesh.primitive_cylinder_add(
    vertices=16,
    radius=pillar_tall_radius,
    depth=pillar_tall_height,
    location=(
        pillar_tall_pos[0],
        pillar_tall_pos[1],
        pillar_tall_pos[2] + pillar_tall_height / 2
    )
)
pillar_tall = bpy.context.active_object
pillar_tall.name = "Pillar_Tall"
bpy.ops.rigidbody.object_add()
pillar_tall.rigid_body.type = 'PASSIVE'

# Create cables
cable_names = ["Cable_LeftFront", "Cable_LeftBack", "Cable_RightFront", "Cable_RightBack"]
cables = []
for i, (corner, top) in enumerate(zip(canopy_corners, pillar_tops)):
    length = cable_length_short if i < 2 else cable_length_tall
    cable = create_cable_between_points(
        start=corner,
        end=top,
        radius=cable_radius,
        length=length,
        name=cable_names[i]
    )
    bpy.ops.rigidbody.object_add()
    cable.rigid_body.type = 'ACTIVE'
    cables.append(cable)

# Create central load block
bpy.ops.mesh.primitive_cube_add(size=1, location=load_center)
load = bpy.context.active_object
load.name = "Load"
load.scale = load_dim
bpy.ops.rigidbody.object_add()
load.rigid_body.type = 'ACTIVE'
load.rigid_body.mass = load_mass

# Add fixed constraints for pillars to ground
bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0,0,0))
empty = bpy.context.active_object
empty.name = "Fixed_Constraints"
for pillar in [pillar_short, pillar_tall]:
    bpy.ops.rigidbody.constraint_add(type='FIXED')
    const = bpy.context.active_object
    const.name = f"Fix_{pillar.name}"
    const.rigid_body_constraint.object1 = empty
    const.rigid_body_constraint.object2 = pillar
    const.rigid_body_constraint.use_breaking = False

# Add hinge constraints for cables
for i, cable in enumerate(cables):
    # Hinge at canopy corner
    bpy.ops.rigidbody.constraint_add(type='HINGE')
    hinge1 = bpy.context.active_object
    hinge1.name = f"Hinge_Canopy_{cable.name}"
    hinge1.rigid_body_constraint.object1 = canopy
    hinge1.rigid_body_constraint.object2 = cable
    hinge1.location = canopy_corners[i]
    # Hinge at pillar top
    bpy.ops.rigidbody.constraint_add(type='HINGE')
    hinge2 = bpy.context.active_object
    hinge2.name = f"Hinge_Pillar_{cable.name}"
    hinge2.rigid_body_constraint.object1 = cable
    hinge2.rigid_body_constraint.object2 = pillar_short if i < 2 else pillar_tall
    hinge2.location = pillar_tops[i]

# Set up rigid body world
bpy.context.scene.rigidbody_world.enabled = True
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 10
bpy.context.scene.frame_end = 500

print("Asymmetric suspension canopy structure created.")