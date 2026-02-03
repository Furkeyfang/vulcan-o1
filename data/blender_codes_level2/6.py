import bpy
import math

# Clear scene
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

# Parameters from summary
base_length = 10.0
truss_height = 3.0
cross_section = 0.2
bottom_chord_length = 5.0
top_chord_length = 5.83095
center_vertical_length = 3.0
side_vertical_length = 1.5
horizontal_length = 2.5
snow_load_total = 7848.0
snow_load_per_top_chord = 3924.0
simulation_frames = 100
gravity_z = -9.81

# Set gravity
bpy.context.scene.gravity = (0, 0, gravity_z)

# Helper to create a cube and set dimensions
def create_member(name, location, scale, rotation=None):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = scale
    if rotation:
        obj.rotation_euler = rotation
    return obj

# Create bottom chords (passive)
bottom1 = create_member("Bottom_Chord_1", 
                        location=(2.5, 0, 0), 
                        scale=(bottom_chord_length/2, cross_section/2, cross_section/2))
bpy.ops.rigidbody.object_add()
bottom1.rigid_body.type = 'PASSIVE'

bottom2 = create_member("Bottom_Chord_2", 
                        location=(7.5, 0, 0), 
                        scale=(bottom_chord_length/2, cross_section/2, cross_section/2))
bpy.ops.rigidbody.object_add()
bottom2.rigid_body.type = 'PASSIVE'

# Create top chords (active, sloped)
top_chord_angle = math.atan2(truss_height, bottom_chord_length)  # ~30.96 degrees
top1 = create_member("Top_Chord_1", 
                     location=(2.5, 0, 1.5), 
                     scale=(top_chord_length/2, cross_section/2, cross_section/2),
                     rotation=(0, top_chord_angle, 0))
bpy.ops.rigidbody.object_add()
# Apply downward force (in negative Z)
top1.rigid_body.force = (0, 0, -snow_load_per_top_chord)

top2 = create_member("Top_Chord_2", 
                     location=(7.5, 0, 1.5), 
                     scale=(top_chord_length/2, cross_section/2, cross_section/2),
                     rotation=(0, -top_chord_angle, 0))
bpy.ops.rigidbody.object_add()
top2.rigid_body.force = (0, 0, -snow_load_per_top_chord)

# Create internal members (active)
center_vert = create_member("Center_Vertical", 
                            location=(5.0, 0, 1.5), 
                            scale=(cross_section/2, cross_section/2, center_vertical_length/2))
bpy.ops.rigidbody.object_add()

left_vert = create_member("Left_Vertical", 
                          location=(2.5, 0, 0.75), 
                          scale=(cross_section/2, cross_section/2, side_vertical_length/2))
bpy.ops.rigidbody.object_add()

right_vert = create_member("Right_Vertical", 
                           location=(7.5, 0, 0.75), 
                           scale=(cross_section/2, cross_section/2, side_vertical_length/2))
bpy.ops.rigidbody.object_add()

left_horiz = create_member("Left_Horizontal", 
                           location=(3.75, 0, 1.5), 
                           scale=(horizontal_length/2, cross_section/2, cross_section/2))
bpy.ops.rigidbody.object_add()

right_horiz = create_member("Right_Horizontal", 
                            location=(6.25, 0, 1.5), 
                            scale=(horizontal_length/2, cross_section/2, cross_section/2))
bpy.ops.rigidbody.object_add()

# Create fixed constraints between connected members
def add_fixed_constraint(obj1, obj2):
    bpy.ops.object.select_all(action='DESELECT')
    obj1.select_set(True)
    obj2.select_set(True)
    bpy.context.view_layer.objects.active = obj1
    bpy.ops.rigidbody.connect()

# List of connections (pairs that share a joint)
connections = [
    (bottom1, top1),          # joint at (0,0,0)
    (bottom1, left_vert),     # joint at (2.5,0,0)
    (bottom1, bottom2),       # joint at (5,0,0)
    (bottom2, right_vert),    # joint at (7.5,0,0)
    (bottom2, top2),          # joint at (10,0,0)
    (top1, center_vert),      # joint at (5,0,3)
    (top2, center_vert),      # joint at (5,0,3)
    (left_vert, left_horiz),  # joint at (2.5,0,1.5)
    (center_vert, left_horiz), # joint at (5,0,1.5)
    (center_vert, right_horiz), # joint at (5,0,1.5)
    (right_vert, right_horiz), # joint at (7.5,0,1.5)
    (bottom1, center_vert),   # joint at (5,0,0)
    (bottom2, center_vert),   # joint at (5,0,0)
]

for obj1, obj2 in connections:
    add_fixed_constraint(obj1, obj2)

# Set simulation end frame
bpy.context.scene.frame_end = simulation_frames

# Optional: bake physics for headless verification (if running with --background)
# bpy.ops.ptcache.bake_all()