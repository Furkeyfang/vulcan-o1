import bpy
import mathutils
from mathutils import Vector

# 1. Clear existing scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# 2. Define parameters from summary
truss_length = 6.0
truss_height = 1.5
truss_depth = 0.3
member_cs = 0.1  # cross-section
num_bays = 3
bay_length = truss_length / num_bays
joint_x = [0.0, bay_length, 2*bay_length, 3*bay_length]
top_z = truss_height
bottom_z = 0.0
load_mass = 300.0
load_size = 0.2
steel_density = 7850.0

# 3. Helper function to create beam between two points
def create_beam(p1, p2, name):
    """Create a cuboid beam from p1 to p2 with square cross-section"""
    # Calculate beam properties
    vec = Vector(p2) - Vector(p1)
    length = vec.length
    mid = (Vector(p1) + Vector(p2)) / 2
    
    # Create cube and scale
    bpy.ops.mesh.primitive_cube_add(size=1.0)
    beam = bpy.context.active_object
    beam.name = name
    beam.scale = (member_cs/2, truss_depth/2, length/2)
    
    # Orient to align Z axis with beam direction
    z_axis = vec.normalized()
    y_axis = Vector((0, 1, 0))
    if abs(z_axis.dot(y_axis)) > 0.99:  # Handle near-vertical case
        x_axis = Vector((1, 0, 0))
        y_axis = z_axis.cross(x_axis).normalized()
    else:
        x_axis = y_axis.cross(z_axis).normalized()
        y_axis = z_axis.cross(x_axis).normalized()
    
    # Set rotation matrix
    beam.matrix_world = mathutils.Matrix.Translation(mid) @ 
                       mathutils.Matrix((x_axis, y_axis, z_axis)).transposed().to_4x4()
    
    # Add rigid body
    bpy.ops.rigidbody.object_add()
    beam.rigid_body.type = 'ACTIVE'
    beam.rigid_body.collision_shape = 'BOX'
    
    # Calculate and set mass (volume * density)
    volume = member_cs * member_cs * length  # Square cross-section
    beam.rigid_body.mass = volume * steel_density
    
    return beam

# 4. Create ground anchor (passive rigid body)
bpy.ops.mesh.primitive_cube_add(size=0.3, location=(0,0,-0.15))
anchor = bpy.context.active_object
anchor.name = "GroundAnchor"
bpy.ops.rigidbody.object_add()
anchor.rigid_body.type = 'PASSIVE'

# 5. Create all truss members
beams = {}

# Horizontal chords (top and bottom)
for i in range(num_bays):
    # Top chord
    p1 = (joint_x[i], 0, top_z)
    p2 = (joint_x[i+1], 0, top_z)
    beams[f"TopChord_{i}"] = create_beam(p1, p2, f"TopChord_{i}")
    
    # Bottom chord
    p1 = (joint_x[i], 0, bottom_z)
    p2 = (joint_x[i+1], 0, bottom_z)
    beams[f"BottomChord_{i}"] = create_beam(p1, p2, f"BottomChord_{i}")

# Vertical members
for i in range(len(joint_x)):
    p1 = (joint_x[i], 0, bottom_z)
    p2 = (joint_x[i], 0, top_z)
    beams[f"Vertical_{i}"] = create_beam(p1, p2, f"Vertical_{i}")

# Diagonal members (Howe pattern)
diag_points = [
    ((joint_x[0], 0, top_z), (joint_x[1], 0, bottom_z)),  # Bay 1
    ((joint_x[1], 0, bottom_z), (joint_x[2], 0, top_z)),  # Bay 2
    ((joint_x[2], 0, top_z), (joint_x[3], 0, bottom_z))   # Bay 3
]
for i, (p1, p2) in enumerate(diag_points):
    beams[f"Diagonal_{i}"] = create_beam(p1, p2, f"Diagonal_{i}")

# 6. Create load platform at free end
load_loc = (joint_x[-1], 0, load_size/2)  # Centered vertically
bpy.ops.mesh.primitive_cube_add(size=1.0, location=load_loc)
load = bpy.context.active_object
load.name = "LoadPlatform"
load.scale = (load_size/2, load_size/2, load_size/2)
bpy.ops.rigidbody.object_add()
load.rigid_body.type = 'ACTIVE'
load.rigid_body.collision_shape = 'BOX'
load.rigid_body.mass = load_mass

# 7. Create fixed constraints for all joints
def add_fixed_constraint(obj_a, obj_b):
    """Add fixed constraint between two objects"""
    bpy.context.view_layer.objects.active = obj_a
    bpy.ops.rigidbody.constraint_add()
    constraint = bpy.context.active_object
    constraint.empty_display_type = 'ARROWS'
    constraint.rigid_body_constraint.type = 'FIXED'
    constraint.rigid_body_constraint.object1 = obj_a
    constraint.rigid_body_constraint.object2 = obj_b
    constraint.location = obj_b.location

# Map joints to connecting beams
joint_connections = {
    (0,0,0): ["BottomChord_0", "Vertical_0", "Diagonal_0"],
    (2,0,1.5): ["TopChord_0", "Vertical_1", "Diagonal_0", "Diagonal_1"],
    (2,0,0): ["BottomChord_1", "Vertical_1", "Diagonal_0"],
    (4,0,1.5): ["TopChord_1", "Vertical_2", "Diagonal_1", "Diagonal_2"],
    (4,0,0): ["BottomChord_2", "Vertical_2", "Diagonal_1"],
    (6,0,1.5): ["TopChord_2", "Vertical_3", "Diagonal_2"],
    (6,0,0): ["BottomChord_2", "Vertical_3", "LoadPlatform", "Diagonal_2"]
}

# Add constraints for each joint
for joint_loc, beam_names in joint_connections.items():
    # Convert beam names to objects
    objs = [beams[name] if name in beams else bpy.data.objects[name] 
            for name in beam_names]
    
    # Connect each object to the first one in the list
    if len(objs) > 1:
        for i in range(1, len(objs)):
            add_fixed_constraint(objs[0], objs[i])

# 8. Connect base to ground anchor
add_fixed_constraint(anchor, beams["BottomChord_0"])
add_fixed_constraint(anchor, beams["Vertical_0"])

# 9. Set up physics world
bpy.context.scene.rigidbody_world.enabled = True
bpy.context.scene.rigidbody_world.time_scale = 1.0
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 50
bpy.context.scene.frame_end = 100

print("Howe Truss Crane Arm constructed successfully.")