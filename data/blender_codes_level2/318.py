import bpy
import math
from mathutils import Vector, Matrix

# Clear scene
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

# Parameters
span = 12.0
deck_width = 2.0
deck_thickness = 0.5
deck_center = Vector((0.0, 0.0, 0.75))
deck_bottom_z = 0.5
anchor_size = 0.5
anchor_left_center = Vector((-5.75, 0.0, 0.25))
anchor_right_center = Vector((5.75, 0.0, 0.25))
strut_width = 0.2
strut_height = 1.5
strut_x_positions = [-4.5, -2.25, 0.0, 2.25, 4.5]
strut_center_z = -0.25
brace_width = 0.2
brace_nominal_length = 2.0
brace_connections = [(-4.5, -5.75), (-2.25, -5.75), (2.25, 5.75), (4.5, 5.75)]
force_magnitude = -8826.0
force_location = Vector((0.0, 0.0, 0.75))
material_density = 1000.0

# Enable rigid body physics
if bpy.context.scene.rigidbody_world is None:
    bpy.ops.rigidbody.world_add()

# Helper: create cube with rigid body
def create_cube(name, location, scale, rb_type='ACTIVE', mass=None):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = scale
    bpy.ops.object.transform_apply(scale=True)
    bpy.ops.rigidbody.object_add()
    obj.rigid_body.type = rb_type
    if mass is not None:
        obj.rigid_body.mass = mass
    else:
        # Calculate mass from volume and density
        volume = scale.x * scale.y * scale.z * 8  # default cube volume = 8 when scale=1
        obj.rigid_body.mass = volume * material_density
    return obj

# Helper: create fixed constraint between two objects
def create_fixed_constraint(name, obj_a, obj_b):
    # Create empty at midpoint for constraint object
    midpoint = (obj_a.location + obj_b.location) / 2
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=midpoint)
    empty = bpy.context.active_object
    empty.name = name
    bpy.ops.rigidbody.constraint_add()
    empty.rigid_body_constraint.type = 'FIXED'
    empty.rigid_body_constraint.object1 = obj_a
    empty.rigid_body_constraint.object2 = obj_b

# 1. Create deck
deck_scale = Vector((span, deck_width, deck_thickness))
deck = create_cube("Deck", deck_center, deck_scale, 'ACTIVE')

# 2. Create ground anchors
anchor_scale = Vector((anchor_size, anchor_size, anchor_size))
anchor_left = create_cube("Anchor_Left", anchor_left_center, anchor_scale, 'PASSIVE')
anchor_right = create_cube("Anchor_Right", anchor_right_center, anchor_scale, 'PASSIVE')

# 3. Create vertical struts
struts = []
for i, x in enumerate(strut_x_positions):
    location = Vector((x, 0.0, strut_center_z))
    scale = Vector((strut_width, strut_width, strut_height))
    strut = create_cube(f"Strut_{i}", location, scale, 'PASSIVE')
    struts.append(strut)
    # Fixed constraint between deck and strut
    create_fixed_constraint(f"Deck_Strut_{i}", deck, strut)

# 4. Create diagonal braces
for i, (deck_x, anchor_x) in enumerate(brace_connections):
    # Determine anchor object
    if anchor_x < 0:
        anchor_obj = anchor_left
        anchor_pos = anchor_left_center
    else:
        anchor_obj = anchor_right
        anchor_pos = anchor_right_center
    deck_attach = Vector((deck_x, 0.0, deck_bottom_z))
    # Vector from deck to anchor
    vec = anchor_pos - deck_attach
    length = vec.length
    # Midpoint
    mid = (deck_attach + anchor_pos) / 2
    # Orientation: rotate local Z to align with vec
    # Default cube's local Z is up (0,0,1). We want to rotate that to vec.normalized()
    z_up = Vector((0,0,1))
    axis = z_up.cross(vec.normalized())
    angle = z_up.angle(vec.normalized())
    # Create cube
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=mid)
    brace = bpy.context.active_object
    brace.name = f"Brace_{i}"
    # Scale: thickness in X,Y, length in Z (but note: after rotation, local Z is along vec)
    brace.scale = Vector((brace_width, brace_width, length/2))  # default cube length=2
    bpy.ops.object.transform_apply(scale=True)
    if axis.length > 0:
        brace.rotation_mode = 'AXIS_ANGLE'
        brace.rotation_axis_angle = (angle, axis.normalized())
    # Add rigid body
    bpy.ops.rigidbody.object_add()
    brace.rigid_body.type = 'ACTIVE'
    # Fixed constraints: brace to deck and brace to anchor
    create_fixed_constraint(f"Brace_Deck_{i}", brace, deck)
    create_fixed_constraint(f"Brace_Anchor_{i}", brace, anchor_obj)

# 5. Apply central downward force as a force field
bpy.ops.object.effector_add(type='FORCE', location=force_location)
force_field = bpy.context.active_object
force_field.name = "Central_Load"
force_field.field.strength = force_magnitude
force_field.field.use_global = False  # local Z direction
force_field.field.direction = 'Z'     # negative Z is downward
# Limit force to affect only the deck (by layer? but in headless we use collections)
# Since we cannot use UI, we'll assign the deck to a separate collection and set force field to affect only that collection.
# Create new collection
load_collection = bpy.data.collections.new("Load_Affected")
bpy.context.scene.collection.children.link(load_collection)
# Move deck to that collection
load_collection.objects.link(deck)
bpy.context.scene.collection.objects.unlink(deck)  # remove from master collection
# Set force field to affect only that collection
force_field.field.collection = load_collection

# 6. Set gravity and simulation steps
bpy.context.scene.rigidbody_world.gravity.z = -9.81
bpy.context.scene.frame_end = 250  # simulate 250 frames

print("Bridge construction complete. Run simulation with blender --background --python script.py")