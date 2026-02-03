import bpy
import mathutils

# Clear scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Parameters from summary
deck_dim = (10.0, 4.0, 0.5)
deck1_center = (5.0, 0.0, 0.75)
deck2_center = (15.5, 0.0, 0.75)
col_radius = 0.5
col_height = 2.0
col_x1 = [2.0, 8.0]
col_x2 = [12.5, 18.5]
col_y = [-1.5, 1.5]
col_z_center = 1.0
hinge_pivot = (10.25, 0.0, 0.75)
mass_per_deck = 650.0

# Create Deck Segment 1
bpy.ops.mesh.primitive_cube_add(size=1.0, location=deck1_center)
deck1 = bpy.context.active_object
deck1.scale = deck_dim
bpy.ops.rigidbody.object_add()
deck1.rigid_body.type = 'ACTIVE'
deck1.rigid_body.mass = mass_per_deck
deck1.name = "Deck1"

# Create Deck Segment 2
bpy.ops.mesh.primitive_cube_add(size=1.0, location=deck2_center)
deck2 = bpy.context.active_object
deck2.scale = deck_dim
bpy.ops.rigidbody.object_add()
deck2.rigid_body.type = 'ACTIVE'
deck2.rigid_body.mass = mass_per_deck
deck2.name = "Deck2"

# Create Support Columns for Segment 1
cols = []
for x in col_x1:
    for y in col_y:
        loc = (x, y, col_z_center)
        bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=col_radius, depth=col_height, location=loc)
        col = bpy.context.active_object
        col.rotation_euler = (0, 0, 0)  # aligned with Z
        bpy.ops.rigidbody.object_add()
        col.rigid_body.type = 'PASSIVE'
        cols.append(col)

# Create Support Columns for Segment 2
for x in col_x2:
    for y in col_y:
        loc = (x, y, col_z_center)
        bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=col_radius, depth=col_height, location=loc)
        col = bpy.context.active_object
        col.rotation_euler = (0, 0, 0)
        bpy.ops.rigidbody.object_add()
        col.rigid_body.type = 'PASSIVE'
        cols.append(col)

# Create Fixed Constraints between each deck and its columns
# Deck1 columns: first four in cols list
for i in range(4):
    bpy.ops.rigidbody.constraint_add()
    const = bpy.context.active_object
    const.rigid_body_constraint.type = 'FIXED'
    const.rigid_body_constraint.object1 = deck1
    const.rigid_body_constraint.object2 = cols[i]
    const.location = hinge_pivot  # constraint location doesn't affect physics

# Deck2 columns: remaining four
for i in range(4, 8):
    bpy.ops.rigidbody.constraint_add()
    const = bpy.context.active_object
    const.rigid_body_constraint.type = 'FIXED'
    const.rigid_body_constraint.object1 = deck2
    const.rigid_body_constraint.object2 = cols[i]
    const.location = hinge_pivot

# Create Hinge Constraint between Deck1 and Deck2
bpy.ops.rigidbody.constraint_add()
hinge = bpy.context.active_object
hinge.rigid_body_constraint.type = 'HINGE'
hinge.rigid_body_constraint.object1 = deck1
hinge.rigid_body_constraint.object2 = deck2
hinge.location = hinge_pivot
# Set hinge axis to Z (global). In Blender, hinge axis is local to constraint object.
# We'll align the constraint empty's rotation to global.
hinge.rotation_euler = (0, 0, 0)
hinge.rigid_body_constraint.use_limit_z = False  # free rotation

# Optional: Set world gravity to default (Z = -9.81)
bpy.context.scene.gravity = (0, 0, -9.81)

print("Bridge construction complete. Deck masses: {} kg each.".format(mass_per_deck))