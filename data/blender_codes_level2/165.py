import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Extract parameters from summary
beam_len = 6.5
beam_w = 0.3
beam_d = 0.3
left_base = (-2.0, 0.0, 0.0)
right_base = (2.0, 0.0, 0.0)
peak = (0.0, 0.0, 6.0)

cb_len = 4.0
cb_w = 0.3
cb_d = 0.3
cb_center = (0.0, 0.0, 3.0)
conn_l = (-1.0, 0.0, 3.0)
conn_r = (1.0, 0.0, 3.0)

load_mass = 2500.0
load_sz = 0.2
load_pos = (0.0, 0.0, 6.0)

beam_angle = math.atan2(6.0, 2.0)  # 71.565 degrees

# Create Ground Plane
bpy.ops.mesh.primitive_plane_add(size=20.0, location=(0,0,-0.1))
ground = bpy.context.active_object
ground.name = "Ground"
bpy.ops.rigidbody.object_add()
ground.rigid_body.type = 'PASSIVE'

# Function to create a beam with proper orientation
def create_beam(name, base_loc, target_loc, length, width, depth):
    # Calculate midpoint and orientation
    mid = ((base_loc[0] + target_loc[0])/2,
           (base_loc[1] + target_loc[1])/2,
           (base_loc[2] + target_loc[2])/2)
    
    # Create cube and scale to beam dimensions
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=mid)
    beam = bpy.context.active_object
    beam.name = name
    
    # Scale: default cube is 2x2x2, adjust for actual dimensions
    beam.scale = (width/2.0, depth/2.0, length/2.0)
    
    # Calculate rotation to align with base→target vector
    vec = (target_loc[0]-base_loc[0], 
           target_loc[1]-base_loc[1], 
           target_loc[2]-base_loc[2])
    length_vec = math.sqrt(vec[0]**2 + vec[1]**2 + vec[2]**2)
    
    # Rotate around Y-axis for XZ plane alignment
    if abs(vec[0]) > 0.001:
        angle = math.atan2(vec[2], vec[0]) + math.pi/2.0
        beam.rotation_euler = (0.0, angle, 0.0)
    else:
        # Vertical beam special case
        beam.rotation_euler = (0.0, 0.0, 0.0)
    
    # Add rigid body
    bpy.ops.rigidbody.object_add()
    beam.rigid_body.type = 'ACTIVE'
    beam.rigid_body.collision_shape = 'BOX'
    beam.rigid_body.mass = 100.0  # Estimated mass ~100kg
    
    return beam

# Create left inclined beam (base to peak)
left_beam = create_beam("LeftBeam", left_base, peak, beam_len, beam_w, beam_d)

# Create right inclined beam (base to peak)
right_beam = create_beam("RightBeam", right_base, peak, beam_len, beam_w, beam_d)

# Create horizontal crossbeam
bpy.ops.mesh.primitive_cube_add(size=1.0, location=cb_center)
crossbeam = bpy.context.active_object
crossbeam.name = "Crossbeam"
crossbeam.scale = (cb_len/2.0, cb_d/2.0, cb_w/2.0)
crossbeam.rotation_euler = (0.0, 0.0, math.pi/2.0)  # Align along X-axis
bpy.ops.rigidbody.object_add()
crossbeam.rigid_body.type = 'ACTIVE'
crossbeam.rigid_body.collision_shape = 'BOX'
crossbeam.rigid_body.mass = 50.0  # Estimated mass ~50kg

# Create load cube
bpy.ops.mesh.primitive_cube_add(size=1.0, location=load_pos)
load = bpy.context.active_object
load.name = "Load"
load.scale = (load_sz/2.0, load_sz/2.0, load_sz/2.0)
bpy.ops.rigidbody.object_add()
load.rigid_body.type = 'ACTIVE'
load.rigid_body.collision_shape = 'BOX'
load.rigid_body.mass = load_mass  # 2500 kg

# Function to create fixed constraint between two objects at location
def create_fixed_constraint(obj1, obj2, constraint_loc, name):
    # Create empty at constraint location
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=constraint_loc)
    empty = bpy.context.active_object
    empty.name = name
    
    # Add rigid body constraint
    bpy.ops.rigidbody.constraint_add()
    constraint = empty.rigid_body_constraint
    constraint.type = 'FIXED'
    constraint.object1 = obj1
    constraint.object2 = obj2
    constraint.disable_collisions = True

# Create constraints
# 1. Left beam base to ground
create_fixed_constraint(left_beam, ground, left_base, "Constraint_LeftBase")

# 2. Right beam base to ground
create_fixed_constraint(right_beam, ground, right_base, "Constraint_RightBase")

# 3. Peak connection between beams
create_fixed_constraint(left_beam, right_beam, peak, "Constraint_Peak")

# 4. Crossbeam to left beam
create_fixed_constraint(crossbeam, left_beam, conn_l, "Constraint_CrossLeft")

# 5. Crossbeam to right beam
create_fixed_constraint(crossbeam, right_beam, conn_r, "Constraint_CrossRight")

# 6. Load to left beam at peak (load sharing through both beams)
create_fixed_constraint(load, left_beam, peak, "Constraint_LoadLeft")

# 7. Load to right beam at peak
create_fixed_constraint(load, right_beam, peak, "Constraint_LoadRight")

# Set physics scene properties
scene = bpy.context.scene
scene.rigidbody_world.steps_per_second = 60
scene.rigidbody_world.solver_iterations = 50
scene.rigidbody_world.use_split_impulse = True

print("A-frame structure created successfully.")