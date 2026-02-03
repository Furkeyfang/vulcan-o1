import bpy
import math
from mathutils import Vector

# ------------------------------------------------------------
# 1. CLEAR SCENE
# ------------------------------------------------------------
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# ------------------------------------------------------------
# 2. PARAMETERS (from summary)
# ------------------------------------------------------------
# Grid
grid_length_x = 8.0
grid_length_y = 8.0
grid_spacing = 1.0
grid_plane_z = 3.0
num_nodes_x = 9
num_nodes_y = 9

# Beams
beam_radius = 0.05
beam_length = 1.0

# Columns
column_radius = 0.1
column_height = 3.0
column_positions = [(0,0), (0,8), (8,0), (8,8), (4,0), (4,8), (0,4), (8,4)]

# Material & Load
steel_density = 7850.0
total_load_mass = 1800.0
gravity = 9.81

# Derived (recalculated for precision)
beam_volume = math.pi * beam_radius**2 * beam_length
beam_steel_mass = beam_volume * steel_density
num_x_beams = (num_nodes_x - 1) * num_nodes_y   # 8*9 = 72
num_y_beams = (num_nodes_y - 1) * num_nodes_x   # 8*9 = 72
total_beams = num_x_beams + num_y_beams         # 144
mass_per_beam = total_load_mass / total_beams   # 12.5
final_beam_mass = beam_steel_mass + mass_per_beam   # ~74.185

column_volume = math.pi * column_radius**2 * column_height
column_mass = column_volume * steel_density   # ~739.844

# ------------------------------------------------------------
# 3. CREATE GROUND PLANE (Passive)
# ------------------------------------------------------------
bpy.ops.mesh.primitive_plane_add(size=20.0, location=(0,0,0))
ground = bpy.context.active_object
ground.name = "Ground"
bpy.ops.rigidbody.object_add()
ground.rigid_body.type = 'PASSIVE'

# ------------------------------------------------------------
# 4. CREATE COLUMNS
# ------------------------------------------------------------
columns = []
for (cx, cy) in column_positions:
    # Column base at (cx, cy, 0), top at (cx, cy, column_height)
    # Create cylinder at midpoint in Z
    loc = (cx, cy, column_height/2.0)
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=32,
        radius=column_radius,
        depth=column_height,
        location=loc
    )
    col = bpy.context.active_object
    col.name = f"Column_{cx}_{cy}"
    # Rotate to align with Z (default is already Z-aligned)
    bpy.ops.rigidbody.object_add()
    col.rigid_body.mass = column_mass
    col.rigid_body.collision_shape = 'MESH'
    columns.append(col)

# ------------------------------------------------------------
# 5. CREATE HORIZONTAL BEAMS
# ------------------------------------------------------------
# We'll store beams in a dict keyed by node coordinates for constraint creation
beam_dict = {}  # (node_x, node_y, orientation) -> beam object
# orientation: 'x' for beams along X, 'y' for beams along Y

# X-direction beams (along X axis)
for j in range(num_nodes_y):          # rows
    y = j * grid_spacing
    for i in range(num_nodes_x - 1):  # columns of beams
        x_start = i * grid_spacing
        x_end = (i+1) * grid_spacing
        # Beam center
        x_center = (x_start + x_end) / 2.0
        loc = (x_center, y, grid_plane_z)
        bpy.ops.mesh.primitive_cylinder_add(
            vertices=16,
            radius=beam_radius,
            depth=beam_length,
            location=loc
        )
        beam = bpy.context.active_object
        beam.name = f"Beam_X_{i}_{j}"
        # Rotate 90° around Y axis to align with X direction
        beam.rotation_euler = (0, math.pi/2, 0)
        # Rigid body
        bpy.ops.rigidbody.object_add()
        beam.rigid_body.mass = final_beam_mass
        beam.rigid_body.collision_shape = 'MESH'
        # Store for constraints: beams connect nodes (i,j) and (i+1,j)
        beam_dict[(i, j, 'x')] = beam

# Y-direction beams (along Y axis)
for i in range(num_nodes_x):          # columns
    x = i * grid_spacing
    for j in range(num_nodes_y - 1):  # rows of beams
        y_start = j * grid_spacing
        y_end = (j+1) * grid_spacing
        y_center = (y_start + y_end) / 2.0
        loc = (x, y_center, grid_plane_z)
        bpy.ops.mesh.primitive_cylinder_add(
            vertices=16,
            radius=beam_radius,
            depth=beam_length,
            location=loc
        )
        beam = bpy.context.active_object
        beam.name = f"Beam_Y_{i}_{j}"
        # Rotate 90° around X axis to align with Y direction
        beam.rotation_euler = (math.pi/2, 0, 0)
        bpy.ops.rigidbody.object_add()
        beam.rigid_body.mass = final_beam_mass
        beam.rigid_body.collision_shape = 'MESH'
        beam_dict[(i, j, 'y')] = beam

