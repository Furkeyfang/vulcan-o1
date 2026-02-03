import bpy
import math
from mathutils import Vector

# 1. Clear existing scene
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

# 2. Parameters from summary
span = 18.0
chord_sect = (0.3, 0.3)  # width, height
post_h = 2.5
bot_z = 5.0
top_z = 7.5
left_post_x = -3.0
right_post_x = 3.0
left_end = -9.0
right_end = 9.0
force_total = 17658.0
mat_density = 7850.0  # steel kg/m³
g = 9.81

# 3. Create rigid body world with appropriate settings
bpy.ops.rigidbody.world_add()
rb_world = bpy.context.scene.rigidbody_world
rb_world.substeps_per_frame = 10
rb_world.solver_iterations = 50
rb_world.time_scale = 0.5  # slower for stability

# 4. Helper function to create box member with physics
def create_member(name, location, dimensions):
    """Create rectangular beam with rigid body physics"""
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = (dimensions[0]/2, dimensions[1]/2, dimensions[2]/2)
    
    # Calculate mass from volume and density
    volume = dimensions[0] * dimensions[1] * dimensions[2]
    mass = volume * mat_density
    
    # Add rigid body
    bpy.ops.rigidbody.object_add()
    obj.rigid_body.type = 'ACTIVE'
    obj.rigid_body.mass = mass
    obj.rigid_body.collision_shape = 'BOX'
    obj.rigid_body.friction = 0.5
    obj.rigid_body.restitution = 0.1
    obj.rigid_body.linear_damping = 0.04
    obj.rigid_body.angular_damping = 0.1
    
    # Lock Y translation and X,Z rotations (2D truss behavior)
    obj.rigid_body.lock_rotation_x = True
    obj.rigid_body.lock_rotation_z = True
    obj.rigid_body.lock_location_y = True
    
    return obj

# 5. Create top chord (18m long, 0.3x0.3 cross-section)
top_chord = create_member("TopChord", 
                         (0, 0, top_z), 
                         (span, chord_sect[0], chord_sect[1]))

# 6. Create bottom chord
bottom_chord = create_member("BottomChord", 
                            (0, 0, bot_z), 
                            (span, chord_sect[0], chord_sect[1]))

# 7. Create queen posts (vertical)
queen_left = create_member("QueenPost_Left",
                          (left_post_x, 0, (top_z + bot_z)/2),
                          (chord_sect[0], chord_sect[1], post_h))

queen_right = create_member("QueenPost_Right",
                           (right_post_x, 0, (top_z + bot_z)/2),
                           (chord_sect[0], chord_sect[1], post_h))

# 8. Create diagonal struts
# Function for diagonal between two points
def create_diagonal(name, p1, p2):
    """Create diagonal member between two 3D points"""
    # Calculate center and dimensions
    center = ((p1[0] + p2[0])/2, (p1[1] + p2[1])/2, (p1[2] + p2[2])/2)
    length = math.sqrt((p2[0]-p1[0])**2 + (p2[1]-p1[1])**2 + (p2[2]-p1[2])**2)
    
    # Create cube and scale
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=center)
    obj = bpy.context.active_object
    obj.name = name
    
    # Scale: thickness in X/Y, length in Z (will rotate)
    obj.scale = (chord_sect[0]/2, chord_sect[1]/2, length/2)
    
    # Calculate rotation to align Z axis with diagonal direction
    direction = Vector(p2) - Vector(p1)
    direction.normalize()
    
    # Find rotation that aligns local Z (0,0,1) with direction
    up = Vector((0, 0, 1))
    if direction.dot(up) < 0.9999:
        rot_axis = up.cross(direction)
        rot_angle = up.angle(direction)
        obj.rotation_mode = 'AXIS_ANGLE'
        obj.rotation_axis_angle = (rot_angle, rot_axis[0], rot_axis[1], rot_axis[2])
    
    # Add rigid body (same as create_member)
    volume = chord_sect[0] * chord_sect[1] * length
    mass = volume * mat_density
    
    bpy.ops.rigidbody.object_add()
    obj.rigid_body.type = 'ACTIVE'
    obj.rigid_body.mass = mass
    obj.rigid_body.collision_shape = 'BOX'
    obj.rigid_body.friction = 0.5
    obj.rigid_body.restitution = 0.1
    obj.rigid_body.linear_damping = 0.04
    obj.rigid_body.angular_damping = 0.1
    obj.rigid_body.lock_rotation_x = True
    obj.rigid_body.lock_rotation_z = True
    obj.rigid_body.lock_location_y = True
    
    return obj

