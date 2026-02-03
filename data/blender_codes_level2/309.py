import bpy
import mathutils

# Clear existing scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Extract variables from parameter summary
segment_count = 10
segment_dim = (1.0, 1.0, 2.0)
base_x = 0.0
base_y = 0.0
base_z_offset = 1.0
lateral_offset_x = 1.0
offset_start_index = 5
load_dim = (1.0, 1.0, 1.0)
load_mass_kg = 1600.0
load_z_offset = 20.5

# Create ground plane
bpy.ops.mesh.primitive_plane_add(size=50.0, location=(0, 0, 0))
ground = bpy.context.active_object
ground.name = "Ground"
bpy.ops.rigidbody.object_add()
ground.rigid_body.type = 'PASSIVE'

# Create segment collection
segments = []
for i in range(segment_count):
    # Calculate position
    seg_x = base_x if i < offset_start_index else lateral_offset_x
    seg_y = base_y
    seg_z = base_z_offset + (i * segment_dim[2])
    
    # Create cube segment
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(seg_x, seg_y, seg_z))
    seg = bpy.context.active_object
    seg.name = f"Segment_{i:02d}"
    seg.scale = segment_dim
    
    # Add rigid body physics
    bpy.ops.rigidbody.object_add()
    seg.rigid_body.mass = 100.0  # Arbitrary mass for segments
    seg.rigid_body.collision_shape = 'BOX'
    segments.append(seg)

# Create fixed constraints between adjacent segments
for i in range(segment_count - 1):
    parent = segments[i]
    child = segments[i + 1]
    
    # Create empty object for constraint pivot (aligned with child's bottom)
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=child.location)
    pivot = bpy.context.active_object
    pivot.name = f"Constraint_{i:02d}_{i+1:02d}"
    
    # Parent empty to parent segment
    pivot.parent = parent
    pivot.matrix_parent_inverse = parent.matrix_world.inverted()
    
    # Create rigid body constraint
    bpy.ops.rigidbody.constraint_add()
    constraint = bpy.context.active_object
    constraint.name = f"Fixed_Constraint_{i:02d}_{i+1:02d}"
    constraint.location = child.location
    
    # Configure constraint
    constraint.rigid_body_constraint.type = 'FIXED'
    constraint.rigid_body_constraint.object1 = parent
    constraint.rigid_body_constraint.object2 = child
    
    # Adjust pivot to connection point (midpoint between segments)
    connection_z = segments[i].location.z + (segment_dim[2] / 2)
    constraint.location.z = connection_z

# Create load block
load_x = lateral_offset_x  # Aligned with upper segments
load_y = base_y
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(load_x, load_y, load_z_offset))
load_block = bpy.context.active_object
load_block.name = "Load_Block"
load_block.scale = load_dim

# Add rigid body physics to load
bpy.ops.rigidbody.object_add()
load_block.rigid_body.mass = load_mass_kg
load_block.rigid_body.collision_shape = 'BOX'

# Create fixed constraint between top segment and load
top_segment = segments[-1]
bpy.ops.object.empty_add(type='PLAIN_AXES', location=top_segment.location)
pivot_top = bpy.context.active_object
pivot_top.name = "Constraint_Top_Load"
pivot_top.parent = top_segment
pivot_top.matrix_parent_inverse = top_segment.matrix_world.inverted()

bpy.ops.rigidbody.constraint_add()
constraint_top = bpy.context.active_object
constraint_top.name = "Fixed_Constraint_Top_Load"
constraint_top.location = top_segment.location
constraint_top.rigid_body_constraint.type = 'FIXED'
constraint_top.rigid_body_constraint.object1 = top_segment
constraint_top.rigid_body_constraint.object2 = load_block

# Adjust pivot to connection point (top of segment)
connection_z = top_segment.location.z + (segment_dim[2] / 2)
constraint_top.location.z = connection_z

# Ensure all objects are visible in view layer
for obj in bpy.data.objects:
    obj.hide_set(False)
    obj.hide_render = False