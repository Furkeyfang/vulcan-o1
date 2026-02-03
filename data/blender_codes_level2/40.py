import bpy
import math
from mathutils import Vector, Euler

def clear_scene():
    """Clear all objects in the scene."""
    if bpy.context.object:
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete()

def create_rigid_body(obj, body_type='PASSIVE', mass=1.0):
    """Add rigid body physics to an object."""
    bpy.context.view_layer.objects.active = obj
    bpy.ops.rigidbody.object_add()
    obj.rigid_body.type = body_type
    if body_type == 'ACTIVE':
        obj.rigid_body.mass = mass
    obj.rigid_body.collision_shape = 'BOX'
    obj.rigid_body.friction = 0.5
    obj.rigid_body.restitution = 0.1

def create_fixed_constraint(obj1, obj2, location):
    """Create a fixed constraint between two objects."""
    # Create empty for constraint
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=location)
    constraint_empty = bpy.context.active_object
    constraint_empty.name = f"Fixed_{obj1.name}_{obj2.name}"
    
    # Add rigid body constraint
    bpy.ops.rigidbody.constraint_add()
    constraint = constraint_empty.rigid_body_constraint
    constraint.type = 'FIXED'
    constraint.object1 = obj1
    constraint.object2 = obj2
    constraint.disable_collisions = True
    
    return constraint_empty

# Clear existing scene
clear_scene()

# Parameters from summary
deck_length = 10.0
deck_width = 2.0
deck_thickness = 0.2
deck_center_z = 0.1

vertical_count = 10
vertical_spacing = 1.0
vertical_x_start = 0.5
vertical_size = (0.1, 0.1, 0.5)
truss_y_offset = 1.05
vertical_center_z = 0.45

diagonal_length = 1.414
diagonal_size = (0.1, 0.1, diagonal_length)
diagonal_angle = math.radians(26.565)

load_mass = 700.0
load_size = (4.0, 2.0, 0.2)
load_center_z = 0.3

support_size = (0.3, 2.2, 0.3)
joint_overlap = 0.005

# Create Deck
bpy.ops.mesh.primitive_cube_add(size=1, location=(deck_length/2, 0, deck_center_z))
deck = bpy.context.active_object
deck.name = "Deck"
deck.scale = (deck_length/2, deck_width/2, deck_thickness/2)
create_rigid_body(deck, 'PASSIVE')

# Create Vertical Struts
verticals = []
for side in [-1, 1]:  # Left and right trusses
    for i in range(vertical_count):
        x_pos = vertical_x_start + i * vertical_spacing
        y_pos = side * truss_y_offset
        
        bpy.ops.mesh.primitive_cube_add(size=1, location=(x_pos, y_pos, vertical_center_z))
        vert = bpy.context.active_object
        vert.name = f"Vertical_{side}_{i}"
        vert.scale = (vertical_size[0]/2, vertical_size[1]/2, vertical_size[2]/2)
        create_rigid_body(vert, 'PASSIVE')
        verticals.append(vert)
        
        # Constraint: vertical to deck
        joint_loc = Vector((x_pos, y_pos, deck_center_z + deck_thickness/2))
        create_fixed_constraint(deck, vert, joint_loc)

