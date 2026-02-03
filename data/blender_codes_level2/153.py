import bpy

# Clear existing objects
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

# Parameters from summary
platform_dim = (4.0, 2.0, 0.5)
level_spacing = 3.0
num_levels = 6
base_center_z = 2.75
top_mass_kg = 1200.0

# Compute platform centers
centers = []
for i in range(num_levels):
    z = base_center_z + i * level_spacing
    centers.append((0.0, 0.0, z))

# Scale factor: Blender default cube is 2x2x2, we want platform_dim
scale_x = platform_dim[0] / 2.0
scale_y = platform_dim[1] / 2.0
scale_z = platform_dim[2] / 2.0

# Create levels
platforms = []
for idx, center in enumerate(centers):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=center)
    plat = bpy.context.active_object
    plat.name = f"Level_{idx+1}"
    plat.scale = (scale_x, scale_y, scale_z)
    
    # Add rigid body
    bpy.ops.rigidbody.object_add()
    if idx == 0:
        # Bottom platform is passive (fixed base)
        plat.rigid_body.type = 'PASSIVE'
    else:
        plat.rigid_body.type = 'ACTIVE'
        plat.rigid_body.mass = 10.0  # nominal mass for structure (kg)
    
    platforms.append(plat)

# Set top platform mass
platforms[-1].rigid_body.mass = top_mass_kg

# Create FIXED constraints between levels
for i in range(1, num_levels):
    upper = platforms[i]
    lower = platforms[i-1]
    
    # Create empty object for constraint (parented to upper platform)
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=upper.location)
    constraint_empty = bpy.context.active_object
    constraint_empty.name = f"Fixed_Constraint_{i}"
    constraint_empty.parent = upper
    
    # Add rigid body constraint
    bpy.ops.rigidbody.constraint_add()
    constraint = constraint_empty.rigid_body_constraint
    constraint.type = 'FIXED'
    constraint.object1 = upper
    constraint.object2 = lower

# Add ground plane for reference (optional)
bpy.ops.mesh.primitive_plane_add(size=20.0, location=(0,0,0))
ground = bpy.context.active_object
bpy.ops.rigidbody.object_add()
ground.rigid_body.type = 'PASSIVE'

# Configure physics world for stability
bpy.context.scene.rigidbody_world.steps_per_second = 250
bpy.context.scene.rigidbody_world.solver_iterations = 50

# Run simulation for 250 frames to settle
bpy.context.scene.frame_end = 250
for frame in range(1, 251):
    bpy.context.scene.frame_set(frame)
    bpy.context.scene.update()

# Verification: print final height of top platform
top = platforms[-1]
top_surface_z = top.location.z + (platform_dim[2] / 2.0)
print(f"Top surface Z after simulation: {top_surface_z:.3f} m")
print(f"Target height: 18.0 m")
print(f"Deviation: {abs(top_surface_z - 18.0):.6f} m")