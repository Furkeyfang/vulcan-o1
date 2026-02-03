import bpy
import math
from mathutils import Vector, Matrix

# 1. Clear existing scene
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

# 2. Define parameters from summary
span = 7.0
peak_h = 1.5
end_v_h = 0.75
chord_section = 0.15
web_section = 0.1
inner_x = 1.65  # Adjusted for ~1.8m diagonal length
top_len = 3.5
force_total = 4905.0
force_per = 1635.0
frames = 100
joint_rad = 0.08

# 3. Helper function to create beam
def create_beam(name, start, end, section, is_chord=False):
    """Create a rectangular beam between two points."""
    length = (end - start).length
    center = (start + end) / 2
    
    bpy.ops.mesh.primitive_cube_add(size=1.0)
    beam = bpy.context.active_object
    beam.name = name
    
    # Scale: length in X, cross-section in Y/Z
    beam.scale.x = length / 2
    beam.scale.y = section / 2
    beam.scale.z = section / 2
    
    # Align to direction vector
    dir_vec = (end - start).normalized()
    if dir_vec.length > 0:
        rot_quat = Vector((1,0,0)).rotation_difference(dir_vec)
        beam.rotation_euler = rot_quat.to_euler()
    
    beam.location = center
    return beam

# 4. Define joint coordinates
joints = {
    "B_left": Vector((-span/2, 0, 0)),
    "B_innerL": Vector((-inner_x, 0, 0)),
    "B_center": Vector((0, 0, 0)),
    "B_innerR": Vector((inner_x, 0, 0)),
    "B_right": Vector((span/2, 0, 0)),
    "T_left": Vector((-span/2, 0, end_v_h)),
    "T_peak": Vector((0, 0, peak_h)),
    "T_right": Vector((span/2, 0, end_v_h))
}

# 5. Create all members
beams = {}
# Bottom chord (single piece)
beams["bottom"] = create_beam("Bottom_Chord", joints["B_left"], joints["B_right"], chord_cross_section, True)

# Top chords (two pieces)
beams["top_left"] = create_beam("Top_Chord_L", joints["T_left"], joints["T_peak"], chord_cross_section, True)
beams["top_right"] = create_beam("Top_Chord_R", joints["T_peak"], joints["T_right"], chord_cross_section, True)

# Vertical members
beams["vert_left"] = create_beam("Vertical_L", joints["B_left"], joints["T_left"], web_cross_section)
beams["vert_center"] = create_beam("Vertical_C", joints["B_center"], joints["T_peak"], web_cross_section)
beams["vert_right"] = create_beam("Vertical_R", joints["B_right"], joints["T_right"], web_cross_section)

# Diagonal members (alternating directions)
beams["diag1"] = create_beam("Diagonal_1", joints["B_innerL"], joints["T_left"], web_cross_section)
beams["diag2"] = create_beam("Diagonal_2", joints["B_innerL"], joints["T_peak"], web_cross_section)
beams["diag3"] = create_beam("Diagonal_3", joints["B_innerR"], joints["T_peak"], web_cross_section)
beams["diag4"] = create_beam("Diagonal_4", joints["B_innerR"], joints["T_right"], web_cross_section)

# 6. Add rigid body physics (all passive initially)
for beam in beams.values():
    bpy.ops.rigidbody.object_add()
    beam.rigid_body.type = 'PASSIVE'
    beam.rigid_body.collision_shape = 'BOX'
    beam.rigid_body.mass = 50.0  # Approximate mass for stability

# 7. Create joint spheres for constraint anchors
joint_objs = {}
for j_name, j_pos in joints.items():
    bpy.ops.mesh.primitive_uv_sphere_add(radius=joint_rad, location=j_pos)
    joint = bpy.context.active_object
    joint.name = f"Joint_{j_name}"
    bpy.ops.rigidbody.object_add()
    joint.rigid_body.type = 'PASSIVE'
    joint_objs[j_name] = joint

# 8. Create fixed constraints between joints and connecting beams
constraint_groups = {
    "left_end": ["B_left", "T_left"],
    "left_inner": ["B_innerL"],
    "center": ["B_center", "T_peak"],
    "right_inner": ["B_innerR"],
    "right_end": ["B_right", "T_right"]
}

# Map beams to their connected joints
beam_connections = {
    "bottom": ["B_left", "B_right"],
    "top_left": ["T_left", "T_peak"],
    "top_right": ["T_peak", "T_right"],
    "vert_left": ["B_left", "T_left"],
    "vert_center": ["B_center", "T_peak"],
    "vert_right": ["B_right", "T_right"],
    "diag1": ["B_innerL", "T_left"],
    "diag2": ["B_innerL", "T_peak"],
    "diag3": ["B_innerR", "T_peak"],
    "diag4": ["B_innerR", "T_right"]
}

for beam_name, beam_obj in beams.items():
    for joint_key in beam_connections[beam_name]:
        joint_obj = joint_objs[joint_key]
        # Add constraint from beam to joint
        constraint = beam_obj.constraints.new(type='RIGID_BODY_JOINT')
        constraint.target = joint_obj
        constraint.object1 = beam_obj
        constraint.object2 = joint_obj
        constraint.type = 'FIXED'

# 9. Apply downward forces to top joints
top_joints = ["T_left", "T_peak", "T_right"]
for tj in top_joints:
    joint_objs[tj].rigid_body.type = 'ACTIVE'
    # Apply initial force (will be sustained via handler)
    joint_objs[tj].rigid_body.force = (0, 0, -force_per)

# 10. Set up frame change handler for sustained force
def apply_forces(scene):
    for tj in top_joints:
        joint_objs[tj].rigid_body.force = (0, 0, -force_per)

# Register handler (only if not in background rendering check)
if not bpy.app.background:
    bpy.app.handlers.frame_change_pre.append(apply_forces)

# 11. Configure simulation
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 50
bpy.context.scene.frame_end = frames

# 12. Bake simulation (headless compatible)
bpy.ops.ptcache.bake_all(bake=True)

print("Howe Truss construction complete. Simulation baked for", frames, "frames.")