# ------------------------------------------------------------
# 6. CREATE FIXED CONSTRAINTS
# ------------------------------------------------------------
# We need to connect beams at each node, and columns to beams and ground.
# Create an empty to parent constraints (optional, for organization)
bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0,0,0))
constraint_parent = bpy.context.active_object
constraint_parent.name = "Constraints"

# Function to create fixed constraint between two objects
def add_fixed_constraint(obj_a, obj_b, location):
    # Create constraint object
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=location)
    const = bpy.context.active_object
    const.name = "Fixed_Constraint"
    const.parent = constraint_parent
    # Add rigid body constraint
    bpy.ops.rigidbody.constraint_add()
    const.rigid_body_constraint.type = 'FIXED'
    const.rigid_body_constraint.object1 = obj_a
    const.rigid_body_constraint.object2 = obj_b

# 6a. Connect beams at interior nodes
# For each node (i,j), collect adjacent beams:
# - Left X-beam: (i-1, j, 'x') if i>0
# - Right X-beam: (i, j, 'x') if i<num_nodes_x-1
# - Bottom Y-beam: (i, j-1, 'y') if j>0
# - Top Y-beam: (i, j, 'y') if j<num_nodes_y-1
for i in range(num_nodes_x):
    for j in range(num_nodes_y):
        x = i * grid_spacing
        y = j * grid_spacing
        node_loc = (x, y, grid_plane_z)
        adjacent_beams = []
        if i > 0:
            adj = beam_dict.get((i-1, j, 'x'))
            if adj: adjacent_beams.append(adj)
        if i < num_nodes_x - 1:
            adj = beam_dict.get((i, j, 'x'))
            if adj: adjacent_beams.append(adj)
        if j > 0:
            adj = beam_dict.get((i, j-1, 'y'))
            if adj: adjacent_beams.append(adj)
        if j < num_nodes_y - 1:
            adj = beam_dict.get((i, j, 'y'))
            if adj: adjacent_beams.append(adj)
        
        # Connect first beam to each subsequent beam at this node
        if len(adjacent_beams) >= 2:
            for k in range(1, len(adjacent_beams)):
                add_fixed_constraint(adjacent_beams[0], adjacent_beams[k], node_loc)

# 6b. Connect columns to ground and to beams at top nodes
for col in columns:
    # Extract column position from name (or store earlier)
    # Parse name "Column_X_Y"
    parts = col.name.split('_')
    cx = float(parts[1])
    cy = float(parts[2])
    col_base_loc = (cx, cy, 0)
    col_top_loc = (cx, cy, grid_plane_z)
    
    # Column to ground constraint (at base)
    add_fixed_constraint(col, ground, col_base_loc)
    
    # Column to beam(s) at top node
    # Find beams connected to this node (cx,cy) at grid_plane_z
    i = int(cx / grid_spacing + 0.1)  # +0.1 for floating precision
    j = int(cy / grid_spacing + 0.1)
    # Collect beams at this node (same logic as above)
    beams_at_node = []
    if i > 0:
        adj = beam_dict.get((i-1, j, 'x'))
        if adj: beams_at_node.append(adj)
    if i < num_nodes_x - 1:
        adj = beam_dict.get((i, j, 'x'))
        if adj: beams_at_node.append(adj)
    if j > 0:
        adj = beam_dict.get((i, j-1, 'y'))
        if adj: beams_at_node.append(adj)
    if j < num_nodes_y - 1:
        adj = beam_dict.get((i, j, 'y'))
        if adj: beams_at_node.append(adj)
    
    # Connect column to first beam at this node (if any)
    if beams_at_node:
        add_fixed_constraint(col, beams_at_node[0], col_top_loc)
    else:
        # Should not happen for specified column positions
        pass

# ------------------------------------------------------------
# 7. SET PHYSICS WORLD PARAMETERS
# ------------------------------------------------------------
bpy.context.scene.use_gravity = True
bpy.context.scene.gravity = (0, 0, -gravity)
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 50
# Add damping for stability
for obj in bpy.context.scene.objects:
    if obj.rigid_body:
        obj.rigid_body.linear_damping = 0.5
        obj.rigid_body.angular_damping = 0.5

# ------------------------------------------------------------
# 8. VERIFICATION SETUP (Optional)
# ------------------------------------------------------------
# To verify node displacements after simulation, we could store original positions
# and compare after simulation runs. However, headless verification requires
# running simulation and then checking locations.
# Since this is a data generation task, we'll note that verification would be
# done by running the simulation and measuring max displacement.
print("Space grid roof structure created.")
print(f"Total beams: {total_beams}, each with mass {final_beam_mass:.3f} kg")
print(f"Columns: {len(columns)}, each with mass {column_mass:.3f} kg")
print("Structure ready for simulation.")