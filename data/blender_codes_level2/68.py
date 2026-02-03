import bpy
import mathutils

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Extract parameters from summary
pillar_w = 0.5
pillar_d = 0.5
pillar_h = 4.0
arm_len = 5.0
arm_w = 0.5
arm_thick = 0.5

pillar_cx = 0.25
pillar_cy = 0.25
pillar_cz = 2.0
arm_cx = 2.5
arm_cy = 0.5
arm_cz = 4.25

force_n = 500 * 9.81
load_x = 5.0
load_y = 0.5
load_z = 4.25

ground_sz = 10.0
sim_frames = 100
fps = 60

# Set scene properties
scene = bpy.context.scene
scene.frame_end = sim_frames
scene.render.fps = fps

# Enable rigid body world
if scene.rigidbody_world is None:
    bpy.ops.rigidbody.world_add()
scene.rigidbody_world.substeps_per_frame = 10
scene.rigidbody_world.solver_iterations = 50

# Create ground plane (passive)
bpy.ops.mesh.primitive_plane_add(size=ground_sz, location=(0, 0, 0))
ground = bpy.context.active_object
ground.name = "Ground"
bpy.ops.rigidbody.object_add()
ground.rigid_body.type = 'PASSIVE'
ground.rigid_body.collision_shape = 'BOX'

# Create vertical pillar (active, but will be constrained)
bpy.ops.mesh.primitive_cube_add(size=1, location=(pillar_cx, pillar_cy, pillar_cz))
pillar = bpy.context.active_object
pillar.name = "Pillar"
pillar.scale = (pillar_w, pillar_d, pillar_h)
bpy.ops.rigidbody.object_add()
pillar.rigid_body.type = 'ACTIVE'
pillar.rigid_body.mass = 100.0  # Estimated mass for stability
pillar.rigid_body.collision_shape = 'BOX'

# Create horizontal arm (active)
bpy.ops.mesh.primitive_cube_add(size=1, location=(arm_cx, arm_cy, arm_cz))
arm = bpy.context.active_object
arm.name = "Arm"
arm.scale = (arm_len, arm_w, arm_thick)
bpy.ops.rigidbody.object_add()
arm.rigid_body.type = 'ACTIVE'
arm.rigid_body.mass = 50.0  # Lighter than pillar
arm.rigid_body.collision_shape = 'BOX'

# Create fixed constraint between pillar and ground
bpy.ops.object.empty_add(type='PLAIN_AXES', location=(pillar_cx, pillar_cy, 0))
constraint_empty = bpy.context.active_object
constraint_empty.name = "Pillar_Ground_Constraint"
bpy.ops.rigidbody.constraint_add()
constraint = constraint_empty.rigid_body_constraint
constraint.type = 'FIXED'
constraint.object1 = ground
constraint.object2 = pillar

# Create fixed constraint between pillar and arm at connection point
bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0.25, 0.25, 4.0))
constraint_empty2 = bpy.context.active_object
constraint_empty2.name = "Pillar_Arm_Constraint"
bpy.ops.rigidbody.constraint_add()
constraint2 = constraint_empty2.rigid_body_constraint
constraint2.type = 'FIXED'
constraint2.object1 = pillar
constraint2.object2 = arm

# Create force field for load (point force at arm end)
bpy.ops.object.effector_add(type='FORCE', location=(load_x, load_y, load_z))
force = bpy.context.active_object
force.name = "Load_Force"
force.field.strength = force_n
force.field.direction = 'Z'
force.field.use_gravity = True
force.field.gravity = -1.0  # Negative Z direction

# Link force field only to arm (using collection)
force_collection = bpy.data.collections.new("Force_Affected")
bpy.context.scene.collection.children.link(force_collection)
force_collection.objects.link(arm)
force_collection.objects.link(force)

# Set force field to affect only objects in its collection
force.field.affect_global = False
force.field.affect_collection = force_collection

# Set up rigid body collision margins (optional for stability)
for obj in [ground, pillar, arm]:
    if obj.rigid_body:
        obj.rigid_body.collision_margin = 0.04

# Set simulation to run in background
bpy.ops.ptcache.bake_all(bake=True)