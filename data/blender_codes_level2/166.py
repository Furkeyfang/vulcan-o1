import bpy
import math

# Clear existing objects
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

# Parameters from summary
H_concrete = 20.0
R_concrete = 1.0
H_steel = 20.0
R_steel = 0.1
D_from_center = 1.2
bar_offset = D_from_center / math.sqrt(2)  # 0.848528
concrete_loc = (0.0, 0.0, H_concrete/2)  # (0,0,10)
steel_locs = [
    (bar_offset, bar_offset, H_steel/2),
    (-bar_offset, bar_offset, H_steel/2),
    (-bar_offset, -bar_offset, H_steel/2),
    (bar_offset, -bar_offset, H_steel/2)
]
load_mass = 8000.0
load_size = 2.5  # Cube side length
load_loc = (0.0, 0.0, H_concrete)  # (0,0,20)
ground_size = 50.0
simulation_frames = 100

# Create ground plane
bpy.ops.mesh.primitive_plane_add(size=ground_size, location=(0,0,0))
ground = bpy.context.active_object
ground.name = "Ground"
bpy.ops.rigidbody.object_add()
ground.rigid_body.type = 'PASSIVE'

# Create concrete core
bpy.ops.mesh.primitive_cylinder_add(
    vertices=32,
    radius=R_concrete,
    depth=H_concrete,
    location=concrete_loc
)
concrete = bpy.context.active_object
concrete.name = "Concrete_Core"
bpy.ops.rigidbody.object_add()
concrete.rigid_body.type = 'PASSIVE'
concrete.rigid_body.collision_shape = 'MESH'

# Create steel reinforcement bars
steel_bars = []
for i, loc in enumerate(steel_locs, 1):
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=16,
        radius=R_steel,
        depth=H_steel,
        location=loc
    )
    steel = bpy.context.active_object
    steel.name = f"Steel_Bar_{i}"
    bpy.ops.rigidbody.object_add()
    steel.rigid_body.type = 'PASSIVE'
    steel.rigid_body.collision_shape = 'MESH'
    steel_bars.append(steel)

# Create fixed constraints between steel bars and concrete core
for steel in steel_bars:
    bpy.ops.object.select_all(action='DESELECT')
    concrete.select_set(True)
    steel.select_set(True)
    bpy.context.view_layer.objects.active = concrete
    bpy.ops.rigidbody.connect_add(type='FIXED')
    constraint = bpy.context.active_object
    constraint.name = f"Constraint_{steel.name}"

# Create load cube
bpy.ops.mesh.primitive_cube_add(size=1.0, location=load_loc)
load = bpy.context.active_object
load.name = "Load"
load.scale = (load_size, load_size, load_size/3)  # Flattened cube
bpy.ops.rigidbody.object_add()
load.rigid_body.type = 'ACTIVE'
load.rigid_body.mass = load_mass
load.rigid_body.collision_shape = 'BOX'

# Set up scene for simulation
scene = bpy.context.scene
scene.frame_end = simulation_frames
scene.rigidbody_world.substeps_per_frame = 10
scene.rigidbody_world.solver_iterations = 50

# Ensure all objects are visible in viewport
for obj in bpy.data.objects:
    obj.hide_viewport = False
    obj.hide_render = False