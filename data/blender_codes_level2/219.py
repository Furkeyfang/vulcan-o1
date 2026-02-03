import bpy
import math

# Clear existing scene
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

# Extract parameters from summary
Lx = 10.0  # roof_length_x
Ly = 12.0  # roof_width_y
beam_h = 0.5  # beam_height_z
grid_sp = 2.0  # grid_spacing
perim_sz = 0.2  # perimeter_beam_size
inter_sz = 0.15  # interior_beam_size
col_rad = 0.3  # column_radius
col_h = 3.0  # column_height
total_mass = 2500.0  # total_mass_kg
area = Lx * Ly  # roof_area
mass_per_area = total_mass / area
num_frames = 100
x_lines = [0.0, 2.0, 4.0, 6.0, 8.0, 10.0]
y_lines = [0.0, 2.0, 4.0, 6.0, 8.0, 10.0, 12.0]
roof_z = 0.5  # roof_bottom_z
col_top_z = roof_z + col_h  # column_top_z
density = 2500.0  # beam_density_kg_per_m3

# Store beam objects for constraint creation
beams = []
beam_dict = {}  # key: (type, index) for easy lookup

# Create X-direction beams (along X-axis at each Y grid line)
for i, y in enumerate(y_lines):
    # Determine if perimeter beam (Y=0 or Y=12)
    is_perimeter = (y == 0.0 or y == 12.0)
    beam_size = perim_sz if is_perimeter else inter_sz
    
    # Create beam cube
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(Lx/2, y, roof_z))
    beam = bpy.context.active_object
    beam.name = f"beam_x_{y}"
    beam.scale = (Lx, beam_size, beam_h)  # Length in X, width in Y, height in Z
    
    # Add rigid body
    bpy.ops.rigidbody.object_add()
    beam.rigid_body.type = 'ACTIVE'
    beam.rigid_body.mass = total_mass / (len(x_lines) * len(y_lines))  # Distributed mass
    
    beams.append(beam)
    beam_dict[('x', y)] = beam

# Create Y-direction beams (along Y-axis at each X grid line)
for i, x in enumerate(x_lines):
    # Determine if perimeter beam (X=0 or X=10)
    is_perimeter = (x == 0.0 or x == 10.0)
    beam_size = perim_sz if is_perimeter else inter_sz
    
    # Create beam cube
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(x, Ly/2, roof_z))
    beam = bpy.context.active_object
    beam.name = f"beam_y_{x}"
    beam.scale = (beam_size, Ly, beam_h)  # Width in X, length in Y, height in Z
    
    # Add rigid body
    bpy.ops.rigidbody.object_add()
    beam.rigid_body.type = 'ACTIVE'
    beam.rigid_body.mass = total_mass / (len(x_lines) * len(y_lines))
    
    beams.append(beam)
    beam_dict[('y', x)] = beam

# Create support columns at corners
corners = [(0.0, 0.0), (Lx, 0.0), (0.0, Ly), (Lx, Ly)]
columns = []
for i, (cx, cy) in enumerate(corners):
    # Column extends from ground (Z=0) to column top (Z=col_h)
    col_center_z = col_h / 2
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=16,
        radius=col_rad,
        depth=col_h,
        location=(cx, cy, col_center_z)
    )
    column = bpy.context.active_object
    column.name = f"column_{i}"
    
    # Add rigid body
    bpy.ops.rigidbody.object_add()
    column.rigid_body.type = 'PASSIVE'  # Fixed to ground
    
    columns.append(column)

# Create fixed constraints at beam intersections
for x in x_lines:
    for y in y_lines:
        # Get beams at this intersection
        beam_x = beam_dict.get(('x', y))
        beam_y = beam_dict.get(('y', x))
        
        if beam_x and beam_y:
            # Create constraint object
            bpy.ops.object.empty_add(type='PLAIN_AXES', location=(x, y, roof_z))
            constraint = bpy.context.active_object
            constraint.name = f"constraint_{x}_{y}"
            
            # Add rigid body constraint
            bpy.ops.rigidbody.constraint_add()
            constraint.rigid_body_constraint.type = 'FIXED'
            constraint.rigid_body_constraint.object1 = beam_x
            constraint.rigid_body_constraint.object2 = beam_y

# Create fixed constraints between columns and intersecting beams
for i, (cx, cy) in enumerate(corners):
    column = columns[i]
    
    # Find intersecting beams at this corner
    beam_x = beam_dict.get(('x', cy))
    beam_y = beam_dict.get(('y', cx))
    
    # Constraint between column and X-direction beam
    if beam_x:
        bpy.ops.object.empty_add(type='PLAIN_AXES', location=(cx, cy, roof_z))
        const1 = bpy.context.active_object
        const1.name = f"col_beamx_const_{i}"
        bpy.ops.rigidbody.constraint_add()
        const1.rigid_body_constraint.type = 'FIXED'
        const1.rigid_body_constraint.object1 = column
        const1.rigid_body_constraint.object2 = beam_x
    
    # Constraint between column and Y-direction beam
    if beam_y:
        bpy.ops.object.empty_add(type='PLAIN_AXES', location=(cx, cy, roof_z))
        const2 = bpy.context.active_object
        const2.name = f"col_beamy_const_{i}"
        bpy.ops.rigidbody.constraint_add()
        const2.rigid_body_constraint.type = 'FIXED'
        const2.rigid_body_constraint.object1 = column
        const2.rigid_body_constraint.object2 = beam_y

# Set up physics world
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 50
bpy.context.scene.frame_end = num_frames

# Adjust mass distribution to achieve exact 2500kg total
# Calculate total beam volume and adjust density
total_beam_mass = sum([b.rigid_body.mass for b in beams])
mass_scale = total_mass / total_beam_mass if total_beam_mass > 0 else 1.0

for beam in beams:
    beam.rigid_body.mass *= mass_scale

print(f"Total beam mass: {sum([b.rigid_body.mass for b in beams]):.2f} kg")
print(f"Target mass: {total_mass:.2f} kg")
print(f"Simulation frames: {num_frames}")