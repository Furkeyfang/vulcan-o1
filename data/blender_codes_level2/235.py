import bpy
import math
from mathutils import Matrix

# Clear scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Extract parameters from summary
c_size = 7.0
g_thick = 0.2
col_h = 3.0
col_sec = 0.2
beam_sec = 0.15
brace_sec = 0.1

g_center = (0.0, 0.0, 0.1)
col_x = 3.4
col_y = 3.4
top_z = 3.0
roof_z = 3.0
beam_x = 3.5
beam_y = 3.5
brace_len = 9.756

load_m = 1200.0
load_thick = 0.1
load_z = 3.1

# Configure rigid body world
if bpy.context.scene.rigidbody_world is None:
    bpy.ops.rigidbody.world_add()
rb_world = bpy.context.scene.rigidbody_world
rb_world.substeps_per_frame = 10
rb_world.solver_iterations = 100
rb_world.use_split_impulse = True
rb_world.collection = None  # Use default

# Helper: Add cube, scale, rigid body
def add_rigid_cube(name, loc, scale, rb_type='ACTIVE', mass=1.0):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=loc)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = scale
    bpy.ops.rigidbody.object_add()
    obj.rigid_body.type = rb_type
    obj.rigid_body.mass = mass
    obj.rigid_body.collision_margin = 0.001
    return obj

# Helper: Add fixed constraint between two objects
def add_fixed_constraint(name, obj1, obj2, loc):
    # Create empty at joint location
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=loc)
    empty = bpy.context.active_object
    empty.name = name
    bpy.ops.rigidbody.constraint_add()
    con = empty.rigid_body_constraint
    con.type = 'FIXED'
    con.object1 = obj1
    con.object2 = obj2

# 1. Ground frame
ground = add_rigid_cube("Ground", g_center, (c_size, c_size, g_thick), 'PASSIVE')

# 2. Four columns
columns = []
for sx in (-1, 1):
    for sy in (-1, 1):
        base_x = sx * col_x
        base_y = sy * col_y
        center_z = col_h / 2  # column base at Z=0
        col = add_rigid_cube(f"Col_{sx}_{sy}", (base_x, base_y, center_z), 
                            (col_sec, col_sec, col_h))
        columns.append(col)
        # Fixed constraint to ground
        joint_loc = (base_x, base_y, 0.0)
        add_fixed_constraint(f"Fix_ColGround_{sx}_{sy}", col, ground, joint_loc)

# 3. Horizontal roof beams
# Beams along X (two pieces at Y = ±beam_y)
beams_x = []
for sy in (-1, 1):
    beam = add_rigid_cube(f"BeamX_{sy}", (0.0, sy * beam_y, roof_z), 
                         (c_size, beam_sec, beam_sec))
    beams_x.append(beam)

# Beams along Y (two pieces at X = ±beam_x)
beams_y = []
for sx in (-1, 1):
    beam = add_rigid_cube(f"BeamY_{sx}", (sx * beam_x, 0.0, roof_z), 
                         (beam_sec, c_size, beam_sec))
    beams_y.append(beam)

all_beams = beams_x + beams_y

# 4. Connect columns to beams (fixed constraints at column tops)
for i, col in enumerate(columns):
    sx = (-1, 1)[(i // 2) % 2]
    sy = (-1, 1)[i % 2]
    top_loc = (sx * col_x, sy * col_y, top_z)
    # Connect to nearest X-beam (beam at Y = sy*beam_y)
    beam_x_target = beams_x[0] if sy == -1 else beams_x[1]
    add_fixed_constraint(f"Fix_ColBeamX_{sx}_{sy}", col, beam_x_target, top_loc)
    # Connect to nearest Y-beam (beam at X = sx*beam_x)
    beam_y_target = beams_y[0] if sx == -1 else beams_y[1]
    add_fixed_constraint(f"Fix_ColBeamY_{sx}_{sy}", col, beam_y_target, top_loc)

# 5. Diagonal braces
braces = []
# Diagonal directions: (sx, sy) -> (-sx, -sy)
for i, col in enumerate(columns):
    sx = (-1, 1)[(i // 2) % 2]
    sy = (-1, 1)[i % 2]
    start = (sx * col_x, sy * col_y, top_z)
    end = (-sx * beam_x, -sy * beam_y, top_z)
    # Center of brace is midpoint
    mid = ((start[0] + end[0])/2, (start[1] + end[1])/2, top_z)
    # Rotation: align Z axis to vector (end-start)
    vec = (end[0]-start[0], end[1]-start[1], 0)
    length = math.hypot(vec[0], vec[1])
    angle = math.atan2(vec[1], vec[0])
    # Create cube and rotate
    brace = add_rigid_cube(f"Brace_{sx}_{sy}", mid, (brace_sec, brace_sec, length))
    # Rotate around global Z by angle, then tilt 90° around local Y
    brace.rotation_euler = (0, math.pi/2, angle)
    braces.append(brace)
    # Fixed constraints at both ends
    add_fixed_constraint(f"Fix_BraceCol_{sx}_{sy}", brace, col, start)
    # Connect to beam intersection at opposite corner
    corner_loc = (-sx * beam_x, -sy * beam_y, top_z)
    # Which beams meet here? X-beam at Y = -sy*beam_y, Y-beam at X = -sx*beam_x
    beam_x_targ = beams_x[0] if -sy == -1 else beams_x[1]
    beam_y_targ = beams_y[0] if -sx == -1 else beams_y[1]
    add_fixed_constraint(f"Fix_BraceBeamX_{sx}_{sy}", brace, beam_x_targ, corner_loc)
    add_fixed_constraint(f"Fix_BraceBeamY_{sx}_{sy}", brace, beam_y_targ, corner_loc)

# 6. Fixed constraints between intersecting beams at each roof corner
for sx in (-1, 1):
    for sy in (-1, 1):
        corner = (sx * beam_x, sy * beam_y, top_z)
        beam_x_obj = beams_x[0] if sy == -1 else beams_x[1]
        beam_y_obj = beams_y[0] if sx == -1 else beams_y[1]
        add_fixed_constraint(f"Fix_BeamXY_{sx}_{sy}", beam_x_obj, beam_y_obj, corner)

# 7. Load plate
load_plate = add_rigid_cube("LoadPlate", (0.0, 0.0, load_z), 
                           (c_size, c_size, load_thick), 'ACTIVE', load_m)
# Increase collision margin for stability
load_plate.rigid_body.collision_margin = 0.005

# 8. Set up simulation length
bpy.context.scene.frame_end = 100

# Optional: Bake simulation for headless verification
# bpy.ops.ptcache.bake_all(bake=True)