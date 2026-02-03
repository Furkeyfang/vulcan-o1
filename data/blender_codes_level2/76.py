import bpy
import math

# Clear existing scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Define parameters from summary
beam_dim = (0.3, 2.0, 0.3)  # width (Y), length (X), height (Z)
beam_center_loc = (1.0, 0.0, 0.15)  # center position
beam_embedded_loc = (0.0, 0.0, 0.0)  # embedded end location

wall_dim = (0.5, 0.5, 2.0)  # wall section representing building structure
wall_loc = (-0.25, 0.0, 1.0)  # positioned behind beam's embedded end

landing_dim = (2.0, 1.5, 0.05)  # length (X), width (Y), thickness (Z)
landing_loc = (2.0, 0.0, 0.325)  # centered on beam's free end, flush on top

cube_size = 0.5
cube_mass = 250.0
cube_loc = (2.0, 0.0, 0.6)  # centered on landing platform

structural_density = 2500.0  # kg/m³ (concrete-like density)

# Enable rigid body physics
bpy.context.scene.rigidbody_world.enabled = True
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 50
bpy.context.scene.gravity = (0.0, 0.0, -9.81)

# Create wall (passive rigid body)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=wall_loc)
wall = bpy.context.active_object
wall.name = "Wall"
wall.scale = (wall_dim[0], wall_dim[1], wall_dim[2])
bpy.ops.rigidbody.object_add()
wall.rigid_body.type = 'PASSIVE'
wall.rigid_body.collision_shape = 'BOX'

# Create beam (active rigid body)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=beam_center_loc)
beam = bpy.context.active_object
beam.name = "Beam"
beam.scale = (beam_dim[0]/2, beam_dim[1]/2, beam_dim[2]/2)  # scale from default 2m cube
bpy.ops.rigidbody.object_add()
beam.rigid_body.type = 'ACTIVE'
beam.rigid_body.collision_shape = 'BOX'
beam.rigid_body.mass = 'DENSITY'
beam.rigid_body.density = structural_density

# Create landing platform (active rigid body)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=landing_loc)
landing = bpy.context.active_object
landing.name = "Landing"
landing.scale = (landing_dim[0]/2, landing_dim[1]/2, landing_dim[2]/2)
bpy.ops.rigidbody.object_add()
landing.rigid_body.type = 'ACTIVE'
landing.rigid_body.collision_shape = 'BOX'
landing.rigid_body.mass = 'DENSITY'
landing.rigid_body.density = structural_density

# Create load cube (active rigid body with specified mass)
bpy.ops.mesh.primitive_cube_add(size=cube_size, location=cube_loc)
cube = bpy.context.active_object
cube.name = "LoadCube"
bpy.ops.rigidbody.object_add()
cube.rigid_body.type = 'ACTIVE'
cube.rigid_body.collision_shape = 'BOX'
cube.rigid_body.mass = cube_mass  # 250 kg

# Create constraints
# 1. Wall to Beam (embedded connection at origin)
bpy.ops.object.select_all(action='DESELECT')
wall.select_set(True)
beam.select_set(True)
bpy.context.view_layer.objects.active = wall
bpy.ops.rigidbody.connect_add()
constraint1 = bpy.context.active_object
constraint1.name = "WallBeam_Fixed"
constraint1.rigid_body_constraint.type = 'FIXED'
constraint1.location = beam_embedded_loc

# 2. Beam to Landing (free end connection)
bpy.ops.object.select_all(action='DESELECT')
beam.select_set(True)
landing.select_set(True)
bpy.context.view_layer.objects.active = beam
bpy.ops.rigidbody.connect_add()
constraint2 = bpy.context.active_object
constraint2.name = "BeamLanding_Fixed"
constraint2.rigid_body_constraint.type = 'FIXED'
constraint2.location = (2.0, 0.0, 0.3)  # at beam's top surface at free end

# 3. Landing to Load Cube
bpy.ops.object.select_all(action='DESELECT')
landing.select_set(True)
cube.select_set(True)
bpy.context.view_layer.objects.active = landing
bpy.ops.rigidbody.connect_add()
constraint3 = bpy.context.active_object
constraint3.name = "LandingCube_Fixed"
constraint3.rigid_body_constraint.type = 'FIXED'
constraint3.location = cube_loc

# Set up simulation parameters
bpy.context.scene.frame_end = 100

# Bake simulation for verification
bpy.ops.ptcache.bake_all(bake=True)

# Verification: Check landing platform Z-position stability
initial_z = landing_loc[2]
final_z = landing.matrix_world.translation.z
displacement = abs(final_z - initial_z)

print(f"Initial landing Z: {initial_z:.3f}m")
print(f"Final landing Z: {final_z:.3f}m")
print(f"Vertical displacement: {displacement:.3f}m")
print(f"Maximum allowed: 0.1m")
print(f"Stability check: {'PASS' if displacement <= 0.1 else 'FAIL'}")

# Optional: Add visualization camera
bpy.ops.object.camera_add(location=(4.0, -3.0, 2.0))
camera = bpy.context.active_object
camera.rotation_euler = (math.radians(60), 0, math.radians(40))
bpy.context.scene.camera = camera