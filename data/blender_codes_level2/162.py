import bpy
import mathutils

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Extract parameters
height = 18.0
outer_x = 1.5
outer_y = 1.5
wall = 0.1
inner_x = 1.3  # outer_x - 2*wall
inner_y = 1.3  # outer_y - 2*wall
base_z = 0.0
center_z = 9.0
force_strength = 58860.0
force_loc = (0.0, 0.0, 18.0)
steel_density = 7850.0  # kg/m³

# Create outer box
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, center_z))
outer = bpy.context.active_object
outer.name = "Column_Outer"
outer.scale = (outer_x, outer_y, height)

# Create inner hollow core (will be subtracted)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, center_z))
inner = bpy.context.active_object
inner.name = "Column_Inner"
inner.scale = (inner_x, inner_y, height)  # Slightly smaller to create walls

# Boolean difference to create hollow section
outer.modifiers.new(name="Boolean", type='BOOLEAN')
outer.modifiers["Boolean"].operation = 'DIFFERENCE'
outer.modifiers["Boolean"].object = inner
bpy.context.view_layer.objects.active = outer
bpy.ops.object.modifier_apply(modifier="Boolean")

# Delete the inner object (no longer needed)
bpy.ops.object.select_all(action='DESELECT')
inner.select_set(True)
bpy.ops.object.delete()

# Select column and add rigid body physics
outer.select_set(True)
bpy.context.view_layer.objects.active = outer
bpy.ops.rigidbody.object_add()
outer.rigid_body.type = 'ACTIVE'
outer.rigid_body.mass = steel_density * (outer_x * outer_y * height - inner_x * inner_y * height)
outer.rigid_body.collision_shape = 'MESH'
outer.rigid_body.friction = 0.5
outer.rigid_body.restitution = 0.1

# Create fixed constraint at base using empty object
bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, base_z))
empty = bpy.context.active_object
empty.name = "Base_Constraint"

# Add rigid body constraint between column and world
bpy.ops.rigidbody.constraint_add()
constraint = bpy.context.active_object
constraint.name = "Fixed_Base"
constraint.rigid_body_constraint.type = 'FIXED'
constraint.rigid_body_constraint.object1 = outer
# object2 left as None to constrain to world

# Position constraint at base
constraint.location = (0, 0, base_z)

# Create force field at top
bpy.ops.object.effector_add(type='FORCE', location=force_loc)
force = bpy.context.active_object
force.name = "Top_Load"
force.field.strength = force_strength
force.field.direction = 'Z'  # Negative Z for downward force
force.field.use_gravity_falloff = False
force.field.falloff_power = 0

# Link force field to column (parent it)
force.parent = outer
force.matrix_parent_inverse = outer.matrix_world.inverted()

# Set up rigid body world for simulation
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 50
bpy.context.scene.rigidbody_world.time_scale = 1.0

# Calculate and print stress for verification
force_n = force_strength
area = outer_x * outer_y - inner_x * inner_y  # 0.56 m²
stress_pa = force_n / area
stress_mpa = stress_pa / 1e6

print(f"Column Design Verification:")
print(f"  Material: Steel")
print(f"  Cross-sectional area: {area:.3f} m²")
print(f"  Applied force: {force_n:.0f} N (6000 kg × 9.81 m/s²)")
print(f"  Compressive stress: {stress_pa:.1f} Pa = {stress_mpa:.3f} MPa")
print(f"  Steel yield strength: 250 MPa")
print(f"  Safety factor: {250/stress_mpa:.1f}")

# Run a brief simulation to show stability
bpy.context.scene.frame_end = 100
print("
Simulation setup complete. Column should remain stable under load.")