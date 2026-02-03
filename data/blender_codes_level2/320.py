import bpy
import mathutils

# Clear existing scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Parameters from summary
base_dim = (10.0, 10.0, 0.5)
base_loc = (0.0, 0.0, 0.0)
column_dim = (1.0, 1.0, 3.0)
column_positions = [(4.0, 4.0), (-4.0, 4.0), (-4.0, -4.0), (4.0, -4.0)]
column_labels = ["FR", "FL", "BL", "BR"]
levels_remove_column = [2, 4, 6]
remove_label = "FL"
remove_index = column_labels.index(remove_label)
level_heights = [1.75, 4.75, 7.75, 10.75, 13.75, 16.75]
load_dim = (2.0, 2.0, 1.0)
load_mass = 1400.0
load_loc = (0.0, 0.0, 18.0)

# Create base platform
bpy.ops.mesh.primitive_cube_add(size=1.0, location=base_loc)
base = bpy.context.active_object
base.name = "BasePlatform"
base.scale = base_dim
bpy.ops.rigidbody.object_add()
base.rigid_body.type = 'PASSIVE'
base.rigid_body.collision_shape = 'BOX'

# Store columns by level and position
columns = {}  # {level: {label: object}}

# Create columns for each level
for level in range(1, 7):
    columns[level] = {}
    z_center = level_heights[level-1]
    
    for idx, (label, (x, y)) in enumerate(zip(column_labels, column_positions)):
        # Skip removed column in specified levels
        if level in levels_remove_column and idx == remove_index:
            continue
        
        # Create column
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(x, y, z_center))
        col = bpy.context.active_object
        col.name = f"Level{level}_{label}"
        col.scale = column_dim
        
        # Add rigid body
        bpy.ops.rigidbody.object_add()
        col.rigid_body.mass = 10.0  # Reasonable mass for concrete column
        col.rigid_body.collision_shape = 'BOX'
        col.rigid_body.friction = 0.5
        col.rigid_body.restitution = 0.1
        
        columns[level][label] = col

# Create fixed constraints
for level in range(1, 7):
    for label in columns[level].keys():
        current_col = columns[level][label]
        
        if level == 1:
            # Constrain to base platform
            bpy.ops.object.empty_add(type='PLAIN_AXES')
            constraint = bpy.context.active_object
            constraint.name = f"Constraint_L{level}_{label}"
            constraint.location = current_col.location
            bpy.ops.rigidbody.constraint_add()
            constraint.rigid_body_constraint.type = 'FIXED'
            constraint.rigid_body_constraint.object1 = current_col
            constraint.rigid_body_constraint.object2 = base
        else:
            # Constrain to column below if it exists
            if label in columns[level-1]:
                bpy.ops.object.empty_add(type='PLAIN_AXES')
                constraint = bpy.context.active_object
                constraint.name = f"Constraint_L{level}_{label}"
                # Position at interface between columns
                interface_z = (level_heights[level-2] + level_heights[level-1]) / 2
                constraint.location = (current_col.location.x, current_col.location.y, interface_z)
                bpy.ops.rigidbody.constraint_add()
                constraint.rigid_body_constraint.type = 'FIXED'
                constraint.rigid_body_constraint.object1 = current_col
                constraint.rigid_body_constraint.object2 = columns[level-1][label]

# Create load cube
bpy.ops.mesh.primitive_cube_add(size=1.0, location=load_loc)
load = bpy.context.active_object
load.name = "LoadCube"
load.scale = load_dim
bpy.ops.rigidbody.object_add()
load.rigid_body.mass = load_mass
load.rigid_body.collision_shape = 'BOX'
load.rigid_body.friction = 0.7
load.rigid_body.restitution = 0.05

# Configure physics world
bpy.context.scene.rigidbody_world.enabled = True
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 10
bpy.context.scene.frame_end = 100

print(f"Tower constructed with {len(columns)} levels")
print(f"Load cube mass: {load_mass} kg")
print(f"Simulation will run for 100 frames")