# Create Diagonal Members
diagonals = []
for side in [-1, 1]:
    y_pos = side * truss_y_offset
    
    # First set of diagonals (bottom-left to top-right)
    for i in range(vertical_count - 1):
        x_center = vertical_x_start + i * vertical_spacing + vertical_spacing/2
        z_center = vertical_center_z
        
        bpy.ops.mesh.primitive_cube_add(size=1, location=(x_center, y_pos, z_center))
        diag = bpy.context.active_object
        diag.name = f"Diagonal_{side}_A_{i}"
        diag.scale = (diagonal_size[0]/2, diagonal_size[1]/2, diagonal_size[2]/2)
        
        # Rotate diagonal
        diag.rotation_euler = Euler((0, diagonal_angle, 0), 'XYZ')
        if side == -1:
            diag.rotation_euler = Euler((0, -diagonal_angle, 0), 'XYZ')
        
        create_rigid_body(diag, 'PASSIVE')
        diagonals.append(diag)
        
        # Constraints: diagonal to verticals
        # Left connection (bottom of vertical i)
        left_vert = verticals[(0 if side == -1 else vertical_count) + i]
        left_joint = Vector((vertical_x_start + i * vertical_spacing, y_pos, deck_center_z + deck_thickness/2 + joint_overlap))
        create_fixed_constraint(left_vert, diag, left_joint)
        
        # Right connection (top of vertical i+1)
        right_vert = verticals[(0 if side == -1 else vertical_count) + i + 1]
        right_joint = Vector((vertical_x_start + (i+1) * vertical_spacing, y_pos, vertical_center_z + vertical_size[2]/2 - joint_overlap))
        create_fixed_constraint(right_vert, diag, right_joint)
    
    # Second set of diagonals (top-left to bottom-right)
    for i in range(vertical_count - 1):
        x_center = vertical_x_start + i * vertical_spacing + vertical_spacing/2
        z_center = vertical_center_z
        
        bpy.ops.mesh.primitive_cube_add(size=1, location=(x_center, y_pos, z_center))
        diag = bpy.context.active_object
        diag.name = f"Diagonal_{side}_B_{i}"
        diag.scale = (diagonal_size[0]/2, diagonal_size[1]/2, diagonal_size[2]/2)
        
        # Rotate diagonal opposite direction
        diag.rotation_euler = Euler((0, -diagonal_angle, 0), 'XYZ')
        if side == -1:
            diag.rotation_euler = Euler((0, diagonal_angle, 0), 'XYZ')
        
        create_rigid_body(diag, 'PASSIVE')
        diagonals.append(diag)
        
        # Constraints
        # Left connection (top of vertical i)
        left_vert = verticals[(0 if side == -1 else vertical_count) + i]
        left_joint = Vector((vertical_x_start + i * vertical_spacing, y_pos, vertical_center_z + vertical_size[2]/2 - joint_overlap))
        create_fixed_constraint(left_vert, diag, left_joint)
        
        # Right connection (bottom of vertical i+1)
        right_vert = verticals[(0 if side == -1 else vertical_count) + i + 1]
        right_joint = Vector((vertical_x_start + (i+1) * vertical_spacing, y_pos, deck_center_z + deck_thickness/2 + joint_overlap))
        create_fixed_constraint(right_vert, diag, right_joint)

# Create Load
bpy.ops.mesh.primitive_cube_add(size=1, location=(deck_length/2, 0, load_center_z))
load = bpy.context.active_object
load.name = "Load"
load.scale = (load_size[0]/2, load_size[1]/2, load_size[2]/2)
create_rigid_body(load, 'ACTIVE', load_mass)

# Create End Supports
# Left support
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, support_size[2]/2))
support_left = bpy.context.active_object
support_left.name = "Support_Left"
support_left.scale = (support_size[0]/2, support_size[1]/2, support_size[2]/2)
create_rigid_body(support_left, 'PASSIVE')

# Right support
bpy.ops.mesh.primitive_cube_add(size=1, location=(deck_length, 0, support_size[2]/2))
support_right = bpy.context.active_object
support_right.name = "Support_Right"
support_right.scale = (support_size[0]/2, support_size[1]/2, support_size[2]/2)
create_rigid_body(support_right, 'PASSIVE')

# Constraints: deck to supports
create_fixed_constraint(deck, support_left, Vector((0, 0, deck_center_z)))
create_fixed_constraint(deck, support_right, Vector((deck_length, 0, deck_center_z)))

# Setup Rigid Body World
bpy.context.scene.rigidbody_world.enabled = True
bpy.context.scene.rigidbody_world.time_scale = 1.0
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 50

print("Warren Truss Bridge constructed successfully.")
print(f"Total objects: {len(bpy.data.objects)}")
print(f"Vertical struts: {len(verticals)}")
print(f"Diagonal members: {len(diagonals)}")