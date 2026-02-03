import bpy
import mathutils

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Extract parameters from summary
tower_w = 1.0
tower_d = 1.0
tower_h = 10.0
left_tower_center = mathutils.Vector((-5.0, 0.0, 5.0))
right_tower_center = mathutils.Vector((5.0, 0.0, 5.0))

platform_len = 10.0
platform_wid = 3.0
platform_thick = 0.5
platform_center = mathutils.Vector((0.0, 0.0, 10.25))

load_mass = 600.0
load_size = 1.0
load_loc = mathutils.Vector((0.0, 0.0, 10.5))

connection_h = 10.0

# Create left tower
bpy.ops.mesh.primitive_cube_add(size=1.0, location=left_tower_center)
left_tower = bpy.context.active_object
left_tower.scale = (tower_w, tower_d, tower_h)
left_tower.name = "LeftTower"
bpy.ops.rigidbody.object_add()
left_tower.rigid_body.type = 'PASSIVE'
left_tower.rigid_body.mass = 1000.0  # Heavy concrete

# Create right tower  
bpy.ops.mesh.primitive_cube_add(size=1.0, location=right_tower_center)
right_tower = bpy.context.active_object
right_tower.scale = (tower_w, tower_d, tower_h)
right_tower.name = "RightTower"
bpy.ops.rigidbody.object_add()
right_tower.rigid_body.type = 'PASSIVE'
right_tower.rigid_body.mass = 1000.0

# Create platform
bpy.ops.mesh.primitive_cube_add(size=1.0, location=platform_center)
platform = bpy.context.active_object
platform.scale = (platform_len, platform_wid, platform_thick)
platform.name = "Platform"
bpy.ops.rigidbody.object_add()
platform.rigid_body.type = 'PASSIVE'
platform.rigid_body.mass = 500.0  # Steel platform

# Create load (active rigid body)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=load_loc)
load = bpy.context.active_object
load.scale = (load_size, load_size, load_size)
load.name = "Load"
bpy.ops.rigidbody.object_add()
load.rigid_body.type = 'ACTIVE'
load.rigid_body.mass = load_mass

# Create fixed constraints between towers and ground (implicit ground at Z=0)
# We'll create an empty at each connection point and parent it appropriately
def create_fixed_constraint(obj1, obj2, constraint_name, location):
    """Create a fixed rigid body constraint between two objects"""
    # Create empty at constraint location
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=location)
    empty = bpy.context.active_object
    empty.name = constraint_name
    
    # Add rigid body constraint
    bpy.ops.rigidbody.constraint_add()
    rb_constraint = empty.rigid_body_constraint
    rb_constraint.type = 'FIXED'
    rb_constraint.object1 = obj1
    rb_constraint.object2 = obj2

# Left tower to ground (constraint at tower base)
create_fixed_constraint(
    left_tower, 
    None,  # Ground is implicit (world)
    "LeftTower_Base_Constraint",
    (-5.0, 0.0, 0.0)
)

# Right tower to ground
create_fixed_constraint(
    right_tower,
    None,
    "RightTower_Base_Constraint", 
    (5.0, 0.0, 0.0)
)

# Platform to left tower (constraint at tower top)
create_fixed_constraint(
    platform,
    left_tower,
    "Left_Platform_Connection",
    (-5.0, 0.0, connection_h)
)

# Platform to right tower
create_fixed_constraint(
    platform,
    right_tower,
    "Right_Platform_Connection",
    (5.0, 0.0, connection_h)
)

# Configure simulation settings for stability
scene = bpy.context.scene
scene.rigidbody_world.steps_per_second = 240
scene.rigidbody_world.solver_iterations = 50

# Add a ground plane for collision
bpy.ops.mesh.primitive_plane_add(size=50.0, location=(0,0,-0.1))
ground = bpy.context.active_object
ground.name = "Ground"
bpy.ops.rigidbody.object_add()
ground.rigid_body.type = 'PASSIVE'

# Verification: Measure horizontal gap between tower centers
gap = (right_tower_center - left_tower_center).length
print(f"Tower center-to-center gap: {gap} meters")
print(f"Design requirement: 10.0 meters")
print(f"Verification: {'PASS' if abs(gap - 10.0) < 0.01 else 'FAIL'}")

# Add simple material colors for visualization (optional but helpful)
def add_material(obj, color):
    mat = bpy.data.materials.new(name=obj.name + "_Mat")
    mat.diffuse_color = color
    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)

add_material(left_tower, (0.6, 0.6, 0.6, 1.0))
add_material(right_tower, (0.6, 0.6, 0.6, 1.0))
add_material(platform, (0.8, 0.7, 0.6, 1.0))
add_material(load, (1.0, 0.2, 0.2, 1.0))
add_material(ground, (0.3, 0.5, 0.3, 1.0))