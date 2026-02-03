import bpy
import math
from mathutils import Vector

# Clear scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Parameters from summary
deck_length_x = 10.0
deck_width_y = 3.0
thickness_min = 0.3
thickness_max = 0.6
pillar_radius = 0.5
pillar_height = 2.0
load_mass_kg = 1000.0
gravity = 9.8
load_force_n = 9800.0
simulation_frames = 100
corner_positions = [(5.0, 1.5), (5.0, -1.5), (-5.0, 1.5), (-5.0, -1.5)]
deck_base_z = 0.0

# Enable rigidbody physics
bpy.context.scene.use_gravity = True
bpy.context.scene.gravity = (0, 0, -gravity)
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 10

# Create varying thickness deck using vertex manipulation
def create_varying_thickness_deck():
    # Create base cube
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, deck_base_z + thickness_min/2))
    deck = bpy.context.active_object
    deck.name = "Bridge_Deck"
    
    # Scale to deck dimensions (uniform scaling for X,Y, initial Z)
    deck.scale = (deck_length_x/2, deck_width_y/2, thickness_min/2)
    
    # Modify vertices for linear thickness variation along Y
    mesh = deck.data
    bm = bmesh.new()
    bm.from_mesh(mesh)
    
    for vert in bm.verts:
        # Get local Y coordinate (-0.5 to 0.5 range after scaling)
        local_y = vert.co.y * 2 / deck_width_y  # Normalize to [-0.5, 0.5]
        
        # Convert to world Y for thickness calculation
        world_y = local_y * deck_width_y/2  # Actually local_y is already in [-0.5,0.5], scale by half width
        
        # Calculate thickness at this Y position
        # Y ranges from -1.5 to 1.5 in world coordinates
        t = (world_y + deck_width_y/2) / deck_width_y  # t ∈ [0,1]
        thickness = thickness_min + (thickness_max - thickness_min) * t
        
        # Adjust Z coordinate based on vertex position (top/bottom)
        if vert.co.z > 0:  # Top vertices
            vert.co.z = thickness/2
        else:  # Bottom vertices
            vert.co.z = -thickness/2
    
    bm.to_mesh(mesh)
    bm.free()
    
    # Update mesh and normals
    mesh.update()
    
    # Add rigidbody physics
    bpy.ops.rigidbody.object_add()
    deck.rigid_body.type = 'ACTIVE'
    deck.rigid_body.mass = 2000.0  # Estimated deck mass
    deck.rigid_body.collision_shape = 'MESH'
    deck.rigid_body.friction = 0.5
    deck.rigid_body.restitution = 0.1
    
    return deck

# Create cylindrical pillars
def create_pillar(location_xy):
    x, y = location_xy
    
    # Calculate thickness at pillar location for deck bottom Z
    t = (y + deck_width_y/2) / deck_width_y
    thickness_at_pillar = thickness_min + (thickness_max - thickness_min) * t
    deck_bottom_z = deck_base_z - thickness_at_pillar/2
    
    # Pillar top connects to deck bottom, pillar extends downward
    pillar_center_z = deck_bottom_z - pillar_height/2
    
    # Create cylinder
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=32,
        radius=pillar_radius,
        depth=pillar_height,
        location=(x, y, pillar_center_z)
    )
    pillar = bpy.context.active_object
    pillar.name = f"Pillar_{x}_{y}"
    
    # Add rigidbody physics
    bpy.ops.rigidbody.object_add()
    pillar.rigid_body.type = 'PASSIVE'
    pillar.rigid_body.collision_shape = 'CYLINDER'
    pillar.rigid_body.friction = 0.7
    
    return pillar

# Create load cube
def create_load():
    # Calculate deck top at center (Y=0)
    thickness_center = (thickness_min + thickness_max) / 2
    load_z = deck_base_z + thickness_center/2 + 0.01  # Slight clearance
    
    # Create small cube for load
    bpy.ops.mesh.primitive_cube_add(size=0.5, location=(0, 0, load_z))
    load = bpy.context.active_object
    load.name = "Load"
    
    # Add rigidbody physics with 1000kg mass
    bpy.ops.rigidbody.object_add()
    load.rigid_body.type = 'ACTIVE'
    load.rigid_body.mass = load_mass_kg
    load.rigid_body.collision_shape = 'BOX'
    load.rigid_body.friction = 0.3
    
    return load

# Create fixed constraints between deck and pillars
def create_fixed_constraints(deck, pillars):
    for pillar in pillars:
        # Create empty object as constraint anchor
        bpy.ops.object.empty_add(type='PLAIN_AXES', location=pillar.location)
        constraint_empty = bpy.context.active_object
        constraint_empty.name = f"Constraint_{pillar.name}"
        
        # Add rigid body constraint
        bpy.ops.rigidbody.constraint_add()
        constraint = constraint_empty.rigid_body_constraint
        
        # Configure as fixed constraint
        constraint.type = 'FIXED'
        constraint.object1 = deck
        constraint.object2 = pillar
        
        # Set constraint limits
        constraint.use_limit_lin_x = True
        constraint.use_limit_lin_y = True
        constraint.use_limit_lin_z = True
        constraint.use_limit_ang_x = True
        constraint.use_limit_ang_y = True
        constraint.use_limit_ang_z = True
        
        # All limits set to 0 (fully fixed)
        for i in range(3):
            constraint.limit_lin_lower[i] = 0
            constraint.limit_lin_upper[i] = 0
            constraint.limit_ang_lower[i] = 0
            constraint.limit_ang_upper[i] = 0

# Main construction
deck = create_varying_thickness_deck()

pillars = []
for corner in corner_positions:
    pillar = create_pillar(corner)
    pillars.append(pillar)

load = create_load()
create_fixed_constraints(deck, pillars)

# Set simulation frames
bpy.context.scene.frame_start = 1
bpy.context.scene.frame_end = simulation_frames

# Bake simulation (headless compatible)
bpy.ops.ptcache.bake_all(bake=True)