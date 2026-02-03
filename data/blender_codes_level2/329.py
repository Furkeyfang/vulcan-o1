import bpy
import math

# Clear existing scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Parameters from summary
truss_length = 6.0
chord_width = 0.1
chord_depth = 0.1
vertical_gap = 0.5
base_size = 1.0
load_force = 4414.5
load_position = (6.0, 0.0, 0.5)
density_max = 5000.0
density_min = 1000.0
vertical_locations = [0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0]
top_chord_center = (3.0, 0.0, 0.55)
bottom_chord_center = (3.0, 0.0, 0.05)
vertical_center_z = 0.3
member_cross_section = (0.1, 0.1)

# Utility: Create cube with rigid body and return object
def create_member(name, location, scale, density=1000.0):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = scale
    bpy.ops.rigidbody.object_add()
    obj.rigid_body.type = 'ACTIVE'
    obj.rigid_body.collision_shape = 'BOX'
    obj.rigid_body.density = density
    return obj

# Utility: Get density based on X position (gradient from max to min)
def get_density(x_pos):
    t = x_pos / truss_length  # Normalized position (0 to 1)
    return density_max - (density_max - density_min) * t

# 1. Create fixed base
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0,0,0))
base = bpy.context.active_object
base.name = "FixedBase"
base.scale = (base_size, base_size, base_size)
bpy.ops.rigidbody.object_add()
base.rigid_body.type = 'PASSIVE'

# 2. Create top chord (6m long)
top_chord = create_member(
    "TopChord",
    top_chord_center,
    (truss_length, chord_width, chord_depth),
    get_density(truss_length/2)  # Average density
)

# 3. Create bottom chord
bottom_chord = create_member(
    "BottomChord",
    bottom_chord_center,
    (truss_length, chord_width, chord_depth),
    get_density(truss_length/2)
)

# 4. Create vertical members at 1m intervals
vertical_members = []
for i, x in enumerate(vertical_locations):
    density = get_density(x)
    vert = create_member(
        f"Vertical_{i}",
        (x, 0.0, vertical_center_z),
        (member_cross_section[0], member_cross_section[1], vertical_gap),
        density
    )
    vertical_members.append(vert)

# 5. Create diagonal members (alternating pattern)
diagonal_members = []
for i in range(len(vertical_locations)-1):
    x1, x2 = vertical_locations[i], vertical_locations[i+1]
    avg_x = (x1 + x2) / 2.0
    density = get_density(avg_x)
    
    # Calculate diagonal length and rotation
    length = math.sqrt((x2-x1)**2 + vertical_gap**2)
    angle = math.atan2(vertical_gap, x2-x1) if i % 2 == 0 else -math.atan2(vertical_gap, x2-x1)
    
    # Center position depends on slope direction
    if i % 2 == 0:  # Downward diagonal (top at x1 to bottom at x2)
        center_z = (0.55 + 0.05) / 2.0
    else:  # Upward diagonal (bottom at x1 to top at x2)
        center_z = (0.05 + 0.55) / 2.0
    
    center_x = (x1 + x2) / 2.0
    center_y = 0.0
    
    # Create and rotate diagonal
    diag = create_member(
        f"Diagonal_{i}",
        (center_x, center_y, center_z),
        (length, member_cross_section[0], member_cross_section[1]),
        density
    )
    
    # Rotate around Y-axis for proper orientation
    diag.rotation_euler = (0.0, angle, 0.0)
    diagonal_members.append(diag)

# 6. Create fixed constraints between base and truss at origin
def add_fixed_constraint(obj_a, obj_b):
    bpy.ops.rigidbody.constraint_add()
    constraint = bpy.context.active_object
    constraint.name = f"Fix_{obj_a.name}_{obj_b.name}"
    constraint.empty_display_type = 'ARROWS'
    constraint.rigid_body_constraint.type = 'FIXED'
    constraint.location = (0, 0, 0)
    
    # Link objects
    constraint.rigid_body_constraint.object1 = obj_a
    constraint.rigid_body_constraint.object2 = obj_b

# Fix bottom chord at origin to base
add_fixed_constraint(base, bottom_chord)

# Fix first vertical member at origin to base
add_fixed_constraint(base, vertical_members[0])

# 7. Apply downward force at free end using force field
bpy.ops.object.empty_add(type='PLAIN_AXES', location=load_position)
force_empty = bpy.context.active_object
force_empty.name = "LoadForce"

# Add force field
bpy.ops.object.effector_add(type='FORCE', location=load_position)
force_field = bpy.context.active_object
force_field.name = "DownwardForce"
force_field.field.strength = -load_force  # Negative Z direction
force_field.field.falloff_power = 0  # Uniform force
force_field.field.distance_max = 0.1  # Only affect nearby objects

# Parent force field to empty for organization
force_field.parent = force_empty

# 8. Set up rigid body world
bpy.context.scene.rigidbody_world.enabled = True
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 10
bpy.context.scene.rigidbody_world.use_split_impulse = True

print("Cantilever truss construction complete. Run simulation to verify deflection.")