import bpy
import math
from mathutils import Vector

# Clear existing scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Parameters from summary
span = 11.0
peak_height = 4.0
end_height = 3.0
bottom_chord_z = 1.5
vertical_height = 1.5

top_chord_dims = (5.5, 0.2, 0.3)
bottom_chord_dims = (5.5, 0.2, 0.3)
vertical_dims = (0.2, 0.2, 1.5)
diagonal_dims = (0.2, 0.2, 3.0)

support_size = (0.5, 0.5, 0.5)
support_left_loc = (0.0, 0.0, 0.25)
support_right_loc = (11.0, 0.0, 0.25)

diag_x_offset = 2.236
midpoint_z = 3.5

total_mass_kg = 850.0
top_chord_mass = total_mass_kg / 2

# Helper function to create beam with physics
def create_beam(name, location, rotation, dimensions, mass=None, rigid_body_type='ACTIVE'):
    """Create a rectangular beam with rigid body physics"""
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = (dimensions[0]/2, dimensions[1]/2, dimensions[2]/2)
    obj.rotation_euler = rotation
    
    # Add rigid body
    bpy.ops.rigidbody.object_add()
    obj.rigid_body.type = rigid_body_type
    obj.rigid_body.collision_shape = 'BOX'
    if mass:
        obj.rigid_body.mass = mass
    return obj

# Helper function to create fixed constraint between two objects
def create_fixed_constraint(obj_a, obj_b):
    """Create a fixed constraint between two objects"""
    # Create empty object as constraint anchor
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=obj_a.location)
    constraint_empty = bpy.context.active_object
    constraint_empty.name = f"Constraint_{obj_a.name}_{obj_b.name}"
    
    # Add rigid body constraint
    bpy.ops.rigidbody.constraint_add()
    constraint = constraint_empty.rigid_body_constraint
    constraint.type = 'FIXED'
    constraint.object1 = obj_a
    constraint.object2 = obj_b
    
    return constraint_empty

# Create ground supports
left_support = create_beam("Left_Support", support_left_loc, (0,0,0), 
                          support_size, rigid_body_type='PASSIVE')
right_support = create_beam("Right_Support", support_right_loc, (0,0,0), 
                           support_size, rigid_body_type='PASSIVE')

# Create bottom chords
bottom_chord_left = create_beam("Bottom_Chord_Left", 
                               (span/4, 0, bottom_chord_z),  # Center at quarter span
                               (0, 0, 0), 
                               bottom_chord_dims)
bottom_chord_right = create_beam("Bottom_Chord_Right", 
                                (3*span/4, 0, bottom_chord_z),  # Center at 3/4 span
                                (0, 0, 0), 
                                bottom_chord_dims)

# Create vertical members
vertical_left = create_beam("Vertical_Left", 
                           (0, 0, (bottom_chord_z + end_height)/2),  # Midpoint
                           (0, 0, 0), 
                           vertical_dims)
vertical_right = create_beam("Vertical_Right", 
                            (span, 0, (bottom_chord_z + end_height)/2), 
                            (0, 0, 0), 
                            vertical_dims)

# Calculate top chord angles
top_chord_angle = math.atan2(peak_height - end_height, span/2)  # Rise/run

# Create top chords with rotation
top_chord_left = create_beam("Top_Chord_Left", 
                            (span/4, 0, (end_height + peak_height)/2),  # Midpoint
                            (0, top_chord_angle, 0),  # Rotate around Y axis
                            top_chord_dims, 
                            mass=top_chord_mass)
top_chord_right = create_beam("Top_Chord_Right", 
                             (3*span/4, 0, (end_height + peak_height)/2), 
                             (0, -top_chord_angle, 0),  # Negative angle for right side
                             top_chord_dims, 
                             mass=top_chord_mass)

# Calculate diagonal angles and positions
# Left diagonals
diag1_angle = math.atan2(midpoint_z - bottom_chord_z, diag_x_offset)  # Bottom to top
diag2_angle = math.atan2(bottom_chord_z - midpoint_z, diag_x_offset)  # Top to bottom

# Create diagonals
diagonal1 = create_beam("Diagonal_1", 
                       (diag_x_offset/2, 0, (bottom_chord_z + midpoint_z)/2),
                       (0, diag1_angle, 0),
                       diagonal_dims)

diagonal2 = create_beam("Diagonal_2", 
                       (diag_x_offset/2, 0, (bottom_chord_z + midpoint_z)/2),
                       (0, diag2_angle, 0),
                       diagonal_dims)

diagonal3 = create_beam("Diagonal_3", 
                       (span - diag_x_offset/2, 0, (bottom_chord_z + midpoint_z)/2),
                       (0, -diag1_angle, 0),  # Mirror of diag1
                       diagonal_dims)

diagonal4 = create_beam("Diagonal_4", 
                       (span - diag_x_offset/2, 0, (bottom_chord_z + midpoint_z)/2),
                       (0, -diag2_angle, 0),  # Mirror of diag2
                       diagonal_dims)

# Create fixed constraints at all joints
constraints = []

# Left support connections
constraints.append(create_fixed_constraint(left_support, bottom_chord_left))
constraints.append(create_fixed_constraint(left_support, vertical_left))

# Left vertical connections
constraints.append(create_fixed_constraint(vertical_left, bottom_chord_left))
constraints.append(create_fixed_constraint(vertical_left, top_chord_left))

# Left diagonal connections
constraints.append(create_fixed_constraint(diagonal1, bottom_chord_left))
constraints.append(create_fixed_constraint(diagonal1, top_chord_left))
constraints.append(create_fixed_constraint(diagonal2, bottom_chord_left))
constraints.append(create_fixed_constraint(diagonal2, top_chord_left))

# Center joint (where top chords meet)
constraints.append(create_fixed_constraint(top_chord_left, top_chord_right))

# Right diagonal connections
constraints.append(create_fixed_constraint(diagonal3, bottom_chord_right))
constraints.append(create_fixed_constraint(diagonal3, top_chord_right))
constraints.append(create_fixed_constraint(diagonal4, bottom_chord_right))
constraints.append(create_fixed_constraint(diagonal4, top_chord_right))

# Right vertical connections
constraints.append(create_fixed_constraint(vertical_right, bottom_chord_right))
constraints.append(create_fixed_constraint(vertical_right, top_chord_right))

# Right support connections
constraints.append(create_fixed_constraint(right_support, bottom_chord_right))
constraints.append(create_fixed_constraint(right_support, vertical_right))

# Center bottom chord connection (where two bottom chords meet)
constraints.append(create_fixed_constraint(bottom_chord_left, bottom_chord_right))

# Set up physics world
bpy.context.scene.rigidbody_world.enabled = True
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 50
bpy.context.scene.frame_end = 100  # 100 frames simulation

print("Scissor truss construction complete. Span verification:")
print(f"Left support at X={left_support.location.x}m")
print(f"Right support at X={right_support.location.x}m")
print(f"Span = {right_support.location.x - left_support.location.x}m")
print(f"Total top chord mass: {top_chord_left.rigid_body.mass + top_chord_right.rigid_body.mass}kg")