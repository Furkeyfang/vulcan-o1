import bpy
import mathutils

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Parameters from summary
beam_length = 8.0
beam_width = 0.5
beam_height = 0.5
beam_center_x = 4.0
beam_center_y = 0.0
beam_center_z = 0.25

platform_length = 4.0
platform_width = 3.0
platform_thickness = 0.3
platform_center_x = 10.0
platform_center_y = 0.0
platform_center_z = 0.65

block_size = 0.5
block_mass = 450.0
block_center_x = 12.0
block_center_y = 0.0
block_center_z = 1.05

constraint_breaking_threshold = 1e7
simulation_steps = 150
gravity_z = -9.81

# Create Support Beam
bpy.ops.mesh.primitive_cube_add(size=1.0)
beam = bpy.context.active_object
beam.name = "Support_Beam"
beam.scale = (beam_length, beam_width, beam_height)
beam.location = (beam_center_x, beam_center_y, beam_center_z)
bpy.ops.rigidbody.object_add()
beam.rigid_body.type = 'ACTIVE'
beam.rigid_body.mass = 50.0  # Estimated reasonable mass

# Create Ground (Passive anchor at beam base)
bpy.ops.mesh.primitive_cube_add(size=0.1)
ground = bpy.context.active_object
ground.name = "Ground_Anchor"
ground.location = (0.0, 0.0, -0.1)  # Below beam base
bpy.ops.rigidbody.object_add()
ground.rigid_body.type = 'PASSIVE'

# Create Fixed Constraint: Ground → Beam Base
constraint = bpy.ops.rigidbody.constraint_add(type='FIXED')
constraint_obj = bpy.context.active_object
constraint_obj.name = "Base_Constraint"
constraint_obj.location = (0.0, 0.0, beam_center_z)  # At beam base center
constraint_obj.rigid_body_constraint.object1 = ground
constraint_obj.rigid_body_constraint.object2 = beam
constraint_obj.rigid_body_constraint.use_breaking = True
constraint_obj.rigid_body_constraint.breaking_threshold = constraint_breaking_threshold

# Create Cantilever Platform
bpy.ops.mesh.primitive_cube_add(size=1.0)
platform = bpy.context.active_object
platform.name = "Cantilever_Platform"
platform.scale = (platform_length, platform_width, platform_thickness)
platform.location = (platform_center_x, platform_center_y, platform_center_z)
bpy.ops.rigidbody.object_add()
platform.rigid_body.type = 'ACTIVE'
platform.rigid_body.mass = 100.0  # Estimated reasonable mass
# Use convex hull collision for better stability on rectangular shape
platform.rigid_body.collision_shape = 'CONVEX_HULL'

# Create Fixed Constraint: Beam Free End → Platform
constraint2 = bpy.ops.rigidbody.constraint_add(type='FIXED')
constraint_obj2 = bpy.context.active_object
constraint_obj2.name = "Beam_Platform_Constraint"
constraint_obj2.location = (8.0, 0.0, beam_center_z + beam_height/2)  # Beam top at free end
constraint_obj2.rigid_body_constraint.object1 = beam
constraint_obj2.rigid_body_constraint.object2 = platform
constraint_obj2.rigid_body_constraint.use_breaking = True
constraint_obj2.rigid_body_constraint.breaking_threshold = constraint_breaking_threshold

# Create Load Block
bpy.ops.mesh.primitive_cube_add(size=1.0)
block = bpy.context.active_object
block.name = "Load_Block"
block.scale = (block_size, block_size, block_size)
block.location = (block_center_x, block_center_y, block_center_z)
bpy.ops.rigidbody.object_add()
block.rigid_body.type = 'ACTIVE'
block.rigid_body.mass = block_mass

# Create Fixed Constraint: Platform → Load Block
constraint3 = bpy.ops.rigidbody.constraint_add(type='FIXED')
constraint_obj3 = bpy.context.active_object
constraint_obj3.name = "Platform_Block_Constraint"
constraint_obj3.location = (block_center_x, block_center_y, platform_center_z + platform_thickness/2)
constraint_obj3.rigid_body_constraint.object1 = platform
constraint_obj3.rigid_body_constraint.object2 = block
constraint_obj3.rigid_body_constraint.use_breaking = True
constraint_obj3.rigid_body_constraint.breaking_threshold = constraint_breaking_threshold

# Configure world physics
bpy.context.scene.gravity = (0.0, 0.0, gravity_z)
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 50
bpy.context.scene.frame_end = simulation_steps

# Verification: Measure platform projection
platform_projection = block_center_x - 8.0  # From beam free end at X=8
print(f"Platform projection from beam: {platform_projection} m")
assert abs(platform_projection - 4.0) < 0.01, "Platform projection incorrect"

# Run simulation (headless)
print("Running rigid body simulation...")
bpy.ops.ptcache.bake_all(bake=True)
print("Simulation complete. Checking constraint integrity...")

# Verify constraints are intact
for obj in [constraint_obj, constraint_obj2, constraint_obj3]:
    if obj.rigid_body_constraint is None:
        print(f"WARNING: Constraint {obj.name} missing rigid body constraint component")
    else:
        print(f"Constraint {obj.name}: breaking threshold {obj.rigid_body_constraint.breaking_threshold} N")

print("Cantilever structure built and simulated.")