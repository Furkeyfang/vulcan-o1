import bpy
import mathutils

# Clear existing scene
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

# Extract parameters
span = 13.0
top_z = 3.0
bottom_z = 1.5
chord_section = (13.0, 0.2, 0.2)
vert_section = (0.2, 0.2, 1.5)
diag_section = (0.2, 0.2, 0.2)
num_panels = 6
panel_w = span / num_panels
diag_len = 2.646
load_force = -9800.0  # Negative for downward
load_loc = (0.0, 0.0, 3.0)
foundations = [(-6.5, 0.0, 1.5), (6.5, 0.0, 1.5)]
vert_x = [-6.5, -4.3333, -2.1667, 0.0, 2.1667, 4.3333, 6.5]

# Create foundation supports (passive rigid bodies)
foundation_objects = []
for loc in foundations:
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=loc)
    f_obj = bpy.context.active_object
    f_obj.scale = (0.3, 0.3, 0.3)
    f_obj.name = f"Foundation_{loc[0]}"
    bpy.ops.rigidbody.object_add()
    f_obj.rigid_body.type = 'PASSIVE'
    foundation_objects.append(f_obj)

# Create bottom chord
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, 0.0, bottom_z))
bottom_chord = bpy.context.active_object
bottom_chord.scale = chord_section
bottom_chord.name = "Bottom_Chord"
bpy.ops.rigidbody.object_add()
bottom_chord.rigid_body.type = 'PASSIVE'

# Create top chord
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, 0.0, top_z))
top_chord = bpy.context.active_object
top_chord.scale = chord_section
top_chord.name = "Top_Chord"
bpy.ops.rigidbody.object_add()
top_chord.rigid_body.type = 'PASSIVE'

# Create vertical members
vertical_objects = []
for i, x_pos in enumerate(vert_x):
    # Vertical center is midway between top and bottom chords
    vert_center_z = (top_z + bottom_z) / 2
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(x_pos, 0.0, vert_center_z))
    vert = bpy.context.active_object
    vert.scale = vert_section
    vert.name = f"Vertical_{i}"
    bpy.ops.rigidbody.object_add()
    vert.rigid_body.type = 'PASSIVE'
    vertical_objects.append(vert)

# Create diagonal members (alternating pattern)
diagonal_objects = []
for i in range(num_panels):  # 6 panels = 6 diagonals
    # Start point: top of current vertical
    start_x = vert_x[i]
    start_z = top_z
    # End point: bottom of next vertical
    end_x = vert_x[i + 1]
    end_z = bottom_z
    
    # Calculate midpoint and rotation for diagonal
    mid_x = (start_x + end_x) / 2
    mid_z = (start_z + end_z) / 2
    
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(mid_x, 0.0, mid_z))
    diag = bpy.context.active_object
    diag.scale = (diag_len, diag_section[1], diag_section[2])
    diag.name = f"Diagonal_{i}"
    
    # Rotate to align with diagonal direction
    direction = mathutils.Vector((end_x - start_x, 0.0, end_z - start_z)).normalized()
    angle = mathutils.Vector((1.0, 0.0, 0.0)).angle(direction)
    axis = mathutils.Vector((0.0, 1.0, 0.0)).cross(direction)
    if axis.length > 0:
        diag.rotation_euler = mathutils.Quaternion(axis.normalized(), angle).to_euler()
    
    bpy.ops.rigidbody.object_add()
    diag.rigid_body.type = 'PASSIVE'
    diagonal_objects.append(diag)

# Create fixed constraints for foundations to bottom chord
for f_obj in foundation_objects:
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=f_obj.location)
    constraint = bpy.context.active_object
    constraint.name = f"Constraint_Foundation_{f_obj.location[0]}"
    bpy.ops.rigidbody.constraint_add()
    constraint.rigid_body_constraint.type = 'FIXED'
    constraint.rigid_body_constraint.object1 = f_obj
    constraint.rigid_body_constraint.object2 = bottom_chord

# Create fixed constraints for verticals to chords
for i, vert in enumerate(vertical_objects):
    # Top connection
    top_loc = (vert_x[i], 0.0, top_z)
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=top_loc)
    constraint_top = bpy.context.active_object
    constraint_top.name = f"Constraint_Top_{i}"
    bpy.ops.rigidbody.constraint_add()
    constraint_top.rigid_body_constraint.type = 'FIXED'
    constraint_top.rigid_body_constraint.object1 = vert
    constraint_top.rigid_body_constraint.object2 = top_chord
    
    # Bottom connection
    bottom_loc = (vert_x[i], 0.0, bottom_z)
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=bottom_loc)
    constraint_bottom = bpy.context.active_object
    constraint_bottom.name = f"Constraint_Bottom_{i}"
    bpy.ops.rigidbody.constraint_add()
    constraint_bottom.rigid_body_constraint.type = 'FIXED'
    constraint_bottom.rigid_body_constraint.object1 = vert
    constraint_bottom.rigid_body_constraint.object2 = bottom_chord

# Create fixed constraints for diagonals
for i, diag in enumerate(diagonal_objects):
    # Top connection (to top chord at vertical i)
    top_loc = (vert_x[i], 0.0, top_z)
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=top_loc)
    constraint_top = bpy.context.active_object
    constraint_top.name = f"Constraint_DiagTop_{i}"
    bpy.ops.rigidbody.constraint_add()
    constraint_top.rigid_body_constraint.type = 'FIXED'
    constraint_top.rigid_body_constraint.object1 = diag
    constraint_top.rigid_body_constraint.object2 = top_chord
    
    # Bottom connection (to bottom chord at vertical i+1)
    bottom_loc = (vert_x[i + 1], 0.0, bottom_z)
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=bottom_loc)
    constraint_bottom = bpy.context.active_object
    constraint_bottom.name = f"Constraint_DiagBottom_{i}"
    bpy.ops.rigidbody.constraint_add()
    constraint_bottom.rigid_body_constraint.type = 'FIXED'
    constraint_bottom.rigid_body_constraint.object1 = diag
    constraint_bottom.rigid_body_constraint.object2 = bottom_chord

# Apply load as force field (limited to top chord center)
bpy.ops.object.empty_add(type='PLAIN_AXES', location=load_loc)
force_field = bpy.context.active_object
force_field.name = "Load_Force_Field"
bpy.ops.object.forcefield_add()
force_field.field.type = 'FORCE'
force_field.field.strength = load_force
force_field.field.use_max_distance = True
force_field.field.distance_max = 0.5  # Only affects nearby objects
force_field.field.falloff_power = 0.0  # Constant within range

# Set gravity and simulation settings
bpy.context.scene.gravity = (0.0, 0.0, -9.8)
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 50

print("Pratt Truss pedestrian overpass constructed with fixed joints and 9800N load.")