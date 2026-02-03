import bpy
import mathutils

# 1. Clear scene
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)

# 2. Define variables from summary
beam_dim = (5.0, 0.5, 0.5)
beam_loc = (2.5, 0.0, 0.25)
cyl_mid_radius = 0.3
cyl_tip_radius = 0.25
cyl_height = 0.5
cyl_mid_loc = (2.5, 0.0, 0.75)
cyl_tip_loc = (5.0, 0.0, 0.75)
mass_mid = 300.0
mass_tip = 200.0
gravity = -9.81

# 3. Set world gravity
bpy.context.scene.use_gravity = True
bpy.context.scene.gravity = mathutils.Vector((0.0, 0.0, gravity))

# 4. Create beam (passive rigid body)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=beam_loc)
beam = bpy.context.active_object
beam.name = "Beam"
beam.scale = beam_dim
bpy.ops.rigidbody.object_add()
beam.rigid_body.type = 'PASSIVE'
beam.rigid_body.collision_shape = 'BOX'
beam.rigid_body.collision_margin = 0.0

# 5. Create mid-span cylinder (active rigid body)
bpy.ops.mesh.primitive_cylinder_add(
    radius=cyl_mid_radius,
    depth=cyl_height,
    location=cyl_mid_loc
)
cyl_mid = bpy.context.active_object
cyl_mid.name = "MidSpanLoad"
cyl_mid.rotation_euler = (0.0, 0.0, 0.0)  # Z-up by default
bpy.ops.rigidbody.object_add()
cyl_mid.rigid_body.type = 'ACTIVE'
cyl_mid.rigid_body.mass = mass_mid
cyl_mid.rigid_body.collision_shape = 'CYLINDER'
cyl_mid.rigid_body.collision_margin = 0.0

# 6. Create tip cylinder (active rigid body)
bpy.ops.mesh.primitive_cylinder_add(
    radius=cyl_tip_radius,
    depth=cyl_height,
    location=cyl_tip_loc
)
cyl_tip = bpy.context.active_object
cyl_tip.name = "TipLoad"
cyl_tip.rotation_euler = (0.0, 0.0, 0.0)
bpy.ops.rigidbody.object_add()
cyl_tip.rigid_body.type = 'ACTIVE'
cyl_tip.rigid_body.mass = mass_tip
cyl_tip.rigid_body.collision_shape = 'CYLINDER'
cyl_tip.rigid_body.collision_margin = 0.0

# 7. Create fixed constraint for beam left end (at world origin)
#    Use an empty object as the world anchor at (0,0,0)
bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0.0, 0.0, 0.0))
anchor = bpy.context.active_object
anchor.name = "FixedAnchor"
bpy.ops.rigidbody.constraint_add()
constraint = bpy.context.active_object
constraint.name = "BeamFixedConstraint"
constraint.rigid_body_constraint.type = 'FIXED'
constraint.rigid_body_constraint.object1 = anchor
constraint.rigid_body_constraint.object2 = beam
constraint.rigid_body_constraint.use_limit_lin_x = True
constraint.rigid_body_constraint.use_limit_lin_y = True
constraint.rigid_body_constraint.use_limit_lin_z = True
constraint.rigid_body_constraint.use_limit_ang_x = True
constraint.rigid_body_constraint.use_limit_ang_y = True
constraint.rigid_body_constraint.use_limit_ang_z = True
for limit in ['limit_lin_x', 'limit_lin_y', 'limit_lin_z',
              'limit_ang_x', 'limit_ang_y', 'limit_ang_z']:
    setattr(constraint.rigid_body_constraint, limit.lower(), 0.0)

# 8. Create fixed constraints bonding cylinders to beam
# Mid-span cylinder constraint
bpy.ops.object.empty_add(type='PLAIN_AXES', location=cyl_mid_loc)
anchor_mid = bpy.context.active_object
anchor_mid.name = "AnchorMid"
bpy.ops.rigidbody.constraint_add()
constraint_mid = bpy.context.active_object
constraint_mid.name = "FixMidToBeam"
constraint_mid.rigid_body_constraint.type = 'FIXED'
constraint_mid.rigid_body_constraint.object1 = beam
constraint_mid.rigid_body_constraint.object2 = cyl_mid

# Tip cylinder constraint
bpy.ops.object.empty_add(type='PLAIN_AXES', location=cyl_tip_loc)
anchor_tip = bpy.context.active_object
anchor_tip.name = "AnchorTip"
bpy.ops.rigidbody.constraint_add()
constraint_tip = bpy.context.active_object
constraint_tip.name = "FixTipToBeam"
constraint_tip.rigid_body_constraint.type = 'FIXED'
constraint_tip.rigid_body_constraint.object1 = beam
constraint_tip.rigid_body_constraint.object2 = cyl_tip

# 9. Set simulation frames
bpy.context.scene.frame_end = 100

print("Cantilever beam setup complete. Run simulation with rigid body physics.")