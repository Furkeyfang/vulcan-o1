import bpy
import mathutils

# Clear existing scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Extract parameters from summary
levels = 5
outer_length = 3.0
outer_width = 2.0
level_height = 3.0
wall_thickness = 0.2
post_cross = 0.2
post_x_offset = outer_length/2 - post_cross/2  # 1.4
post_y_offset = outer_width/2 - post_cross/2   # 0.9
long_beam_dim = (outer_length, wall_thickness, wall_thickness)
short_beam_dim = (wall_thickness, outer_width, wall_thickness)
load_mass = 1000.0
load_size = 1.0
load_z_position = levels * level_height + load_size/2  # 15.5
simulation_frames = 500

# Store object references for constraint creation
level_objects = [[] for _ in range(levels)]  # List per level
post_objects = [[] for _ in range(levels)]   # Corner posts per level

# Enable rigid body physics
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 50

# Create levels
for level in range(levels):
    base_z = level * level_height
    center_z = base_z + level_height/2
    
    # Create 4 corner posts for this level
    post_locations = [
        (post_x_offset, post_y_offset, center_z),
        (post_x_offset, -post_y_offset, center_z),
        (-post_x_offset, post_y_offset, center_z),
        (-post_x_offset, -post_y_offset, center_z)
    ]
    
    for i, loc in enumerate(post_locations):
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=loc)
        post = bpy.context.active_object
        post.scale = (post_cross/2, post_cross/2, level_height/2)
        post.name = f"Level_{level+1}_Post_{i+1}"
        bpy.ops.object.transform_apply(scale=True)
        bpy.ops.rigidbody.object_add()
        post.rigid_body.type = 'ACTIVE'
        post.rigid_body.collision_shape = 'BOX'
        post.rigid_body.mass = 50.0  # Reasonable mass for steel post
        level_objects[level].append(post)
        post_objects[level].append(post)
    
    # Create horizontal beams (bottom and top)
    beam_locations = [
        # Bottom long beams (Y = ±0.9)
        (0.0, post_y_offset, base_z),
        (0.0, -post_y_offset, base_z),
        # Top long beams (Y = ±0.9)
        (0.0, post_y_offset, base_z + level_height),
        (0.0, -post_y_offset, base_z + level_height),
        # Bottom short beams (X = ±1.4)
        (post_x_offset, 0.0, base_z),
        (-post_x_offset, 0.0, base_z),
        # Top short beams (X = ±1.4)
        (post_x_offset, 0.0, base_z + level_height),
        (-post_x_offset, 0.0, base_z + level_height)
    ]
    
    beam_dimensions = [long_beam_dim, long_beam_dim, long_beam_dim, long_beam_dim,
                      short_beam_dim, short_beam_dim, short_beam_dim, short_beam_dim]
    
    for i, (loc, dim) in enumerate(zip(beam_locations, beam_dimensions)):
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=loc)
        beam = bpy.context.active_object
        beam.scale = (dim[0]/2, dim[1]/2, dim[2]/2)
        beam.name = f"Level_{level+1}_Beam_{i+1}"
        bpy.ops.object.transform_apply(scale=True)
        bpy.ops.rigidbody.object_add()
        beam.rigid_body.type = 'ACTIVE'
        beam.rigid_body.collision_shape = 'BOX'
        beam.rigid_body.mass = 30.0  # Reasonable mass for steel beam
        level_objects[level].append(beam)

# Create fixed constraints within each level
for level in range(levels):
    objects_in_level = level_objects[level]
    
    # Connect each post to all beams in same level
    for post in post_objects[level]:
        for beam in objects_in_level:
            if beam != post:  # Don't constrain object to itself
                # Create constraint object
                bpy.ops.object.empty_add(type='PLAIN_AXES', location=post.location)
                constraint_empty = bpy.context.active_object
                constraint_empty.name = f"Constraint_L{level+1}_{post.name[-6:]}_to_{beam.name[-6:]}"
                
                # Add rigid body constraint
                bpy.ops.rigidbody.constraint_add()
                constraint = constraint_empty.rigid_body_constraint
                constraint.type = 'FIXED'
                constraint.object1 = post
                constraint.object2 = beam

# Create fixed constraints between levels (posts to posts)
for level in range(1, levels):
    top_posts = post_objects[level-1]
    bottom_posts = post_objects[level]
    
    for top_post, bottom_post in zip(top_posts, bottom_posts):
        # Create constraint at midpoint
        mid_point = (mathutils.Vector(top_post.location) + 
                    mathutils.Vector(bottom_post.location)) / 2
        
        bpy.ops.object.empty_add(type='PLAIN_AXES', location=mid_point)
        constraint_empty = bpy.context.active_object
        constraint_empty.name = f"Constraint_L{level}_to_L{level+1}_Post{top_post.name[-1]}"
        
        bpy.ops.rigidbody.constraint_add()
        constraint = constraint_empty.rigid_body_constraint
        constraint.type = 'FIXED'
        constraint.object1 = top_post
        constraint.object2 = bottom_post

# Create load cube
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, 0.0, load_z_position))
load_cube = bpy.context.active_object
load_cube.scale = (load_size/2, load_size/2, load_size/2)
load_cube.name = "Load_1000kg"
bpy.ops.object.transform_apply(scale=True)
bpy.ops.rigidbody.object_add()
load_cube.rigid_body.type = 'ACTIVE'
load_cube.rigid_body.collision_shape = 'BOX'
load_cube.rigid_body.mass = load_mass

# Fix load to top level beams
top_beams = [obj for obj in level_objects[-1] if "Beam" in obj.name and abs(obj.location.z - (levels-1)*level_height - level_height) < 0.1]

for beam in top_beams[:2]:  # Connect to two top beams for stability
    bpy.ops.object.empty_add(type='PLAIN_AXES', 
                           location=((load_cube.location + beam.location) / 2))
    constraint_empty = bpy.context.active_object
    constraint_empty.name = f"Constraint_Load_to_{beam.name}"
    
    bpy.ops.rigidbody.constraint_add()
    constraint = constraint_empty.rigid_body_constraint
    constraint.type = 'FIXED'
    constraint.object1 = load_cube
    constraint.object2 = beam

# Create base platform (static ground)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, 0.0, -0.5))
base = bpy.context.active_object
base.scale = (10.0, 10.0, 0.5)
base.name = "Ground"
bpy.ops.object.transform_apply(scale=True)
bpy.ops.rigidbody.object_add()
base.rigid_body.type = 'PASSIVE'
base.rigid_body.collision_shape = 'BOX'

# Fix bottom posts to ground
for post in post_objects[0]:
    bpy.ops.object.empty_add(type='PLAIN_AXES', 
                           location=((post.location + mathutils.Vector((0,0,-0.25))) / 2))
    constraint_empty = bpy.context.active_object
    constraint_empty.name = f"Constraint_{post.name}_to_Ground"
    
    bpy.ops.rigidbody.constraint_add()
    constraint = constraint_empty.rigid_body_constraint
    constraint.type = 'FIXED'
    constraint.object1 = post
    constraint.object2 = base

# Set simulation parameters
bpy.context.scene.frame_end = simulation_frames
bpy.context.scene.rigidbody_world.enabled = True

print(f"Scaffold construction complete. {len(level_objects)} levels created.")
print(f"Total components: {sum(len(level) for level in level_objects) + 2} objects")
print(f"Load: {load_mass} kg at Z={load_z_position}m")
print(f"Simulation ready for {simulation_frames} frames")