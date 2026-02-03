import bpy
import math
from mathutils import Matrix

# Clear scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Parameters from summary
span_x = 5.5
chord_width = 0.2
chord_height = 0.2
vertical_gap = 1.5
king_post_height = 1.5
strut_length = 1.8
deck_width = 5.5
deck_depth = 0.5
deck_thickness = 0.1
weight_size = 0.5
load_mass = 220

bottom_chord_z = 0.1
top_chord_z = 1.8
king_post_z = 0.95
deck_z = 1.95
weight_z = 2.25
strut_angle = math.atan(1.6 / 2.75)  # ≈30.1 degrees

# Enable rigid body physics
if bpy.context.scene.rigidbody_world is None:
    bpy.ops.rigidbody.world_add()

# Helper function to add rigid body
def add_rigidbody(obj, rb_type='PASSIVE', mass=1.0):
    bpy.ops.rigidbody.object_add()
    obj.rigid_body.type = rb_type
    obj.rigid_body.mass = mass
    obj.rigid_body.collision_shape = 'BOX'

# 1. Bottom Chord
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, bottom_chord_z))
bottom_chord = bpy.context.active_object
bottom_chord.scale = (span_x/2, chord_width/2, chord_height/2)
bottom_chord.name = "Bottom_Chord"
add_rigidbody(bottom_chord)

# 2. Top Chord
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, top_chord_z))
top_chord = bpy.context.active_object
top_chord.scale = (span_x/2, chord_width/2, chord_height/2)
top_chord.name = "Top_Chord"
add_rigidbody(top_chord)

# 3. King Post
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, king_post_z))
king_post = bpy.context.active_object
king_post.scale = (chord_width/2, chord_width/2, king_post_height/2)
king_post.name = "King_Post"
add_rigidbody(king_post)

# 4. Diagonal Struts (left and right)
for x_sign in [-1, 1]:
    # Create at origin
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0))
    strut = bpy.context.active_object
    strut.scale = (chord_width/2, chord_width/2, strut_length/2)
    strut.name = f"Strut_{'Left' if x_sign < 0 else 'Right'}"
    
    # Rotate to correct angle
    strut.rotation_euler = (0, strut_angle if x_sign < 0 else -strut_angle, 0)
    
    # Position: midpoint between top chord end and king post base
    mid_x = x_sign * span_x / 4
    mid_z = (top_chord_z + bottom_chord_z + chord_height) / 2
    strut.location = (mid_x, 0, mid_z)
    
    add_rigidbody(strut)
    
    # Store for constraint creation
    if x_sign < 0:
        strut_left = strut
    else:
        strut_right = strut

# 5. Roof Deck
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, deck_z))
deck = bpy.context.active_object
deck.scale = (deck_width/2, deck_depth/2, deck_thickness/2)
deck.name = "Roof_Deck"
add_rigidbody(deck)

# 6. Weight Block
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, weight_z))
weight = bpy.context.active_object
weight.scale = (weight_size/2, weight_size/2, weight_size/2)
weight.name = "Weight_Block"
add_rigidbody(weight, rb_type='ACTIVE', mass=load_mass)

# 7. Fixed Constraints for all joints
def add_fixed_constraint(obj1, obj2):
    # Create empty for constraint
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0,0,0))
    empty = bpy.context.active_object
    empty.name = f"Constraint_{obj1.name}_{obj2.name}"
    
    # Add rigid body constraint
    bpy.ops.rigidbody.constraint_add()
    constraint = empty.rigid_body_constraint
    constraint.type = 'FIXED'
    constraint.object1 = obj1
    constraint.object2 = obj2

# Apply constraints
add_fixed_constraint(bottom_chord, king_post)          # Center joint
add_fixed_constraint(top_chord, king_post)             # Top center joint

# Left diagonal connections
add_fixed_constraint(top_chord, strut_left)
add_fixed_constraint(bottom_chord, strut_left)

# Right diagonal connections  
add_fixed_constraint(top_chord, strut_right)
add_fixed_constraint(bottom_chord, strut_right)

# Deck to top chord (optional but improves stability)
add_fixed_constraint(top_chord, deck)

# Set simulation parameters
bpy.context.scene.frame_end = 100
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 10

print("King Post truss construction complete. Run simulation for 100 frames.")