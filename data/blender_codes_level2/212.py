import bpy
import mathutils
from mathutils import Vector
import math

# Clear existing scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Extract parameters from summary
span = 18.0
peak_height = 3.0
bottom_chord_z = 0.0
chord_cross = 0.2
brace_cross = 0.15

# Node definitions
nodes = {
    'A': Vector((-9.0, 0.0, 0.0)),
    'B': Vector((-4.5, 0.0, 0.0)),
    'C': Vector((0.0, 0.0, 0.0)),
    'D': Vector((4.5, 0.0, 0.0)),
    'E': Vector((9.0, 0.0, 0.0)),
    'F': Vector((-9.0, 0.0, 0.0)),  # Same as A
    'G': Vector((-4.5, 0.0, 1.5)),
    'H': Vector((0.0, 0.0, 3.0)),
    'I': Vector((4.5, 0.0, 1.5)),
    'J': Vector((9.0, 0.0, 0.0)),   # Same as E
}

# Member definitions: (start, end, is_chord)
members = [
    ('A', 'B', True),   # Bottom chord 1
    ('B', 'C', True),   # Bottom chord 2
    ('C', 'D', True),   # Bottom chord 3
    ('D', 'E', True),   # Bottom chord 4
    ('F', 'G', True),   # Top chord left outer
    ('G', 'H', True),   # Top chord left inner
    ('H', 'I', True),   # Top chord right inner
    ('I', 'J', True),   # Top chord right outer
    ('B', 'G', False),  # Vertical left
    ('C', 'H', False),  # Vertical center
    ('D', 'I', False),  # Vertical right
    ('G', 'C', False),  # Diagonal left
    ('I', 'C', False),  # Diagonal right
]

# Function to create a structural member
def create_member(start_vec, end_vec, is_chord):
    # Calculate member properties
    direction = end_vec - start_vec
    length = direction.length
    midpoint = (start_vec + end_vec) / 2
    
    # Create cube
    bpy.ops.mesh.primitive_cube_add(size=1, location=midpoint)
    obj = bpy.context.active_object
    obj.name = f"Member_{len(bpy.data.objects)}"
    
    # Set cross-section and length
    cross = chord_cross if is_chord else brace_cross
    obj.scale = (length / 2, cross / 2, cross / 2)
    
    # Calculate rotation
    up = Vector((0, 0, 1))
    rot_quat = direction.to_track_quat('X', 'Z')
    obj.rotation_euler = rot_quat.to_euler()
    
    # Apply transform
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    
    # Add rigid body
    bpy.ops.rigidbody.object_add()
    return obj

# Create all members
member_objects = []
for start, end, is_chord in members:
    member = create_member(nodes[start], nodes[end], is_chord)
    member_objects.append(member)

# Set bottom chords as passive (first 4 members)
for i in range(4):
    member_objects[i].rigid_body.type = 'PASSIVE'

# Create fixed constraints at joints
constraint_groups = {
    'A': [0],      # Bottom chord 1 start
    'B': [0, 1, 8, 11],  # Bottom chord 1 end, 2 start, vertical, diagonal
    'C': [1, 2, 9, 11, 12],  # Bottom chord 2 end, 3 start, vertical, 2 diagonals
    'D': [2, 3, 10, 12], # Bottom chord 3 end, 4 start, vertical, diagonal
    'E': [3],      # Bottom chord 4 end
    'F': [4],      # Top chord left start
    'G': [4, 5, 8, 11],   # Top chord left end, right start, vertical, diagonal
    'H': [5, 6, 9],       # Top chord peak, vertical center
    'I': [6, 7, 10, 12],  # Top chord right peak, vertical, diagonal
    'J': [7],      # Top chord right end
}

for joint_name, member_indices in constraint_groups.items():
    if len(member_indices) > 1:
        # Create constraints between first member and all others at joint
        base_obj = member_objects[member_indices[0]]
        for i in range(1, len(member_indices)):
            target_obj = member_objects[member_indices[i]]
            
            # Create empty for constraint pivot at joint location
            bpy.ops.object.empty_add(type='PLAIN_AXES', location=nodes[joint_name])
            empty = bpy.context.active_object
            empty.name = f"Constraint_{joint_name}_{i}"
            
            # Add rigid body constraint
            bpy.ops.rigidbody.constraint_add()
            constraint = bpy.context.active_object.rigid_body_constraint
            constraint.type = 'FIXED'
            constraint.object1 = base_obj
            constraint.object2 = target_obj
            
            # Parent constraint to empty
            constraint_obj = bpy.context.active_object
            constraint_obj.parent = empty

# Set up physics world
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 50

# Apply load to top chords (2000kg = 19620N distributed)
top_chord_indices = [4, 5, 6, 7]
force_per_member = 19620 / len(top_chord_indices)

for idx in top_chord_indices:
    obj = member_objects[idx]
    if not obj.rigid_body:
        bpy.ops.rigidbody.object_add()
    
    # Add force field for downward load
    bpy.ops.object.effector_add(type='FORCE', location=obj.location)
    force = bpy.context.active_object
    force.field.strength = -force_per_member
    force.field.shape = 'POINT'
    force.field.falloff_power = 0
    force.field.distance_max = 0.1
    force.parent = obj

# Set simulation frames
bpy.context.scene.frame_start = 1
bpy.context.scene.frame_end = 100

print("Fink truss construction complete. Ready for simulation.")