import bpy
import math
from mathutils import Vector

# Clear scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# ===== PARAMETERS =====
base_side = 3.0
column_width = 0.5
column_height = 20.0
brace_interval = 2.0
brace_length = 3.0
brace_width = 0.2
brace_height = 0.2
step_length = 0.8
step_width = 0.3
step_thickness = 0.05
platform_size = 3.0
platform_height = 0.5
mass_block_size = 1.0
load_mass = 600.0

# Derived
base_radius = base_side / 2.0
sqrt3 = math.sqrt(3.0)
vertex1 = Vector((base_radius, -base_side * sqrt3 / 4.0, 0.0))
vertex2 = Vector((-base_radius, -base_side * sqrt3 / 4.0, 0.0))
vertex3 = Vector((0.0, base_side * sqrt3 / 4.0, 0.0))
vertices = [vertex1, vertex2, vertex3]
num_brace_levels = int(column_height / brace_interval) + 1
steps_total = math.ceil(column_height / step_width)
spiral_radius = base_radius - column_width/2.0 - 0.1
angular_increment = (2.0 * math.pi) / (column_height / step_width)
step_rise = step_width  # each step rises by its width
platform_z = column_height  # bottom of platform at tower top
mass_block_z = column_height + platform_height + mass_block_size/2.0

# ===== STRUCTURAL FRAMEWORK =====
structural_objects = []

# Create three vertical columns
for i, vert in enumerate(vertices):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=vert + Vector((0, 0, column_height/2.0)))
    col = bpy.context.active_object
    col.scale = (column_width, column_width, column_height)
    col.name = f"Column_{i+1}"
    structural_objects.append(col)

# Create horizontal cross-braces at each level
for level in range(num_brace_levels):
    z_pos = level * brace_interval
    # Brace between vertex1 and vertex2
    v1 = vertex1 + Vector((0, 0, z_pos))
    v2 = vertex2 + Vector((0, 0, z_pos))
    center = (v1 + v2) / 2.0
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=center)
    brace = bpy.context.active_object
    brace.scale = (brace_length, brace_width, brace_height)
    # Rotate to align with vertices
    direction = v2 - v1
    angle = math.atan2(direction.y, direction.x)
    brace.rotation_euler.z = angle
    brace.name = f"Brace_1-2_L{level}"
    structural_objects.append(brace)
    
    # Brace between vertex2 and vertex3
    v2 = vertex2 + Vector((0, 0, z_pos))
    v3 = vertex3 + Vector((0, 0, z_pos))
    center = (v2 + v3) / 2.0
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=center)
    brace = bpy.context.active_object
    brace.scale = (brace_length, brace_width, brace_height)
    direction = v3 - v2
    angle = math.atan2(direction.y, direction.x)
    brace.rotation_euler.z = angle
    brace.name = f"Brace_2-3_L{level}"
    structural_objects.append(brace)
    
    # Brace between vertex3 and vertex1
    v3 = vertex3 + Vector((0, 0, z_pos))
    v1 = vertex1 + Vector((0, 0, z_pos))
    center = (v3 + v1) / 2.0
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=center)
    brace = bpy.context.active_object
    brace.scale = (brace_length, brace_width, brace_height)
    direction = v1 - v3
    angle = math.atan2(direction.y, direction.x)
    brace.rotation_euler.z = angle
    brace.name = f"Brace_3-1_L{level}"
    structural_objects.append(brace)

# Create top platform
bpy.ops.mesh.primitive_cube_add(size=1.0, location=Vector((0, 0, platform_z + platform_height/2.0)))
platform = bpy.context.active_object
platform.scale = (platform_size, platform_size, platform_height)
platform.name = "Top_Platform"
structural_objects.append(platform)

# Apply rigid body physics to all structural elements as passive
for obj in structural_objects:
    bpy.ops.rigidbody.object_add({'object': obj})
    obj.rigid_body.type = 'PASSIVE'
    obj.rigid_body.collision_shape = 'BOX'

# ===== SPIRAL STAIRCASE =====
stair_objects = []
for step_idx in range(steps_total):
    angle = step_idx * angular_increment
    x = spiral_radius * math.cos(angle)
    y = spiral_radius * math.sin(angle)
    z = step_idx * step_rise + step_thickness/2.0
    
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=Vector((x, y, z)))
    step = bpy.context.active_object
    step.scale = (step_length, step_width, step_thickness)
    # Rotate step to face outward
    step.rotation_euler.z = angle + math.pi/2.0
    step.name = f"Step_{step_idx:03d}"
    stair_objects.append(step)
    
    # Add rigid body to step
    bpy.ops.rigidbody.object_add({'object': step})
    step.rigid_body.type = 'ACTIVE'
    step.rigid_body.mass = 5.0  # approximate step mass
    step.rigid_body.collision_shape = 'BOX'

# Create hinge constraints for steps to nearest column
for step_idx, step in enumerate(stair_objects):
    # Find nearest column (by angle sector)
    angle = step_idx * angular_increment
    angle_norm = angle % (2.0*math.pi)
    sector = int(angle_norm / (2.0*math.pi/3.0))  # 0,1,2 for three columns
    column = structural_objects[sector]  # columns are first three objects
    
    # Create empty for constraint
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=step.location)
    empty = bpy.context.active_object
    empty.name = f"Hinge_Anchor_{step_idx:03d}"
    
    # Parent empty to column
    empty.parent = column
    
    # Add rigid body constraint
    bpy.ops.rigidbody.constraint_add({'object': empty})
    constraint = empty.rigid_body_constraint
    constraint.type = 'HINGE'
    constraint.object1 = step
    constraint.object2 = None  # connected to world via empty parented to column
    constraint.use_breaking = True
    constraint.breaking_threshold = 1000.0

# ===== LOAD MASS =====
bpy.ops.mesh.primitive_cube_add(size=1.0, location=Vector((0, 0, mass_block_z)))
mass_block = bpy.context.active_object
mass_block.scale = (mass_block_size, mass_block_size, mass_block_size)
mass_block.name = "Load_Mass"
bpy.ops.rigidbody.object_add({'object': mass_block})
mass_block.rigid_body.type = 'ACTIVE'
mass_block.rigid_body.mass = load_mass
mass_block.rigid_body.collision_shape = 'BOX'

# ===== SCENE SETUP =====
# Enable rigid body world
bpy.context.scene.rigidbody_world.enabled = True
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 50

# Set end frame for simulation
bpy.context.scene.frame_end = 500

print("Emergency stair tower construction complete. Ready for physics simulation.")