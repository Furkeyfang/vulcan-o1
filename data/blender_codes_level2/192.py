import bpy
import math
from mathutils import Matrix, Vector

# Clear scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Extract variables from summary
base_dim = (10.0, 0.5, 0.5)
base_loc = (0.0, 0.0, 0.0)
leg_nom_len = 10.2
leg_act_len = 11.1803398875
leg_scale = leg_act_len / leg_nom_len
leg_dim = (leg_nom_len, 0.5, 0.5)
leg1_start = Vector((-5.0, 0.0, 0.0))
leg2_start = Vector((5.0, 0.0, 0.0))
top_vertex = Vector((0.0, 0.0, 10.0))
crossbeam_dim = (9.0, 0.5, 0.5)
crossbeam_loc = (0.0, 0.0, 5.0)
pipe_dim = (2.0, 0.3, 0.3)
pipe_loc = (0.0, 0.0, 10.0)
steel_density = 7850.0
load_mass = 1200.0
joint_offset = 0.25

# Enable rigid body physics
bpy.context.scene.use_gravity = True
bpy.context.scene.gravity = (0.0, 0.0, -9.81)

def create_beam(name, dim, location, rotation, rb_type='ACTIVE'):
    """Create a beam with physics"""
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = (dim[0]/2.0, dim[1]/2.0, dim[2]/2.0)
    obj.rotation_euler = rotation
    
    # Apply scale and rotation
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    
    # Add rigid body
    bpy.ops.rigidbody.object_add()
    obj.rigid_body.type = rb_type
    obj.rigid_body.collision_shape = 'BOX'
    obj.rigid_body.mass = dim[0] * dim[1] * dim[2] * steel_density
    obj.rigid_body.friction = 0.5
    obj.rigid_body.restitution = 0.1
    
    return obj

def create_fixed_constraint(obj_a, obj_b, pivot):
    """Create fixed constraint between two objects"""
    # Create empty at pivot point
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=pivot)
    empty = bpy.context.active_object
    empty.name = f"Constraint_{obj_a.name}_{obj_b.name}"
    
    # Add rigid body constraint
    bpy.ops.rigidbody.constraint_add()
    constraint = empty.rigid_body_constraint
    constraint.type = 'FIXED'
    constraint.object1 = obj_a
    constraint.object2 = obj_b
    
    return empty

# 1. Create base (passive - fixed to ground)
base = create_beam("Base", base_dim, base_loc, (0.0, 0.0, 0.0), 'PASSIVE')

# 2. Create legs (active)
# Leg1: from (-5,0,0) to (0,0,10)
leg1_dir = (top_vertex - leg1_start).normalized()
leg1_rot = Vector((1.0, 0.0, 0.0)).rotation_difference(leg1_dir).to_euler()
leg1_loc = leg1_start + (top_vertex - leg1_start)/2.0 + Vector((0.0, joint_offset, 0.0))
leg1 = create_beam("Leg1", leg_dim, leg1_loc, leg1_rot)
leg1.scale.x *= leg_scale
bpy.ops.object.transform_apply(scale=True)

# Leg2: from (5,0,0) to (0,0,10)
leg2_dir = (top_vertex - leg2_start).normalized()
leg2_rot = Vector((1.0, 0.0, 0.0)).rotation_difference(leg2_dir).to_euler()
leg2_loc = leg2_start + (top_vertex - leg2_start)/2.0 + Vector((0.0, -joint_offset, 0.0))
leg2 = create_beam("Leg2", leg_dim, leg2_loc, leg2_rot)
leg2.scale.x *= leg_scale
bpy.ops.object.transform_apply(scale=True)

# 3. Create crossbeam at Z=5
crossbeam = create_beam("Crossbeam", crossbeam_dim, crossbeam_loc, (0.0, 0.0, 0.0))

# 4. Create pipe holder
pipe = create_beam("PipeHolder", pipe_dim, pipe_loc, (0.0, 0.0, 0.0))

# 5. Create joints with fixed constraints
# Base-Leg1 joint
create_fixed_constraint(base, leg1, leg1_start + Vector((0.0, joint_offset/2.0, 0.0)))
# Base-Leg2 joint
create_fixed_constraint(base, leg2, leg2_start + Vector((0.0, -joint_offset/2.0, 0.0)))
# Leg1-Top joint (offset to avoid collision)
create_fixed_constraint(leg1, pipe, top_vertex + Vector((0.0, joint_offset, 0.0)))
# Leg2-Top joint
create_fixed_constraint(leg2, pipe, top_vertex + Vector((0.0, -joint_offset, 0.0)))

# Crossbeam-Leg1 joint (at Z=5, X=-2.5)
cross_leg1_pos = Vector((-2.5, 0.0, 5.0)) + Vector((0.0, joint_offset, 0.0))
create_fixed_constraint(crossbeam, leg1, cross_leg1_pos)

# Crossbeam-Leg2 joint (at Z=5, X=2.5)
cross_leg2_pos = Vector((2.5, 0.0, 5.0)) + Vector((0.0, -joint_offset, 0.0))
create_fixed_constraint(crossbeam, leg2, cross_leg2_pos)

# 6. Create load (1200kg mass attached to pipe holder)
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.2, location=pipe_loc + Vector((0.0, 0.0, -0.5)))
load = bpy.context.active_object
load.name = "Load"
bpy.ops.rigidbody.object_add()
load.rigid_body.type = 'ACTIVE'
load.rigid_body.mass = load_mass
load.rigid_body.collision_shape = 'SPHERE'

# Attach load to pipe holder
create_fixed_constraint(pipe, load, pipe_loc + Vector((0.0, 0.0, -0.3)))

# 7. Configure simulation
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 50
bpy.context.scene.frame_end = 300

# 8. Verification setup (store initial position)
pipe["initial_z"] = pipe_loc.z

print("Structure built. Total base mass:", base.rigid_body.mass, "kg")
print("Load applied:", load_mass, "kg")
print("Steel density:", steel_density, "kg/m³")