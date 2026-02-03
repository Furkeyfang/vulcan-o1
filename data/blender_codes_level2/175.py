import bpy
import math
from mathutils import Vector, Matrix

# Clear existing scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Parameters from summary
L = 10.0
leg_w = 1.0
leg_d = 1.0
leg_h = 20.0
cbeam_len = 10.0
cbeam_w = 0.5
cbeam_h = 0.5
col_w = 1.0
col_d = 1.0
col_h = 22.0
R = L / math.sqrt(3)
struct_mass = 100.0
ground_mass = 10000.0
load_mass = 1000.0

# Vertex coordinates (at ground level)
vertices = [
    Vector((R, 0.0, 0.0)),
    Vector((R * math.cos(math.radians(120)), R * math.sin(math.radians(120)), 0.0)),
    Vector((R * math.cos(math.radians(240)), R * math.sin(math.radians(240)), 0.0))
]

# Create ground plane
bpy.ops.mesh.primitive_plane_add(size=50, location=(0,0,0))
ground = bpy.context.active_object
ground.name = "Ground"
bpy.ops.rigidbody.object_add()
ground.rigid_body.type = 'PASSIVE'
ground.rigid_body.mass = ground_mass
ground.rigid_body.collision_shape = 'BOX'

# Create three legs
legs = []
for i, v in enumerate(vertices):
    bpy.ops.mesh.primitive_cube_add(size=1, location=(v.x, v.y, leg_h/2))
    leg = bpy.context.active_object
    leg.name = f"Leg_{i+1}"
    leg.scale = (leg_w, leg_d, leg_h)
    bpy.ops.rigidbody.object_add()
    leg.rigid_body.type = 'ACTIVE'
    leg.rigid_body.mass = struct_mass
    leg.rigid_body.collision_shape = 'BOX'
    legs.append(leg)

# Create three crossbeams at top (Z=20)
crossbeams = []
# Connection pairs: (0,1), (1,2), (2,0)
pairs = [(0,1), (1,2), (2,0)]
for i, (a_idx, b_idx) in enumerate(pairs):
    # Midpoint between two vertices at Z=20
    mid = (vertices[a_idx] + vertices[b_idx]) / 2
    mid.z = leg_h  # Top of legs
    
    # Direction vector between vertices
    dir_vec = vertices[b_idx] - vertices[a_idx]
    angle = math.atan2(dir_vec.y, dir_vec.x)
    
    bpy.ops.mesh.primitive_cube_add(size=1, location=mid)
    beam = bpy.context.active_object
    beam.name = f"Crossbeam_{i+1}"
    beam.scale = (cbeam_len, cbeam_w, cbeam_h)
    beam.rotation_euler = (0, 0, angle)
    bpy.ops.rigidbody.object_add()
    beam.rigid_body.type = 'ACTIVE'
    beam.rigid_body.mass = struct_mass
    beam.rigid_body.collision_shape = 'BOX'
    crossbeams.append(beam)

# Create central column
bpy.ops.mesh.primitive_cube_add(size=1, location=(0,0,col_h/2))
column = bpy.context.active_object
column.name = "Central_Column"
column.scale = (col_w, col_d, col_h)
bpy.ops.rigidbody.object_add()
column.rigid_body.type = 'ACTIVE'
column.rigid_body.mass = struct_mass
column.rigid_body.collision_shape = 'BOX'

# Create load point (visual indicator and mass)
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.5, location=(0,0,col_h))
load = bpy.context.active_object
load.name = "Load_Point"
bpy.ops.rigidbody.object_add()
load.rigid_body.type = 'ACTIVE'
load.rigid_body.mass = load_mass
load.rigid_body.collision_shape = 'SPHERE'

# Create FIXED constraints
def create_fixed_constraint(obj1, obj2, name):
    # Create empty for constraint
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=obj1.location)
    constraint = bpy.context.active_object
    constraint.name = name
    
    # Setup rigid body constraint
    bpy.ops.rigidbody.constraint_add()
    rb_const = constraint.rigid_body_constraint
    rb_const.type = 'FIXED'
    rb_const.object1 = obj1
    rb_const.object2 = obj2

# Fix legs to ground
for i, leg in enumerate(legs):
    create_fixed_constraint(leg, ground, f"Leg{i+1}_Ground_Fix")

# Fix crossbeams to legs (each beam connects two legs)
for i, beam in enumerate(crossbeams):
    a_idx, b_idx = pairs[i]
    create_fixed_constraint(beam, legs[a_idx], f"Beam{i+1}_Leg{a_idx+1}_Fix")
    create_fixed_constraint(beam, legs[b_idx], f"Beam{i+1}_Leg{b_idx+1}_Fix")

# Fix column to all three crossbeams
for i, beam in enumerate(crossbeams):
    create_fixed_constraint(column, beam, f"Column_Beam{i+1}_Fix")

# Fix load to column top
create_fixed_constraint(load, column, "Load_Column_Fix")

# Setup simulation parameters
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 50
bpy.context.scene.frame_end = 500