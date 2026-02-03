import bpy
import math

# Clear existing
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

# Extract variables from summary
density = 7850
col_h = 6.0
col_r = 0.5
col_loc = (0.0, 0.0, 3.0)
deck_l = 4.5
deck_w = 3.0
deck_t = 0.3
deck_loc = (2.25, 0.0, 6.15)
c_rad = 0.8
c_h = 1.0
lever = 1.5
c_loc = (-1.5, 0.0, 6.5)
hinge_piv = (-1.5, 0.0, 6.0)
load_f = 500 * 9.81
load_pt = (2.25, 0.0, 6.15)
init_torque = 200000
target_rot = 1.5
sim_frames = 100
subs = 10
solver_iter = 50

# Enable rigidbody world
if bpy.context.scene.rigidbody_world is None:
    bpy.ops.rigidbody.world_add()
bpy.context.scene.rigidbody_world.enabled = True
bpy.context.scene.rigidbody_world.substeps_per_frame = subs
bpy.context.scene.rigidbody_world.solver_iterations = solver_iter
bpy.context.scene.frame_end = sim_frames

# --- Create Column ---
bpy.ops.mesh.primitive_cylinder_add(
    vertices=32,
    radius=col_r,
    depth=col_h,
    location=col_loc
)
column = bpy.context.active_object
column.name = "Column"
bpy.ops.rigidbody.object_add()
column.rigid_body.type = 'PASSIVE'
column.rigid_body.collision_shape = 'CYLINDER'
# Set material density (mass computed automatically)
column.rigid_body.mass = density * (math.pi * col_r**2 * col_h)

# --- Create Deck ---
bpy.ops.mesh.primitive_cube_add(size=1.0, location=deck_loc)
deck = bpy.context.active_object
deck.name = "Deck"
deck.scale = (deck_l, deck_w, deck_t)
bpy.ops.rigidbody.object_add()
deck.rigid_body.type = 'ACTIVE'
deck.rigid_body.collision_shape = 'BOX'
deck.rigid_body.mass = density * (deck_l * deck_w * deck_t)

# Fixed constraint between deck and column
bpy.ops.object.select_all(action='DESELECT')
deck.select_set(True)
column.select_set(True)
bpy.context.view_layer.objects.active = column
bpy.ops.rigidbody.constraint_add()
con = bpy.context.active_object
con.name = "Fixed_Deck_Column"
con.rigid_body_constraint.type = 'FIXED'
con.rigid_body_constraint.object1 = column
con.rigid_body_constraint.object2 = deck

# --- Create Counterweight ---
bpy.ops.mesh.primitive_cylinder_add(
    vertices=32,
    radius=c_rad,
    depth=c_h,
    location=c_loc
)
counter = bpy.context.active_object
counter.name = "Counterweight"
bpy.ops.rigidbody.object_add()
counter.rigid_body.type = 'ACTIVE'
counter.rigid_body.collision_shape = 'CYLINDER'
counter.rigid_body.mass = density * (math.pi * c_rad**2 * c_h)

# Hinge constraint between counterweight and column
bpy.ops.object.select_all(action='DESELECT')
counter.select_set(True)
column.select_set(True)
bpy.context.view_layer.objects.active = column
bpy.ops.rigidbody.constraint_add()
hinge = bpy.context.active_object
hinge.name = "Hinge_Counterweight"
hinge.rigid_body_constraint.type = 'HINGE'
hinge.rigid_body_constraint.object1 = column
hinge.rigid_body_constraint.object2 = counter
hinge.rigid_body_constraint.pivot_type = 'CUSTOM'
hinge.location = hinge_piv
hinge.rigid_body_constraint.use_limit_ang_z = True
hinge.rigid_body_constraint.limit_ang_z_lower = math.radians(-5)
hinge.rigid_body_constraint.limit_ang_z_upper = math.radians(5)
# Motor setup
hinge.rigid_body_constraint.use_motor_ang = True
hinge.rigid_body_constraint.motor_ang_target_velocity = 0.0  # static hold
hinge.rigid_body_constraint.motor_ang_max_torque = init_torque

# --- Apply Load Force ---
# Create force field at load point
bpy.ops.object.empty_add(type='PLAIN_AXES', location=load_pt)
force_empty = bpy.context.active_object
force_empty.name = "Load_Force"
bpy.ops.object.forcefield_add()
force_empty.field.type = 'FORCE'
force_empty.field.strength = -load_f  # downward
force_empty.field.use_max_distance = True
force_empty.field.distance_max = 0.5  # affect only nearby objects
# Parent force field to deck so it moves with deck
force_empty.parent = deck

# --- Simulation and Measurement ---
# Function to measure hinge rotation
def get_hinge_rotation():
    # Counterweight's local Y rotation relative to rest pose
    return math.degrees(counter.rotation_euler.y)

# Bake simulation with torque adjustment
bpy.context.scene.frame_set(1)
torque = init_torque
for attempt in range(10):
    hinge.rigid_body_constraint.motor_ang_max_torque = torque
    # Bake simulation
    bpy.ops.ptcache.bake_all(bake=True)
    # Measure at last frame
    bpy.context.scene.frame_set(sim_frames)
    rot = abs(get_hinge_rotation())
    print(f"Attempt {attempt}: Torque={torque} N·m, Rotation={rot:.2f}°")
    if rot < target_rot:
        print(f"SUCCESS: Final rotation {rot:.2f}° < {target_rot}°")
        break
    else:
        # Adjust torque proportionally (since excess torque causes less rotation)
        torque *= (target_rot / max(rot, 0.1))
        # Clear cache for next bake
        bpy.ops.ptcache.free_bake_all()
        bpy.context.scene.frame_set(1)
        # Reset positions
        counter.rotation_euler.y = 0.0
        counter.keyframe_insert(data_path="rotation_euler", frame=1)
        deck.location = deck_loc
        deck.keyframe_insert(data_path="location", frame=1)
else:
    print(f"WARNING: Could not achieve <{target_rot}° after 10 attempts")

# Final verification output
print(f"Final motor torque: {hinge.rigid_body_constraint.motor_ang_max_torque:.1f} N·m")
print(f"Final rotation: {get_hinge_rotation():.2f}°")