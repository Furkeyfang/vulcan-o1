import bpy
import mathutils

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Parameters from summary
pl_x = 8.0
pl_y = 4.0
pl_thick = 0.5
base_z = 0.25
col_w = 0.5
col_h = 3.0
first_col_z = 2.0
mid_plat_z = 3.75
second_col_z = 5.5
top_plat_z = 7.25
off_x = 3.75
off_y = 1.75
plat_mass = 1500.0
corners = [(off_x, off_y), (off_x, -off_y), (-off_x, off_y), (-off_x, -off_y)]
sim_frames = 100
gravity = -9.81

# Enable rigid body physics
if bpy.context.scene.rigidbody_world is None:
    bpy.ops.rigidbody.world_add()
bpy.context.scene.rigidbody_world.enabled = True
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 10
bpy.context.scene.rigidbody_world.gravity = mathutils.Vector((0, 0, gravity))

# Function to create fixed constraint between two objects
def create_fixed_constraint(obj_a, obj_b, name="Fixed_Constraint"):
    # Create empty object for constraint
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0,0,0))
    constraint = bpy.context.active_object
    constraint.name = name
    constraint.empty_display_size = 0.5
    
    # Add rigid body constraint
    bpy.ops.rigidbody.constraint_add()
    constraint.rigid_body_constraint.type = 'FIXED'
    constraint.rigid_body_constraint.object1 = obj_a
    constraint.rigid_body_constraint.object2 = obj_b
    constraint.rigid_body_constraint.disable_collisions = True

# Create base platform
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, base_z))
base = bpy.context.active_object
base.name = "Base_Platform"
base.scale = (pl_x, pl_y, pl_thick)
bpy.ops.rigidbody.object_add()
base.rigid_body.type = 'PASSIVE'  # Fixed to world
base.rigid_body.mass = plat_mass
base.rigid_body.collision_shape = 'BOX'

# Create first level columns
first_columns = []
for i, (cx, cy) in enumerate(corners):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(cx, cy, first_col_z))
    col = bpy.context.active_object
    col.name = f"First_Column_{i+1}"
    col.scale = (col_w, col_w, col_h)
    bpy.ops.rigidbody.object_add()
    col.rigid_body.type = 'ACTIVE'
    col.rigid_body.collision_shape = 'BOX'
    first_columns.append(col)
    
    # Fixed constraint to base
    create_fixed_constraint(base, col, f"Base_Column_{i+1}_Fix")

# Create middle platform
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, mid_plat_z))
mid = bpy.context.active_object
mid.name = "Middle_Platform"
mid.scale = (pl_x, pl_y, pl_thick)
bpy.ops.rigidbody.object_add()
mid.rigid_body.type = 'ACTIVE'
mid.rigid_body.mass = plat_mass
mid.rigid_body.collision_shape = 'BOX'

# Fix middle platform to first columns
for i, col in enumerate(first_columns):
    create_fixed_constraint(col, mid, f"Col{i+1}_Mid_Fix")

# Create second level columns
second_columns = []
for i, (cx, cy) in enumerate(corners):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(cx, cy, second_col_z))
    col = bpy.context.active_object
    col.name = f"Second_Column_{i+1}"
    col.scale = (col_w, col_w, col_h)
    bpy.ops.rigidbody.object_add()
    col.rigid_body.type = 'ACTIVE'
    col.rigid_body.collision_shape = 'BOX'
    second_columns.append(col)
    
    # Fixed constraint to middle platform
    create_fixed_constraint(mid, col, f"Mid_Col{i+1}_Fix")

# Create top platform
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, top_plat_z))
top = bpy.context.active_object
top.name = "Top_Platform"
top.scale = (pl_x, pl_y, pl_thick)
bpy.ops.rigidbody.object_add()
top.rigid_body.type = 'ACTIVE'
top.rigid_body.mass = plat_mass
top.rigid_body.collision_shape = 'BOX'

# Fix top platform to second columns
for i, col in enumerate(second_columns):
    create_fixed_constraint(col, top, f"Col{i+1}_Top_Fix")

# Bake simulation for verification
bpy.context.scene.frame_end = sim_frames
bpy.ops.ptcache.free_bake_all()  # Clear any existing caches
bpy.ops.ptcache.bake_all(bake=True)  # Bake physics

print(f"Structure built. Simulating {sim_frames} frames with gravity={gravity} m/s²")