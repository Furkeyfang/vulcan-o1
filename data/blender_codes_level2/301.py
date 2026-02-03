import bpy
import math

# Clear scene
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)

# Parameters from summary
seg_count = 8
seg_dim = (2.0, 2.0, 2.0)
col_height = 16.0
seg_height = 2.0
total_twist = 45.0
twist_inc = total_twist / (seg_count - 1)  # 6.42857°
base_z = 1.0
load_mass = 1000.0
load_dim = (1.0, 1.0, 1.0)
load_z = 16.5
bottom_passive = True

# Create column segments
segments = []
for i in range(seg_count):
    # Calculate position
    seg_z = base_z + (i * seg_height)
    
    # Calculate rotation (cumulative)
    rot_z_deg = i * twist_inc
    rot_z_rad = math.radians(rot_z_deg)
    
    # Create cube
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, 0.0, seg_z))
    seg = bpy.context.active_object
    seg.scale = seg_dim
    seg.rotation_euler = (0.0, 0.0, rot_z_rad)
    seg.name = f"Segment_{i}"
    
    # Add rigid body
    bpy.ops.rigidbody.object_add()
    if i == 0 and bottom_passive:
        seg.rigid_body.type = 'PASSIVE'
    else:
        seg.rigid_body.type = 'ACTIVE'
        seg.rigid_body.mass = 1.0  # Uniform density
    
    segments.append(seg)

# Create fixed constraints between segments
for i in range(seg_count - 1):
    # Create constraint empty at interface
    interface_z = base_z + (i * seg_height) + (seg_height / 2)
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0.0, 0.0, interface_z))
    constraint = bpy.context.active_object
    constraint.name = f"Constraint_{i}_{i+1}"
    
    # Add rigid body constraint
    bpy.ops.rigidbody.constraint_add()
    constraint.rigid_body_constraint.type = 'FIXED'
    constraint.rigid_body_constraint.object1 = segments[i]
    constraint.rigid_body_constraint.object2 = segments[i + 1]

# Create load cube
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, 0.0, load_z))
load = bpy.context.active_object
load.scale = load_dim
load.rotation_euler = (0.0, 0.0, math.radians(total_twist))
load.name = "Load_1000kg"

# Add rigid body to load
bpy.ops.rigidbody.object_add()
load.rigid_body.type = 'ACTIVE'
load.rigid_body.mass = load_mass

# Constraint between top segment and load
bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0.0, 0.0, col_height))
top_constraint = bpy.context.active_object
top_constraint.name = "Top_Constraint"
bpy.ops.rigidbody.constraint_add()
top_constraint.rigid_body_constraint.type = 'FIXED'
top_constraint.rigid_body_constraint.object1 = segments[-1]
top_constraint.rigid_body_constraint.object2 = load

# Set gravity (standard Earth gravity in Blender units)
if bpy.context.scene.rigidbody_world:
    bpy.context.scene.rigidbody_world.gravity[2] = -9.81

# Optional: Set substeps for stability
bpy.context.scene.rigidbody_world.substeps_per_frame = 10
bpy.context.scene.rigidbody_world.solver_iterations = 50

print(f"Column constructed: {seg_count} segments, {total_twist}° total twist")
print(f"Load: {load_mass} kg at Z={load_z}")