import bpy
import math

# Clear existing scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# ========== PARAMETERS ==========
# Tower dimensions
strut_length = 5.0
strut_width = 0.2
strut_cross_section = (strut_width, strut_width, strut_length)
tower_footprint = 2.0
num_sections = 5
total_height = 25.0

# Cross-brace dimensions
brace_long = 2.0
brace_short = 0.1
brace_cross_section = (brace_short, brace_long, brace_short)

# Platform dimensions
platform_size = (2.0, 2.0, 0.1)
platform_height = total_height + platform_size[2]/2

# Load parameters
load_mass_kg = 280.0
gravity = 9.81
force_newtons = load_mass_kg * gravity

# Position arrays
strut_positions = [(-1,-1), (-1,1), (1,-1), (1,1)]
brace_x_positions = [(0, -1), (0, 1)]  # X-direction braces at Y=±1
brace_y_positions = [(-1, 0), (1, 0)]  # Y-direction braces at X=±1

# Simulation settings
simulation_frames = 100
frame_rate = 24
time_step = 1/frame_rate

# ========== FUNCTION DEFINITIONS ==========
def create_cube(name, location, scale, rotation=(0,0,0)):
    """Create a cube with given parameters"""
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = scale
    obj.rotation_euler = rotation
    return obj

def add_rigidbody(obj, type='ACTIVE', mass=1.0):
    """Add rigid body physics to object"""
    bpy.context.view_layer.objects.active = obj
    bpy.ops.rigidbody.object_add()
    obj.rigid_body.type = type
    obj.rigid_body.mass = mass
    obj.rigid_body.collision_shape = 'BOX'
    return obj

def create_fixed_constraint(obj1, obj2):
    """Create a fixed constraint between two objects"""
    # Create empty for constraint
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=obj1.location)
    empty = bpy.context.active_object
    empty.name = f"Constraint_{obj1.name}_{obj2.name}"
    
    # Add rigid body constraint
    bpy.ops.rigidbody.constraint_add()
    empty.rigid_body_constraint.type = 'FIXED'
    empty.rigid_body_constraint.object1 = obj1
    empty.rigid_body_constraint.object2 = obj2
    
    return empty

# ========== SCENE SETUP ==========
# Set scene properties for physics
scene = bpy.context.scene
scene.frame_end = simulation_frames
scene.rigidbody_world.time_scale = 1.0
scene.rigidbody_world.steps_per_second = frame_rate
scene.rigidbody_world.solver_iterations = 50

# ========== CREATE BASE PLATE ==========
# Create a passive base at ground level
base = create_cube("Base", (0,0,0), (tower_footprint*1.5, tower_footprint*1.5, 0.5))
add_rigidbody(base, type='PASSIVE', mass=0)

# ========== BUILD TOWER SECTIONS ==========
tower_objects = []  # Store all tower objects for constraints
previous_struts = []  # Store struts from previous section

for section in range(num_sections):
    base_z = section * strut_length
    section_name = f"Section_{section}"
    
    current_struts = []
    
    # Create 4 vertical struts for this section
    for i, (x_offset, y_offset) in enumerate(strut_positions):
        strut_name = f"{section_name}_Strut_{i}"
        strut_z = base_z + strut_length/2
        
        strut = create_cube(
            name=strut_name,
            location=(x_offset, y_offset, strut_z),
            scale=strut_cross_section
        )
        add_rigidbody(strut, mass=50.0)  # Mass for steel (~7850 kg/m³ * 0.04m³ = ~314kg)
        tower_objects.append(strut)
        current_struts.append(strut)
        
        # Connect to previous section's strut (if not first section)
        if section > 0:
            prev_strut = previous_struts[i]
            create_fixed_constraint(prev_strut, strut)
    
    # Create cross-braces for this section (top and bottom)
    for level in [0, 1]:  # 0 = bottom, 1 = top
        level_z = base_z + (level * strut_length)
        
        # X-direction braces (span Y-axis)
        for i, (x_pos, y_pos) in enumerate(brace_x_positions):
            brace_name = f"{section_name}_BraceX_{level}_{i}"
            rotation = (0, 0, 0)  # Aligned with Y-axis
            
            brace = create_cube(
                name=brace_name,
                location=(x_pos, y_pos, level_z),
                scale=brace_cross_section,
                rotation=rotation
            )
            add_rigidbody(brace, mass=5.0)
            tower_objects.append(brace)
            
            # Connect to adjacent struts
            left_strut = current_struts[0 if y_pos < 0 else 1]
            right_strut = current_struts[2 if y_pos < 0 else 3]
            create_fixed_constraint(brace, left_strut)
            create_fixed_constraint(brace, right_strut)
        
        # Y-direction braces (span X-axis)
        for i, (x_pos, y_pos) in enumerate(brace_y_positions):
            brace_name = f"{section_name}_BraceY_{level}_{i}"
            rotation = (0, 0, math.pi/2)  # Rotated 90° to align with X-axis
            
            brace = create_cube(
                name=brace_name,
                location=(x_pos, y_pos, level_z),
                scale=brace_cross_section,
                rotation=rotation
            )
            add_rigidbody(brace, mass=5.0)
            tower_objects.append(brace)
            
            # Connect to adjacent struts
            front_strut = current_struts[0 if x_pos < 0 else 2]
            back_strut = current_struts[1 if x_pos < 0 else 3]
            create_fixed_constraint(brace, front_strut)
            create_fixed_constraint(brace, back_strut)
    
    previous_struts = current_struts
    
    # Connect bottom of first section to base
    if section == 0:
        for strut in current_struts:
            create_fixed_constraint(base, strut)

# ========== CREATE LOAD PLATFORM ==========
platform = create_cube(
    name="Load_Platform",
    location=(0, 0, platform_height),
    scale=platform_size
)
add_rigidbody(platform, mass=50.0)  # Platform mass

# Connect platform to top struts
for strut in previous_struts:
    create_fixed_constraint(platform, strut)

# ========== APPLY LOAD FORCE ==========
# Create force field for downward load
bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, platform_height))
force_field = bpy.context.active_object
force_field.name = "Load_Force_Field"

bpy.ops.object.forcefield_add()
force_field.field.type = 'FORCE'
force_field.field.strength = -force_newtons  # Negative for downward force
force_field.field.use_max_distance = True
force_field.field.distance_max = 0.5  # Only affect platform
force_field.field.falloff_power = 0

# Parent force field to platform
force_field.parent = platform

# ========== FINAL SCENE SETUP ==========
# Set gravity
scene.rigidbody_world.gravity = (0, 0, -gravity)

print(f"Tower construction complete. Height: {total_height}m")
print(f"Load: {load_mass_kg}kg ({force_newtons:.1f}N)")
print(f"Simulation frames: {simulation_frames}")