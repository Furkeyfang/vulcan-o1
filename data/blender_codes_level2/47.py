import bpy
import math

# Clear scene
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

# Extract parameters
span = 14.0
c_w = 0.2
c_d = 0.2
top_z = 3.0
bot_z = 2.8
mod_base = 2.8
n_tri = 5
n_top_j = 6
n_bot_j = 6
total_j = 12
mass = 1600.0
g = 9.81
F_total = mass * g
F_per_seg = F_total / n_tri

# Calculate joint positions
top_joints = []
bot_joints = []
for i in range(n_top_j):
    x = -span/2 + i * mod_base
    top_joints.append((x, 0.0, top_z))
    bot_joints.append((x, 0.0, bot_z))

# Create joint empties (passive rigid bodies)
joint_empties = []
for i, pos in enumerate(top_joints + bot_joints):
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=pos)
    emp = bpy.context.active_object
    emp.name = f"Joint_{i:02d}"
    bpy.ops.rigidbody.object_add()
    emp.rigid_body.type = 'PASSIVE'
    joint_empties.append(emp)

# Function to create a structural member between two points
def create_member(pos1, pos2, name):
    # Calculate midpoint, length, and direction
    mid = ((pos1[0]+pos2[0])/2, (pos1[1]+pos2[1])/2, (pos1[2]+pos2[2])/2)
    length = math.dist(pos1, pos2)
    # Create cube
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=mid)
    obj = bpy.context.active_object
    obj.name = name
    # Scale: cross-section c_w x c_d, length 'length'
    obj.scale = (c_w/2, c_d/2, length/2)  # Default cube side=2, so /2
    # Rotate to align with direction vector
    direction = (pos2[0]-pos1[0], pos2[1]-pos1[1], pos2[2]-pos1[2])
    obj.rotation_mode = 'QUATERNION'
    obj.rotation_quaternion = (1,0,0,0)  # Default
    if length > 0.001:
        # Find rotation from +Z to direction
        axis = (0,0,1)
        target = direction
        rot_quat = axis.rotation_difference(target)
        obj.rotation_quaternion = rot_quat
    # Add active rigid body
    bpy.ops.rigidbody.object_add()
    obj.rigid_body.type = 'ACTIVE'
    obj.rigid_body.collision_shape = 'BOX'
    return obj

# Create top chord (horizontal members)
top_members = []
for i in range(n_tri):
    top_members.append(create_member(top_joints[i], top_joints[i+1], f"Top_{i}"))

# Create bottom chord (horizontal members)
bot_members = []
for i in range(n_tri):
    bot_members.append(create_member(bot_joints[i], bot_joints[i+1], f"Bot_{i}"))

# Create diagonal web members (alternating pattern)
web_members = []
for i in range(n_tri):
    if i % 2 == 0:  # Even: bottom->top diagonal
        web_members.append(create_member(bot_joints[i], top_joints[i+1], f"Web_{i}_up"))
    else:           # Odd: top->bottom diagonal
        web_members.append(create_member(top_joints[i], bot_joints[i+1], f"Web_{i}_down"))

# Add Fixed constraints between members and joints
def add_fixed_constraint(obj_a, obj_b):
    bpy.ops.object.empty_add(type='PLAIN_AXES')
    const_empty = bpy.context.active_object
    const_empty.name = f"Fix_{obj_a.name}_{obj_b.name}"
    const_empty.location = ((obj_a.location[0]+obj_b.location[0])/2,
                            (obj_a.location[1]+obj_b.location[1])/2,
                            (obj_a.location[2]+obj_b.location[2])/2)
    bpy.ops.rigidbody.constraint_add()
    const = const_empty.rigid_body_constraint
    const.type = 'FIXED'
    const.object1 = obj_a
    const.object2 = obj_b

# Connect each member to its two joints
# Top chord connections
for i, mem in enumerate(top_members):
    add_fixed_constraint(mem, joint_empties[i])      # Left joint
    add_fixed_constraint(mem, joint_empties[i+1])    # Right joint

# Bottom chord connections
offset = n_top_j  # Index offset for bottom joints
for i, mem in enumerate(bot_members):
    add_fixed_constraint(mem, joint_empties[offset + i])
    add_fixed_constraint(mem, joint_empties[offset + i + 1])

# Web member connections (alternating)
for i, mem in enumerate(web_members):
    if i % 2 == 0:  # Bottom->top
        add_fixed_constraint(mem, joint_empties[offset + i])   # Bottom joint
        add_fixed_constraint(mem, joint_empties[i+1])          # Top joint
    else:           # Top->bottom
        add_fixed_constraint(mem, joint_empties[i])            # Top joint
        add_fixed_constraint(mem, joint_empties[offset + i+1]) # Bottom joint

# Apply downward force to top chord members
for mem in top_members:
    mem.rigid_body.use_gravity = True
    # Add constant force in negative Z direction
    bpy.ops.object.forcefield_add(type='FORCE')
    force = bpy.context.active_object
    force.name = f"Force_{mem.name}"
    force.location = mem.location
    force.field.strength = -F_per_seg
    force.field.falloff_power = 0
    # Link force to top chord member
    bpy.ops.object.select_all(action='DESELECT')
    mem.select_set(True)
    force.select_set(True)
    bpy.context.view_layer.objects.active = force
    bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)

# Configure rigid body world
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 50
bpy.context.scene.frame_end = 250  # Simulation duration