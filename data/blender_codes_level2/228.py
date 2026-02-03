import bpy
import math
from mathutils import Vector

# Clear scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# ====================
# PARAMETERS
# ====================
span = 20.0
peak_height = 4.0
truss_width_y = 2.0
beam_cross = 0.2
conn_rad = 0.1
conn_dep = 0.2
bottom_z = 0.0
sup_left_x = -10.0
sup_right_x = 10.0
panel = 5.0

# Joint coordinates (X, Y, Z)
J0 = (sup_left_x, 0.0, bottom_z)
J1 = (-panel, 0.0, bottom_z)
J2 = (0.0, 0.0, bottom_z)
J3 = (panel, 0.0, bottom_z)
J4 = (sup_right_x, 0.0, bottom_z)
T1 = (-panel, 0.0, 2.0)
T2 = (panel, 0.0, 2.0)
PEAK = (0.0, 0.0, peak_height)

total_load = 23544.0
load_per_beam = total_load / 4.0  # 4 top chord beams
sim_frames = 100
max_deflect = 0.1

# ====================
# HELPER FUNCTIONS
# ====================
def create_beam_between(p1, p2, name):
    """Create a cuboid beam between two points with cross-section beam_cross x truss_width_y."""
    # Calculate length and direction
    v1 = Vector(p1)
    v2 = Vector(p2)
    length = (v2 - v1).length
    direction = (v2 - v1).normalized()
    
    # Create cube at midpoint
    mid = (v1 + v2) * 0.5
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=mid)
    beam = bpy.context.active_object
    beam.name = name
    
    # Scale: X=beam_cross (thickness in truss plane), Y=truss_width_y, Z=length
    beam.scale = (beam_cross, truss_width_y, length)
    
    # Rotate to align Z axis with beam direction
    # Default cube Z axis is (0,0,1) in local space
    up = Vector((0, 0, 1))
    rot_quat = up.rotation_difference(direction)
    beam.rotation_euler = rot_quat.to_euler()
    
    # Add rigid body (active by default)
    bpy.ops.rigidbody.object_add()
    return beam

def create_connector_at(pos, name):
    """Create cylindrical connector at position."""
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=16,
        radius=conn_rad,
        depth=conn_dep,
        location=pos
    )
    conn = bpy.context.active_object
    conn.name = name
    # Scale Y to match truss width
    conn.scale.y = truss_width_y / conn_dep
    # Rotate so cylinder axis is Y (for connection along width)
    conn.rotation_euler.x = math.pi / 2.0
    # Add rigid body
    bpy.ops.rigidbody.object_add()
    return conn

def add_fixed_constraint(obj_a, obj_b):
    """Add a fixed constraint between two objects."""
    bpy.context.view_layer.objects.active = obj_a
    bpy.ops.rigidbody.constraint_add()
    const = obj_a.constraints[-1]
    const.type = 'FIXED'
    const.object1 = obj_a
    const.object2 = obj_b

# ====================
# CREATE TRUSS MEMBERS
# ====================
# Joint connectors (all active initially)
connectors = {}
joints = [J0, J1, J2, J3, J4, T1, T2, PEAK]
joint_names = ['J0', 'J1', 'J2', 'J3', 'J4', 'T1', 'T2', 'PEAK']
for pos, name in zip(joints, joint_names):
    connectors[name] = create_connector_at(pos, f"Conn_{name}")

# Make support connectors passive
connectors['J0'].rigid_body.type = 'PASSIVE'
connectors['J4'].rigid_body.type = 'PASSIVE'

# Beams
beams = {}
# Bottom chord
beams['B0'] = create_beam_between(J0, J1, "Beam_J0-J1")
beams['B1'] = create_beam_between(J1, J2, "Beam_J1-J2")
beams['B2'] = create_beam_between(J2, J3, "Beam_J2-J3")
beams['B3'] = create_beam_between(J3, J4, "Beam_J3-J4")
# Top chord
beams['T0'] = create_beam_between(J0, T1, "Beam_J0-T1")
beams['T1'] = create_beam_between(T1, PEAK, "Beam_T1-Peak")
beams['T2'] = create_beam_between(PEAK, T2, "Beam_Peak-T2")
beams['T3'] = create_beam_between(T2, J4, "Beam_T2-J4")
# Diagonals
beams['D1'] = create_beam_between(J1, PEAK, "Beam_J1-Peak")
beams['D2'] = create_beam_between(J3, PEAK, "Beam_J3-Peak")
# Verticals
beams['V1'] = create_beam_between(J1, T1, "Beam_J1-T1")
beams['V2'] = create_beam_between(J3, T2, "Beam_J3-T2")

# ====================
# CREATE CONSTRAINTS
# ====================
# Connect each beam to its two end connectors
beam_connections = [
    ('B0', 'J0', 'J1'), ('B1', 'J1', 'J2'), ('B2', 'J2', 'J3'), ('B3', 'J3', 'J4'),
    ('T0', 'J0', 'T1'), ('T1', 'T1', 'PEAK'), ('T2', 'PEAK', 'T2'), ('T3', 'T2', 'J4'),
    ('D1', 'J1', 'PEAK'), ('D2', 'J3', 'PEAK'),
    ('V1', 'J1', 'T1'), ('V2', 'J3', 'T2')
]

for beam_name, conn1, conn2 in beam_connections:
    add_fixed_constraint(beams[beam_name], connectors[conn1])
    add_fixed_constraint(beams[beam_name], connectors[conn2])
    # Also connect the two connectors at each joint (redundant but ensures rigidity)
    add_fixed_constraint(connectors[conn1], connectors[conn2])

# ====================
# APPLY LOADS
# ====================
# Apply downward force to top chord beams
top_beams = [beams['T0'], beams['T1'], beams['T2'], beams['T3']]
for beam in top_beams:
    # Add force field (downward, negative Z)
    bpy.ops.object.forcefield_add(type='FORCE')
    ff = beam.force_fields[-1]
    ff.strength = -load_per_beam  # Negative for downward
    ff.falloff_power = 0  # Uniform
    ff.use_max_distance = True
    ff.distance_max = 10.0  # Enough to cover beam

# ====================
# SET UP RIGID BODY WORLD
# ====================
if bpy.context.scene.rigidbody_world is None:
    bpy.ops.rigidbody.world_add()
rw = bpy.context.scene.rigidbody_world
rw.time_scale = 1.0
rw.substeps_per_frame = 10
rw.solver_iterations = 10
rw.use_split_impulse = True

# ====================
# CREATE GROUND PLANE
# ====================
bpy.ops.mesh.primitive_plane_add(size=50.0, location=(0,0,-0.5))
ground = bpy.context.active_object
ground.name = "Ground"
bpy.ops.rigidbody.object_add()
ground.rigid_body.type = 'PASSIVE'

# ====================
# SIMULATION SETTINGS
# ====================
bpy.context.scene.frame_end = sim_frames
# Set gravity to standard (Z down)
rw.gravity = (0.0, 0.0, -9.81)

print("Truss construction complete. Simulation ready.")
print(f"Load applied: {total_load} N total, {load_per_beam} N per top beam.")
print(f"Run simulation with: bpy.ops.ptcache.bake_all(bake=True)")