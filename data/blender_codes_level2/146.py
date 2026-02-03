import bpy
import mathutils

# Clear existing scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Parameters from summary
cube_dim = (2.0, 2.0, 2.0)
num_cubes = 10
base_loc = (0.0, 0.0, 0.0)
stack_spacing = 2.0
load_mass = 500.0
load_radius = 0.5
load_height = 20.0
sim_frames = 500
rb_damping = 0.5
rb_angular_damping = 0.5
constraint_margin = 0.04

# Set simulation end frame
bpy.context.scene.frame_end = sim_frames

# Enable rigid body world
if bpy.context.scene.rigidbody_world is None:
    bpy.ops.rigidbody.world_add()
bpy.context.scene.rigidbody_world.substeps_per_frame = 10
bpy.context.scene.rigidbody_world.solver_iterations = 50

# Create mast cubes
cube_objects = []
for i in range(num_cubes):
    # Calculate position
    z_pos = base_loc[2] + i * stack_spacing
    location = (base_loc[0], base_loc[1], z_pos)
    
    # Create cube
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location)
    cube = bpy.context.active_object
    cube.name = f"Mast_Cube_{i+1:02d}"
    cube.scale = cube_dim
    
    # Add rigid body
    bpy.ops.rigidbody.object_add()
    if i == 0:
        # Base cube is passive (fixed anchor)
        cube.rigid_body.type = 'PASSIVE'
        cube.rigid_body.collision_shape = 'BOX'
        cube.rigid_body.friction = 1.0
        cube.rigid_body.restitution = 0.0
    else:
        # Upper cubes are active but constrained
        cube.rigid_body.type = 'ACTIVE'
        cube.rigid_body.collision_shape = 'BOX'
        cube.rigid_body.mass = 100.0  # Assume concrete density ~ 25 kg/m³ × 8 m³
        cube.rigid_body.friction = 1.0
        cube.rigid_body.restitution = 0.0
        cube.rigid_body.linear_damping = rb_damping
        cube.rigid_body.angular_damping = rb_angular_damping
    
    cube_objects.append(cube)

# Create fixed constraints between adjacent cubes
for i in range(num_cubes - 1):
    parent_cube = cube_objects[i]
    child_cube = cube_objects[i + 1]
    
    # Create empty object for constraint
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=parent_cube.location)
    constraint_empty = bpy.context.active_object
    constraint_empty.name = f"Fixed_Constraint_{i+1:02d}"
    
    # Add rigid body constraint
    bpy.ops.rigidbody.constraint_add()
    constraint = constraint_empty.rigid_body_constraint
    constraint.type = 'FIXED'
    constraint.object1 = parent_cube
    constraint.object2 = child_cube
    constraint.disable_collisions = True
    constraint.breaking_threshold = 10000.0  # Very high to prevent breaking
    constraint.use_breaking = True
    constraint.margin = constraint_margin
    
    # Parent constraint to parent cube for organization
    constraint_empty.parent = parent_cube

# Create lateral load mass (sphere)
bpy.ops.mesh.primitive_uv_sphere_add(radius=load_radius, location=(0.0, 0.0, load_height))
load_sphere = bpy.context.active_object
load_sphere.name = "Lateral_Load_Mass"

# Add rigid body to load
bpy.ops.rigidbody.object_add()
load_sphere.rigid_body.type = 'ACTIVE'
load_sphere.rigid_body.collision_shape = 'SPHERE'
load_sphere.rigid_body.mass = load_mass
load_sphere.rigid_body.linear_damping = 0.1
load_sphere.rigid_body.angular_damping = 0.1

# Create fixed constraint between top cube and load
top_cube = cube_objects[-1]
bpy.ops.object.empty_add(type='PLAIN_AXES', location=top_cube.location)
load_constraint_empty = bpy.context.active_object
load_constraint_empty.name = "Load_Constraint"

bpy.ops.rigidbody.constraint_add()
load_constraint = load_constraint_empty.rigid_body_constraint
load_constraint.type = 'FIXED'
load_constraint.object1 = top_cube
load_constraint.object2 = load_sphere
load_constraint.disable_collisions = False
load_constraint.margin = constraint_margin
load_constraint_empty.parent = top_cube

# Apply lateral force using force field
bpy.ops.object.effector_add(type='FORCE', location=(0.0, 0.0, load_height))
force_field = bpy.context.active_object
force_field.name = "Lateral_Force_Field"
force_field.field.strength = load_mass * 9.81  # F = m * g (500 kg × 9.81 m/s²)
force_field.field.direction = (1.0, 0.0, 0.0)  # X-direction lateral force
force_field.field.falloff_power = 0.0
force_field.field.use_max_distance = True
force_field.field.distance_max = 1.0  # Only affect objects within 1m

# Set gravity to standard Earth gravity
bpy.context.scene.rigidbody_world.gravity = (0.0, 0.0, -9.81)

# Organize scene collection
mast_collection = bpy.data.collections.new("Crane_Mast")
bpy.context.scene.collection.children.link(mast_collection)

constraints_collection = bpy.data.collections.new("Constraints")
bpy.context.scene.collection.children.link(constraints_collection)

# Move objects to appropriate collections
for obj in cube_objects + [load_sphere]:
    for col in obj.users_collection:
        col.objects.unlink(obj)
    mast_collection.objects.link(obj)

for obj in [obj for obj in bpy.data.objects if "Constraint" in obj.name]:
    for col in obj.users_collection:
        col.objects.unlink(obj)
    constraints_collection.objects.link(obj)

# Link force field to scene collection
bpy.context.scene.collection.objects.link(force_field)

print(f"Crane mast construction complete with {num_cubes} cubes and {load_mass} kg lateral load.")