import bpy
import mathutils

# Clear scene
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

# Define variables from parameter summary
base_platform_size = (4.0, 4.0, 0.5)
base_platform_loc = (0.0, 0.0, 0.25)
beam_cross_section = 0.2
vertical_beam_height = 3.0
level_heights = [0.0, 3.0, 6.0, 9.0]
corner_positions = [(2.0, 2.0), (2.0, -2.0), (-2.0, 2.0), (-2.0, -2.0)]
horizontal_beam_length = 4.0
top_platform_loc = (0.0, 0.0, 9.25)
load_cube_size = 1.0
load_cube_mass = 900.0
load_cube_loc = (0.0, 0.0, 9.75)
constraint_strength = 1000000.0

# Function to create a beam with physics
def create_beam(dimensions, location, name, passive=True):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location)
    beam = bpy.context.active_object
    beam.name = name
    beam.scale = (dimensions[0]/2, dimensions[1]/2, dimensions[2]/2)
    bpy.ops.rigidbody.object_add()
    beam.rigid_body.type = 'PASSIVE' if passive else 'ACTIVE'
    beam.rigid_body.collision_shape = 'BOX'
    return beam

# Function to create fixed constraint between two objects
def create_fixed_constraint(obj1, obj2, name):
    # Create empty for constraint
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=obj1.location)
    empty = bpy.context.active_object
    empty.name = name
    empty.empty_display_size = 0.5
    
    # Add rigid body constraint
    bpy.ops.rigidbody.constraint_add()
    constraint = empty.rigid_body_constraint
    constraint.type = 'FIXED'
    constraint.object1 = obj1
    constraint.object2 = obj2
    constraint.use_breaking = True
    constraint.breaking_threshold = constraint_strength
    return empty

# 1. Create base platform
base = create_beam(base_platform_size, base_platform_loc, "Base_Platform", passive=True)

# Store all objects for constraint creation
vertical_beams = []
horizontal_beams = []

# 2. Create three levels
for level in range(3):
    base_z = level_heights[level]
    top_z = level_heights[level + 1]
    
    # Vertical beams for this level
    level_verticals = []
    for i, (x, y) in enumerate(corner_positions):
        beam_z = (base_z + top_z) / 2  # Center of beam
        beam = create_beam(
            (beam_cross_section, beam_cross_section, vertical_beam_height),
            (x, y, beam_z),
            f"Vertical_L{level+1}_C{i}",
            passive=True
        )
        level_verticals.append(beam)
        vertical_beams.append(beam)
    
    # Horizontal cross-beams at top of level (except last level)
    if level < 2:
        level_horizontals = []
        # X-direction beams (front and back)
        for y_sign in [1, -1]:
            beam = create_beam(
                (horizontal_beam_length, beam_cross_section, beam_cross_section),
                (0.0, y_sign * 2.0, top_z),
                f"Horizontal_X_L{level+1}_Y{y_sign}",
                passive=True
            )
            level_horizontals.append(beam)
            horizontal_beams.append(beam)
        
        # Y-direction beams (left and right)
        for x_sign in [1, -1]:
            beam = create_beam(
                (beam_cross_section, horizontal_beam_length, beam_cross_section),
                (x_sign * 2.0, 0.0, top_z),
                f"Horizontal_Y_L{level+1}_X{x_sign}",
                passive=True
            )
            level_horizontals.append(beam)
            horizontal_beams.append(beam)
        
        # Connect vertical beams to horizontal beams
        for i, vert in enumerate(level_verticals):
            for horiz in level_horizontals:
                create_fixed_constraint(vert, horiz, f"Joint_L{level+1}_V{i}_H{horiz.name}")
    
    # Connect vertical beams to base or previous level
    if level == 0:
        # Connect to base platform
        for i, vert in enumerate(level_verticals):
            create_fixed_constraint(base, vert, f"Base_Joint_V{i}")
    else:
        # Connect to previous level's horizontals
        prev_horizontals = [obj for obj in horizontal_beams if f"L{level}" in obj.name]
        for i, vert in enumerate(level_verticals):
            for horiz in prev_horizontals:
                create_fixed_constraint(vert, horiz, f"Stack_Joint_L{level}_V{i}")

# 3. Create top platform
top_platform = create_beam(base_platform_size, top_platform_loc, "Top_Platform", passive=True)

# Connect top platform to level 3 verticals
level3_verticals = [obj for obj in vertical_beams if "L3" in obj.name]
for i, vert in enumerate(level3_verticals):
    create_fixed_constraint(top_platform, vert, f"Top_Joint_V{i}")

# 4. Create load cube
bpy.ops.mesh.primitive_cube_add(size=1.0, location=load_cube_loc)
load_cube = bpy.context.active_object
load_cube.name = "Load_Cube"
load_cube.scale = (load_cube_size/2, load_cube_size/2, load_cube_size/2)
bpy.ops.rigidbody.object_add()
load_cube.rigid_body.type = 'ACTIVE'
load_cube.rigid_body.mass = load_cube_mass
load_cube.rigid_body.collision_shape = 'BOX'

# 5. Fix load to top platform
create_fixed_constraint(top_platform, load_cube, "Load_Attachment")

# Set up physics world for verification
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 50
bpy.context.scene.frame_end = 500

print("Tower construction complete. Run simulation for 500 frames to verify stability.")