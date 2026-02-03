import bpy
import math
from mathutils import Vector

# Clear existing scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Parameters from summary
tower_height = 10.0
bay_height = 1.0
cross_section = 0.1
width = 1.0
depth = 1.0
num_bays = 10
num_levels = 11
diagonal_length = 1.41421356237  # sqrt(2)
load_mass_kg = 300.0
gravity = 9.81
load_force_newton = load_mass_kg * gravity
base_z = 0.0
joint_tolerance = 0.001
corner_coords = [(0,0), (1,0), (1,1), (0,1)]

# Store all created members for constraint creation
members = []

def create_member(name, location, rotation, dimensions, is_static=False):
    """Create a structural member as cube with rigid body physics"""
    # Create cube
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location)
    member = bpy.context.active_object
    member.name = name
    member.scale = dimensions
    
    # Apply rotation
    member.rotation_euler = rotation
    
    # Add rigid body
    bpy.ops.rigidbody.object_add()
    if is_static:
        member.rigid_body.type = 'PASSIVE'
    else:
        member.rigid_body.type = 'ACTIVE'
        member.rigid_body.collision_shape = 'BOX'
    
    return member

# Create vertical columns at four corners
for i, (x, y) in enumerate(corner_coords):
    for level in range(num_bays):  # 10 segments per column
        z_pos = base_z + (level * bay_height) + (bay_height / 2)
        vert = create_member(
            name=f"Vertical_{i}_{level}",
            location=(x, y, z_pos),
            rotation=(0, 0, 0),
            dimensions=(cross_section, cross_section, bay_height),
            is_static=(level == 0)  # Base level is passive
        )
        members.append(vert)

# Create horizontal members in X and Y directions at each level
for level in range(num_levels):  # 11 levels (0 to 10 inclusive)
    z_pos = base_z + (level * bay_height)
    
    # X-direction horizontals (front and back)
    for y in [0, depth]:
        horiz_x = create_member(
            name=f"Horizontal_X_{y}_{level}",
            location=(width/2, y, z_pos),
            rotation=(0, 0, 0),
            dimensions=(width, cross_section, cross_section),
            is_static=(level == 0)
        )
        members.append(horiz_x)
    
    # Y-direction horizontals (left and right)
    for x in [0, width]:
        horiz_y = create_member(
            name=f"Horizontal_Y_{x}_{level}",
            location=(x, depth/2, z_pos),
            rotation=(0, 0, 0),
            dimensions=(cross_section, depth, cross_section),
            is_static=(level == 0)
        )
        members.append(horiz_y)

# Create diagonal members in alternating pattern
# Each bay has diagonals in both directions for each vertical face
for bay in range(num_bays):
    z_base = base_z + (bay * bay_height)
    
    # Front face (Y=0)
    # Diagonal 1: bottom-left to top-right
    diag1 = create_member(
        name=f"Diagonal_Front1_{bay}",
        location=(width/2, 0, z_base + bay_height/2),
        rotation=(0, -math.pi/4, 0),  # 45° rotation in XZ plane
        dimensions=(cross_section, cross_section, diagonal_length),
        is_static=(bay == 0)
    )
    members.append(diag1)
    
    # Diagonal 2: bottom-right to top-left
    diag2 = create_member(
        name=f"Diagonal_Front2_{bay}",
        location=(width/2, 0, z_base + bay_height/2),
        rotation=(0, math.pi/4, 0),  # -45° rotation
        dimensions=(cross_section, cross_section, diagonal_length),
        is_static=(bay == 0)
    )
    members.append(diag2)
    
    # Back face (Y=depth) - same pattern
    diag3 = create_member(
        name=f"Diagonal_Back1_{bay}",
        location=(width/2, depth, z_base + bay_height/2),
        rotation=(0, -math.pi/4, 0),
        dimensions=(cross_section, cross_section, diagonal_length),
        is_static=(bay == 0)
    )
    members.append(diag3)
    
    diag4 = create_member(
        name=f"Diagonal_Back2_{bay}",
        location=(width/2, depth, z_base + bay_height/2),
        rotation=(0, math.pi/4, 0),
        dimensions=(cross_section, cross_section, diagonal_length),
        is_static=(bay == 0)
    )
    members.append(diag4)
    
    # Left face (X=0) - rotated 90° for YZ plane
    diag5 = create_member(
        name=f"Diagonal_Left1_{bay}",
        location=(0, depth/2, z_base + bay_height/2),
        rotation=(math.pi/4, 0, 0),  # 45° rotation in YZ plane
        dimensions=(cross_section, cross_section, diagonal_length),
        is_static=(bay == 0)
    )
    members.append(diag5)
    
    diag6 = create_member(
        name=f"Diagonal_Left2_{bay}",
        location=(0, depth/2, z_base + bay_height/2),
        rotation=(-math.pi/4, 0, 0),  # -45° rotation
        dimensions=(cross_section, cross_section, diagonal_length),
        is_static=(bay == 0)
    )
    members.append(diag6)
    
    # Right face (X=width)
    diag7 = create_member(
        name=f"Diagonal_Right1_{bay}",
        location=(width, depth/2, z_base + bay_height/2),
        rotation=(math.pi/4, 0, 0),
        dimensions=(cross_section, cross_section, diagonal_length),
        is_static=(bay == 0)
    )
    members.append(diag7)
    
    diag8 = create_member(
        name=f"Diagonal_Right2_{bay}",
        location=(width, depth/2, z_base + bay_height/2),
        rotation=(-math.pi/4, 0, 0),
        dimensions=(cross_section, cross_section, diagonal_length),
        is_static=(bay == 0)
    )
    members.append(diag8)

# Create load application plate at top center
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(width/2, depth/2, tower_height))
load_plate = bpy.context.active_object
load_plate.name = "Load_Plate"
load_plate.scale = (0.3, 0.3, 0.05)  # Small plate for force application
bpy.ops.rigidbody.object_add()
load_plate.rigid_body.type = 'ACTIVE'

# Apply lateral force (in positive X direction)
load_plate.rigid_body.kinematic = True  # Kinematic to apply force
# Force will be applied in animation or simulation setup
# In headless mode, we can set initial velocity or use force field
# Create force field for lateral load
bpy.ops.object.effector_add(type='FORCE', location=(width/2, depth/2, tower_height))
force_field = bpy.context.active_object
force_field.name = "Lateral_Force"
force_field.field.strength = load_force_newton
force_field.field.direction = 'X'  # Positive X direction
force_field.field.falloff_power = 0
force_field.field.use_max_distance = True
force_field.field.distance_max = 0.5  # Only affect nearby objects

# Create FIXED constraints between adjacent members at joints
# Simplified approach: connect load plate to top horizontals
for member in members:
    if abs(member.location.z - tower_height) < 0.5:  # Top level members
        bpy.ops.object.select_all(action='DESELECT')
        load_plate.select_set(True)
        member.select_set(True)
        bpy.context.view_layer.objects.active = load_plate
        bpy.ops.rigidbody.constraint_add(type='FIXED')

# Set up rigid body world for simulation
if bpy.context.scene.rigidbody_world is None:
    bpy.ops.rigidbody.world_add()
bpy.context.scene.rigidbody_world.enabled = True
bpy.context.scene.rigidbody_world.substeps_per_frame = 10
bpy.context.scene.rigidbody_world.solver_iterations = 50

print(f"Warren Truss Tower created with {len(members)} structural members")
print(f"Lateral load of {load_force_newton:.1f} N applied at top center")