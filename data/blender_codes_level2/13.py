import bpy
import math
from mathutils import Vector, Matrix

# Clear existing scene
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

# Define parameters from summary
tie_length = 6.0
tie_width = 0.2
tie_height = 0.2
tie_start = Vector((-3.0, 0.0, 0.0))
tie_end = Vector((3.0, 0.0, 0.0))
tie_center = Vector((0.0, 0.0, 0.0))

rafter_length = math.sqrt(3**2 + 2**2)  # sqrt(13)
rafter_width = 0.2
rafter_height = 0.2
left_rafter_start = Vector((-3.0, 0.0, 0.0))
left_rafter_end = Vector((0.0, 0.0, 2.0))
left_rafter_mid = Vector((-1.5, 0.0, 1.0))
right_rafter_start = Vector((3.0, 0.0, 0.0))
right_rafter_end = Vector((0.0, 0.0, 2.0))
right_rafter_mid = Vector((1.5, 0.0, 1.0))

king_length = 2.0
king_width = 0.2
king_height = 0.2
king_start = Vector((0.0, 0.0, 0.0))
king_end = Vector((0.0, 0.0, 2.0))
king_center = Vector((0.0, 0.0, 1.0))

force_magnitude = 4905.0
force_location = Vector((0.0, 0.0, 2.0))
simulation_frames = 100

# Function to create beam with correct orientation
def create_beam(name, length, width, height, location, direction):
    """Create a beam oriented along direction vector"""
    # Create cube (default 2x2x2)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location)
    beam = bpy.context.active_object
    beam.name = name
    
    # Scale: length along X, width along Y, height along Z
    beam.scale = (length/2.0, width/2.0, height/2.0)
    
    # Calculate rotation to align local X-axis with direction
    if direction.length > 0:
        direction.normalize()
        x_axis = Vector((1.0, 0.0, 0.0))
        rotation = x_axis.rotation_difference(direction)
        beam.rotation_euler = rotation.to_euler()
    
    # Add rigid body
    bpy.ops.rigidbody.object_add()
    beam.rigid_body.type = 'ACTIVE'
    beam.rigid_body.collision_shape = 'BOX'
    beam.rigid_body.mass = length * width * height * 500  # Density-based mass
    
    return beam

# Create tie beam (horizontal along X)
tie_direction = tie_end - tie_start
tie_beam = create_beam("TieBeam", tie_length, tie_width, tie_height, 
                       tie_center, tie_direction)

# Create left rafter
left_dir = left_rafter_end - left_rafter_start
left_rafter = create_beam("LeftRafter", rafter_length, rafter_width, 
                          rafter_height, left_rafter_mid, left_dir)

# Create right rafter
right_dir = right_rafter_end - right_rafter_start
right_rafter = create_beam("RightRafter", rafter_length, rafter_width, 
                           rafter_height, right_rafter_mid, right_dir)

# Create king post (vertical along Z)
king_direction = king_end - king_start
king_post = create_beam("KingPost", king_length, king_width, 
                        king_height, king_center, king_direction)

# Function to create fixed constraint between two objects
def create_fixed_constraint(obj_a, obj_b, location, name):
    """Create a fixed constraint between two objects at location"""
    # Create empty for constraint
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=location)
    empty = bpy.context.active_object
    empty.name = name
    
    # Add rigid body constraint
    bpy.ops.rigidbody.constraint_add()
    constraint = empty.rigid_body_constraint
    constraint.type = 'FIXED'
    constraint.object1 = obj_a
    constraint.object2 = obj_b
    
    return empty

# Create fixed constraints at all joints
constraints = []
constraints.append(create_fixed_constraint(tie_beam, left_rafter, 
                                          left_rafter_start, "Constraint_LeftJoint"))
constraints.append(create_fixed_constraint(tie_beam, right_rafter, 
                                          right_rafter_start, "Constraint_RightJoint"))
constraints.append(create_fixed_constraint(left_rafter, king_post, 
                                          left_rafter_end, "Constraint_ApexLeft"))
constraints.append(create_fixed_constraint(right_rafter, king_post, 
                                          right_rafter_end, "Constraint_ApexRight"))
constraints.append(create_fixed_constraint(king_post, tie_beam, 
                                          king_start, "Constraint_Center"))

# Apply downward force at apex using force field
bpy.ops.object.effector_add(type='FORCE', location=force_location)
force_field = bpy.context.active_object
force_field.name = "ApexForce"
force_field.field.type = 'FORCE'
force_field.field.strength = -force_magnitude  # Negative for downward
force_field.field.use_max_distance = True
force_field.field.max_distance = 0.1  # Only affect apex region
force_field.field.falloff_power = 0  # Constant force within range

# Link force field to king post via proximity (already at same location)
# Force field will affect all rigid bodies within 0.1m of apex

# Set up simulation parameters
bpy.context.scene.frame_end = simulation_frames
bpy.context.scene.rigidbody_world.time_scale = 1.0
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 50

# Ensure all objects are visible and selectable
for obj in bpy.data.objects:
    obj.hide_viewport = False
    obj.hide_render = False

print("King post truss constructed with fixed constraints and load applied.")