import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Parameters from summary
R = 30.0
arc_len = 18.0
theta = 0.6  # radians
deck_w = 4.0
deck_t = 0.5
deck_center = (0.0, 0.0, 0.25)
end_angle = 0.3
end_x = 8.865806
end_y = 1.340647
col_rad = 0.5
col_h = 3.0
col_top_z = 0.0
col_bot_z = -3.0
cube_sz = 1.0
cube_mass = 900.0
cube_center = (0.0, 0.0, 1.0)
segments = 36

# Create curved deck using array of segments
for i in range(segments):
    phi = -end_angle + (2 * end_angle * i / (segments - 1))
    x = R * math.sin(phi)
    y = R * (1 - math.cos(phi))
    
    # Create segment (small rectangular beam)
    bpy.ops.mesh.primitive_cube_add(size=1.0)
    seg = bpy.context.active_object
    seg.name = f"Deck_Seg_{i:03d}"
    
    # Scale to segment dimensions
    seg_len = arc_len / segments
    seg.scale = (seg_len, deck_w, deck_t)
    
    # Position and rotate
    seg.location = (x, y - R, deck_center[2])  # Subtract R to center at origin
    seg.rotation_euler = (0, 0, phi)
    
    # Join segments (first segment becomes parent)
    if i > 0:
        seg.select_set(True)
        bpy.context.view_layer.objects.active = bpy.data.objects["Deck_Seg_000"]
        bpy.ops.object.join()

# Rename joined deck
deck = bpy.context.active_object
deck.name = "Bridge_Deck"

# Add rigid body to deck
bpy.ops.rigidbody.object_add()
deck.rigid_body.type = 'ACTIVE'
deck.rigid_body.mass = 500.0  # Estimated deck mass
deck.rigid_body.collision_shape = 'MESH'

# Create support columns
supports = []
for side in [-1, 1]:
    bpy.ops.mesh.primitive_cylinder_add(
        radius=col_rad,
        depth=col_h,
        location=(side * end_x, -end_y, (col_top_z + col_bot_z) / 2)
    )
    col = bpy.context.active_object
    col.name = f"Support_{'Left' if side < 0 else 'Right'}"
    col.rotation_euler = (math.pi/2, 0, 0)  # Cylinder axis along Z
    
    # Add rigid body (passive/fixed)
    bpy.ops.rigidbody.object_add()
    col.rigid_body.type = 'PASSIVE'
    supports.append(col)

# Create load cube
bpy.ops.mesh.primitive_cube_add(size=1.0, location=cube_center)
cube = bpy.context.active_object
cube.name = "Load_Cube"
cube.scale = (cube_sz, cube_sz, cube_sz)

# Add rigid body with specified mass
bpy.ops.rigidbody.object_add()
cube.rigid_body.type = 'ACTIVE'
cube.rigid_body.mass = cube_mass

# Create fixed constraints between deck and supports
for i, col in enumerate(supports):
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=col.location)
    empty = bpy.context.active_object
    empty.name = f"Constraint_Deck_Support_{i}"
    
    bpy.ops.rigidbody.constraint_add()
    constraint = empty.rigid_body_constraint
    constraint.type = 'FIXED'
    
    # Link objects
    constraint.object1 = deck
    constraint.object2 = col

# Create fixed constraint between deck and cube
bpy.ops.object.empty_add(type='PLAIN_AXES', location=cube_center)
empty = bpy.context.active_object
empty.name = "Constraint_Deck_Cube"

bpy.ops.rigidbody.constraint_add()
constraint = empty.rigid_body_constraint
constraint.type = 'FIXED'
constraint.object1 = deck
constraint.object2 = cube

# Set physics scene properties for stability
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 50
bpy.context.scene.rigidbody_world.collection = bpy.data.collections.new("Physics_Objects")