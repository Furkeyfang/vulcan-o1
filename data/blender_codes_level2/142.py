import bpy
import mathutils

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Parameters from summary
segment_count = 8
segment_dim = (1.0, 1.0, 1.0)
segment_spacing = 1.0
base_z_offset = 0.5
load_dim = (1.0, 1.0, 0.5)
load_mass = 1200.0
load_z = 8.25
constraint_offset_z = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0]
simulation_frames = 100
steel_friction = 0.5
steel_restitution = 0.3

# Create tower segments
segments = []
for i in range(segment_count):
    z_pos = base_z_offset + (i * segment_spacing)
    
    # Create cube segment
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, 0.0, z_pos))
    segment = bpy.context.active_object
    segment.scale = segment_dim
    segment.name = f"Segment_{i}"
    
    # Add rigid body physics (all passive)
    bpy.ops.rigidbody.object_add()
    segment.rigid_body.type = 'PASSIVE'
    segment.rigid_body.friction = steel_friction
    segment.rigid_body.restitution = steel_restitution
    
    segments.append(segment)

# Create fixed constraints between segments
for i in range(len(segments) - 1):
    # Create constraint empty at interface
    const_z = constraint_offset_z[i]
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0.0, 0.0, const_z))
    constraint = bpy.context.active_object
    constraint.name = f"Fixed_Constraint_{i}"
    
    # Add rigid body constraint
    bpy.ops.rigidbody.constraint_add()
    rb_constraint = constraint.rigid_body_constraint
    rb_constraint.type = 'FIXED'
    
    # Connect adjacent segments
    rb_constraint.object1 = segments[i]
    rb_constraint.object2 = segments[i + 1]

# Create load cube
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, 0.0, load_z))
load = bpy.context.active_object
load.scale = load_dim
load.name = "Load_Cube"

# Add rigid body physics (active with mass)
bpy.ops.rigidbody.object_add()
load.rigid_body.type = 'ACTIVE'
load.rigid_body.mass = load_mass
load.rigid_body.friction = steel_friction
load.rigid_body.restitution = steel_restitution

# Configure simulation settings
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 50
bpy.context.scene.frame_end = simulation_frames

# Ensure proper collision margins
for obj in segments + [load]:
    if obj.rigid_body:
        obj.rigid_body.use_margin = True
        obj.rigid_body.collision_margin = 0.04

print("Tower construction complete. Ready for simulation.")