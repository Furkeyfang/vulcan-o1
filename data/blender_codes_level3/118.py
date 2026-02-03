import bpy
import mathutils

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Extract parameters
base_dim = (3.0, 3.0, 0.5)
base_loc = (0.0, 0.0, 0.0)
column_dim = (0.5, 0.5, 3.5)
column_loc = (0.0, 0.0, 2.0)
boom_dim = (4.0, 0.3, 0.3)
boom_loc = (2.0, 0.0, 4.0)
payload_dim = (0.5, 0.5, 0.5)
payload_loc = (4.0, 0.0, 4.0)
hinge_loc = (0.0, 0.0, 4.0)
motor_velocity = 1.0

# Ensure rigid body world exists
if bpy.context.scene.rigidbody_world is None:
    bpy.ops.rigidbody.world_add()

# 1. Base Platform (Static)
bpy.ops.mesh.primitive_cube_add(size=1, location=base_loc)
base = bpy.context.active_object
base.name = "Base"
base.scale = (base_dim[0]/2, base_dim[1]/2, base_dim[2]/2)  # Blender cube size=2, scale to dimensions
bpy.ops.rigidbody.object_add()
base.rigid_body.type = 'PASSIVE'

# 2. Vertical Column (Static, fixed to base)
bpy.ops.mesh.primitive_cube_add(size=1, location=column_loc)
column = bpy.context.active_object
column.name = "Column"
column.scale = (column_dim[0]/2, column_dim[1]/2, column_dim[2]/2)
bpy.ops.rigidbody.object_add()
column.rigid_body.type = 'PASSIVE'

# 3. Boom Arm (Dynamic)
bpy.ops.mesh.primitive_cube_add(size=1, location=boom_loc)
boom = bpy.context.active_object
boom.name = "Boom"
boom.scale = (boom_dim[0]/2, boom_dim[1]/2, boom_dim[2]/2)
bpy.ops.rigidbody.object_add()
boom.rigid_body.type = 'ACTIVE'
boom.rigid_body.mass = 5.0  # kg

# 4. Payload Cube (Dynamic)
bpy.ops.mesh.primitive_cube_add(size=1, location=payload_loc)
payload = bpy.context.active_object
payload.name = "Payload"
payload.scale = (payload_dim[0]/2, payload_dim[1]/2, payload_dim[2]/2)
bpy.ops.rigidbody.object_add()
payload.rigid_body.type = 'ACTIVE'
payload.rigid_body.mass = 10.0  # heavier than boom

# 5. Constraints
# Column fixed to Base
bpy.ops.object.select_all(action='DESELECT')
column.select_set(True)
base.select_set(True)
bpy.context.view_layer.objects.active = base
bpy.ops.rigidbody.connect_add()
con1 = bpy.context.active_object
con1.name = "Base_Column_Fixed"
con1.rigid_body_constraint.type = 'FIXED'
con1.rigid_body_constraint.object1 = base
con1.rigid_body_constraint.object2 = column

# Hinge between Column and Boom
bpy.ops.object.select_all(action='DESELECT')
column.select_set(True)
boom.select_set(True)
bpy.context.view_layer.objects.active = boom
bpy.ops.rigidbody.connect_add()
con2 = bpy.context.active_object
con2.name = "Column_Boom_Hinge"
con2.rigid_body_constraint.type = 'HINGE'
con2.rigid_body_constraint.object1 = column
con2.rigid_body_constraint.object2 = boom
con2.location = hinge_loc
# Hinge axis local to column/boom: use world Y axis
con2.rigid_body_constraint.axis_primary = 'Y'
# Enable motor
con2.rigid_body_constraint.use_motor = True
con2.rigid_body_constraint.motor_type = 'VELOCITY'
con2.rigid_body_constraint.motor_velocity = motor_velocity

# Fixed between Boom and Payload
bpy.ops.object.select_all(action='DESELECT')
boom.select_set(True)
payload.select_set(True)
bpy.context.view_layer.objects.active = payload
bpy.ops.rigidbody.connect_add()
con3 = bpy.context.active_object
con3.name = "Boom_Payload_Fixed"
con3.rigid_body_constraint.type = 'FIXED'
con3.rigid_body_constraint.object1 = boom
con3.rigid_body_constraint.object2 = payload

# 6. Initial rotation: ensure boom is horizontal (along +X)
boom.rotation_euler = (0, 0, 0)
payload.rotation_euler = (0, 0, 0)

# Set gravity to default -9.81 Z for realistic lift
bpy.context.scene.rigidbody_world.gravity = (0, 0, -9.81)

print("Crane assembly complete. Hinge motor set to", motor_velocity, "rad/s.")