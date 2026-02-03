import bpy
import math

# Clear existing scene
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

# Define parameters from summary
span_length = 15.0
truss_spacing = 2.0
top_chord_dim = (15.0, 0.3, 0.3)
bottom_chord_dim = (15.0, 0.3, 0.3)
vertical_dim = (0.2, 0.2, 1.5)
diagonal_dim = (0.2, 0.2, 2.12132)
top_chord_z = 1.6
bottom_chord_z = 0.0
num_panels = 10
panel_width = 1.5
load_dim = (1.0, 1.0, 0.5)
load_mass = 1200.0
load_z = top_chord_z + 0.15 + 0.25  # 1.6 + 0.15 + 0.25 = 2.0

# Store objects for constraint creation
truss_objects = []

# Function to create rigid body with consistent settings
def add_rigidbody(obj, body_type='ACTIVE', mass=1.0):
    bpy.ops.rigidbody.object_add()
    obj.rigid_body.type = body_type
    obj.rigid_body.mass = mass
    obj.rigid_body.collision_shape = 'BOX'
    return obj

# Create two parallel trusses
for truss_index in [0, 1]:
    y_offset = truss_index * truss_spacing
    
    # Create top chord
    bpy.ops.mesh.primitive_cube_add(size=1, location=(span_length/2, y_offset, top_chord_z))
    top_chord = bpy.context.active_object
    top_chord.scale = (top_chord_dim[0]/2, top_chord_dim[1]/2, top_chord_dim[2]/2)
    add_rigidbody(top_chord, 'ACTIVE', 50.0)  # Estimated mass
    truss_objects.append(top_chord)
    
    # Create bottom chord
    bpy.ops.mesh.primitive_cube_add(size=1, location=(span_length/2, y_offset, bottom_chord_z))
    bottom_chord = bpy.context.active_object
    bottom_chord.scale = (bottom_chord_dim[0]/2, bottom_chord_dim[1]/2, bottom_chord_dim[2]/2)
    add_rigidbody(bottom_chord, 'ACTIVE', 50.0)
    truss_objects.append(bottom_chord)
    
    # Create vertical members at each joint
    verticals = []
    for i in range(num_panels + 1):
        x_pos = i * panel_width
        z_pos = bottom_chord_z + vertical_dim[2]/2
        bpy.ops.mesh.primitive_cube_add(size=1, location=(x_pos, y_offset, z_pos))
        vert = bpy.context.active_object
        vert.scale = (vertical_dim[0]/2, vertical_dim[1]/2, vertical_dim[2]/2)
        add_rigidbody(vert, 'ACTIVE', 5.0)
        verticals.append(vert)
        truss_objects.append(vert)
    
    # Create diagonal members (alternating direction)
    diagonals = []
    for i in range(num_panels):
        x_mid = (i * panel_width) + (panel_width/2)
        z_mid = (top_chord_z + bottom_chord_z) / 2
        
        bpy.ops.mesh.primitive_cube_add(size=1, location=(x_mid, y_offset, z_mid))
        diag = bpy.context.active_object
        diag.scale = (diagonal_dim[0]/2, diagonal_dim[1]/2, diagonal_dim[2]/2)
        
        # Rotate 45° based on direction
        if i % 2 == 0:  # Slope downward right
            diag.rotation_euler = (0, 0, -math.pi/4)
        else:  # Slope downward left
            diag.rotation_euler = (0, 0, math.pi/4)
        
        add_rigidbody(diag, 'ACTIVE', 8.0)
        diagonals.append(diag)
        truss_objects.append(diag)

# Create load cube at center
bpy.ops.mesh.primitive_cube_add(size=1, location=(span_length/2, truss_spacing/2, load_z))
load_cube = bpy.context.active_object
load_cube.scale = (load_dim[0]/2, load_dim[1]/2, load_dim[2]/2)
add_rigidbody(load_cube, 'ACTIVE', load_mass)

# Create fixed supports at bridge ends (passive rigid bodies)
support_size = 0.5
for end_x in [0, span_length]:
    for y in [0, truss_spacing]:
        bpy.ops.mesh.primitive_cube_add(size=1, location=(end_x, y, -support_size/2))
        support = bpy.context.active_object
        support.scale = (support_size/2, support_size/2, support_size/2)
        add_rigidbody(support, 'PASSIVE', 1000.0)

# Create fixed constraints between truss members
# Note: In headless mode, we must use context override for constraint creation
override = {'scene': bpy.context.scene}

# Constrain chords to verticals at each joint
for truss_idx in [0, 1]:
    y_offset = truss_idx * truss_spacing
    for i in range(num_panels + 1):
        x_pos = i * panel_width
        
        # Find vertical at this position
        vert = None
        for obj in bpy.data.objects:
            if abs(obj.location.x - x_pos) < 0.01 and abs(obj.location.y - y_offset) < 0.01:
                if "Cube" in obj.name and obj.dimensions.z > 1.0:  # Likely vertical
                    vert = obj
                    break
        
        if vert:
            # Constrain to top chord (select vert then top_chord)
            for obj in bpy.data.objects:
                if abs(obj.location.y - y_offset) < 0.01 and obj.dimensions.x > 10.0:  # Top chord
                    bpy.ops.rigidbody.constraint_add()
                    const = bpy.context.active_object
                    const.rigid_body_constraint.type = 'FIXED'
                    const.rigid_body_constraint.object1 = vert
                    const.rigid_body_constraint.object2 = obj
                    break
            
            # Constrain to bottom chord
            for obj in bpy.data.objects:
                if abs(obj.location.y - y_offset) < 0.01 and obj.dimensions.x > 10.0 and obj.location.z < 0.1:  # Bottom chord
                    bpy.ops.rigidbody.constraint_add()
                    const = bpy.context.active_object
                    const.rigid_body_constraint.type = 'FIXED'
                    const.rigid_body_constraint.object1 = vert
                    const.rigid_body_constraint.object2 = obj
                    break

# Set up rigid body world
bpy.context.scene.rigidbody_world.enabled = True
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 50
bpy.context.scene.frame_end = 100

# Ensure proper collision margins
for obj in bpy.data.objects:
    if obj.rigid_body:
        obj.rigid_body.use_margin = True
        obj.rigid_body.collision_margin = 0.0