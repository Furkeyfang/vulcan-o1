import bpy
import math

# Clear existing scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Parameters from summary
v_height = 22.0
v_section = (0.5, 0.5)
tri_side = 3.0
brace_heights = [5.0, 10.0, 15.0, 20.0]
brace_dim = (3.0, 0.3, 0.3)
plat_size = (2.0, 2.0, 0.2)
plat_loc = (1.5, 0.866, 22.1)
cube_size = 0.8
cube_mass = 180.0
cube_loc = (1.5, 0.866, 22.5)
base_verts = [(0.0, 0.0, 0.0), (3.0, 0.0, 0.0), (1.5, 2.598, 0.0)]

# Create ground plane
bpy.ops.mesh.primitive_plane_add(size=20.0, location=(0,0,0))
ground = bpy.context.active_object
bpy.ops.rigidbody.object_add()
ground.rigid_body.type = 'PASSIVE'
ground.name = "Ground"

# Function to create beam with physics
def create_beam(name, location, dimensions, rotation=(0,0,0)):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location)
    beam = bpy.context.active_object
    beam.name = name
    beam.scale = (dimensions[0], dimensions[1], dimensions[2])
    bpy.ops.rigidbody.object_add()
    beam.rigid_body.type = 'PASSIVE'
    beam.rigid_body.collision_shape = 'BOX'
    if rotation != (0,0,0):
        beam.rotation_euler = rotation
    return beam

# Create vertical beams
vertical_beams = []
for i, (x,y,z) in enumerate(base_verts):
    v_name = f"Vertical_Beam_{chr(65+i)}"
    v_center_z = v_height / 2.0
    v_dim = (v_section[0], v_section[1], v_height)
    v_beam = create_beam(v_name, (x, y, v_center_z), v_dim)
    vertical_beams.append(v_beam)

# Create horizontal braces
brace_pairs = [(0,1), (1,2), (2,0)]  # Beam indices: AB, BC, CA
rotation_angles = [0, math.radians(60), math.radians(120)]  # For triangle sides

for level in brace_heights:
    for (i,j), angle in zip(brace_pairs, rotation_angles):
        # Midpoint between two beams at this height
        x1, y1, _ = base_verts[i]
        x2, y2, _ = base_verts[j]
        mid_x = (x1 + x2) / 2.0
        mid_y = (y1 + y2) / 2.0
        
        brace_name = f"Brace_{chr(65+i)}{chr(65+j)}_Z{level}"
        brace = create_beam(brace_name, (mid_x, mid_y, level), brace_dim, (0,0,angle))
        
        # Adjust length scaling to match exact distance
        actual_dist = math.sqrt((x2-x1)**2 + (y2-y1)**2)
        scale_factor = actual_dist / brace_dim[0]
        brace.scale.x *= scale_factor

# Create triangular platform (simplified as cube for rigid body)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=plat_loc)
platform = bpy.context.active_object
platform.name = "Top_Platform"
platform.scale = (plat_size[0], plat_size[1], plat_size[2])
bpy.ops.rigidbody.object_add()
platform.rigid_body.type = 'PASSIVE'
platform.rigid_body.collision_shape = 'BOX'

# Create load cube
bpy.ops.mesh.primitive_cube_add(size=1.0, location=cube_loc)
cube = bpy.context.active_object
cube.name = "Load_Cube"
cube.scale = (cube_size, cube_size, cube_size)
bpy.ops.rigidbody.object_add()
cube.rigid_body.type = 'ACTIVE'
cube.rigid_body.mass = cube_mass
cube.rigid_body.collision_shape = 'BOX'

# Create fixed constraints between all connected parts
constraint_objects = vertical_beams + [platform] + [ground]

# Function to add fixed constraint
def add_fixed_constraint(obj_a, obj_b):
    bpy.context.view_layer.objects.active = obj_a
    bpy.ops.rigidbody.constraint_add()
    constraint = obj_a.rigid_body.constraints[-1]
    constraint.type = 'FIXED'
    constraint.object2 = obj_b

# Constraint vertical beams to ground
for beam in vertical_beams:
    add_fixed_constraint(beam, ground)

# Constraint platform to all three vertical beams
for beam in vertical_beams:
    add_fixed_constraint(platform, beam)

# Constraint horizontal braces to vertical beams
for brace in bpy.data.objects:
    if brace.name.startswith("Brace_"):
        # Determine which vertical beams this connects to from name
        if "AB" in brace.name:
            beam_a, beam_b = vertical_beams[0], vertical_beams[1]
        elif "BC" in brace.name:
            beam_a, beam_b = vertical_beams[1], vertical_beams[2]
        elif "CA" in brace.name:
            beam_a, beam_b = vertical_beams[2], vertical_beams[0]
        
        add_fixed_constraint(brace, beam_a)
        add_fixed_constraint(brace, beam_b)

# Setup rigid body world
bpy.context.scene.rigidbody_world.enabled = True
bpy.context.scene.rigidbody_world.time_scale = 1.0
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 50
bpy.context.scene.frame_end = 250  # 4+ seconds simulation

print("Triangular radar mast construction complete. Run simulation to verify stability.")