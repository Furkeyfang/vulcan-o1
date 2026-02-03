import bpy
import math
import mathutils

# Clear scene
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

# Define variables from parameter_summary
platform_dim = (10.0, 10.0, 0.5)
platform_center = (5.0, 5.0, 0.25)
core_dim = (1.5, 1.5, 25.0)
core_offset_x = 1.2
core_base = (1.2, 0.0, 0.0)
core_top_center = (1.95, 0.75, 25.0)
beam_dim = (0.5, 0.5, 25.0)
beam_positions = [(0.0, 0.0, 0.0), (9.5, 0.0, 0.0), (0.0, 9.5, 0.0), (9.5, 9.5, 0.0)]
cross_beam_dim = (0.3, 0.3, 4.0)
platform_corners_top = [(0.0, 0.0, 0.5), (10.0, 0.0, 0.5), (0.0, 10.0, 0.5), (10.0, 10.0, 0.5)]
platform_corners_z25 = [(0.0, 0.0, 25.0), (10.0, 0.0, 25.0), (0.0, 10.0, 25.0), (10.0, 10.0, 25.0)]
core_corners_top = [(1.2, 0.0, 25.0), (2.7, 0.0, 25.0), (1.2, 1.5, 25.0), (2.7, 1.5, 25.0)]
load_mass = 1500.0
gravity = 9.81

# Create ground plane (passive rigid body)
bpy.ops.mesh.primitive_plane_add(size=50, location=(0,0,-0.1))
ground = bpy.context.active_object
ground.name = "Ground"
bpy.ops.rigidbody.object_add()
ground.rigid_body.type = 'PASSIVE'

# Create platform
bpy.ops.mesh.primitive_cube_add(size=1, location=platform_center)
platform = bpy.context.active_object
platform.name = "Platform"
platform.scale = platform_dim
bpy.ops.rigidbody.object_add()
platform.rigid_body.type = 'ACTIVE'
platform.rigid_body.mass = load_mass

# Create core column
bpy.ops.mesh.primitive_cube_add(size=1, location=(
    core_base[0] + core_dim[0]/2,
    core_base[1] + core_dim[1]/2,
    core_dim[2]/2
))
core = bpy.context.active_object
core.name = "Core"
core.scale = core_dim
bpy.ops.rigidbody.object_add()
core.rigid_body.type = 'ACTIVE'
core.rigid_body.mass = core_dim[0] * core_dim[1] * core_dim[2] * 2400  # Concrete density ~2400 kg/m³

# Create support beams
support_beams = []
for i, pos in enumerate(beam_positions):
    bpy.ops.mesh.primitive_cube_add(size=1, location=(
        pos[0] + beam_dim[0]/2,
        pos[1] + beam_dim[1]/2,
        beam_dim[2]/2
    ))
    beam = bpy.context.active_object
    beam.name = f"Support_Beam_{i+1}"
    beam.scale = beam_dim
    bpy.ops.rigidbody.object_add()
    beam.rigid_body.type = 'ACTIVE'
    beam.rigid_body.mass = beam_dim[0] * beam_dim[1] * beam_dim[2] * 2400
    support_beams.append(beam)

# Create cross-beams
cross_beams = []
for i in range(4):
    # Calculate vector from core corner to platform corner at Z=25
    start = mathutils.Vector(core_corners_top[i])
    end = mathutils.Vector(platform_corners_z25[i])
    direction = end - start
    length = direction.length
    
    # Create beam at midpoint
    midpoint = (start + end) / 2
    bpy.ops.mesh.primitive_cube_add(size=1, location=midpoint)
    cross_beam = bpy.context.active_object
    cross_beam.name = f"Cross_Beam_{i+1}"
    
    # Scale to correct dimensions (length adjusted for direction)
    cross_beam.scale = (
        cross_beam_dim[0],
        cross_beam_dim[1],
        length / 2  # Divide by 2 because cube primitive has size=1 gives length=1
    )
    
    # Rotate to align with direction vector
    up = mathutils.Vector((0, 0, 1))
    rot_quat = direction.to_track_quat('-Z', 'Y')
    cross_beam.rotation_euler = rot_quat.to_euler()
    
    bpy.ops.rigidbody.object_add()
    cross_beam.rigid_body.type = 'ACTIVE'
    cross_beam.rigid_body.mass = cross_beam_dim[0] * cross_beam_dim[1] * length * 2400
    cross_beams.append(cross_beam)

