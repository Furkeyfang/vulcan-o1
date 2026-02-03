import bpy
import math
from mathutils import Matrix

# Clear scene
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

# Define variables from parameter summary
L = 4.0
truss_depth = 0.5
top_z = 1.0
bottom_z = 0.5
chord_cs = 0.2
chord_len = 4.0
diag_cs = 0.2
diag_len = 0.5
num_seg = 4
seg_len = 1.0
cyl_rad = 0.05
cyl_dep = 0.1
load_mass = 200.0
load_sz = 0.5
load_x = 4.0
load_y = 0.0
load_z = 1.35
support_x = 0.0

# Joint positions (top then bottom)
joints = [
    (0.0, 0.0, top_z), (1.0, 0.0, top_z), (2.0, 0.0, top_z),
    (3.0, 0.0, top_z), (4.0, 0.0, top_z), (0.0, 0.0, bottom_z),
    (1.0, 0.0, bottom_z), (2.0, 0.0, bottom_z), (3.0, 0.0, bottom_z),
    (4.0, 0.0, bottom_z)
]

# Diagonal endpoints (start, end)
diagonals = [
    ((0.0, 0.0, bottom_z), (1.0, 0.0, top_z)),
    ((1.0, 0.0, top_z), (2.0, 0.0, bottom_z)),
    ((2.0, 0.0, bottom_z), (3.0, 0.0, top_z)),
    ((3.0, 0.0, top_z), (4.0, 0.0, bottom_z))
]

# Create top chord
bpy.ops.mesh.primitive_cube_add(size=1.0)
top_chord = bpy.context.active_object
top_chord.name = "TopChord"
top_chord.location = (L/2.0, 0.0, top_z)
top_chord.scale = (chord_cs/2.0, chord_cs/2.0, chord_len/2.0)
bpy.ops.rigidbody.object_add()
top_chord.rigid_body.type = 'ACTIVE'
top_chord.rigid_body.collision_shape = 'BOX'

# Create bottom chord  
bpy.ops.mesh.primitive_cube_add(size=1.0)
bot_chord = bpy.context.active_object
bot_chord.name = "BottomChord"
bot_chord.location = (L/2.0, 0.0, bottom_z)
bot_chord.scale = (chord_cs/2.0, chord_cs/2.0, chord_len/2.0)
bpy.ops.rigidbody.object_add()
bot_chord.rigid_body.type = 'ACTIVE'
bot_chord.rigid_body.collision_shape = 'BOX'

# Create diagonal members
for i, (start, end) in enumerate(diagonals):
    bpy.ops.mesh.primitive_cube_add(size=1.0)
    diag = bpy.context.active_object
    diag.name = f"Diagonal_{i}"
    
    # Calculate midpoint and rotation
    mid = ((start[0]+end[0])/2, (start[1]+end[1])/2, (start[2]+end[2])/2)
    dx = end[0] - start[0]
    dz = end[2] - start[2]
    length = math.sqrt(dx**2 + dz**2)
    angle = math.atan2(dz, dx)
    
    diag.location = mid
    diag.rotation_euler = (0.0, angle, 0.0)
    diag.scale = (diag_cs/2.0, diag_cs/2.0, length/2.0)
    
    bpy.ops.rigidbody.object_add()
    diag.rigid_body.type = 'ACTIVE'
    diag.rigid_body.collision_shape = 'BOX'

# Create cylindrical connectors
cylinders = []
for i, (x, y, z) in enumerate(joints):
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=1.0, depth=2.0)
    cyl = bpy.context.active_object
    cyl.name = f"Joint_{i}"
    cyl.location = (x, y, z)
    cyl.rotation_euler = (0.0, 0.0, math.pi/2.0)  # Orient along Y-axis
    cyl.scale = (cyl_rad, cyl_rad, cyl_dep/2.0)
    
    bpy.ops.rigidbody.object_add()
    # First two joints (top and bottom at X=0) are support
    if (x == support_x and z == top_z) or (x == support_x and z == bottom_z):
        cyl.rigid_body.type = 'PASSIVE'
    else:
        cyl.rigid_body.type = 'ACTIVE'
    cyl.rigid_body.collision_shape = 'CYLINDER'
    cylinders.append(cyl)

# Create load cube
bpy.ops.mesh.primitive_cube_add(size=1.0)
load = bpy.context.active_object
load.name = "Load"
load.location = (load_x, load_y, load_z)
load.scale = (load_sz/2.0, load_sz/2.0, load_sz/2.0)
bpy.ops.rigidbody.object_add()
load.rigid_body.type = 'ACTIVE'
load.rigid_body.mass = load_mass
load.rigid_body.collision_shape = 'BOX'

# Create fixed constraints between all structural elements
# First get all structural objects (excluding load)
structural = [top_chord, bot_chord] + [obj for obj in bpy.data.objects if "Diagonal" in obj.name] + cylinders

# Create constraints between each cylinder and intersecting members
for cyl in cylinders:
    cyl_pos = cyl.location
    
    # Check if cylinder is at a chord endpoint
    for chord in [top_chord, bot_chord]:
        # Create constraint
        bpy.ops.object.select_all(action='DESELECT')
        cyl.select_set(True)
        chord.select_set(True)
        bpy.context.view_layer.objects.active = cyl
        bpy.ops.rigidbody.connect_add(type='FIXED')
        
        # Configure constraint
        constraint = bpy.context.object.rigid_body_constraint
        constraint.object1 = cyl
        constraint.object2 = chord
    
    # Check if cylinder is at a diagonal endpoint
    for diag in [obj for obj in bpy.data.objects if "Diagonal" in obj.name]:
        diag_end1 = diag.matrix_world @ ((-diag_cs/2, 0, -diag.dimensions.z/2))
        diag_end2 = diag.matrix_world @ ((-diag_cs/2, 0, diag.dimensions.z/2))
        
        # Simple distance check (approximate)
        dist1 = (Vector(diag_end1) - Vector(cyl_pos)).length
        dist2 = (Vector(diag_end2) - Vector(cyl_pos)).length
        if dist1 < 0.15 or dist2 < 0.15:
            bpy.ops.object.select_all(action='DESELECT')
            cyl.select_set(True)
            diag.select_set(True)
            bpy.context.view_layer.objects.active = cyl
            bpy.ops.rigidbody.connect_add(type='FIXED')
            
            constraint = bpy.context.object.rigid_body_constraint
            constraint.object1 = cyl
            constraint.object2 = diag

# Set up rigid body world
bpy.context.scene.rigidbody_world.steps_per_second = 240
bpy.context.scene.rigidbody_world.solver_iterations = 50
bpy.context.scene.rigidbody_world.use_split_impulse = True
bpy.context.scene.rigidbody_world.time_scale = 1.0