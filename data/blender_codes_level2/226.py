import bpy
import math
from mathutils import Vector, Matrix

# Clear scene
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

# Parameters from summary
span = 16.0
peak_height = 4.0
eave_height = 2.0
bottom_height = 0.0
truss_spacing = 4.0
cross_brace_spacing = 2.0

top_chord_section = (0.2, 0.2)
bottom_chord_section = (0.2, 0.2)
cross_brace_section = (0.2, 0.2)
cross_brace_length = 4.0

left_eave = Vector((-span/2, 0, eave_height))
right_eave = Vector((span/2, 0, eave_height))
peak = Vector((0.0, 0, peak_height))
left_bottom = Vector((-span/2, 0, bottom_height))
right_bottom = Vector((span/2, 0, bottom_height))
crossing = Vector((0.0, 0, bottom_height + (peak_height - bottom_height) * 0.25))

total_load_N = 16000.0
gravity = 9.8

frames = 100
substeps = 10
solver_iterations = 50

# Helper function to create a beam between two points
def create_beam(end1, end2, cross_section, name):
    # Calculate length and direction
    vec = end2 - end1
    length = vec.length
    center = (end1 + end2) / 2
    
    # Create cube
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=center)
    beam = bpy.context.active_object
    beam.name = name
    
    # Scale: default cube is 2x2x2, so to get cross_section (x,y) and length:
    # We want local X and Y scaled to cross_section/2? Actually, default cube has width 2 in all axes.
    # To get a beam of cross_section (0.2,0.2) and length L, we scale by (0.1, 0.1, L/2).
    sx = cross_section[0] / 2.0
    sy = cross_section[1] / 2.0
    sz = length / 2.0
    beam.scale = (sx, sy, sz)
    
    # Rotate to align local Z with vec
    # Default cube's local Z is (0,0,1). We want to rotate that to vec.normalized().
    z_axis = Vector((0, 0, 1))
    target_axis = vec.normalized()
    if z_axis.dot(target_axis) < 0.9999:
        # Calculate rotation
        rot_quat = z_axis.rotation_difference(target_axis)
        beam.rotation_euler = rot_quat.to_euler()
    else:
        beam.rotation_euler = (0, 0, 0)
    
    # Update mesh
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    
    return beam

# Helper to create a joint empty at location
def create_joint(location, name):
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=location)
    empty = bpy.context.active_object
    empty.name = name
    # Add rigid body, set to passive
    bpy.ops.rigidbody.object_add()
    empty.rigid_body.type = 'PASSIVE'
    return empty

# Set up rigid body world
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = solver_iterations
bpy.context.scene.rigidbody_world.use_split_impulse = True
bpy.context.scene.rigidbody_world.substeps_per_frame = substeps
bpy.context.scene.rigidbody_world.gravity = (0, 0, -gravity)

# Create trusses
truss_y_positions = [-truss_spacing/2, truss_spacing/2]
joint_empties = {}  # key: (x, y, z) tuple, value: empty object
beams = []

for i, y in enumerate(truss_y_positions):
    truss_prefix = f"Truss_{i+1}"
    # Define joints for this truss (offset in Y)
    le = left_eave + Vector((0, y, 0))
    re = right_eave + Vector((0, y, 0))
    pk = peak + Vector((0, y, 0))
    lb = left_bottom + Vector((0, y, 0))
    rb = right_bottom + Vector((0, y, 0))
    cr = crossing + Vector((0, y, 0))
    
    # Create joint empties (if not already created for the other truss at same X,Z? but Y differs)
    # We'll create unique empties for each truss joint.
    joints = [
        (le, f"{truss_prefix}_Joint_LeftEave"),
        (re, f"{truss_prefix}_Joint_RightEave"),
        (pk, f"{truss_prefix}_Joint_Peak"),
        (lb, f"{truss_prefix}_Joint_LeftBottom"),
        (rb, f"{truss_prefix}_Joint_RightBottom"),
        (cr, f"{truss_prefix}_Joint_Crossing"),
    ]
    for loc, name in joints:
        empty = create_joint(loc, name)
        joint_empties[(loc.x, loc.y, loc.z)] = empty
    
    # Create beams and link to joints
    # Top chords
    beam1 = create_beam(le, pk, top_chord_section, f"{truss_prefix}_TopChord_Left")
    beam2 = create_beam(pk, re, top_chord_section, f"{truss_prefix}_TopChord_Right")
    # Bottom chords (left bottom to crossing, crossing to right bottom)
    beam3 = create_beam(lb, cr, bottom_chord_section, f"{truss_prefix}_BottomChord_Left")
    beam4 = create_beam(cr, rb, bottom_chord_section, f"{truss_prefix}_BottomChord_Right")
    
    # Add rigid body to beams (active by default)
    for beam in [beam1, beam2, beam3, beam4]:
        bpy.ops.rigidbody.object_add()
        beam.rigid_body.collision_shape = 'BOX'
        beams.append(beam)
        # Store beam for later constraint creation
    
    # Create fixed constraints between beam and its two joint empties
    beam_joint_pairs = [
        (beam1, le, pk),
        (beam2, pk, re),
        (beam3, lb, cr),
        (beam4, cr, rb),
    ]
    for beam, j1, j2 in beam_joint_pairs:
        for j in [j1, j2]:
            key = (j.x, j.y, j.z)
            if key in joint_empties:
                # Create constraint
                bpy.ops.rigidbody.constraint_add(type='FIXED')
                constraint = bpy.context.active_object
                constraint.name = f"{beam.name}_to_{joint_empties[key].name}_Constraint"
                constraint.rigid_body_constraint.object1 = beam
                constraint.rigid_body_constraint.object2 = joint_empties[key]
                constraint.rigid_body_constraint.use_override_solver_iterations = True
                constraint.rigid_body_constraint.solver_iterations = 50

