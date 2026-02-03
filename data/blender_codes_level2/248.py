import bpy
import mathutils

# Clear scene
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

# Enable rigid body world
if bpy.context.scene.rigidbody_world is None:
    bpy.ops.rigidbody.world_add()
bpy.context.scene.rigidbody_world.enabled = True

# Parameters
span = 12.0
peak_height = 2.0
truss_width = 1.0
cube_section = 0.2
panel_length = 1.0
panel_width = 0.5
panel_thickness = 0.05
deck_length = 12.0
deck_width = 1.0
deck_thickness = 0.1
force_newtons = 4905.0
steel_density = 7850.0
num_panels_per_row = 10
panel_spacing_x = 1.2
panel_start_x = 0.6
deck_z = 2.15
panel_z = 2.225

# Function to create truss member between two points
def create_member(p1, p2, name):
    # Calculate direction vector and length
    v = mathutils.Vector(p2) - mathutils.Vector(p1)
    length = v.length
    mid = (mathutils.Vector(p1) + mathutils.Vector(p2)) / 2
    
    # Create cube at midpoint
    bpy.ops.mesh.primitive_cube_add(size=1, location=mid)
    obj = bpy.context.active_object
    obj.name = name
    
    # Scale: cross-section 0.2×0.2, length = member length, width = truss_width
    obj.scale = (cube_section/2, truss_width/2, length/2)
    
    # Rotate to align with direction vector
    if length > 0:
        rot_quat = mathutils.Vector((0, 0, 1)).rotation_difference(v.normalized())
        obj.rotation_euler = rot_quat.to_euler()
    
    # Add rigid body
    bpy.ops.rigidbody.object_add()
    obj.rigid_body.mass = steel_density * (cube_section * cube_section * length)
    return obj

# Create supports (passive rigid bodies)
supports = []
for x in [0.0, span]:
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x, 0, 0))
    sup = bpy.context.active_object
    sup.scale = (0.3, 0.3, 0.3)
    sup.name = f"Support_{x}"
    bpy.ops.rigidbody.object_add()
    sup.rigid_body.type = 'PASSIVE'
    supports.append(sup)

# Define truss joint coordinates (x, y, z)
joints = {
    'A': (0.0, 0.0, 0.0),      # Left end bottom
    'B': (3.0, 0.0, 0.0),      # Bottom chord 1/4
    'C': (6.0, 0.0, 0.0),      # Bottom chord center
    'D': (9.0, 0.0, 0.0),      # Bottom chord 3/4
    'E': (12.0, 0.0, 0.0),     # Right end bottom
    'F': (0.0, 0.0, 0.0),      # Left end top (same as A)
    'G': (3.0, 0.0, 1.0),      # Top chord 1/4
    'H': (6.0, 0.0, 2.0),      # Peak
    'I': (9.0, 0.0, 1.0),      # Top chord 3/4
    'J': (12.0, 0.0, 0.0)      # Right end top (same as E)
}

# Create truss members
members = []
# Bottom chord
members.append(create_member(joints['A'], joints['B'], "Bottom_AB"))
members.append(create_member(joints['B'], joints['C'], "Bottom_BC"))
members.append(create_member(joints['C'], joints['D'], "Bottom_CD"))
members.append(create_member(joints['D'], joints['E'], "Bottom_DE"))
# Top chord
members.append(create_member(joints['F'], joints['G'], "Top_FG"))
members.append(create_member(joints['G'], joints['H'], "Top_GH"))
members.append(create_member(joints['H'], joints['I'], "Top_HI"))
members.append(create_member(joints['I'], joints['J'], "Top_IJ"))
# Web members
members.append(create_member(joints['B'], joints['G'], "Web_BG"))
members.append(create_member(joints['G'], joints['C'], "Web_GC"))
members.append(create_member(joints['C'], joints['H'], "Web_CH"))
members.append(create_member(joints['C'], joints['I'], "Web_CI"))
members.append(create_member(joints['D'], joints['I'], "Web_DI"))

# Create roof deck
bpy.ops.mesh.primitive_cube_add(size=1, location=(span/2, 0, deck_z))
deck = bpy.context.active_object
deck.scale = (deck_length/2, deck_width/2, deck_thickness/2)
deck.name = "RoofDeck"
bpy.ops.rigidbody.object_add()
deck.rigid_body.mass = steel_density * (deck_length * deck_width * deck_thickness)

# Create solar panels (2 rows)
panels = []
for row in [0, 1]:
    y_pos = -0.25 if row == 0 else 0.25
    for i in range(num_panels_per_row):
        x_pos = panel_start_x + i * panel_spacing_x
        bpy.ops.mesh.primitive_cube_add(size=1, location=(x_pos, y_pos, panel_z))
        panel = bpy.context.active_object
        panel.scale = (panel_length/2, panel_width/2, panel_thickness/2)
        panel.name = f"Panel_{row}_{i}"
        bpy.ops.rigidbody.object_add()
        panel.rigid_body.mass = 20.0  # ~10kg/m²
        panels.append(panel)

# Function to add fixed constraint between two objects
def add_fixed_constraint(obj1, obj2):
    # Create empty object as constraint anchor
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=obj1.location)
    empty = bpy.context.active_object
    empty.name = f"Constraint_{obj1.name}_{obj2.name}"
    
    # Add rigid body constraint
    bpy.ops.rigidbody.constraint_add()
    constraint = empty.rigid_body_constraint
    constraint.type = 'FIXED'
    constraint.object1 = obj1
    constraint.object2 = obj2

# Add constraints at all joints
joint_objects = {}
for obj in members + supports:
    # Simple joint detection by proximity (cube centers)
    loc = obj.location
    key = (round(loc.x, 1), round(loc.z, 1))
    if key not in joint_objects:
        joint_objects[key] = []
    joint_objects[key].append(obj)

# Constrain objects sharing same joint
for joint, objs in joint_objects.items():
    if len(objs) > 1:
        for i in range(len(objs)):
            for j in range(i+1, len(objs)):
                add_fixed_constraint(objs[i], objs[j])

# Constrain deck to top chord members (attach at 4 points)
top_chord_members = [m for m in members if m.name.startswith("Top")]
for top_member in top_chord_members:
    add_fixed_constraint(deck, top_member)

# Constrain panels to deck
for panel in panels:
    add_fixed_constraint(panel, deck)

# Apply downward force to deck
deck.rigid_body.force_type = 'FORCE'
deck.rigid_body.force = (0, 0, -force_newtons)