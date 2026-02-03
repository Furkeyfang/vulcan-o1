import bpy
import math

# 1. Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# 2. Parameters from summary
deck_dim = (14.0, 4.0, 0.5)
deck_loc = (0.0, 0.0, 0.5)
arch_radius = 6.0
arch_thickness = 0.3
arch_y_length = 4.0
left_arch_center = (-5.0, 0.0, -5.75)
right_arch_center = (5.0, 0.0, -5.75)
load_mass_kg = 700.0
load_dim = (1.0, 1.0, 1.0)
load_loc = (0.0, 0.0, 1.25)
constraint_offset_y = 1.8

# 3. Create Bridge Deck (flat plate)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=deck_loc)
deck = bpy.context.active_object
deck.name = "BridgeDeck"
deck.scale = (deck_dim[0]/2, deck_dim[1]/2, deck_dim[2]/2)  # Blender cube is 2x2x2 default
bpy.ops.rigidbody.object_add()
deck.rigid_body.type = 'PASSIVE'
deck.rigid_body.mass = 500.0  # reasonable mass for deck

# 4. Function to create one curved arch support (semi-cylinder shell)
def create_arch_support(name, center_loc):
    # Create a cylinder, then cut to semi-cylinder
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=32,
        radius=arch_radius,
        depth=arch_y_length,
        location=center_loc
    )
    arch = bpy.context.active_object
    arch.name = name
    
    # Enter edit mode to cut cylinder in half (semi-cylindrical)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    # Bisect along XZ plane, keep +Y half (adjust based on orientation)
    bpy.ops.mesh.bisect(
        plane_co=(center_loc[0], center_loc[1], center_loc[2]),
        plane_no=(0.0, 1.0, 0.0),
        clear_inner=True,
        clear_outer=False
    )
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # Add Solidify modifier to give thickness (shell)
    bpy.ops.object.modifier_add(type='SOLIDIFY')
    arch.modifiers["Solidify"].thickness = arch_thickness
    arch.modifiers["Solidify"].offset = 0.0
    bpy.ops.object.modifier_apply(modifier="Solidify")
    
    # Rotate 90° around X so arch curves upward (cylinder default is vertical)
    arch.rotation_euler = (math.radians(90.0), 0.0, 0.0)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
    
    # Add rigid body
    bpy.ops.rigidbody.object_add()
    arch.rigid_body.type = 'PASSIVE'
    arch.rigid_body.mass = 300.0
    return arch

# 5. Create both arches
left_arch = create_arch_support("LeftArch", left_arch_center)
right_arch = create_arch_support("RightArch", right_arch_center)

# 6. Create Load Block
bpy.ops.mesh.primitive_cube_add(size=1.0, location=load_loc)
load_block = bpy.context.active_object
load_block.name = "LoadBlock"
load_block.scale = (load_dim[0]/2, load_dim[1]/2, load_dim[2]/2)
bpy.ops.rigidbody.object_add()
load_block.rigid_body.type = 'ACTIVE'
load_block.rigid_body.mass = load_mass_kg

# 7. Create Fixed Constraints at deck-arch contact points
def create_fixed_constraint(name, obj_a, obj_b, location):
    # Create empty as constraint anchor
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=location)
    empty = bpy.context.active_object
    empty.name = name
    empty.empty_display_size = 0.5
    
    # Add rigid body constraint
    bpy.ops.rigidbody.constraint_add()
    constraint = empty.rigid_body_constraint
    constraint.type = 'FIXED'
    constraint.object1 = obj_a
    constraint.object2 = obj_b

# Contact points: at each arch, two points along Y-direction
contact_points = [
    ("Constraint_Left_Front", deck, left_arch, (-5.0, -constraint_offset_y, 0.25)),
    ("Constraint_Left_Back", deck, left_arch, (-5.0, constraint_offset_y, 0.25)),
    ("Constraint_Right_Front", deck, right_arch, (5.0, -constraint_offset_y, 0.25)),
    ("Constraint_Right_Back", deck, right_arch, (5.0, constraint_offset_y, 0.25))
]

for name, obj_a, obj_b, loc in contact_points:
    create_fixed_constraint(name, obj_a, obj_b, loc)

# 8. Setup physics world
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 50
bpy.context.scene.frame_end = 100

print("Bridge assembly complete. Ready for simulation.")