# Create cross-bracing beams at intervals along X
# Generate X positions from -span/2 to span/2 with step cross_brace_spacing
x_positions = [x for x in range(int(-span/2), int(span/2)+1, int(cross_brace_spacing))]
# For each X, compute Z on roof surface (top chord line)
for x in x_positions:
    # Linear interpolation between eave and peak
    if x <= 0:
        # left side: from left eave to peak
        t = (x - (-span/2)) / (span/2)  # 0 at left eave, 1 at peak
        z = eave_height + (peak_height - eave_height) * t
    else:
        # right side: from peak to right eave
        t = (x - 0) / (span/2)  # 0 at peak, 1 at right eave
        z = peak_height - (peak_height - eave_height) * t
    # Create beam from (x, -truss_spacing/2, z) to (x, truss_spacing/2, z)
    end1 = Vector((x, -truss_spacing/2, z))
    end2 = Vector((x, truss_spacing/2, z))
    beam = create_beam(end1, end2, cross_brace_section, f"CrossBrace_X{x}")
    bpy.ops.rigidbody.object_add()
    beam.rigid_body.collision_shape = 'BOX'
    beams.append(beam)
    # Connect to joint empties at these points? We'll create empties if they don't exist.
    for end in [end1, end2]:
        key = (end.x, end.y, end.z)
        if key not in joint_empties:
            empty = create_joint(end, f"Joint_CrossBrace_{key}")
            joint_empties[key] = empty
        # Constraint
        bpy.ops.rigidbody.constraint_add(type='FIXED')
        constraint = bpy.context.active_object
        constraint.name = f"{beam.name}_to_{joint_empties[key].name}_Constraint"
        constraint.rigid_body_constraint.object1 = beam
        constraint.rigid_body_constraint.object2 = joint_empties[key]
        constraint.rigid_body_constraint.use_override_solver_iterations = True
        constraint.rigid_body_constraint.solver_iterations = 50

# Apply load to top chord beams
# Identify top chord beams by name
top_chord_beams = [obj for obj in beams if "TopChord" in obj.name]
force_per_beam = total_load_N / len(top_chord_beams)
for beam in top_chord_beams:
    # Add a constant force in negative Z direction
    # We can use rigid body force field or directly apply force each frame? 
    # For simplicity, we add a force to the rigid body (this is a one-time impulse, not constant).
    # Instead, we use a force field (wind) limited to these beams.
    # Create a wind force field directed downward.
    pass

# Create a force field for downward load
bpy.ops.object.effector_add(type='FORCE', location=(0, 0, peak_height))
force_field = bpy.context.active_object
force_field.name = "RoofLoad_ForceField"
force_field.field.type = 'FORCE'
force_field.field.strength = total_load_N  # total force
force_field.field.flow = 0  # no noise
force_field.field.use_max_distance = True
force_field.field.distance_max = 2.0  # affect only near roof
force_field.field.falloff_power = 0  # constant
# Limit to top chord beams: we can use a vertex group or collision, but simpler: set force field to affect only selected objects.
# We'll assign the force field to a collection and set collection in rigid body world.
# However, in headless we can't easily set up such dependencies. Alternative: apply force as a constant force on each beam's rigid body via Python handler.
# We'll use a frame change handler to apply force each frame.

def apply_constant_force(scene):
    for beam in top_chord_beams:
        if beam.rigid_body:
            # Apply force in world coordinates (downward)
            beam.rigid_body.apply_force((0, 0, -force_per_beam))

# Register handler
bpy.app.handlers.frame_change_pre.append(apply_constant_force)

# Set simulation length
bpy.context.scene.frame_end = frames

# Run simulation (in headless, we can bake or just set frame)
# We'll advance frame by frame and record peak deflection
peak_empty = joint_empties.get((peak.x, peak.y, peak.z))
if peak_empty:
    print(f"Initial peak position: {peak_empty.location.z}")
    # Store initial Z
    initial_z = peak_empty.location.z

# To run simulation, we would step through frames, but in headless we can use bpy.ops.ptcache.bake_all()
# However, that requires a cache. Instead, we set up the scene and rely on external script to advance frames.
# For completeness, we'll add a script to bake rigid body simulation.
bpy.context.scene.rigidbody_world.point_cache.frame_end = frames
# Uncomment the following line to bake simulation (may take time)
# bpy.ops.ptcache.bake_all(bake=True)

print("Structure created. Simulation set up.")