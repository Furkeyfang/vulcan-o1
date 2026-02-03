import bpy
import math
from mathutils import Matrix, Vector

# Clear scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Parameters from summary
col_size = (0.5, 0.5, 3.0)
col_loc = (0.0, 0.0, 1.5)
beam_dim = (4.0, 0.5, 0.3)
beam_loc = (2.0, 0.0, 3.15)
brace_length = 2.593
brace_dim = (brace_length, 0.3, 0.2)
brace_angle = 39.5
brace_start = (0.0, 0.0, 1.5)
brace_end = (2.0, 0.0, 3.15)
mass_dim = (4.0, 0.5, 0.1)
mass_loc = (2.0, 0.0, 3.35)
mass_value = 600.0

# 1. Create Support Column
bpy.ops.mesh.primitive_cube_add(size=1.0, location=col_loc)
column = bpy.context.active_object
column.name = "Column"
column.scale = (col_size[0]/2, col_size[1]/2, col_size[2]/2)  # Cube default 2x2x2
bpy.ops.rigidbody.object_add()
column.rigid_body.type = 'PASSIVE'
column.rigid_body.collision_shape = 'BOX'

# 2. Create Main Beam
bpy.ops.mesh.primitive_cube_add(size=1.0, location=beam_loc)
beam = bpy.context.active_object
beam.name = "MainBeam"
beam.scale = (beam_dim[0]/2, beam_dim[1]/2, beam_dim[2]/2)
bpy.ops.rigidbody.object_add()
beam.rigid_body.type = 'PASSIVE'
beam.rigid_body.collision_shape = 'BOX'

# 3. Create Diagonal Brace
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0,0,0))
brace = bpy.context.active_object
brace.name = "DiagonalBrace"
brace.scale = (brace_dim[0]/2, brace_dim[1]/2, brace_dim[2]/2)

# Position and rotate brace between start and end points
start_vec = Vector(brace_start)
end_vec = Vector(brace_end)
center = (start_vec + end_vec) / 2
direction = (end_vec - start_vec).normalized()

brace.location = center
# Align object's X axis with direction vector
up = Vector((0,0,1))
angle = direction.angle(up)
axis = up.cross(direction).normalized()
if axis.length < 0.001:
    axis = Vector((1,0,0))
brace.rotation_mode = 'AXIS_ANGLE'
brace.rotation_axis_angle = (angle, axis.x, axis.y, axis.z)

bpy.ops.rigidbody.object_add()
brace.rigid_body.type = 'PASSIVE'
brace.rigid_body.collision_shape = 'BOX'

# 4. Create Load Mass
bpy.ops.mesh.primitive_cube_add(size=1.0, location=mass_loc)
mass = bpy.context.active_object
mass.name = "LoadMass"
mass.scale = (mass_dim[0]/2, mass_dim[1]/2, mass_dim[2]/2)
bpy.ops.rigidbody.object_add()
mass.rigid_body.type = 'ACTIVE'
mass.rigid_body.mass = mass_value
mass.rigid_body.collision_shape = 'BOX'

# 5. Create Fixed Constraints
def add_fixed_constraint(obj_a, obj_b):
    bpy.context.view_layer.objects.active = obj_a
    bpy.ops.rigidbody.constraint_add()
    const = obj_a.rigid_body.constraints[-1]
    const.type = 'FIXED'
    const.object1 = obj_a
    const.object2 = obj_b

# Column to Beam (at supported end)
add_fixed_constraint(column, beam)

# Column to Brace (at lower connection)
add_fixed_constraint(column, brace)

# Beam to Brace (at upper connection)
add_fixed_constraint(beam, brace)

# Beam to Mass (load attachment)
add_fixed_constraint(beam, mass)

# 6. Setup Physics World
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 50
bpy.context.scene.frame_end = 100  # Simulation duration

# 7. Verification Setup
# Add empty at beam free end to track deflection
bpy.ops.object.empty_add(type='PLAIN_AXES', location=(4.0, 0.0, 3.15))
marker = bpy.context.active_object
marker.name = "DeflectionMarker"
marker.parent = beam  # Move with beam if it deflects (though rigid)

print("Structure created. Run simulation with:")
print("bpy.ops.ptcache.bake_all(bake=True)")
print(f"Deflection marker at: {marker.location}")
print(f"Initial Z: {marker.location.z}")
print(f"Maximum allowed deflection: {0.05}")