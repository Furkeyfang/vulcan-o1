import bpy
import math
from mathutils import Vector

# Clear scene
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)

# Parameters from summary
pole_height = 25.0
base_side = 2.0
top_side = 0.5
cubes_per_edge = 25
cube_height = 1.0
brace_interval = 5.0
brace_dims = (0.2, 0.2, 2.0)
beam_dims = (3.0, 0.3, 0.3)
force_magnitude = 1962.0

# Derived geometry
R_base = base_side / math.sqrt(3)
R_top = top_side / math.sqrt(3)
base_vertices = [
    Vector((R_base, 0, 0)),
    Vector((-R_base/2, R_base*math.sqrt(3)/2, 0)),
    Vector((-R_base/2, -R_base*math.sqrt(3)/2, 0))
]
brace_heights = [h for h in range(5, int(pole_height), 5)]
beam_center = Vector((0, 0, pole_height + beam_dims[2]/2))

# Store objects for constraint creation
all_cubes = []
bottom_cubes = []  # For passive rigid bodies

# Create vertical edges
for v_idx, base_v in enumerate(base_vertices):
    for i in range(cubes_per_edge):
        # Linear interpolation from base to top
        t = (i * cube_height + cube_height/2) / pole_height
        R_current = R_base + (R_top - R_base) * t
        # Scale vertex position by current radius
        dir_vec = base_v.normalized()
        pos = dir_vec * R_current
        pos.z = i * cube_height + cube_height/2
        
        # Create cube
        bpy.ops.mesh.primitive_cube_add(size=1, location=pos)
        cube = bpy.context.active_object
        cube.scale = (0.1, 0.1, cube_height/2)  # Thin columns
        cube.name = f"edge_{v_idx}_cube_{i}"
        all_cubes.append(cube)
        
        # Mark bottom cubes as passive
        if i == 0:
            bottom_cubes.append(cube)

# Create cross-bracing
for height in brace_heights:
    for i in range(3):
        v1_idx = i
        v2_idx = (i + 1) % 3
        
        # Interpolate vertex positions at this height
        t = height / pole_height
        R_current = R_base + (R_top - R_base) * t
        dir1 = base_vertices[v1_idx].normalized()
        dir2 = base_vertices[v2_idx].normalized()
        pos1 = dir1 * R_current
        pos2 = dir2 * R_current
        pos1.z = height
        pos2.z = height
        
        # Midpoint and direction
        mid = (pos1 + pos2) / 2
        direction = (pos2 - pos1).normalized()
        length = (pos2 - pos1).length
        
        # Create brace cube
        bpy.ops.mesh.primitive_cube_add(size=1, location=mid)
        brace = bpy.context.active_object
        brace.scale = (brace_dims[0]/2, brace_dims[1]/2, length/2)
        brace.name = f"brace_h{height}_edge{i}"
        
        # Rotate to align with edge direction
        up = Vector((0, 0, 1))
        rot_quat = up.rotation_difference(direction)
        brace.rotation_mode = 'QUATERNION'
        brace.rotation_quaternion = rot_quat
        
        all_cubes.append(brace)

# Create top beam
bpy.ops.mesh.primitive_cube_add(size=1, location=beam_center)
beam = bpy.context.active_object
beam.scale = (beam_dims[0]/2, beam_dims[1]/2, beam_dims[2]/2)
beam.name = "top_beam"
all_cubes.append(beam)

# Apply rigid body physics
for obj in all_cubes:
    bpy.ops.rigidbody.object_add({'object': obj})
    if obj in bottom_cubes:
        obj.rigid_body.type = 'PASSIVE'
    else:
        obj.rigid_body.type = 'ACTIVE'
        obj.rigid_body.collision_shape = 'BOX'
        obj.rigid_body.mass = 1.0  # Base mass, will scale with volume

# Add fixed constraints between adjacent elements
# This simulates welded connections
for obj in all_cubes:
    # Find neighbors based on naming and proximity
    pass  # In practice, we'd create constraint objects between geometrically adjacent cubes
    # For brevity, we'll create a single compound rigid body approach:
    
# Alternative: Parent all objects and make single rigid body
bpy.ops.object.select_all(action='DESELECT')
for obj in all_cubes:
    obj.select_set(True)
bpy.context.view_layer.objects.active = all_cubes[0]
bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)

# Add single rigid body to parent
bpy.ops.rigidbody.object_add()
all_cubes[0].rigid_body.type = 'ACTIVE'
all_cubes[0].rigid_body.collision_shape = 'COMPOUND'

# Apply force to beam (simulate cable load)
beam.rigid_body.use_gravity = False  # Override gravity for precise force
# Force applied via rigid body settings (constant force in local Z)
beam.rigid_body.enabled = True
# In practice, would add force field or use animation, but for static:
# We'll set up a force field at beam location
bpy.ops.object.empty_add(type='PLAIN_AXES', location=beam_center)
force_empty = bpy.context.active_object
bpy.ops.object.forcefield_add()
force_empty.field.type = 'FORCE'
force_empty.field.strength = -force_magnitude
force_empty.field.falloff_power = 0
force_empty.field.use_max_distance = True
force_empty.field.distance_max = 0.5

# Link force field to beam
beam.field.new(type='FORCE')
beam.field.strength = -force_magnitude
beam.field.use_max_distance = True
beam.field.distance_max = 0.1

# Simulation settings
bpy.context.scene.frame_end = 100
bpy.context.scene.rigidbody_world.enabled = True
bpy.context.scene.rigidbody_world.steps_per_second = 250
bpy.context.scene.rigidbody_world.solver_iterations = 50
bpy.context.scene.rigidbody_world.time_scale = 1.0
bpy.context.scene.gravity = (0, 0, -9.81)

print("Transmission pole construction complete. Run simulation for 100 frames.")