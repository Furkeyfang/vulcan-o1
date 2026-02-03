import bpy
import math
from mathutils import Vector, Matrix

# 1. Clear scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# 2. Define variables from parameter_summary
tie_beam_length = 4.8
tie_beam_cross = 0.2
tie_beam_z = 0.5
king_post_height = 1.2
king_post_cross = 0.1
rafter_length = 2.6
rafter_cross = 0.15
roof_deck_size = (5.0, 2.0, 0.05)
roof_load_mass = 180
gravity = 9.81
roof_force = 1765.8
# Adjusted geometry due to rafter length constraint
king_post_top_z = tie_beam_z + math.sqrt(rafter_length**2 - (tie_beam_length/2)**2)  # 1.5m
tie_beam_end_x = tie_beam_length / 2  # 2.4m
rafter_slope_angle = math.degrees(math.atan((king_post_top_z - tie_beam_z) / tie_beam_end_x))  # ~22.62°
roof_deck_center_z = (tie_beam_z + king_post_top_z)/2 + rafter_cross/2 + roof_deck_size[2]/2  # ~1.1m
roof_deck_overhang = (roof_deck_size[0] - tie_beam_length) / 2  # 0.1m

# 3. Create Tie Beam (Passive Rigid Body)
bpy.ops.mesh.primitive_cube_add(size=1.0)
tie_beam = bpy.context.active_object
tie_beam.name = "TieBeam"
tie_beam.scale = (tie_beam_length, tie_beam_cross, tie_beam_cross)
tie_beam.location = (0, 0, tie_beam_z)
bpy.ops.rigidbody.object_add()
tie_beam.rigid_body.type = 'PASSIVE'
tie_beam.rigid_body.collision_shape = 'BOX'

# 4. Create King Post (Active Rigid Body, Fixed to Tie Beam)
bpy.ops.mesh.primitive_cube_add(size=1.0)
king_post = bpy.context.active_object
king_post.name = "KingPost"
king_post.scale = (king_post_cross, king_post_cross, king_post_height)
king_post.location = (0, 0, tie_beam_z + king_post_height/2)
bpy.ops.rigidbody.object_add()
king_post.rigid_body.type = 'ACTIVE'
king_post.rigid_body.collision_shape = 'BOX'
king_post.rigid_body.mass = 50  # Estimated mass based on volume and density

# Fixed constraint between King Post and Tie Beam
bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, tie_beam_z))
constraint_empty = bpy.context.active_object
constraint_empty.name = "KingPost_Fixed"
bpy.ops.rigidbody.constraint_add()
constraint_empty.rigid_body_constraint.type = 'FIXED'
constraint_empty.rigid_body_constraint.object1 = tie_beam
constraint_empty.rigid_body_constraint.object2 = king_post

# 5. Create Rafters (Active Rigid Bodies)
rafter_points = [
    (tie_beam_end_x, 0, tie_beam_z),   # Left tie beam end
    (-tie_beam_end_x, 0, tie_beam_z),  # Right tie beam end
]
for i, (start_x, start_y, start_z) in enumerate(rafter_points):
    # Calculate rafter endpoint at King Post top
    end_point = Vector((0, 0, king_post_top_z))
    start_point = Vector((start_x, start_y, start_z))
    direction = end_point - start_point
    length = direction.length
    center = (start_point + end_point) / 2
    
    # Create rafter cube
    bpy.ops.mesh.primitive_cube_add(size=1.0)
    rafter = bpy.context.active_object
    rafter.name = f"Rafter_{'Left' if i==0 else 'Right'}"
    rafter.scale = (length, rafter_cross, rafter_cross)
    rafter.location = center
    
    # Rotate to align with direction vector
    up = Vector((0, 0, 1))
    rot_quat = direction.to_track_quat('Z', 'Y')
    rafter.rotation_euler = rot_quat.to_euler()
    
    # Add rigid body
    bpy.ops.rigidbody.object_add()
    rafter.rigid_body.type = 'ACTIVE'
    rafter.rigid_body.collision_shape = 'BOX'
    rafter.rigid_body.mass = 30  # Estimated mass
    
    # Hinge constraint at tie beam end
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=start_point)
    hinge1 = bpy.context.active_object
    hinge1.name = f"Hinge_TieBeam_{i}"
    bpy.ops.rigidbody.constraint_add()
    hinge1.rigid_body_constraint.type = 'HINGE'
    hinge1.rigid_body_constraint.object1 = tie_beam
    hinge1.rigid_body_constraint.object2 = rafter
    hinge1.rigid_body_constraint.use_angular_x = False
    hinge1.rigid_body_constraint.use_angular_y = True
    hinge1.rigid_body_constraint.use_angular_z = False
    
    # Hinge constraint at King Post top
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=end_point)
    hinge2 = bpy.context.active_object
    hinge2.name = f"Hinge_KingPost_{i}"
    bpy.ops.rigidbody.constraint_add()
    hinge2.rigid_body_constraint.type = 'HINGE'
    hinge2.rigid_body_constraint.object1 = king_post
    hinge2.rigid_body_constraint.object2 = rafter
    hinge2.rigid_body_constraint.use_angular_x = False
    hinge2.rigid_body_constraint.use_angular_y = True
    hinge2.rigid_body_constraint.use_angular_z = False

# 6. Create Roof Deck (Active Rigid Body with Load Mass)
bpy.ops.mesh.primitive_cube_add(size=1.0)
roof_deck = bpy.context.active_object
roof_deck.name = "RoofDeck"
roof_deck.scale = roof_deck_size
roof_deck.location = (0, 0, roof_deck_center_z)
bpy.ops.rigidbody.object_add()
roof_deck.rigid_body.type = 'ACTIVE'
roof_deck.rigid_body.collision_shape = 'BOX'
roof_deck.rigid_body.mass = roof_load_mass  # 180 kg distributed load

# Fixed constraints between Roof Deck and Rafters
rafters = [obj for obj in bpy.data.objects if obj.name.startswith("Rafter_")]
for rafter in rafters:
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, roof_deck_center_z))
    deck_constraint = bpy.context.active_object
    deck_constraint.name = f"Deck_Fixed_{rafter.name}"
    bpy.ops.rigidbody.constraint_add()
    deck_constraint.rigid_body_constraint.type = 'FIXED'
    deck_constraint.rigid_body_constraint.object1 = roof_deck
    deck_constraint.rigid_body_constraint.object2 = rafter

# 7. Set gravity for simulation
bpy.context.scene.use_gravity = True
bpy.context.scene.gravity = (0, 0, -gravity)

print("King Post truss construction complete. Ready for simulation.")