import bpy
import math

# Clear existing scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Parameters from summary
floor_count = 8
floor_width = 4.0
floor_depth = 4.0
floor_height = 3.0
mass_light = 200.0
mass_heavy = 400.0
base_z = 0.0
first_floor_center_z = 1.5
constraint_offset_z = 0.1

# Collection for organization
tower_collection = bpy.data.collections.new("Tower")
bpy.context.scene.collection.children.link(tower_collection)

# Store floor objects for constraint creation
floor_objects = []

# Create floors
for i in range(floor_count):
    floor_num = i + 1  # 1-based indexing
    
    # Calculate position
    floor_center_z = (i * floor_height) + first_floor_center_z
    
    # Create cuboid floor
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, 0.0, floor_center_z))
    floor_obj = bpy.context.active_object
    floor_obj.name = f"Floor_{floor_num}"
    
    # Scale to correct dimensions (default cube is 2x2x2, so scale by half dimensions)
    floor_obj.scale = (floor_width / 2.0, floor_depth / 2.0, floor_height / 2.0)
    
    # Apply scale to avoid issues
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    
    # Assign rigid body properties
    bpy.ops.rigidbody.object_add()
    
    # Set mass based on alternating pattern (floor 1 is light)
    if i % 2 == 0:  # Even indices (0,2,4,6) → light floors (1,3,5,7)
        floor_obj.rigid_body.mass = mass_light
        floor_obj.name += "_Light"
    else:  # Odd indices (1,3,5,7) → heavy floors (2,4,6,8)
        floor_obj.rigid_body.mass = mass_heavy
        floor_obj.name += "_Heavy"
    
    # First floor is passive (foundation), others are active
    if i == 0:
        floor_obj.rigid_body.type = 'PASSIVE'
    else:
        floor_obj.rigid_body.type = 'ACTIVE'
        # Disable gravity for active floors since they're constrained
        floor_obj.rigid_body.enabled = True
        floor_obj.rigid_body.kinematic = False
    
    # Move to tower collection
    if floor_obj.users_collection:
        for coll in floor_obj.users_collection:
            coll.objects.unlink(floor_obj)
    tower_collection.objects.link(floor_obj)
    
    floor_objects.append(floor_obj)

# Create fixed constraints between floors
for i in range(1, floor_count):
    floor_above = floor_objects[i]
    floor_below = floor_objects[i-1]
    
    # Create constraint empty
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0.0, 0.0, floor_below.location.z + floor_height/2 + constraint_offset_z))
    constraint_obj = bpy.context.active_object
    constraint_obj.name = f"Constraint_Floor{i}_to_{i+1}"
    
    # Add rigid body constraint
    bpy.ops.rigidbody.constraint_add()
    constraint = constraint_obj.rigid_body_constraint
    constraint.type = 'FIXED'
    
    # Link the two floors
    constraint.object1 = floor_below
    constraint.object2 = floor_above
    
    # Disable breaking for permanent bond
    constraint.use_breaking = False
    
    # Move to tower collection
    if constraint_obj.users_collection:
        for coll in constraint_obj.users_collection:
            coll.objects.unlink(constraint_obj)
    tower_collection.objects.link(constraint_obj)

# Verify total mass
total_mass = 0.0
for i, obj in enumerate(floor_objects):
    total_mass += obj.rigid_body.mass

print(f"Tower constructed with {floor_count} floors")
print(f"Total mass: {total_mass} kg (Expected: 2000 kg)")
print(f"Mass pattern: {'✓' if total_mass == 2000 else '✗'}")

# Set up rigid body world for simulation (optional)
bpy.context.scene.rigidbody_world.enabled = True
bpy.context.scene.rigidbody_world.collection = tower_collection