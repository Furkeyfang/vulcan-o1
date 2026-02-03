import bpy
import mathutils
from mathutils import Vector, Matrix

# Clear scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Extract parameters from summary
frame_h = 12.0
frame_w = 4.0
frame_d = 0.5
base_half = 2.0
cross = 0.5
beam_len = 4.0
braceA_len = 12.165
braceB_len = 7.211
col_pos = [(-2, -2, 0), (2, -2, 0), (-2, 2, 0), (2, 2, 0)]
beam_pos = [(-2, -2, 12), (2, -2, 12), (-2, 2, 12), (2, 2, 12)]
beam_or = ['x', 'x', 'y', 'y']
braceA_s = Vector((-2, -2, 12))
braceA_e = Vector((-2, 0, 0))
braceB_s = Vector((-2, -2, 12))
braceB_e = Vector((-2, 2, 6))
load_m = 800.0
load_pos = (0, 0, 12)
load_sz = 0.8
sim_frames = 100

# Enable rigid body world
if not bpy.context.scene.rigidbody_world:
    bpy.ops.rigidbody.world_add()
rb_world = bpy.context.scene.rigidbody_world
rb_world.steps_per_second = 60
rb_world.solver_iterations = 50

# Helper: Create cube with rigid body
def create_cube(name, location, scale, rb_type='PASSIVE', mass=1.0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = scale
    bpy.ops.rigidbody.object_add()
    obj.rigid_body.type = rb_type
    obj.rigid_body.mass = mass
    obj.rigid_body.collision_shape = 'BOX'
    return obj

# Helper: Create diagonal brace
def create_brace(name, start, end, cross_section):
    direction = end - start
    length = direction.length
    center = (start + end) / 2
    
    # Create rotated cube aligned with direction
    bpy.ops.mesh.primitive_cube_add(size=1, location=center)
    obj = bpy.context.active_object
    obj.name = name
    
    # Scale: cross-section × cross-section × length
    obj.scale = (cross_section/2, cross_section/2, length/2)
    
    # Align Z axis with direction
    z_axis = Vector((0, 0, 1))
    rot_quat = z_axis.rotation_difference(direction.normalized())
    obj.rotation_mode = 'QUATERNION'
    obj.rotation_quaternion = rot_quat
    
    # Add rigid body
    bpy.ops.rigidbody.object_add()
    obj.rigid_body.type = 'PASSIVE'
    return obj

# Helper: Create fixed constraint between two objects
def create_fixed_constraint(obj1, obj2):
    bpy.ops.object.select_all(action='DESELECT')
    obj1.select_set(True)
    bpy.context.view_layer.objects.active = obj1
    bpy.ops.rigidbody.constraint_add()
    con = bpy.context.active_object
    con.name = f"Fix_{obj1.name}_{obj2.name}"
    con.rigid_body_constraint.type = 'FIXED'
    con.rigid_body_constraint.object1 = obj1
    con.rigid_body_constraint.object2 = obj2

# Create 4 vertical columns
columns = []
for i, pos in enumerate(col_pos):
    col = create_cube(f"Column_{i}", pos, (cross/2, cross/2, frame_h/2))
    columns.append(col)

# Create 4 horizontal top beams
beams = []
for i, (pos, orient) in enumerate(zip(beam_pos, beam_or)):
    if orient == 'x':
        scale = (beam_len/2, cross/2, cross/2)
    else:  # 'y'
        scale = (cross/2, beam_len/2, cross/2)
    beam = create_cube(f"Beam_{i}", pos, scale)
    beams.append(beam)

# Create diagonal braces on left side
braceA = create_brace("Brace_A", braceA_s, braceA_e, cross)
braceB = create_brace("Brace_B", braceB_s, braceB_e, cross)

# Create load cube at center
load = create_cube("Load", load_pos, (load_sz/2, load_sz/2, load_sz/2), 'ACTIVE', load_m)
load.rigid_body.linear_damping = 0.1  # Reduce oscillation

# Create fixed constraints for all connections
all_elements = columns + beams + [braceA, braceB]
for i, elem1 in enumerate(all_elements):
    for elem2 in all_elements[i+1:]:
        # Check proximity for connection (within 0.6m)
        if (elem1.location - elem2.location).length < 0.6:
            create_fixed_constraint(elem1, elem2)

# Set simulation frames
bpy.context.scene.frame_end = sim_frames

# Bake simulation for headless verification
bpy.ops.ptcache.bake_all(bake=True)

print("Asymmetric frame construction complete. Simulation baked for 100 frames.")