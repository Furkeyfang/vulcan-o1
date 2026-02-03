import bpy
import mathutils

# Clear scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Parameters from summary
beam_dim = (0.3, 0.3, 4.0)
beam_center = (0.0, 2.0, 3.0)
panel_dim = (3.5, 2.0, 0.05)
panel_center = (0.0, 3.0, 3.175)
wall_anchor_loc = (0.0, 0.0, 3.0)
connection_loc = (0.0, 4.0, 3.0)
force_magnitude = 4414.5
gravity_z = -9.81
simulation_frames = 100
tolerance = 0.1

# Set gravity
bpy.context.scene.use_gravity = True
bpy.context.scene.gravity = (0, 0, gravity_z)

# Create Main Beam
bpy.ops.mesh.primitive_cube_add(size=1, location=beam_center)
beam = bpy.context.active_object
beam.name = "Main_Beam"
beam.scale = (beam_dim[0]/2, beam_dim[1]/2, beam_dim[2]/2)  # Default cube is 2x2x2
bpy.ops.rigidbody.object_add()
beam.rigid_body.type = 'ACTIVE'
beam.rigid_body.collision_shape = 'BOX'
beam.rigid_body.mass = 100  # Estimated steel beam mass

# Create Roof Panel
bpy.ops.mesh.primitive_cube_add(size=1, location=panel_center)
panel = bpy.context.active_object
panel.name = "Roof_Panel"
panel.scale = (panel_dim[0]/2, panel_dim[1]/2, panel_dim[2]/2)
bpy.ops.rigidbody.object_add()
panel.rigid_body.type = 'ACTIVE'
panel.rigid_body.collision_shape = 'BOX'
panel.rigid_body.mass = 50  # Estimated panel mass

# Create Wall Anchor (Empty)
bpy.ops.object.empty_add(type='PLAIN_AXES', location=wall_anchor_loc)
anchor = bpy.context.active_object
anchor.name = "Wall_Anchor"
bpy.ops.rigidbody.object_add()
anchor.rigid_body.type = 'PASSIVE'

# Create Fixed Constraint: Anchor → Beam
bpy.ops.object.empty_add(type='PLAIN_AXES', location=wall_anchor_loc)
constraint_anchor = bpy.context.active_object
constraint_anchor.name = "Constraint_Anchor_Beam"
bpy.ops.rigidbody.constraint_add()
constraint_anchor.rigid_body_constraint.type = 'FIXED'
constraint_anchor.rigid_body_constraint.object1 = anchor
constraint_anchor.rigid_body_constraint.object2 = beam

# Create Fixed Constraint: Beam → Panel
bpy.ops.object.empty_add(type='PLAIN_AXES', location=connection_loc)
constraint_connection = bpy.context.active_object
constraint_connection.name = "Constraint_Beam_Panel"
bpy.ops.rigidbody.constraint_add()
constraint_connection.rigid_body_constraint.type = 'FIXED'
constraint_connection.rigid_body_constraint.object1 = beam
constraint_connection.rigid_body_constraint.object2 = panel

# Create Force Field (affects only panel)
bpy.ops.object.empty_add(type='PLAIN_AXES', location=panel_center)
force_field = bpy.context.active_object
force_field.name = "Force_Field"
bpy.ops.object.forcefield_add(type='FORCE')
force_field.field.strength = force_magnitude
force_field.field.direction = 'Z'
force_field.field.use_max_distance = True
force_field.field.distance_max = 0.05  # Only affect objects within 5cm
force_field.field.falloff_power = 0

# Link force field to panel via vertex group (simulate distributed load)
# Create vertex group in panel and assign all vertices
panel.vertex_groups.new(name="Force_Group")
vg = panel.vertex_groups["Force_Group"]
for vert in panel.data.vertices:
    vg.add([vert.index], 1.0, 'ADD')
force_field.field.vertex_group = "Force_Group"

# Set simulation length
bpy.context.scene.frame_end = simulation_frames

# Optional: Bake simulation for verification
# (In headless mode, we would run simulation via command line)
print("Setup complete. Run with: blender --background --python script.py")