# Create four diagonals
diag1 = create_diagonal("Diag_TopLeft_to_BottomLeft",
                       (left_post_x, 0, top_z),      # Top of left post
                       (left_end, 0, bot_z))         # Left end of bottom chord

diag2 = create_diagonal("Diag_BottomLeft_to_TopLeft",
                       (left_post_x, 0, bot_z),      # Bottom of left post
                       (left_end, 0, top_z))         # Left end of top chord

diag3 = create_diagonal("Diag_TopRight_to_BottomRight",
                       (right_post_x, 0, top_z),     # Top of right post
                       (right_end, 0, bot_z))        # Right end of bottom chord

diag4 = create_diagonal("Diag_BottomRight_to_TopRight",
                       (right_post_x, 0, bot_z),     # Bottom of right post
                       (right_end, 0, top_z))        # Right end of top chord

# 9. Create fixed constraints at connection points
def add_fixed_constraint(obj1, obj2, location):
    """Add fixed constraint between two objects at specified location"""
    bpy.context.scene.cursor.location = location
    
    # Deselect all and select the two objects
    bpy.ops.object.select_all(action='DESELECT')
    obj1.select_set(True)
    obj2.select_set(True)
    bpy.context.view_layer.objects.active = obj1
    
    # Add constraint
    bpy.ops.rigidbody.constraint_add()
    constr = bpy.context.active_object
    constr.name = f"Fixed_{obj1.name}_{obj2.name}"
    constr.rigid_body_constraint.type = 'FIXED'
    constr.rigid_body_constraint.object1 = obj1
    constr.rigid_body_constraint.object2 = obj2

# Connect top chord to queen posts
add_fixed_constraint(top_chord, queen_left, (left_post_x, 0, top_z))
add_fixed_constraint(top_chord, queen_right, (right_post_x, 0, top_z))

# Connect bottom chord to queen posts
add_fixed_constraint(bottom_chord, queen_left, (left_post_x, 0, bot_z))
add_fixed_constraint(bottom_chord, queen_right, (right_post_x, 0, bot_z))

# Connect diagonals
# Left side
add_fixed_constraint(diag1, queen_left, (left_post_x, 0, top_z))
add_fixed_constraint(diag1, bottom_chord, (left_end, 0, bot_z))
add_fixed_constraint(diag2, queen_left, (left_post_x, 0, bot_z))
add_fixed_constraint(diag2, top_chord, (left_end, 0, top_z))

# Right side
add_fixed_constraint(diag3, queen_right, (right_post_x, 0, top_z))
add_fixed_constraint(diag3, bottom_chord, (right_end, 0, bot_z))
add_fixed_constraint(diag4, queen_right, (right_post_x, 0, bot_z))
add_fixed_constraint(diag4, top_chord, (right_end, 0, top_z))

# 10. Apply distributed load on top chord
# Create multiple force application points along top chord
num_load_points = 7
for i in range(num_load_points):
    x_pos = left_end + (i * span/(num_load_points-1))
    # Create empty to apply force
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(x_pos, 0, top_z + 0.5))
    empty = bpy.context.active_object
    empty.name = f"ForcePoint_{i}"
    
    # Add force field
    bpy.ops.object.effector_add(type='FORCE', location=empty.location)
    force = bpy.context.active_object
    force.name = f"Force_{i}"
    force.field.strength = -force_total / num_load_points  # Negative for downward
    force.field.falloff_power = 0
    force.field.distance_max = 2.0
    force.field.use_max_distance = True
    
    # Parent to empty
    force.parent = empty

# 11. Create supports at ends (passive rigid bodies)
support_left = create_member("Support_Left", (left_end, 0, bot_z - 0.5), (0.6, 0.6, 1.0))
support_left.rigid_body.type = 'PASSIVE'
support_right = create_member("Support_Right", (right_end, 0, bot_z - 0.5), (0.6, 0.6, 1.0))
support_right.rigid_body.type = 'PASSIVE'

# Fix bottom chord to supports
add_fixed_constraint(bottom_chord, support_left, (left_end, 0, bot_z))
add_fixed_constraint(bottom_chord, support_right, (right_end, 0, bot_z))

# 12. Set up collision margins (prevents penetration)
for obj in bpy.data.objects:
    if hasattr(obj, 'rigid_body') and obj.rigid_body:
        obj.rigid_body.collision_margin = 0.001

print("Queen Post truss construction complete. Simulation ready.")