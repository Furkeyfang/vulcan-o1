import bpy
import math

# Clear scene
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

# Parameters from summary
col_sz = (0.5, 0.5, 17.0)
tri_side = 2.0
circum_r = tri_side / math.sqrt(3.0)
v_a = (0.0, circum_r, 0.0)
v_b = (tri_side/2, -circum_r/2, 0.0)
v_c = (-tri_side/2, -circum_r/2, 0.0)
brace_lvls = [0.5, 8.5, 16.5]
brace_sz = (0.2, 2.0, 0.2)
plat_sz = (2.0, 2.0, 0.5)
plat_cent = (0.0, 0.0, 17.0)
load_sz = (0.5, 0.5, 0.5)
load_mass = 300.0
load_cent = (0.0, 0.0, 17.25)

# Function to create rigid body object
def make_passive(obj):
    bpy.ops.rigidbody.object_add()
    obj.rigid_body.type = 'PASSIVE'
    obj.rigid_body.collision_shape = 'BOX'

# Create three vertical columns
vertices = [v_a, v_b, v_c]
columns = []
for i, v in enumerate(vertices):
    bpy.ops.mesh.primitive_cube_add(size=1, location=v)
    col = bpy.context.active_object
    col.scale = col_sz
    col.name = f"Column_{i}"
    make_passive(col)
    columns.append(col)

# Create cross-braces at three levels
for z in brace_lvls:
    # Brace between A and B
    mid_ab = ((v_a[0]+v_b[0])/2, (v_a[1]+v_b[1])/2, z)
    bpy.ops.mesh.primitive_cube_add(size=1, location=mid_ab)
    brace_ab = bpy.context.active_object
    brace_ab.scale = brace_sz
    # Rotate to align with AB vector
    angle = math.atan2(v_b[1]-v_a[1], v_b[0]-v_a[0])
    brace_ab.rotation_euler.z = angle
    make_passive(brace_ab)
    
    # Brace between B and C
    mid_bc = ((v_b[0]+v_c[0])/2, (v_b[1]+v_c[1])/2, z)
    bpy.ops.mesh.primitive_cube_add(size=1, location=mid_bc)
    brace_bc = bpy.context.active_object
    brace_bc.scale = brace_sz
    angle = math.atan2(v_c[1]-v_b[1], v_c[0]-v_b[0])
    brace_bc.rotation_euler.z = angle
    make_passive(brace_bc)
    
    # Brace between C and A
    mid_ca = ((v_c[0]+v_a[0])/2, (v_c[1]+v_a[1])/2, z)
    bpy.ops.mesh.primitive_cube_add(size=1, location=mid_ca)
    brace_ca = bpy.context.active_object
    brace_ca.scale = brace_sz
    angle = math.atan2(v_a[1]-v_c[1], v_a[0]-v_c[0])
    brace_ca.rotation_euler.z = angle
    make_passive(brace_ca)

# Create top platform
bpy.ops.mesh.primitive_cube_add(size=1, location=plat_cent)
platform = bpy.context.active_object
platform.scale = plat_sz
make_passive(platform)

# Create load cube
bpy.ops.mesh.primitive_cube_add(size=1, location=load_cent)
load = bpy.context.active_object
load.scale = load_sz
bpy.ops.rigidbody.object_add()
load.rigid_body.mass = load_mass
load.rigid_body.collision_shape = 'BOX'

# Add fixed constraints between all connected parts
def add_fixed_constraint(obj1, obj2, location):
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=location)
    empty = bpy.context.active_object
    bpy.ops.rigidbody.constraint_add()
    constraint = empty.rigid_body_constraint
    constraint.type = 'FIXED'
    constraint.object1 = obj1
    constraint.object2 = obj2

# Constrain columns to platform at top
for col in columns:
    top_pos = (col.location.x, col.location.y, 17.0)
    add_fixed_constraint(col, platform, top_pos)

# Constrain columns to braces at each level
for z in brace_lvls:
    # Column A to braces
    add_fixed_constraint(columns[0], bpy.data.objects.get(f"Cube.{3*brace_lvls.index(z)}"), (v_a[0], v_a[1], z))
    # Column B to braces  
    add_fixed_constraint(columns[1], bpy.data.objects.get(f"Cube.{3*brace_lvls.index(z)+1}"), (v_b[0], v_b[1], z))
    # Column C to braces
    add_fixed_constraint(columns[2], bpy.data.objects.get(f"Cube.{3*brace_lvls.index(z)+2}"), (v_c[0], v_c[1], z))

# Setup physics world
bpy.context.scene.rigidbody_world.enabled = True
bpy.context.scene.rigidbody_world.time_scale = 1.0
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 50
bpy.context.scene.frame_end = 100