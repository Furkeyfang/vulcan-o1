import bpy
import math
from mathutils import Vector

# Clear existing scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# ====================
# PARAMETERS
# ====================
# Foundation
foundation_side = 6.0
foundation_thickness = 0.5
foundation_vertices = [
    (0.0, 3.464, 0.0),
    (-3.0, -1.732, 0.0),
    (3.0, -1.732, 0.0)
]

# Columns
column_side = 0.5
column_height = 12.0
column_positions = [
    (0.0, 3.175, 0.0),
    (-2.75, -1.588, 0.0),
    (2.75, -1.588, 0.0)
]

# Deck
deck_side = 4.0
deck_thickness = 0.5
deck_center_z = 12.25
deck_vertices = [
    (0.0, 2.309, deck_center_z),
    (-2.0, -1.155, deck_center_z),
    (2.0, -1.155, deck_center_z)
]

# Ladder
rung_width = 0.2
rung_depth = 0.2
rung_height = 0.5
rung_spacing = 0.5
num_rungs = 23
first_rung_z = 0.25
ladder_column_index = 0

# Load
load_mass = 200.0
load_size = 1.0
load_position = (0.0, 0.0, 12.75)

# ====================
# UTILITY FUNCTIONS
# ====================
def create_triangle_prism(vertices, thickness, name):
    """Create triangular prism from 3 base vertices"""
    # Create mesh for triangle base
    mesh = bpy.data.meshes.new(name + "_mesh")
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    
    # Create vertices (top face)
    verts = []
    faces = []
    
    # Bottom face vertices
    for v in vertices:
        verts.append(Vector(v))
    
    # Top face vertices (shifted by thickness in Z)
    for v in vertices:
        verts.append(Vector((v[0], v[1], v[2] + thickness)))
    
    # Faces (triangles for sides and ends)
    # Bottom triangle
    faces.append((0, 1, 2))
    # Top triangle
    faces.append((3, 4, 5))
    # Side faces (quads)
    faces.append((0, 3, 4, 1))  # Side 1
    faces.append((1, 4, 5, 2))  # Side 2
    faces.append((2, 5, 3, 0))  # Side 3
    
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    
    return obj

def add_fixed_constraint(obj_a, obj_b):
    """Add fixed constraint between two objects"""
    bpy.context.view_layer.objects.active = obj_a
    bpy.ops.rigidbody.constraint_add()
    constraint = obj_a.rigid_body_constraint
    constraint.type = 'FIXED'
    constraint.object2 = obj_b

# ====================
# CREATE FOUNDATION
# ====================
foundation = create_triangle_prism(
    foundation_vertices, 
    foundation_thickness, 
    "Foundation"
)
foundation.location = (0, 0, foundation_thickness/2)  # Center thickness
bpy.ops.rigidbody.object_add()
foundation.rigid_body.type = 'PASSIVE'
foundation.rigid_body.collision_shape = 'MESH'

# ====================
# CREATE COLUMNS
# ====================
columns = []
for i, pos in enumerate(column_positions):
    bpy.ops.mesh.primitive_cube_add(size=1, location=pos)
    col = bpy.context.active_object
    col.name = f"Column_{i+1}"
    col.scale = (column_side, column_side, column_height)
    col.location.z += column_height/2  # Move up so base at ground
    bpy.ops.rigidbody.object_add()
    col.rigid_body.type = 'ACTIVE'
    col.rigid_body.mass = 500.0  # Heavy columns
    col.rigid_body.collision_shape = 'BOX'
    columns.append(col)
    
    # Fixed constraint to foundation
    add_fixed_constraint(col, foundation)

# ====================
# CREATE DECK
# ====================
deck = create_triangle_prism(deck_vertices, deck_thickness, "Deck")
deck.location.z = deck_center_z  # Already positioned in vertices
bpy.ops.rigidbody.object_add()
deck.rigid_body.type = 'ACTIVE'
deck.rigid_body.mass = 300.0  # Heavy deck
deck.rigid_body.collision_shape = 'MESH'

# Fix deck to all three columns
for col in columns:
    add_fixed_constraint(deck, col)

# ====================
# CREATE LADDER RUNGS
# ====================
ladder_column_pos = column_positions[ladder_column_index]
for i in range(num_rungs):
    z_pos = first_rung_z + i * rung_spacing
    bpy.ops.mesh.primitive_cube_add(
        size=1,
        location=(ladder_column_pos[0] + column_side/2 + rung_width/2,
                 ladder_column_pos[1],
                 z_pos)
    )
    rung = bpy.context.active_object
    rung.name = f"Rung_{i+1}"
    rung.scale = (rung_width, rung_depth, rung_height)
    bpy.ops.rigidbody.object_add()
    rung.rigid_body.type = 'ACTIVE'
    rung.rigid_body.mass = 5.0
    rung.rigid_body.collision_shape = 'BOX'
    
    # Fix rung to column
    add_fixed_constraint(rung, columns[ladder_column_index])

# ====================
# CREATE LOAD
# ====================
bpy.ops.mesh.primitive_cube_add(size=1, location=load_position)
load = bpy.context.active_object
load.name = "Load"
load.scale = (load_size, load_size, load_size)
bpy.ops.rigidbody.object_add()
load.rigid_body.type = 'ACTIVE'
load.rigid_body.mass = load_mass
load.rigid_body.collision_shape = 'BOX'

# ====================
# SETUP PHYSICS WORLD
# ====================
bpy.context.scene.rigidbody_world.enabled = True
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 50
bpy.context.scene.rigidbody_world.use_split_impulse = True
bpy.context.scene.frame_end = 500

# Enable all collisions
for obj in bpy.context.scene.objects:
    if hasattr(obj, 'rigid_body'):
        obj.rigid_body.use_margin = True
        obj.rigid_body.collision_margin = 0.04

print("Fire-watch tower construction complete. Simulation ready.")