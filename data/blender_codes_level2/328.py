import bpy
import mathutils
from mathutils import Vector, Matrix
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Parameters from summary
col_w = 1.0
col_d = 1.0
col_h = 16.0
col_center_z = 8.0
beam_cs = 0.2
beam_len = 4.062
beam_starts = [Vector((0.5,0,0)), Vector((0,0.5,4)), Vector((-0.5,0,8)), Vector((0,-0.5,12))]
beam_ends = [Vector((0,0.5,4)), Vector((-0.5,0,8)), Vector((0,-0.5,12)), Vector((0.5,0,16))]
load_size = 0.5
load_mass = 1300.0
load_z = 16.25
con_radius = 0.1
frames = 100

# Enable rigid body physics
if bpy.context.scene.rigidbody_world is None:
    bpy.ops.rigidbody.world_add()

# 1. Create central column
bpy.ops.mesh.primitive_cube_add(size=2.0, location=(0,0,col_center_z))
col = bpy.context.active_object
col.name = "CentralColumn"
col.scale = (col_w/2.0, col_d/2.0, col_h/2.0)  # Scale from default 2m cube
bpy.ops.object.transform_apply(scale=True)
bpy.ops.rigidbody.object_add()
col.rigid_body.type = 'PASSIVE'
col.rigid_body.collision_shape = 'BOX'

# 2. Create spiral bracing beams
def create_beam(start, end, name):
    """Create a beam between two points with proper orientation"""
    # Calculate beam properties
    vec = end - start
    length = vec.length
    center = (start + end) / 2.0
    
    # Create beam (default 2m cube)
    bpy.ops.mesh.primitive_cube_add(size=2.0, location=center)
    beam = bpy.context.active_object
    beam.name = name
    
    # Scale to desired dimensions
    # Scale Z by length/2 (since default cube is 2m tall)
    # Scale X and Y by beam_cs/2
    beam.scale = (beam_cs/2.0, beam_cs/2.0, length/2.0)
    bpy.ops.object.transform_apply(scale=True)
    
    # Rotate to align with direction vector
    if vec.length > 0:
        # Default cube orientation has local Z up
        z_axis = Vector((0, 0, 1))
        rot_quat = z_axis.rotation_difference(vec)
        beam.rotation_mode = 'QUATERNION'
        beam.rotation_quaternion = rot_quat
    
    # Add rigid body
    bpy.ops.rigidbody.object_add()
    beam.rigid_body.type = 'PASSIVE'
    beam.rigid_body.collision_shape = 'BOX'
    
    return beam

beams = []
for i, (start, end) in enumerate(zip(beam_starts, beam_ends)):
    beam = create_beam(start, end, f"Beam_{i+1}")
    beams.append(beam)

# 3. Create fixed constraints between beams and column
def create_fixed_constraint(obj_a, obj_b, pivot_loc, name):
    """Create a fixed constraint at specified pivot location"""
    # Create empty for constraint
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=pivot_loc)
    empty = bpy.context.active_object
    empty.name = name
    empty.empty_display_size = con_radius
    
    # Add rigid body constraint
    bpy.ops.rigidbody.constraint_add()
    empty.rigid_body_constraint.type = 'FIXED'
    empty.rigid_body_constraint.object1 = obj_a
    empty.rigid_body_constraint.object2 = obj_b
    empty.rigid_body_constraint.use_breaking = True
    empty.rigid_body_constraint.breaking_threshold = 10000.0  # High threshold

# Create constraints at beam endpoints
for i, beam in enumerate(beams):
    # Start point constraint
    create_fixed_constraint(
        beam, col, 
        beam_starts[i], 
        f"Con_Beam{i+1}_Start"
    )
    # End point constraint
    create_fixed_constraint(
        beam, col, 
        beam_ends[i], 
        f"Con_Beam{i+1}_End"
    )

# 4. Create load cube
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0,0,load_z))
load = bpy.context.active_object
load.name = "Load"
load.scale = (load_size/2.0, load_size/2.0, load_size/2.0)
bpy.ops.object.transform_apply(scale=True)
bpy.ops.rigidbody.object_add()
load.rigid_body.type = 'ACTIVE'
load.rigid_body.mass = load_mass
load.rigid_body.collision_shape = 'BOX'
load.rigid_body.use_deactivation = False

# 5. Configure simulation
bpy.context.scene.frame_end = frames
bpy.context.scene.rigidbody_world.time_scale = 1.0
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 50

# Optional: Add floor for complete stability
bpy.ops.mesh.primitive_plane_add(size=20.0, location=(0,0,-0.1))
floor = bpy.context.active_object
floor.name = "Floor"
bpy.ops.rigidbody.object_add()
floor.rigid_body.type = 'PASSIVE'

print(f"Structure built. Simulation ready for {frames} frames.")