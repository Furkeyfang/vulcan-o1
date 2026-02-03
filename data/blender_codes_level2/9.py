import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Parameters from summary
span_x = 9.0
width_y = 2.0
truss_height_z = 1.5
member_cross = 0.2
num_bays = 5
bay_length = span_x / num_bays
diagonal_length = math.sqrt(bay_length**2 + truss_height_z**2)
pillar_size = (0.5, 0.5, 1.0)
pillar_left_loc = (-span_x/2, 0.0, pillar_size[2]/2)
pillar_right_loc = (span_x/2, 0.0, pillar_size[2]/2)
truss_y_pos = width_y / 2
truss_y_neg = -width_y / 2
bottom_z = 0.0
top_z = truss_height_z
load_mass_kg = 450.0
gravity = 9.81
total_force_n = load_mass_kg * gravity
force_per_top_member = total_force_n / (2 * num_bays)  # 2 trusses, num_bays top members each

def create_member(name, length, loc, rot_euler):
    """Create a cube member scaled to length, oriented by Euler angles (radians)."""
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=loc)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = (member_cross, member_cross, length)
    obj.rotation_euler = rot_euler
    bpy.ops.rigidbody.object_add()
    obj.rigid_body.type = 'ACTIVE'
    obj.rigid_body.collision_shape = 'BOX'
    return obj

def create_fixed_constraint(obj_a, obj_b):
    """Create a fixed rigid body constraint between two objects."""
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=obj_a.location)
    empty = bpy.context.active_object
    empty.name = f"Constraint_{obj_a.name}_{obj_b.name}"
    bpy.ops.rigidbody.constraint_add()
    empty.rigid_body_constraint.type = 'FIXED'
    empty.rigid_body_constraint.object1 = obj_a
    empty.rigid_body_constraint.object2 = obj_b

# Create support pillars (passive rigid bodies)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=pillar_left_loc)
pillar_left = bpy.context.active_object
pillar_left.name = "Pillar_Left"
pillar_left.scale = pillar_size
bpy.ops.rigidbody.object_add()
pillar_left.rigid_body.type = 'PASSIVE'

bpy.ops.mesh.primitive_cube_add(size=1.0, location=pillar_right_loc)
pillar_right = bpy.context.active_object
pillar_right.name = "Pillar_Right"
pillar_right.scale = pillar_size
bpy.ops.rigidbody.object_add()
pillar_right.rigid_body.type = 'PASSIVE'

# Create truss members for both sides (Y positive and negative)
for side_name, y_pos in [("Pos", truss_y_pos), ("Neg", truss_y_neg)]:
    # Bottom chord (horizontal members)
    for i in range(num_bays):
        x_center = -span_x/2 + (i + 0.5) * bay_length
        loc = (x_center, y_pos, bottom_z)
        bot_member = create_member(f"Bottom_{side_name}_{i}", bay_length, loc, (0, 0, 0))
        # Fix first bottom member to left pillar, last to right pillar
        if i == 0:
            create_fixed_constraint(bot_member, pillar_left)
        elif i == num_bays - 1:
            create_fixed_constraint(bot_member, pillar_right)

    # Top chord (horizontal members)
    for i in range(num_bays):
        x_center = -span_x/2 + (i + 0.5) * bay_length
        loc = (x_center, y_pos, top_z)
        top_member = create_member(f"Top_{side_name}_{i}", bay_length, loc, (0, 0, 0))
        # Apply uniform load as downward force on each top member
        top_member.rigid_body.use_gravity = False
        top_member.rigid_body.kinematic = True  # We'll apply force manually, but for static scene we can skip dynamics
        # In a dynamic simulation, we would add force here.

    # Diagonal members (alternating pattern)
    for i in range(num_bays):
        # Diagonal from bottom-left to top-right (sloping upward right)
        x_start = -span_x/2 + i * bay_length
        x_end = x_start + bay_length
        x_center = (x_start + x_end) / 2
        z_center = (bottom_z + top_z) / 2
        loc = (x_center, y_pos, z_center)
        angle = math.atan2(truss_height_z, bay_length)
        diag = create_member(f"Diag_{side_name}_{i}_UR", diagonal_length, loc, (0, angle, 0))
        # Fix diagonal ends to bottom and top chords (joints will be created later)

    # Create joints via fixed constraints at intersections
    # We'll collect objects and create constraints at shared coordinates
    objects_by_loc = {}
    for obj in bpy.context.scene.objects:
        if obj.name.startswith(("Bottom_", "Top_", "Diag_")):
            loc_key = (round(obj.location.x, 3), round(obj.location.y, 3), round(obj.location.z, 3))
            objects_by_loc.setdefault(loc_key, []).append(obj)
    
    # Create fixed constraints between all objects at each joint location
    for loc, objs in objects_by_loc.items():
        if len(objs) > 1:
            for i in range(len(objs)):
                for j in range(i+1, len(objs)):
                    create_fixed_constraint(objs[i], objs[j])

# Note: For a full dynamic simulation, you would need to set forces, gravity, and run the simulation.
# This code sets up the static structure with fixed constraints ready for simulation.