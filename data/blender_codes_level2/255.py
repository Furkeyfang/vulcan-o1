import bpy
import math
from mathutils import Vector, Matrix

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Parameters from summary
rw = 15.0
rl = 15.0
rh = 5.0
beam_cs = 0.2
beam_main = 15.0
beam_diag = 2.12132
spacing = 3.0
n_beams = 6
load_mass = 4000.0
gravity_val = 9.81
total_force = load_mass * gravity_val
sim_frames = 100

# Calculate beam center height (account for 0.2m thickness)
beam_z = rh + beam_cs/2

# Create node dictionary: {(x,y): node_object}
nodes = {}

# Create 7x7 grid nodes (0,3,6,9,12,15 positions)
for i in range(n_beams + 1):
    x = i * spacing
    for j in range(n_beams + 1):
        y = j * spacing
        bpy.ops.mesh.primitive_cube_add(size=0.1, location=(x, y, beam_z))
        node = bpy.context.active_object
        node.name = f"Node_{i}_{j}"
        bpy.ops.rigidbody.object_add()
        node.rigid_body.type = 'PASSIVE'
        nodes[(x, y)] = node

# Create cell center nodes (6x6 centers)
center_nodes = {}
for i in range(n_beams):
    for j in range(n_beams):
        cx = i * spacing + spacing/2
        cy = j * spacing + spacing/2
        bpy.ops.mesh.primitive_cube_add(size=0.1, location=(cx, cy, beam_z))
        cnode = bpy.context.active_object
        cnode.name = f"Center_{i}_{j}"
        bpy.ops.rigidbody.object_add()
        cnode.rigid_body.type = 'PASSIVE'
        center_nodes[(i, j)] = cnode

# Create longitudinal beams (along X)
for y_idx in range(n_beams + 1):
    y = y_idx * spacing
    for x_idx in range(n_beams):
        x1 = x_idx * spacing
        x2 = (x_idx + 1) * spacing
        # Create beam
        bpy.ops.mesh.primitive_cube_add(size=1, location=((x1+x2)/2, y, beam_z))
        beam = bpy.context.active_object
        beam.scale = (spacing, beam_cs, beam_cs)
        beam.name = f"Longitudinal_{x_idx}_{y_idx}"
        bpy.ops.rigidbody.object_add()
        beam.rigid_body.mass = 100.0  # Approximate mass
        
        # Create fixed constraints to nodes
        for node_pos in [(x1, y), (x2, y)]:
            constraint = beam.constraints.new(type='RIGID_BODY_JOINT')
            constraint.object1 = beam
            constraint.object2 = nodes[node_pos]
            constraint.pivot_type = 'CENTER'
            constraint.disable_collisions = True

# Create transverse beams (along Y)
for x_idx in range(n_beams + 1):
    x = x_idx * spacing
    for y_idx in range(n_beams):
        y1 = y_idx * spacing
        y2 = (y_idx + 1) * spacing
        bpy.ops.mesh.primitive_cube_add(size=1, location=(x, (y1+y2)/2, beam_z))
        beam = bpy.context.active_object
        beam.scale = (beam_cs, spacing, beam_cs)
        beam.name = f"Transverse_{x_idx}_{y_idx}"
        bpy.ops.rigidbody.object_add()
        beam.rigid_body.mass = 100.0
        
        for node_pos in [(x, y1), (x, y2)]:
            constraint = beam.constraints.new(type='RIGID_BODY_JOINT')
            constraint.object1 = beam
            constraint.object2 = nodes[node_pos]
            constraint.pivot_type = 'CENTER'
            constraint.disable_collisions = True

# Create diagonal bracing beams (from corners to center)
for i in range(n_beams):
    for j in range(n_beams):
        corners = [
            (i*spacing, j*spacing),
            ((i+1)*spacing, j*spacing),
            (i*spacing, (j+1)*spacing),
            ((i+1)*spacing, (j+1)*spacing)
        ]
        center_node = center_nodes[(i, j)]
        cx, cy, cz = center_node.location
        
        for corner_x, corner_y in corners:
            # Calculate midpoint and orientation
            mx, my = (corner_x + cx)/2, (corner_y + cy)/2
            bpy.ops.mesh.primitive_cube_add(size=1, location=(mx, my, cz))
            diag = bpy.context.active_object
            diag.name = f"Diagonal_{i}_{j}_{corner_x}_{corner_y}"
            
            # Scale to diagonal length
            length = math.sqrt((corner_x-cx)**2 + (corner_y-cy)**2)
            diag.scale = (length, beam_cs, beam_cs)
            
            # Rotate to align with diagonal direction
            angle = math.atan2(cy-corner_y, cx-corner_x)
            diag.rotation_euler.z = angle
            
            bpy.ops.rigidbody.object_add()
            diag.rigid_body.mass = 50.0
            
            # Constraints to corner and center nodes
            for node_obj in [nodes[(corner_x, corner_y)], center_node]:
                constraint = diag.constraints.new(type='RIGID_BODY_JOINT')
                constraint.object1 = diag
                constraint.object2 = node_obj
                constraint.pivot_type = 'CENTER'
                constraint.disable_collisions = True

# Apply distributed load as forces on nodes
total_nodes = len(nodes) + len(center_nodes)
force_per_node = total_force / total_nodes / 10  # Reduced for stability

for node_dict in [nodes, center_nodes]:
    for node in node_dict.values():
        node.rigid_body.enabled = True
        # Apply downward force (negative Z)
        if node.rigid_body is not None:
            # Force will be applied in animation frame
            node.rigid_body.use_gravity = True
            # Additional constant force
            node.keyframe_insert(data_path="rigid_body.force", frame=1)
            node.rigid_body.force = (0, 0, -force_per_node)
            node.keyframe_insert(data_path="rigid_body.force", frame=sim_frames)

# Setup physics world
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 50
bpy.context.scene.frame_end = sim_frames

print(f"Created space frame roof with {len(nodes)} grid nodes and {len(center_nodes)} center nodes")
print(f"Total load: {total_force}N distributed as {force_per_node:.1f}N per node")