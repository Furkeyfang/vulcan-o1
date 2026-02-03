import bpy
import math
from mathutils import Vector, Matrix

# Clear scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Parameters from summary
span = 12.0
tie_beam_dim = (12.0, 0.3, 0.3)
king_post_height = 3.0
queen_post_height = 2.0
member_cross_section = 0.3
rafter_length = 6.5
ridge_beam_length = 1.0
purlin_cross_section = 0.2
purlin_interval = 2.0
load_total_N = 8825.85
num_load_beams = 4
force_per_beam = load_total_N / num_load_beams
sim_frames = 100

# Helper: create beam with rigid body
def create_beam(name, size, location, rotation=(0,0,0), scale=(1,1,1), rigid_type='PASSIVE'):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = (size[0]*scale[0], size[1]*scale[1], size[2]*scale[2])
    obj.rotation_euler = rotation
    bpy.ops.rigidbody.object_add()
    obj.rigid_body.type = rigid_type
    obj.rigid_body.collision_shape = 'BOX'
    return obj

# Helper: create fixed constraint between two objects
def create_fixed_constraint(obj1, obj2):
    # Create empty for constraint
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=obj1.location)
    empty = bpy.context.active_object
    empty.name = f"Constraint_{obj1.name}_{obj2.name}"
    # Add rigid body constraint
    bpy.ops.rigidbody.constraint_add()
    con = empty.rigid_body_constraint
    con.type = 'FIXED'
    con.object1 = obj1
    con.object2 = obj2

# 1. Tie Beam
tie_beam = create_beam("TieBeam", (tie_beam_dim[0], member_cross_section, member_cross_section), (0,0,0))

# 2. King Posts (left and right)
king_left = create_beam("KingPost_L", (member_cross_section, member_cross_section, king_post_height), 
                        (-span/2, 0, king_post_height/2))
king_right = create_beam("KingPost_R", (member_cross_section, member_cross_section, king_post_height), 
                         (span/2, 0, king_post_height/2))

# 3. Queen Post
queen_post = create_beam("QueenPost", (member_cross_section, member_cross_section, queen_post_height), 
                         (0, 0, queen_post_height/2))

# 4. Rafters (diagonal)
# Vector from king post top to queen post top
v_left = Vector((0,0,queen_post_height)) - Vector((-span/2,0,king_post_height))
v_right = Vector((0,0,queen_post_height)) - Vector((span/2,0,king_post_height))
# Rotation angles: align local X-axis with vector
def align_rotation(vec):
    # Project to XZ plane
    vec_flat = Vector((vec.x, 0, vec.z))
    angle_z = math.atan2(vec_flat.x, vec_flat.z)  # rotation around Y axis
    # Length in XZ plane
    flat_len = vec_flat.length
    angle_y = math.atan2(-vec.y, flat_len)  # rotation around Z axis? Actually need 3D orientation.
    # Use matrix to align X axis along vec
    x_axis = Vector((1,0,0))
    rot_quat = x_axis.rotation_difference(vec)
    return rot_quat.to_euler()

# Create rafters as cubes scaled to length
rafter_left = create_beam("Rafter_L", (rafter_length, member_cross_section, member_cross_section),
                          location=((-span/2 + 0)/2, 0, (king_post_height + queen_post_height)/2),
                          rotation=align_rotation(v_left))
rafter_right = create_beam("Rafter_R", (rafter_length, member_cross_section, member_cross_section),
                           location=((span/2 + 0)/2, 0, (king_post_height + queen_post_height)/2),
                           rotation=align_rotation(v_right))

# 5. Ridge Beam
ridge = create_beam("RidgeBeam", (ridge_beam_length, member_cross_section, member_cross_section),
                    (0, 0, queen_post_height), rigid_type='ACTIVE')

# 6. Purlins (3 along each rafter)
purlins = []
rafter_vec = v_left.normalized()
for i in range(1, 4):  # 2m, 4m, 6m intervals
    d = purlin_interval * i
    if d > v_left.length:
        continue
    # Point on left rafter at distance d from king post
    p_left = Vector((-span/2,0,king_post_height)) + rafter_vec * d
    # Purlin is horizontal 12m beam at this height
    purlin = create_beam(f"Purlin_{i}", (span, purlin_cross_section, purlin_cross_section),
                         (0, 0, p_left.z), rigid_type='ACTIVE')
    purlins.append(purlin)

# 7. Fixed Constraints
create_fixed_constraint(tie_beam, king_left)
create_fixed_constraint(tie_beam, king_right)
create_fixed_constraint(tie_beam, queen_post)
create_fixed_constraint(king_left, rafter_left)
create_fixed_constraint(king_right, rafter_right)
create_fixed_constraint(queen_post, rafter_left)
create_fixed_constraint(queen_post, rafter_right)
create_fixed_constraint(queen_post, ridge)
create_fixed_constraint(rafter_left, ridge)
create_fixed_constraint(rafter_right, ridge)
# Purlin constraints
for purlin in purlins:
    create_fixed_constraint(rafter_left, purlin)
    create_fixed_constraint(rafter_right, purlin)

# 8. Apply Forces (as force field)
# Create a downward force field affecting only ridge and purlins
bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0,0,5))
force_field = bpy.context.active_object
force_field.name = "Load_Field"
bpy.ops.object.forcefield_toggle()
ff = force_field.field
ff.type = 'FORCE'
ff.strength = -force_per_beam  # Negative for downward
ff.falloff_power = 0
ff.use_max_distance = True
ff.distance_max = 20.0
# Limit to specific objects (ridge + purlins)
ff.affected_collection = bpy.data.collections.new("LoadGroup")
load_group = ff.affected_collection
for obj in [ridge] + purlins:
    if obj.name not in load_group.objects:
        load_group.objects.link(obj)

# 9. Setup Physics World
bpy.context.scene.rigidbody_world.enabled = True
bpy.context.scene.rigidbody_world.time_scale = 0.1  # Slower for stability
bpy.context.scene.frame_end = sim_frames

# 10. Verification setup: store queen post initial Z
queen_post['initial_z'] = queen_post.location.z

# Run simulation (in headless, this would be via blender --background --python script.py)
# The actual simulation would be executed by Blender's timeline.