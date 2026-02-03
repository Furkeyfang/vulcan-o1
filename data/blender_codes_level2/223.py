import bpy
import math
from mathutils import Vector

# Clear scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Parameters from summary
roof_width = 10.0
roof_depth = 5.0
ridge_x = 0.0
break_x = 3.0
eave_x = 5.0
ridge_z = 5.196
break_z = 1.732
eave_z = 0.0
beam_cross = 0.2
num_rafters_y = 6
rafter_spacing = roof_depth / (num_rafters_y - 1)
load_mass = 700.0
beam_density = 500.0
beam_margin = 0.04

# Enable rigid body physics
bpy.context.scene.rigidbody_world.steps_per_second = 250
bpy.context.scene.rigidbody_world.solver_iterations = 50

def create_beam(name, start, end):
    """Create a beam between two points with proper orientation"""
    # Calculate beam properties
    length = (Vector(end) - Vector(start)).length
    mid = ((start[0] + end[0])/2, (start[1] + end[1])/2, (start[2] + end[2])/2)
    
    # Create cube and scale to beam dimensions
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=mid)
    beam = bpy.context.active_object
    beam.name = name
    
    # Scale: cross-section 0.2m, length as calculated
    beam.scale = (beam_cross/2, beam_cross/2, length/2)
    
    # Rotate to align with direction vector
    direction = Vector(end) - Vector(start)
    up = Vector((0, 0, 1))
    rot_quat = direction.to_track_quat('Z', 'Y')
    beam.rotation_euler = rot_quat.to_euler()
    
    # Add rigid body
    bpy.ops.rigidbody.object_add()
    beam.rigid_body.type = 'ACTIVE'
    beam.rigid_body.collision_shape = 'BOX'
    beam.rigid_body.collision_margin = beam_margin
    beam.rigid_body.mass = beam_density * (beam_cross**2 * length)
    
    return beam

def create_fixed_constraint(obj1, obj2, location):
    """Create FIXED constraint between two objects"""
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=location)
    empty = bpy.context.active_object
    empty.name = f"Constraint_{obj1.name}_{obj2.name}"
    
    bpy.ops.rigidbody.constraint_add()
    empty.rigid_body_constraint.type = 'FIXED'
    empty.rigid_body_constraint.object1 = obj1
    empty.rigid_body_constraint.object2 = obj2

# Create central ridge beam (passive - static reference)
ridge_start = (ridge_x, -roof_depth/2, ridge_z)
ridge_end = (ridge_x, roof_depth/2, ridge_z)
ridge_beam = create_beam("RidgeBeam", ridge_start, ridge_end)
ridge_beam.rigid_body.type = 'PASSIVE'

# Create rafters along Y-axis
rafters = []
for i in range(num_rafters_y):
    y_pos = -roof_depth/2 + i * rafter_spacing
    
    # Right side upper rafter (ridge to break)
    ru = create_beam(f"Rafter_Upper_R_{i}", 
                     (ridge_x, y_pos, ridge_z), 
                     (break_x, y_pos, break_z))
    
    # Right side lower rafter (break to eave)
    rl = create_beam(f"Rafter_Lower_R_{i}",
                     (break_x, y_pos, break_z),
                     (eave_x, y_pos, eave_z))
    
    # Left side upper rafter (mirrored)
    lu = create_beam(f"Rafter_Upper_L_{i}",
                     (ridge_x, y_pos, ridge_z),
                     (-break_x, y_pos, break_z))
    
    # Left side lower rafter (mirrored)
    ll = create_beam(f"Rafter_Lower_L_{i}",
                     (-break_x, y_pos, break_z),
                     (-eave_x, y_pos, eave_z))
    
    rafters.append((ru, rl, lu, ll))
    
    # Create constraints for right side
    create_fixed_constraint(ridge_beam, ru, (ridge_x, y_pos, ridge_z))
    create_fixed_constraint(ru, rl, (break_x, y_pos, break_z))
    
    # Create constraints for left side
    create_fixed_constraint(ridge_beam, lu, (ridge_x, y_pos, ridge_z))
    create_fixed_constraint(lu, ll, (-break_x, y_pos, break_z))

# Create horizontal tie beams at eaves
eave_beams = []
break_beams = []
for i in range(num_rafters_y):
    y_pos = -roof_depth/2 + i * rafter_spacing
    
    # Eave tie beam (right to left)
    eb = create_beam(f"EaveBeam_{i}",
                     (-eave_x, y_pos, eave_z),
                     (eave_x, y_pos, eave_z))
    eave_beams.append(eb)
    
    # Break point tie beam
    bb = create_beam(f"BreakBeam_{i}",
                     (-break_x, y_pos, break_z),
                     (break_x, y_pos, break_z))
    break_beams.append(bb)
    
    # Connect eave beams to rafters
    for rafter_set in rafters:
        if abs(rafter_set[1].location.y - y_pos) < 0.001:  # Right lower rafter
            create_fixed_constraint(rafter_set[1], eb, (eave_x, y_pos, eave_z))
        if abs(rafter_set[3].location.y - y_pos) < 0.001:  # Left lower rafter
            create_fixed_constraint(rafter_set[3], eb, (-eave_x, y_pos, eave_z))
    
    # Connect break beams to rafters
    for rafter_set in rafters:
        if abs(rafter_set[0].location.y - y_pos) < 0.001:  # Right upper rafter
            create_fixed_constraint(rafter_set[0], bb, (break_x, y_pos, break_z))
        if abs(rafter_set[2].location.y - y_pos) < 0.001:  # Left upper rafter
            create_fixed_constraint(rafter_set[2], bb, (-break_x, y_pos, break_z))

# Create distributed load plane
bpy.ops.mesh.primitive_plane_add(size=1.0, location=(0, 0, ridge_z + 0.1))
load_plane = bpy.context.active_object
load_plane.name = "LoadPlane"
load_plane.scale = (roof_width/2, roof_depth/2, 1.0)

# Add rigid body to load plane
bpy.ops.rigidbody.object_add()
load_plane.rigid_body.type = 'ACTIVE'
load_plane.rigid_body.collision_shape = 'MESH'
load_plane.rigid_body.mass = load_mass
load_plane.rigid_body.collision_margin = 0.01

# Set gravity and simulation properties
bpy.context.scene.gravity = (0, 0, -9.81)

print("Gambrel roof structure created with distributed load simulation")
print(f"Structure includes: {len(rafters)*4} rafters, {len(eave_beams)} eave beams, {len(break_beams)} break beams")
print(f"Total load: {load_mass} kg distributed across {roof_width * roof_depth:.1f} m² area")