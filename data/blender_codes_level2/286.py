import bpy
import mathutils

# Clear scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Parameters from summary
base_dim = (2.0, 2.0, 0.5)
step_dim = (1.5, 0.5, 0.2)
base_loc = (0.0, 0.0, 0.25)
step1_loc = (1.75, 0.0, 0.35)
step2_loc = (3.25, 0.0, 0.55)
step3_loc = (4.75, 0.0, 0.75)
total_load_kg = 600.0
gravity = 9.81
load_per_step_N = 1962.0
step_top_area = 0.75  # 1.5 * 0.5 m²

# Enable rigid body physics
if not bpy.context.scene.rigidbody_world:
    bpy.ops.rigidbody.world_add()
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 50

# Create Base (Passive)
bpy.ops.mesh.primitive_cube_add(size=1, location=base_loc)
base = bpy.context.active_object
base.scale = base_dim
base.name = "Base"
bpy.ops.rigidbody.object_add()
base.rigid_body.type = 'PASSIVE'
base.rigid_body.collision_shape = 'BOX'
base.rigid_body.mass = 1000.0  # Heavy foundation

# Create Step 1
bpy.ops.mesh.primitive_cube_add(size=1, location=step1_loc)
step1 = bpy.context.active_object
step1.scale = step_dim
step1.name = "Step1"
bpy.ops.rigidbody.object_add()
step1.rigid_body.type = 'ACTIVE'
step1.rigid_body.collision_shape = 'BOX'
step1.rigid_body.mass = 50.0  # Structural mass

# Create Step 2
bpy.ops.mesh.primitive_cube_add(size=1, location=step2_loc)
step2 = bpy.context.active_object
step2.scale = step_dim
step2.name = "Step2"
bpy.ops.rigidbody.object_add()
step2.rigid_body.type = 'ACTIVE'
step2.rigid_body.collision_shape = 'BOX'
step2.rigid_body.mass = 50.0

# Create Step 3
bpy.ops.mesh.primitive_cube_add(size=1, location=step3_loc)
step3 = bpy.context.active_object
step3.scale = step_dim
step3.name = "Step3"
bpy.ops.rigidbody.object_add()
step3.rigid_body.type = 'ACTIVE'
step3.rigid_body.collision_shape = 'BOX'
step3.rigid_body.mass = 50.0

# Create Fixed Constraints
def create_fixed_constraint(obj1, obj2, name):
    # Create empty for constraint
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=((obj1.location.x + obj2.location.x)/2, 
                                                          (obj1.location.y + obj2.location.y)/2,
                                                          (obj1.location.z + obj2.location.z)/2))
    constraint = bpy.context.active_object
    constraint.name = name
    bpy.ops.rigidbody.constraint_add()
    rb_constraint = constraint.rigid_body_constraint
    rb_constraint.type = 'FIXED'
    rb_constraint.object1 = obj1
    rb_constraint.object2 = obj2

create_fixed_constraint(base, step1, "Base_Step1_Fixed")
create_fixed_constraint(step1, step2, "Step1_Step2_Fixed")
create_fixed_constraint(step2, step3, "Step2_Step3_Fixed")

# Apply Distributed Load via Force Fields
def add_force_field(location, strength, name):
    bpy.ops.object.effector_add(type='FORCE', location=location)
    force = bpy.context.active_object
    force.name = name
    force.field.type = 'FORCE'
    force.field.strength = strength
    force.field.direction = 'Z'
    force.field.use_gravity = False
    force.field.z_gravity = -1.0  # Downward
    force.field.falloff_power = 0
    force.field.distance_max = 0.3  # Cover top surface area
    # Shape to match step area
    force.field.shape = 'SURFACE'
    force.scale = (step_dim[0], step_dim[1], 0.1)

# Force strength in Newtons (negative for downward)
force_strength = -load_per_step_N / gravity  # Convert to Blender units (kg-force)
add_force_field((step1_loc[0], step1_loc[1], step1_loc[2] + step_dim[2]/2), 
                force_strength, "Load_Step1")
add_force_field((step2_loc[0], step2_loc[1], step2_loc[2] + step_dim[2]/2), 
                force_strength, "Load_Step2")
add_force_field((step3_loc[0], step3_loc[1], step3_loc[2] + step_dim[2]/2), 
                force_strength, "Load_Step3")

# Set up animation and verification
initial_positions = {
    'step1': step1.location.copy(),
    'step2': step2.location.copy(),
    'step3': step3.location.copy()
}

# Run simulation
bpy.context.scene.frame_end = 100
print("Simulation setup complete. Run with: bpy.ops.ptcache.bake_all(bake=True)")

# Verification function (to be called after baking)
def verify_stability():
    max_drift = 0.0
    for step_obj, init_pos in [('step1', initial_positions['step1']),
                               ('step2', initial_positions['step2']),
                               ('step3', initial_positions['step3'])]:
        obj = bpy.data.objects[step_obj.capitalize()]
        drift = (obj.location - init_pos).length
        max_drift = max(max_drift, drift)
        print(f"{step_obj}: Drift = {drift:.3f}m")
    
    print(f"Maximum drift: {max_drift:.3f}m")
    print(f"Stability check: {'PASS' if max_drift < 0.1 else 'FAIL'}")
    return max_drift < 0.1

# Note: In headless mode, baking requires:
# bpy.ops.ptcache.bake_all(bake=True)
# Then call verify_stability()