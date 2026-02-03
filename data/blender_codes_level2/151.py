import bpy
import math

# Clear existing scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Parameters from summary
base_size = (4.0, 4.0, 0.5)
base_loc = (0.0, 0.0, 0.25)

col_radius = 0.3
col_height = 16.0
col_z_center = 8.5
col_offsets = [(-2.0, -2.0), (-2.0, 2.0), (2.0, -2.0), (2.0, 2.0)]

frame_size = (4.0, 4.0, 0.5)
frame_loc = (0.0, 0.0, 16.75)

holder_radius = 0.8
holder_height = 0.5
holder_loc = (0.0, 0.0, 17.25)
holder_mass = 1500.0

steel_density = 7850.0

# Enable rigid body physics
bpy.context.scene.use_gravity = True
bpy.context.scene.gravity = (0.0, 0.0, -9.81)

# ========== 1. BASE PLATFORM ==========
bpy.ops.mesh.primitive_cube_add(size=1.0, location=base_loc)
base = bpy.context.active_object
base.name = "BasePlatform"
base.scale = base_size
bpy.ops.rigidbody.object_add()
base.rigid_body.type = 'PASSIVE'
base.rigid_body.collision_shape = 'BOX'

# ========== 2. FOUR VERTICAL COLUMNS ==========
columns = []
for i, (dx, dy) in enumerate(col_offsets, 1):
    col_loc = (dx, dy, col_z_center)
    bpy.ops.mesh.primitive_cylinder_add(
        radius=col_radius,
        depth=col_height,
        location=col_loc
    )
    col = bpy.context.active_object
    col.name = f"Column_{i}"
    col.rotation_euler = (math.pi/2, 0, 0)  # Rotate to vertical
    
    # Rigid body with steel density
    bpy.ops.rigidbody.object_add()
    col.rigid_body.type = 'ACTIVE'
    col.rigid_body.collision_shape = 'CYLINDER'
    col.rigid_body.mass = steel_density * (math.pi * col_radius**2 * col_height)
    columns.append(col)

# ========== 3. TOP FRAME ==========
bpy.ops.mesh.primitive_cube_add(size=1.0, location=frame_loc)
frame = bpy.context.active_object
frame.name = "TopFrame"
frame.scale = frame_size
bpy.ops.rigidbody.object_add()
frame.rigid_body.type = 'ACTIVE'
frame.rigid_body.collision_shape = 'BOX'
frame.rigid_body.mass = steel_density * (frame_size[0] * frame_size[1] * frame_size[2])

# ========== 4. PIPE HOLDER ==========
bpy.ops.mesh.primitive_cylinder_add(
    radius=holder_radius,
    depth=holder_height,
    location=holder_loc
)
holder = bpy.context.active_object
holder.name = "PipeHolder"
holder.rotation_euler = (math.pi/2, 0, 0)  # Rotate to vertical

bpy.ops.rigidbody.object_add()
holder.rigid_body.type = 'ACTIVE'
holder.rigid_body.collision_shape = 'CYLINDER'
holder.rigid_body.mass = holder_mass  # Direct mass assignment

# ========== 5. FIXED CONSTRAINTS ==========
def create_fixed_constraint(obj_a, obj_b, constraint_loc, constraint_name):
    """Create a fixed constraint between two rigid bodies at specified location"""
    # Create empty for constraint pivot
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=constraint_loc)
    empty = bpy.context.active_object
    empty.name = constraint_name
    
    # Add rigid body constraint
    bpy.ops.rigidbody.constraint_add()
    constraint = empty.rigid_body_constraint
    constraint.type = 'FIXED'
    constraint.object1 = obj_a
    constraint.object2 = obj_b
    
    return empty

# Base-to-Column constraints (at column bases)
for i, col in enumerate(columns):
    base_loc = (col_offsets[i][0], col_offsets[i][1], 0.5)
    create_fixed_constraint(
        base, col, base_loc, f"BaseCol_Constraint_{i+1}"
    )

# Column-to-Frame constraints (at column tops)
for i, col in enumerate(columns):
    top_loc = (col_offsets[i][0], col_offsets[i][1], 16.5)
    create_fixed_constraint(
        col, frame, top_loc, f"ColFrame_Constraint_{i+1}"
    )

# Frame-to-Holder constraint (at holder base)
create_fixed_constraint(
    frame, holder, (0.0, 0.0, 17.0), "FrameHolder_Constraint"
)

# ========== 6. FINAL SETTINGS ==========
# Set collision margins for stability
for obj in bpy.data.objects:
    if hasattr(obj, 'rigid_body') and obj.rigid_body:
        obj.rigid_body.collision_margin = 0.04

# Set simulation substeps for stability
bpy.context.scene.rigidbody_world.substeps_per_frame = 10
bpy.context.scene.rigidbody_world.solver_iterations = 50

print("Pipe rack structure created with fixed constraints and 1500 kg pipe load.")