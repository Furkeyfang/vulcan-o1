import bpy
import math
from mathutils import Vector, Matrix

# Clear existing scene
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

# Parameters from summary
span_total = 8.0
peak_height = 2.0
beam_cross = 0.2
beam_y_width = 0.2
bottom_chord_len = 4.0
upper_chord_len = 2.828
vertical_post_height = 1.0
diagonal_brace_len = 2.236
snow_mass = 400.0

joints = {
    "bottom_left": Vector((-4.0, 0.0, 0.0)),
    "bottom_mid_left": Vector((-2.0, 0.0, 0.0)),
    "bottom_center": Vector((0.0, 0.0, 0.0)),
    "bottom_mid_right": Vector((2.0, 0.0, 0.0)),
    "bottom_right": Vector((4.0, 0.0, 0.0)),
    "peak": Vector((0.0, 0.0, 2.0)),
    "outer_post_top_left": Vector((-4.0, 0.0, 1.0)),
    "inner_post_top_left": Vector((-2.0, 0.0, 1.0)),
    "inner_post_top_right": Vector((2.0, 0.0, 1.0)),
    "outer_post_top_right": Vector((4.0, 0.0, 1.0))
}

def create_beam_between(p1, p2, name, cross_section=beam_cross, y_width=beam_y_width):
    """Create a rectangular beam between two points."""
    # Calculate length and direction
    vec = p2 - p1
    length = vec.length
    direction = vec.normalized()
    
    # Create a cube and scale to beam dimensions
    # Default cube is 2x2x2, so scale factors: length/2, cross_section/2, y_width/2
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0,0,0))
    beam = bpy.context.active_object
    beam.name = name
    beam.scale = (length / 2.0, cross_section / 2.0, y_width / 2.0)
    
    # Rotate to align with direction
    # Default cube local X is along global X; we need to rotate so local X aligns with 'direction'
    up = Vector((0, 0, 1))
    rot_quat = direction.to_track_quat('X', 'Z')
    beam.rotation_euler = rot_quat.to_euler()
    
    # Move to midpoint
    beam.location = (p1 + p2) / 2.0
    
    return beam

# Create all truss members
beams = []

# Bottom chords (horizontal)
beams.append(create_beam_between(
    joints["bottom_left"],
    joints["bottom_center"],
    "BottomChord_Left"
))
beams.append(create_beam_between(
    joints["bottom_center"],
    joints["bottom_right"],
    "BottomChord_Right"
))

# Upper chords (sloped)
beams.append(create_beam_between(
    joints["bottom_mid_left"],
    joints["peak"],
    "UpperChord_Left"
))
beams.append(create_beam_between(
    joints["bottom_mid_right"],
    joints["peak"],
    "UpperChord_Right"
))

# Vertical posts
beams.append(create_beam_between(
    joints["bottom_left"],
    joints["outer_post_top_left"],
    "VerticalPost_OuterLeft"
))
beams.append(create_beam_between(
    joints["bottom_mid_left"],
    joints["inner_post_top_left"],
    "VerticalPost_InnerLeft"
))
beams.append(create_beam_between(
    joints["bottom_mid_right"],
    joints["inner_post_top_right"],
    "VerticalPost_InnerRight"
))
beams.append(create_beam_between(
    joints["bottom_right"],
    joints["outer_post_top_right"],
    "VerticalPost_OuterRight"
))

# Diagonal braces
beams.append(create_beam_between(
    joints["outer_post_top_left"],
    joints["bottom_mid_left"],
    "DiagonalBrace_Left"
))
beams.append(create_beam_between(
    joints["outer_post_top_right"],
    joints["bottom_mid_right"],
    "DiagonalBrace_Right"
))

# Add rigid body physics to all beams as PASSIVE (truss is fixed)
for beam in beams:
    bpy.ops.object.select_all(action='DESELECT')
    beam.select_set(True)
    bpy.context.view_layer.objects.active = beam
    bpy.ops.rigidbody.object_add()
    beam.rigid_body.type = 'PASSIVE'
    beam.rigid_body.collision_shape = 'BOX'

# Create a snow load plate (distributed mass)
# Plate covers the entire top surface of the truss: from X=-4 to 4, Z from 0 to 2, but shaped as two slopes.
# Simplify: create a thin rectangular plate covering the entire span at average height.
plate_length = span_total
plate_width = beam_y_width * 2  # Slightly wider than truss
plate_thickness = 0.05
plate_location = Vector((0.0, 0.0, peak_height * 0.7))  # Average height

bpy.ops.mesh.primitive_cube_add(size=1, location=plate_location)
snow_plate = bpy.context.active_object
snow_plate.name = "SnowLoadPlate"
snow_plate.scale = (plate_length / 2.0, plate_width / 2.0, plate_thickness / 2.0)

# Add rigid body as ACTIVE with mass
bpy.ops.object.select_all(action='DESELECT')
snow_plate.select_set(True)
bpy.context.view_layer.objects.active = snow_plate
bpy.ops.rigidbody.object_add()
snow_plate.rigid_body.type = 'ACTIVE'
snow_plate.rigid_body.mass = snow_mass
snow_plate.rigid_body.collision_shape = 'BOX'

# Create fixed constraints at all joints to connect beams and plate
# Collect all objects at each joint (within tolerance)
tolerance = 0.01
constraint_objects = beams + [snow_plate]

for joint_name, joint_pos in joints.items():
    # Find objects whose bounding boxes include the joint
    nearby_objs = []
    for obj in constraint_objects:
        # Simple distance check from object origin to joint (approximate)
        if (obj.location - joint_pos).length < 2.0:  # Loose threshold
            nearby_objs.append(obj)
    
    if len(nearby_objs) > 1:
        # Create an empty at joint for constraint reference
        bpy.ops.object.empty_add(type='PLAIN_AXES', location=joint_pos)
        empty = bpy.context.active_object
        empty.name = f"Constraint_{joint_name}"
        
        # Add rigid body constraint (fixed) between first object and others
        for i in range(1, len(nearby_objs)):
            bpy.ops.object.select_all(action='DESELECT')
            nearby_objs[0].select_set(True)
            bpy.context.view_layer.objects.active = nearby_objs[0]
            bpy.ops.rigidbody.constraint_add()
            const = bpy.context.active_object
            const.name = f"Fixed_{joint_name}_{i}"
            const.rigid_body_constraint.type = 'FIXED'
            const.rigid_body_constraint.object1 = nearby_objs[0]
            const.rigid_body_constraint.object2 = nearby_objs[i]
            const.location = joint_pos

# Set world gravity for simulation
bpy.context.scene.use_gravity = True
bpy.context.scene.gravity = (0.0, 0.0, -9.81)

# Ensure rigid body world is enabled
if not bpy.context.scene.rigidbody_world:
    bpy.ops.rigidbody.world_add()