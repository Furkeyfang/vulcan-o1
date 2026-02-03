import bpy
import mathutils

# Clear existing scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Extract parameters from summary
# Dimensions
wt = 0.5  # wall_thickness
ww = 1.0  # wall_width
wh = 2.0  # wall_height
wl = 3.0  # walkway_length
wwi = 1.0  # walkway_width
wth = 0.1  # walkway_thickness
ps = 0.05  # post_size
ph = 1.0   # post_height
rl = 3.0   # rail_length
rs = 0.05  # rail_size
cs = 0.5   # cube_size

# Positions
wall_center = mathutils.Vector((-0.25, 0.0, 1.0))
walkway_center = mathutils.Vector((1.5, 0.0, 1.95))
post_left_center = mathutils.Vector((3.0, -0.475, 2.5))
post_right_center = mathutils.Vector((3.0, 0.475, 2.5))
rail_center = mathutils.Vector((1.5, 0.0, 2.975))
load_center = mathutils.Vector((2.75, 0.0, 2.25))

# Mass
load_mass = 400.0

# Enable rigid body physics
bpy.context.scene.use_gravity = True

# 1. Create Support Wall
bpy.ops.mesh.primitive_cube_add(size=1.0, location=wall_center)
wall = bpy.context.active_object
wall.name = "SupportWall"
wall.scale = (wt, ww, wh)
bpy.ops.rigidbody.object_add()
wall.rigid_body.type = 'PASSIVE'

# 2. Create Walkway Platform
bpy.ops.mesh.primitive_cube_add(size=1.0, location=walkway_center)
walkway = bpy.context.active_object
walkway.name = "Walkway"
walkway.scale = (wl, wwi, wth)
bpy.ops.rigidbody.object_add()
walkway.rigid_body.type = 'PASSIVE'

# 3. Create Fixed Constraint between Wall and Walkway
# First, ensure walkway is selected then add constraint
bpy.context.view_layer.objects.active = walkway
bpy.ops.object.constraint_add(type='FIXED')
constraint = walkway.constraints[-1]
constraint.name = "Wall_Attachment"
constraint.target = wall

# 4. Create Railing Posts (parented to walkway for simplicity)
# Left post
bpy.ops.mesh.primitive_cube_add(size=1.0, location=post_left_center)
post_left = bpy.context.active_object
post_left.name = "Post_Left"
post_left.scale = (ps, ps, ph)
post_left.parent = walkway

# Right post
bpy.ops.mesh.primitive_cube_add(size=1.0, location=post_right_center)
post_right = bpy.context.active_object
post_right.name = "Post_Right"
post_right.scale = (ps, ps, ph)
post_right.parent = walkway

# 5. Create Horizontal Rail
bpy.ops.mesh.primitive_cube_add(size=1.0, location=rail_center)
rail = bpy.context.active_object
rail.name = "Handrail"
rail.scale = (rl, rs, rs)
rail.parent = walkway

# Add rigid body to the entire railing system (via walkway parent)
walkway.rigid_body.collision_shape = 'MESH'

# 6. Create Test Load
bpy.ops.mesh.primitive_cube_add(size=1.0, location=load_center)
load = bpy.context.active_object
load.name = "TestLoad"
load.scale = (cs, cs, cs)
bpy.ops.rigidbody.object_add()
load.rigid_body.type = 'ACTIVE'
load.rigid_body.mass = load_mass

# Ensure proper collision margins
for obj in [wall, walkway, load]:
    if obj.rigid_body:
        obj.rigid_body.collision_margin = 0.0

# Set simulation parameters
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 10

print("Cantilever walkway construction complete. Structure is ready for simulation.")