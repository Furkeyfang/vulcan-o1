import bpy
import math
from mathutils import Vector

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Extract parameters
mast_height = 20.0
mast_radius = 0.5
lean_angle_deg = 4.0
lean_angle_rad = math.radians(lean_angle_deg)
base_size = (4.0, 4.0, 0.5)
base_top_z = 0.25
mast_top_x = mast_height * math.sin(lean_angle_rad)
mast_top_z = base_top_z + mast_height * math.cos(lean_angle_rad)
cube_size = 0.5
cube_mass = 200.0
cube_z = mast_top_z + cube_size/2
wire_radius = 0.05
wire_length = 15.0
corner_positions = [
    (2.0, 2.0, base_top_z),
    (2.0, -2.0, base_top_z),
    (-2.0, 2.0, base_top_z),
    (-2.0, -2.0, base_top_z)
]

# Create base platform
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0))
base = bpy.context.active_object
base.name = "BasePlatform"
base.scale = (base_size[0], base_size[1], base_size[2])
bpy.ops.rigidbody.object_add()
base.rigid_body.type = 'PASSIVE'

# Create mast (cylinder)
bpy.ops.mesh.primitive_cylinder_add(
    vertices=32,
    radius=mast_radius,
    depth=mast_height,
    location=(0, 0, base_top_z)
)
mast = bpy.context.active_object
mast.name = "Mast"
mast.rotation_euler = (0, lean_angle_rad, 0)  # Rotate around Y-axis
bpy.ops.rigidbody.object_add()
mast.rigid_body.type = 'ACTIVE'
mast.rigid_body.mass = 100.0  # Estimated mass for stability

# Create load cube
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(mast_top_x, 0, cube_z))
load = bpy.context.active_object
load.name = "LoadCube"
load.scale = (cube_size, cube_size, cube_size)
bpy.ops.rigidbody.object_add()
load.rigid_body.type = 'ACTIVE'
load.rigid_body.mass = cube_mass

# Create guy wires
wires = []
for i, corner in enumerate(corner_positions):
    # Calculate vector from mast top to corner
    start = Vector((mast_top_x, 0, mast_top_z))
    end = Vector(corner)
    direction = end - start
    distance = direction.length
    
    # Create wire cylinder at midpoint
    mid_point = (start + end) / 2
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=16,
        radius=wire_radius,
        depth=distance,
        location=mid_point
    )
    wire = bpy.context.active_object
    wire.name = f"GuyWire_{i+1}"
    
    # Orient cylinder to point from start to end
    wire.rotation_euler = (0, 0, 0)  # Reset
    up = Vector((0, 0, 1))
    rot_axis = up.cross(direction.normalized())
    rot_angle = up.angle(direction.normalized())
    if rot_axis.length > 0:
        wire.rotation_mode = 'AXIS_ANGLE'
        wire.rotation_axis_angle = (rot_angle, rot_axis.x, rot_axis.y, rot_axis.z)
    
    bpy.ops.rigidbody.object_add()
    wire.rigid_body.type = 'ACTIVE'
    wire.rigid_body.mass = 5.0  # Light wire mass
    wires.append(wire)

# Add fixed constraints
# Mast to Base
bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, base_top_z))
constraint_empty = bpy.context.active_object
constraint_empty.name = "MastBase_Constraint"
bpy.ops.rigidbody.constraint_add()
constraint_empty.rigid_body_constraint.type = 'FIXED'
constraint_empty.rigid_body_constraint.object1 = base
constraint_empty.rigid_body_constraint.object2 = mast

# Load to Mast
bpy.ops.object.empty_add(type='PLAIN_AXES', location=(mast_top_x, 0, mast_top_z))
constraint_empty2 = bpy.context.active_object
constraint_empty2.name = "LoadMast_Constraint"
bpy.ops.rigidbody.constraint_add()
constraint_empty2.rigid_body_constraint.type = 'FIXED'
constraint_empty2.rigid_body_constraint.object1 = mast
constraint_empty2.rigid_body_constraint.object2 = load

# Guy wire constraints (top to mast, bottom to base corners)
for i, (wire, corner) in enumerate(zip(wires, corner_positions)):
    # Top constraint (wire to mast)
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(mast_top_x, 0, mast_top_z))
    top_constraint = bpy.context.active_object
    top_constraint.name = f"WireTop_Constraint_{i+1}"
    bpy.ops.rigidbody.constraint_add()
    top_constraint.rigid_body_constraint.type = 'FIXED'
    top_constraint.rigid_body_constraint.object1 = mast
    top_constraint.rigid_body_constraint.object2 = wire
    
    # Bottom constraint (wire to base corner)
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=corner)
    bottom_constraint = bpy.context.active_object
    bottom_constraint.name = f"WireBottom_Constraint_{i+1}"
    bpy.ops.rigidbody.constraint_add()
    bottom_constraint.rigid_body_constraint.type = 'FIXED'
    bottom_constraint.rigid_body_constraint.object1 = base
    bottom_constraint.rigid_body_constraint.object2 = wire

# Set up physics world
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 50
bpy.context.scene.frame_end = 500

print(f"Mast top position: ({mast_top_x:.3f}, 0, {mast_top_z:.3f})")
print(f"Load position: ({mast_top_x:.3f}, 0, {cube_z:.3f})")
print("Structure created with fixed constraints")