import bpy
import math
from mathutils import Vector

# Clear existing scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=True)

# Define all variables from parameter summary
span = 15.0
truss_height = 10.0
num_segments = 10
segment_length = 1.5
top_z = 10.0
bottom_z = 0.0
chord_width = 0.2
chord_depth = 0.2
web_width = 0.15
web_depth = 0.15
node_radius = 0.1
node_depth = 0.2
support_width = 0.5
support_depth = 0.5
support_height = 1.0
total_load_kg = 1400.0
gravity = 9.81
total_force_newton = total_load_kg * gravity
nodes_per_top_chord = 11
force_per_node = total_force_newton / nodes_per_top_chord

# Generate node positions
node_x_positions = [ -span/2 + i * segment_length for i in range(nodes_per_top_chord) ]
top_nodes = [Vector((x, 0.0, top_z)) for x in node_x_positions]
bottom_nodes = [Vector((x, 0.0, bottom_z)) for x in node_x_positions]

# Collection for organization
truss_collection = bpy.data.collections.new("HoweTruss")
bpy.context.scene.collection.children.link(truss_collection)

# Function to create and position objects in truss collection
def create_object(name, primitive, location, scale=None, rotation=None):
    if primitive == "CUBE":
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=location)
    elif primitive == "CYLINDER":
        bpy.ops.mesh.primitive_cylinder_add(radius=1.0, depth=1.0, location=location)
    
    obj = bpy.context.active_object
    obj.name = name
    
    if scale:
        obj.scale = scale
    if rotation:
        obj.rotation_euler = rotation
    
    # Move to truss collection
    if obj.users_collection:
        for coll in obj.users_collection:
            coll.objects.unlink(obj)
    truss_collection.objects.link(obj)
    
    return obj

# Create connection nodes (cylinders)
node_objects = {}
for i, pos in enumerate(top_nodes):
    obj = create_object(f"TopNode_{i}", "CYLINDER", pos, 
                        scale=(node_radius, node_radius, node_depth/2))
    node_objects[f"top_{i}"] = obj

for i, pos in enumerate(bottom_nodes):
    obj = create_object(f"BottomNode_{i}", "CYLINDER", pos,
                        scale=(node_radius, node_radius, node_depth/2))
    node_objects[f"bottom_{i}"] = obj

# Create top chord beams (cubes)
for i in range(num_segments):
    start_pos = top_nodes[i]
    end_pos = top_nodes[i+1]
    mid_pos = (start_pos + end_pos) / 2
    length = (end_pos - start_pos).length
    
    # Cube oriented along X axis
    obj = create_object(f"TopChord_{i}", "CUBE", mid_pos,
                       scale=(length/2, chord_width/2, chord_depth/2))
    
    # Add fixed constraints to nodes
    bpy.ops.rigidbody.constraint_add()
    constraint = bpy.context.active_object
    constraint.name = f"Constraint_TopChord_{i}_Start"
    constraint.rigid_body_constraint.type = 'FIXED'
    constraint.rigid_body_constraint.object1 = node_objects[f"top_{i}"]
    constraint.rigid_body_constraint.object2 = obj
    
    bpy.ops.rigidbody.constraint_add()
    constraint = bpy.context.active_object
    constraint.name = f"Constraint_TopChord_{i}_End"
    constraint.rigid_body_constraint.type = 'FIXED'
    constraint.rigid_body_constraint.object1 = obj
    constraint.rigid_body_constraint.object2 = node_objects[f"top_{i+1}"]

# Create bottom chord beams (identical to top)
for i in range(num_segments):
    start_pos = bottom_nodes[i]
    end_pos = bottom_nodes[i+1]
    mid_pos = (start_pos + end_pos) / 2
    length = (end_pos - start_pos).length
    
    obj = create_object(f"BottomChord_{i}", "CUBE", mid_pos,
                       scale=(length/2, chord_width/2, chord_depth/2))
    
    # Constraints
    bpy.ops.rigidbody.constraint_add()
    constraint = bpy.context.active_object
    constraint.name = f"Constraint_BottomChord_{i}_Start"
    constraint.rigid_body_constraint.type = 'FIXED'
    constraint.rigid_body_constraint.object1 = node_objects[f"bottom_{i}"]
    constraint.rigid_body_constraint.object2 = obj
    
    bpy.ops.rigidbody.constraint_add()
    constraint = bpy.context.active_object
    constraint.name = f"Constraint_BottomChord_{i}_End"
    constraint.rigid_body_constraint.type = 'FIXED'
    constraint.rigid_body_constraint.object1 = obj
    constraint.rigid_body_constraint.object2 = node_objects[f"bottom_{i+1}"]

# Create vertical members
for i in range(nodes_per_top_chord):
    start_pos = bottom_nodes[i]
    end_pos = top_nodes[i]
    mid_pos = (start_pos + end_pos) / 2
    height = truss_height
    
    obj = create_object(f"Vertical_{i}", "CUBE", mid_pos,
                       scale=(web_width/2, web_depth/2, height/2))
    
    # Constraints
    bpy.ops.rigidbody.constraint_add()
    constraint = bpy.context.active_object
    constraint.name = f"Constraint_Vertical_{i}_Bottom"
    constraint.rigid_body_constraint.type = 'FIXED'
    constraint.rigid_body_constraint.object1 = node_objects[f"bottom_{i}"]
    constraint.rigid_body_constraint.object2 = obj
    
    bpy.ops.rigidbody.constraint_add()
    constraint = bpy.context.active_object
    constraint.name = f"Constraint_Vertical_{i}_Top"
    constraint.rigid_body_constraint.type = 'FIXED'
    constraint.rigid_body_constraint.object1 = obj
    constraint.rigid_body_constraint.object2 = node_objects[f"top_{i}"]

