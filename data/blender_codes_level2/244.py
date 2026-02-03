import bpy
import math

# 1. Clear existing scene
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

# 2. Define parameters from summary
span = 6.0
chord_w = 0.3
chord_h = 0.3
bottom_z = 2.0
top_z = 3.0
kpost_len = 1.0
kpost_w = 0.3
strut_len = 3.16227766
strut_w = 0.3
strut_h = 0.3
load_force = 2943.0
sim_frames = 100

# Pre-calculated positions
left_strut_center = (-1.5, 0.0, 2.5)
right_strut_center = (1.5, 0.0, 2.5)
king_post_center = (0.0, 0.0, 2.5)
left_end = (-3.0, 0.0, 2.0)
right_end = (3.0, 0.0, 2.0)
king_top = (0.0, 0.0, 3.0)
king_bottom = (0.0, 0.0, 2.0)

# 3. Create Bottom Chord (Passive Anchor)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0,0,bottom_z))
bottom = bpy.context.active_object
bottom.scale = (span, chord_w, chord_h)
bottom.name = "Bottom_Chord"
bpy.ops.rigidbody.object_add()
bottom.rigid_body.type = 'PASSIVE'

# 4. Create Top Chord (Active)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0,0,top_z))
top = bpy.context.active_object
top.scale = (span, chord_w, chord_h)
top.name = "Top_Chord"
bpy.ops.rigidbody.object_add()

# 5. Create King Post (Vertical Member)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=king_post_center)
king = bpy.context.active_object
king.scale = (kpost_w, kpost_w, kpost_len)
king.name = "King_Post"
bpy.ops.rigidbody.object_add()

# 6. Create Left Diagonal Strut
bpy.ops.mesh.primitive_cube_add(size=1.0, location=left_strut_center)
left_strut = bpy.context.active_object
left_strut.scale = (strut_len, strut_w, strut_h)
left_strut.name = "Left_Strut"
# Calculate rotation: atan2(dz, dx) for XZ plane
angle = math.atan2(1.0, 3.0)  # vertical rise=1, horizontal run=3
left_strut.rotation_euler = (0, 0, angle)  # Rotate around Y axis (Euler ZYX order)
bpy.ops.rigidbody.object_add()

# 7. Create Right Diagonal Strut
bpy.ops.mesh.primitive_cube_add(size=1.0, location=right_strut_center)
right_strut = bpy.context.active_object
right_strut.scale = (strut_len, strut_w, strut_h)
right_strut.name = "Right_Strut"
right_strut.rotation_euler = (0, 0, -angle)  # Symmetric opposite rotation
bpy.ops.rigidbody.object_add()

# 8. Establish FIXED Constraints
def add_fixed_constraint(obj_a, obj_b, pivot_a, pivot_b):
    """Create fixed constraint between two objects at specified local pivots"""
    constraint = obj_a.constraints.new(type='RIGID_BODY_JOINT')
    constraint.object = obj_b
    constraint.pivot_type = 'CUSTOM'
    constraint.use_override_solver_iterations = True
    constraint.solver_iterations = 50
    # Set pivot points in local coordinates
    constraint.pivot_x = pivot_a[0]
    constraint.pivot_y = pivot_a[1]
    constraint.pivot_z = pivot_a[2]
    constraint.target_pivot_x = pivot_b[0]
    constraint.target_pivot_y = pivot_b[1]
    constraint.target_pivot_z = pivot_b[2]

# King Post to Bottom Chord (at bottom of king post)
add_fixed_constraint(king, bottom, 
                     (0,0,-kpost_len/2),  # Local: bottom of king post
                     (0,0,0))             # Local: center of bottom chord

# King Post to Top Chord (at top of king post)
add_fixed_constraint(king, top,
                     (0,0,kpost_len/2),   # Local: top of king post
                     (0,0,0))             # Local: center of top chord

# Left Strut to Bottom Chord (at left endpoint)
# Strut local: negative X end (scaled by strut_len/2)
add_fixed_constraint(left_strut, bottom,
                     (-strut_len/2, 0, 0),  # Local: left end of strut
                     (-span/2, 0, 0))       # Local: left end of bottom chord

# Left Strut to King Post (at king post top)
add_fixed_constraint(left_strut, king,
                     (strut_len/2, 0, 0),   # Local: right end of strut
                     (0, 0, kpost_len/2))   # Local: top of king post

# Right Strut to Bottom Chord (at right endpoint)
add_fixed_constraint(right_strut, bottom,
                     (-strut_len/2, 0, 0),  # Local: left end of strut (toward center)
                     (span/2, 0, 0))        # Local: right end of bottom chord

# Right Strut to King Post (at king post top)
add_fixed_constraint(right_strut, king,
                     (strut_len/2, 0, 0),   # Local: right end of strut
                     (0, 0, kpost_len/2))   # Local: top of king post

# 9. Apply Distributed Load on Top Chord
# Create force field affecting only top chord
bpy.ops.object.effector_add(type='FORCE', location=(0,0,top_z))
force = bpy.context.active_object
force.field.strength = -load_force  # Negative Z direction
force.field.use_max_distance = True
force.field.distance_max = 0.2  # Only affect nearby objects
force.field.falloff_power = 0.0  # Constant force within range

# 10. Configure Physics World
bpy.context.scene.rigidbody_world.time_scale = 1.0
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 50
bpy.context.scene.frame_end = sim_frames

print("King Post Truss assembly complete. Run simulation for", sim_frames, "frames.")