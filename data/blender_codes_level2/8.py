import bpy
import math
from mathutils import Vector, Matrix

# Clear scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Extract parameters from summary
truss_length = 7.0
bay_length = 1.0
top_z = 1.0
bottom_z = 0.0
cross_section = 0.1
num_bays = 7
load_mass = 250.0
load_size = 0.2
load_pos = (7.0, 0.0, 0.5)
base_pos = (0.0, 0.0, 0.0)
steel_density = 7850.0
sim_frames = 100

# Create storage for objects and constraints
objects = {}
constraints_to_create = []

# Function to create box member
def create_member(name, location, scale, rotation=(0,0,0)):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = scale
    if rotation != (0,0,0):
        obj.rotation_euler = rotation
    # Add rigid body
    bpy.ops.rigidbody.object_add()
    obj.rigid_body.mass = steel_density * (scale.x * scale.y * scale.z)
    obj.rigid_body.collision_shape = 'BOX'
    objects[name] = obj
    return obj

# Function to create fixed constraint between two objects
def create_fixed_constraint(obj1, obj2, location):
    # Create empty for constraint
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=location)
    empty = bpy.context.active_object
    empty.name = f"Constraint_{obj1.name}_{obj2.name}"
    empty.empty_display_size = 0.05
    
    # Add rigid body constraint
    bpy.ops.rigidbody.constraint_add()
    constraint = bpy.context.active_object
    constraint.name = f"Fixed_{obj1.name}_{obj2.name}"
    constraint.rigid_body_constraint.type = 'FIXED'
    constraint.rigid_body_constraint.object1 = obj1
    constraint.rigid_body_constraint.object2 = obj2
    
    # Parent constraint to empty for organization
    constraint.parent = empty
    return constraint

# Create top chord segments
for i in range(num_bays):
    x_pos = (i * bay_length) + (bay_length / 2)
    name = f"Top_Chord_{i}"
    scale = Vector((bay_length, cross_section, cross_section))
    create_member(name, (x_pos, 0, top_z), scale)

# Create bottom chord segments
for i in range(num_bays):
    x_pos = (i * bay_length) + (bay_length / 2)
    name = f"Bottom_Chord_{i}"
    scale = Vector((bay_length, cross_section, cross_section))
    create_member(name, (x_pos, 0, bottom_z), scale)

# Create vertical members at each joint
for i in range(num_bays + 1):
    x_pos = i * bay_length
    name = f"Vertical_{i}"
    scale = Vector((cross_section, cross_section, top_z - bottom_z))
    create_member(name, (x_pos, 0, (top_z + bottom_z)/2), scale)

# Create diagonal members (Pratt pattern)
for i in range(num_bays):
    x_pos = (i * bay_length) + (bay_length / 2)
    z_pos = (top_z + bottom_z) / 2
    
    if i % 2 == 0:  # Diagonal from top-left to bottom-right
        name = f"Diagonal_{i}_TL_BR"
        rotation = (0, -math.atan2(top_z - bottom_z, bay_length), 0)
    else:  # Diagonal from bottom-left to top-right
        name = f"Diagonal_{i}_BL_TR"
        rotation = (0, math.atan2(top_z - bottom_z, bay_length), 0)
    
    diag_length = math.sqrt(bay_length**2 + (top_z - bottom_z)**2)
    scale = Vector((diag_length, cross_section, cross_section))
    create_member(name, (x_pos, 0, z_pos), scale, rotation)

# Create load cube
bpy.ops.mesh.primitive_cube_add(size=1.0, location=load_pos)
load = bpy.context.active_object
load.name = "Load"
load.scale = (load_size, load_size, load_size)
bpy.ops.rigidbody.object_add()
load.rigid_body.mass = load_mass
load.rigid_body.collision_shape = 'BOX'
objects["Load"] = load

# Create base anchor (passive rigid body)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=base_pos)
base = bpy.context.active_object
base.name = "Base_Anchor"
base.scale = (cross_section * 3, cross_section * 3, cross_section * 3)
bpy.ops.rigidbody.object_add()
base.rigid_body.type = 'PASSIVE'
objects["Base_Anchor"] = base

# Connect verticals to chords at each joint
for i in range(num_bays + 1):
    x_pos = i * bay_length
    joint_pos = (x_pos, 0, bottom_z)
    
    # Connect vertical to bottom chord (if not at ends where chord segments don't exist)
    if i < num_bays:  # Connect to right half of bottom chord segment
        create_fixed_constraint(
            objects[f"Vertical_{i}"],
            objects[f"Bottom_Chord_{i}"],
            joint_pos
        )
    
    if i > 0:  # Connect to left half of previous bottom chord segment
        create_fixed_constraint(
            objects[f"Vertical_{i}"],
            objects[f"Bottom_Chord_{i-1}"],
            joint_pos
        )
    
    # Connect vertical to top chord
    joint_pos_top = (x_pos, 0, top_z)
    if i < num_bays:
        create_fixed_constraint(
            objects[f"Vertical_{i}"],
            objects[f"Top_Chord_{i}"],
            joint_pos_top
        )
    
    if i > 0:
        create_fixed_constraint(
            objects[f"Vertical_{i}"],
            objects[f"Top_Chord_{i-1}"],
            joint_pos_top
        )

# Connect diagonals to chords
for i in range(num_bays):
    if i % 2 == 0:  # TL-BR diagonal
        # Connect to top chord at left end
        create_fixed_constraint(
            objects[f"Diagonal_{i}_TL_BR"],
            objects[f"Top_Chord_{i}"],
            (i * bay_length, 0, top_z)
        )
        # Connect to bottom chord at right end
        create_fixed_constraint(
            objects[f"Diagonal_{i}_TL_BR"],
            objects[f"Bottom_Chord_{i}"],
            ((i+1) * bay_length, 0, bottom_z)
        )
    else:  # BL-TR diagonal
        # Connect to bottom chord at left end
        create_fixed_constraint(
            objects[f"Diagonal_{i}_BL_TR"],
            objects[f"Bottom_Chord_{i-1}"],
            (i * bay_length, 0, bottom_z)
        )
        # Connect to top chord at right end
        create_fixed_constraint(
            objects[f"Diagonal_{i}_BL_TR"],
            objects[f"Top_Chord_{i}"],
            ((i+1) * bay_length, 0, top_z)
        )

# Connect chords at intermediate joints (where segments meet)
for i in range(1, num_bays):
    joint_pos_top = (i * bay_length, 0, top_z)
    create_fixed_constraint(
        objects[f"Top_Chord_{i-1}"],
        objects[f"Top_Chord_{i}"],
        joint_pos_top
    )
    
    joint_pos_bottom = (i * bay_length, 0, bottom_z)
    create_fixed_constraint(
        objects[f"Bottom_Chord_{i-1}"],
        objects[f"Bottom_Chord_{i}"],
        joint_pos_bottom
    )

# Connect base to first vertical and first bottom chord
create_fixed_constraint(objects["Vertical_0"], objects["Base_Anchor"], base_pos)
create_fixed_constraint(objects["Bottom_Chord_0"], objects["Base_Anchor"], base_pos)

# Connect load to last bottom chord segment
create_fixed_constraint(load, objects[f"Bottom_Chord_{num_bays-1}"], load_pos)

# Set up physics world
bpy.context.scene.rigidbody_world.enabled = True
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 50
bpy.context.scene.frame_end = sim_frames

# Run simulation (headless compatible)
bpy.ops.ptcache.bake_all(bake=True)