# Create diagonal members (alternating pattern)
for i in range(num_segments):
    if i % 2 == 0:  # Even: bottom-left to top-right
        start_node = node_objects[f"bottom_{i}"]
        end_node = node_objects[f"top_{i+1}"]
        name_prefix = "Diagonal_Even"
    else:  # Odd: top-left to bottom-right
        start_node = node_objects[f"top_{i}"]
        end_node = node_objects[f"bottom_{i+1}"]
        name_prefix = "Diagonal_Odd"
    
    start_pos = start_node.location
    end_pos = end_node.location
    mid_pos = (start_pos + end_pos) / 2
    length = (end_pos - start_pos).length
    
    # Calculate rotation to align cube along diagonal
    direction = (end_pos - start_pos).normalized()
    obj = create_object(f"{name_prefix}_{i}", "CUBE", mid_pos,
                       scale=(length/2, web_width/2, web_depth/2))
    
    # Align object's X axis to the diagonal direction
    # Default cube X is along world X, need to rotate
    obj.rotation_mode = 'QUATERNION'
    obj.rotation_quaternion = direction.to_track_quat('X', 'Z')
    
    # Constraints
    bpy.ops.rigidbody.constraint_add()
    constraint = bpy.context.active_object
    constraint.name = f"Constraint_{name_prefix}_{i}_Start"
    constraint.rigid_body_constraint.type = 'FIXED'
    constraint.rigid_body_constraint.object1 = start_node
    constraint.rigid_body_constraint.object2 = obj
    
    bpy.ops.rigidbody.constraint_add()
    constraint = bpy.context.active_object
    constraint.name = f"Constraint_{name_prefix}_{i}_End"
    constraint.rigid_body_constraint.type = 'FIXED'
    constraint.rigid_body_constraint.object1 = obj
    constraint.rigid_body_constraint.object2 = end_node

# Create ground supports at both ends
left_support_pos = Vector((-span/2, 0.0, -support_height/2))
right_support_pos = Vector((span/2, 0.0, -support_height/2))

left_support = create_object("GroundSupport_Left", "CUBE", left_support_pos,
                            scale=(support_width/2, support_depth/2, support_height/2))
right_support = create_object("GroundSupport_Right", "CUBE", right_support_pos,
                             scale=(support_width/2, support_depth/2, support_height/2))

# Fix bottom end nodes to ground supports
bpy.ops.rigidbody.constraint_add()
constraint = bpy.context.active_object
constraint.name = "Constraint_LeftSupport"
constraint.rigid_body_constraint.type = 'FIXED'
constraint.rigid_body_constraint.object1 = left_support
constraint.rigid_body_constraint.object2 = node_objects["bottom_0"]

bpy.ops.rigidbody.constraint_add()
constraint = bpy.context.active_object
constraint.name = "Constraint_RightSupport"
constraint.rigid_body_constraint.type = 'FIXED'
constraint.rigid_body_constraint.object1 = right_support
constraint.rigid_body_constraint.object2 = node_objects[f"bottom_{num_segments}"]

# Add rigid body physics to all objects
for obj in truss_collection.objects:
    bpy.context.view_layer.objects.active = obj
    bpy.ops.rigidbody.object_add()
    
    # Ground supports are passive, everything else is active
    if "GroundSupport" in obj.name:
        obj.rigid_body.type = 'PASSIVE'
    else:
        obj.rigid_body.type = 'ACTIVE'
        obj.rigid_body.mass = 100.0  # Arbitrary mass for stability

# Apply forces to top nodes
for i in range(nodes_per_top_chord):
    node_obj = node_objects[f"top_{i}"]
    if node_obj.rigid_body:
        node_obj.rigid_body.enabled = True
        # Apply constant downward force
        node_obj.keyframe_insert(data_path="rigid_body.kinematic", frame=1)
        # Force will be applied in animation through constant force field or Python handler
        # For simplicity, we'll create a constant force field attached to each top node
        bpy.ops.object.effector_add(type='FORCE', location=node_obj.location)
        force_field = bpy.context.active_object
        force_field.name = f"Force_TopNode_{i}"
        force_field.field.strength = -force_per_node  # Negative for downward
        force_field.field.falloff_power = 0
        force_field.field.use_max_distance = True
        force_field.field.distance_max = 0.5  # Only affect nearby objects
        
        # Parent force field to node
        force_field.parent = node_obj
        force_field.location = (0, 0, 0)  # Local to parent

# Set up physics world
bpy.context.scene.rigidbody_world.enabled = True
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 50

# Set simulation length
bpy.context.scene.frame_end = 1000

print(f"Howe Truss constructed successfully with {len(truss_collection.objects)} objects")
print(f"Total load: {total_force_newton:.2f}N distributed across {nodes_per_top_chord} nodes ({force_per_node:.2f}N each)")