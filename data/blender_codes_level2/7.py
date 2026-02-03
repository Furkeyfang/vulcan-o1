import bpy
import math
from mathutils import Matrix, Euler

# Clear scene
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

# Parameters from summary
L = 5.0
W = 1.0
H = 1.0
chord_dim = (5.0, 0.1, 0.1)
web_dim = (0.1, 0.1, 1.0)
diag_length = math.sqrt((L/3)**2 + H**2)  # 1.943m for 1.6667m spacing
diag_dim = (diag_length, 0.1, 0.1)
web_positions = [-L/2, -L/6, L/6, L/2]  # [-2.5, -0.83333, 0.83333, 2.5]
top_y_positions = [-W/2, W/2]  # [-0.5, 0.5]
bottom_y_positions = [-W/2, W/2]
load_dim = (0.5, 0.5, 0.5)
load_mass = 400.0
load_pos = (0.0, 0.0, H + load_dim[2]/2)  # (0,0,1.25)
constraint_cube_size = 0.05
member_mass = 100.0

# Store objects for constraint creation
objects_dict = {}

def create_cube(name, location, dimensions, rotation=(0,0,0)):
    """Create a cube with physics"""
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = (dimensions[0]/2, dimensions[1]/2, dimensions[2]/2)  # Convert to radius
    
    # Apply rotation if needed
    if rotation != (0,0,0):
        obj.rotation_euler = Euler(rotation, 'XYZ')
    
    # Add rigid body
    bpy.ops.rigidbody.object_add()
    obj.rigid_body.type = 'ACTIVE'
    obj.rigid_body.mass = member_mass
    obj.rigid_body.collision_shape = 'BOX'
    
    return obj

def add_fixed_constraint(obj1, obj2, location):
    """Create a fixed constraint between two objects at specified location"""
    # Create small cube at connection point
    bpy.ops.mesh.primitive_cube_add(size=constraint_cube_size, location=location)
    constraint_cube = bpy.context.active_object
    constraint_cube.name = f"Constraint_{obj1.name}_{obj2.name}"
    constraint_cube.hide_render = True
    constraint_cube.hide_viewport = True
    
    # Add rigid body to constraint cube
    bpy.ops.rigidbody.object_add()
    constraint_cube.rigid_body.type = 'ACTIVE'
    constraint_cube.rigid_body.mass = 0.1  # Minimal mass
    constraint_cube.rigid_body.collision_shape = 'BOX'
    
    # Create constraint from obj1 to constraint cube
    bpy.ops.rigidbody.constraint_add()
    constraint = bpy.context.active_object
    constraint.name = f"Fix_{obj1.name}_to_{constraint_cube.name}"
    constraint.empty_display_type = 'ARROWS'
    constraint.rigid_body_constraint.type = 'FIXED'
    constraint.rigid_body_constraint.object1 = obj1
    constraint.rigid_body_constraint.object2 = constraint_cube
    
    # Create constraint from obj2 to constraint cube
    bpy.ops.rigidbody.constraint_add()
    constraint2 = bpy.context.active_object
    constraint2.name = f"Fix_{obj2.name}_to_{constraint_cube.name}"
    constraint2.empty_display_type = 'ARROWS'
    constraint2.rigid_body_constraint.type = 'FIXED'
    constraint2.rigid_body_constraint.object1 = obj2
    constraint2.rigid_body_constraint.object2 = constraint_cube
    
    return constraint_cube

# Create top chords
for i, y in enumerate(top_y_positions):
    obj = create_cube(f"TopChord_{i}", (0, y, H), chord_dim)
    objects_dict[f"top_chord_{i}"] = obj

# Create bottom chords
for i, y in enumerate(bottom_y_positions):
    obj = create_cube(f"BottomChord_{i}", (0, y, 0), chord_dim)
    objects_dict[f"bottom_chord_{i}"] = obj