# Create constraints
def add_fixed_constraint(obj_a, obj_b, frame_a=(0,0,0), frame_b=(0,0,0)):
    # Create empty for constraint
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0,0,0))
    constraint_empty = bpy.context.active_object
    constraint_empty.name = f"Constraint_{obj_a.name}_to_{obj_b.name}"
    
    # Add rigid body constraint
    bpy.ops.rigidbody.constraint_add()
    constraint = constraint_empty.rigid_body_constraint
    constraint.type = 'FIXED'
    constraint.object1 = obj_a
    constraint.object2 = obj_b
    
    # Set constraint frames
    constraint.frame_in_a = frame_a
    constraint.frame_in_b = frame_b
    
    return constraint

# Platform to ground constraint
add_fixed_constraint(platform, ground, 
                     frame_a=(0,0,0),  # Platform base center
                     frame_b=(platform_center[0], platform_center[1], 0))  # Ground below platform

# Core to ground constraint
add_fixed_constraint(core, ground,
                     frame_a=(0,0,-core_dim[2]/2),  # Core base
                     frame_b=(core_base[0] + core_dim[0]/2, 
                              core_base[1] + core_dim[1]/2, 
                              0))  # Ground below core

# Support beams to ground constraints
for i, beam in enumerate(support_beams):
    pos = beam_positions[i]
    add_fixed_constraint(beam, ground,
                         frame_a=(0,0,-beam_dim[2]/2),  # Beam base
                         frame_b=(pos[0] + beam_dim[0]/2,
                                  pos[1] + beam_dim[1]/2,
                                  0))  # Ground below beam

# Support beams to platform constraints
for i, beam in enumerate(support_beams):
    # Connect beam base to platform corner
    corner_pos = platform_corners_top[i]
    # Local position in platform coordinates
    local_pos = (
        corner_pos[0] - platform_center[0],
        corner_pos[1] - platform_center[1],
        corner_pos[2] - platform_center[2]
    )
    add_fixed_constraint(beam, platform,
                         frame_a=(0,0,-beam_dim[2]/2),  # Beam base
                         frame_b=local_pos)  # Platform corner

# Cross-beams to core constraints
for i, cross_beam in enumerate(cross_beams):
    # Connect to appropriate core corner
    core_corner_local = (
        core_corners_top[i][0] - (core_base[0] + core_dim[0]/2),
        core_corners_top[i][1] - (core_base[1] + core_dim[1]/2),
        core_corners_top[i][2] - core_dim[2]/2
    )
    add_fixed_constraint(cross_beam, core,
                         frame_a=(0,0,-cross_beam.scale.z),  # One end of cross-beam
                         frame_b=core_corner_local)

# Cross-beams to platform corners at Z=25 (via support beams)
for i, cross_beam in enumerate(cross_beams):
    # Connect to support beam at platform corner
    support_beam = support_beams[i]
    # Local position at top of support beam
    beam_top_local = (0, 0, beam_dim[2]/2)
    add_fixed_constraint(cross_beam, support_beam,
                         frame_a=(0,0,cross_beam.scale.z),  # Other end of cross-beam
                         frame_b=beam_top_local)

# Set world physics properties
bpy.context.scene.gravity[2] = -gravity  # Negative Z for downward gravity

# Verify offset is correct
print(f"Core offset from platform center in X: {core_offset_x}m")
print(f"Core base position: {core_base}")
print(f"Platform load: {load_mass}kg = {load_mass * gravity}N")
print(f"Structure ready for simulation")