# Create vertical webs
for i, x in enumerate(web_positions):
    for j, y in enumerate([-W/2, W/2]):  # Front and back
        obj = create_cube(f"Web_{i}_{j}", (x, y, H/2), web_dim)
        objects_dict[f"web_{i}_{j}"] = obj
        
        # Connect to chords
        top_chord_key = f"top_chord_{0 if y<0 else 1}"
        bottom_chord_key = f"bottom_chord_{0 if y<0 else 1}"
        
        # Create constraints at top and bottom
        top_conn_pos = (x, y, H)
        bottom_conn_pos = (x, y, 0)
        
        # Store connection points for later constraint creation
        if 'connections' not in objects_dict:
            objects_dict['connections'] = []
        objects_dict['connections'].append({
            'type': 'web_top',
            'pos': top_conn_pos,
            'objs': [obj, objects_dict[top_chord_key]]
        })
        objects_dict['connections'].append({
            'type': 'web_bottom',
            'pos': bottom_conn_pos,
            'objs': [obj, objects_dict[bottom_chord_key]]
        })

# Create diagonal braces (alternating pattern)
# Front plane (y = -0.5)
diag_angle = math.atan2(H, L/3)  # Angle for diagonal
for i in range(3):  # 3 diagonals per side
    x_start = web_positions[i]
    x_end = web_positions[i+1]
    
    # Front diagonals (alternating direction)
    y = -W/2
    mid_x = (x_start + x_end) / 2
    mid_z = H/2
    
    if i % 2 == 0:  # Diagonal from bottom-left to top-right
        rotation = (0, -diag_angle, 0)
    else:  # Diagonal from top-left to bottom-right
        rotation = (0, diag_angle, 0)
    
    obj = create_cube(f"Diag_Front_{i}", (mid_x, y, mid_z), diag_dim, rotation)
    objects_dict[f"diag_front_{i}"] = obj
    
    # Store connection points
    objects_dict['connections'].append({
        'type': 'diag_front_start',
        'pos': (x_start, y, H if i%2==0 else 0),
        'objs': [obj, objects_dict[f"web_{i}_{0}" if y<0 else f"web_{i}_{1}"]]
    })
    objects_dict['connections'].append({
        'type': 'diag_front_end',
        'pos': (x_end, y, 0 if i%2==0 else H),
        'objs': [obj, objects_dict[f"web_{i+1}_{0}" if y<0 else f"web_{i+1}_{1}"]]
    })

# Back plane (y = 0.5)
for i in range(3):
    x_start = web_positions[i]
    x_end = web_positions[i+1]
    
    y = W/2
    mid_x = (x_start + x_end) / 2
    mid_z = H/2
    
    if i % 2 == 1:  # Opposite pattern to front
        rotation = (0, -diag_angle, 0)
    else:
        rotation = (0, diag_angle, 0)
    
    obj = create_cube(f"Diag_Back_{i}", (mid_x, y, mid_z), diag_dim, rotation)
    objects_dict[f"diag_back_{i}"] = obj
    
    # Store connection points
    objects_dict['connections'].append({
        'type': 'diag_back_start',
        'pos': (x_start, y, H if i%2==1 else 0),
        'objs': [obj, objects_dict[f"web_{i}_{0}" if y<0 else f"web_{i}_{1}"]]
    })
    objects_dict['connections'].append({
        'type': 'diag_back_end',
        'pos': (x_end, y, 0 if i%2==1 else H),
        'objs': [obj, objects_dict[f"web_{i+1}_{0}" if y<0 else f"web_{i+1}_{1}"]]
    })

# Create central load
bpy.ops.mesh.primitive_cube_add(size=1.0, location=load_pos)
load = bpy.context.active_object
load.name = "CentralLoad"
load.scale = (load_dim[0]/2, load_dim[1]/2, load_dim[2]/2)
bpy.ops.rigidbody.object_add()
load.rigid_body.type = 'ACTIVE'
load.rigid_body.mass = load_mass
load.rigid_body.collision_shape = 'BOX'

# Create all constraints from stored connection points
constraint_cubes = []
if 'connections' in objects_dict:
    for conn in objects_dict['connections']:
        if len(conn['objs']) == 2:
            constraint_cube = add_fixed_constraint(conn['objs'][0], conn['objs'][1], conn['pos'])
            constraint_cubes.append(constraint_cube)

# Add ground plane for stability
bpy.ops.mesh.primitive_plane_add(size=20.0, location=(0,0,-0.1))
ground = bpy.context.active_object
ground.name = "Ground"
bpy.ops.rigidbody.object_add()
ground.rigid_body.type = 'PASSIVE'

# Set physics world settings for stable simulation
bpy.context.scene.rigidbody_world.steps_per_second = 240
bpy.context.scene.rigidbody_world.solver_iterations = 50
bpy.context.scene.frame_end = 100

print("Box truss construction complete. Run simulation for 100 frames.")