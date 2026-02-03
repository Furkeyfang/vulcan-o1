import bpy
import mathutils
from math import sqrt, radians

# ========== PARAMETERS ==========
bay_height = 3.0
rigid_bay_dim = (2.0, 2.0, 3.0)
flexible_vert_dim = (1.0, 1.0, 3.0)
cross_section_offset = 1.0
diagonal_length = sqrt(2**2 + 2**2 + 3**2)  # ≈4.123
load_plate_dim = (3.0, 3.0, 0.5)
load_mass = 1500.0
base_z_positions = [0.0, 3.0, 6.0, 9.0, 12.0, 15.0]
hinge_limits = (radians(-5.0), radians(5.0))  # ±5°
rigid_body_damping = 0.5
load_plate_z = 18.25

# ========== SCENE SETUP ==========
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

# Set physics scene properties
scene = bpy.context.scene
scene.rigidbody_world.steps_per_second = 60
scene.rigidbody_world.solver_iterations = 50

# ========== CREATION FUNCTIONS ==========
def create_cube(name, location, dimensions, rigid_body_type='ACTIVE', mass=10.0):
    """Create cube with rigid body physics"""
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = (dimensions[0]/2, dimensions[1]/2, dimensions[2]/2)  # Blender cube size=2
    
    bpy.ops.rigidbody.object_add()
    obj.rigid_body.type = rigid_body_type
    obj.rigid_body.mass = mass
    obj.rigid_body.linear_damping = rigid_body_damping
    obj.rigid_body.angular_damping = rigid_body_damping
    return obj

def create_diagonal_brace(name, start_point, end_point, dim_z=1.0):
    """Create diagonal cross-brace between two points"""
    # Calculate center and orientation
    center = ((start_point[0] + end_point[0])/2,
              (start_point[1] + end_point[1])/2,
              (start_point[2] + end_point[2])/2)
    
    direction = mathutils.Vector(end_point) - mathutils.Vector(start_point)
    length = direction.length
    
    # Create rotated cube
    bpy.ops.mesh.primitive_cube_add(size=1, location=center)
    obj = bpy.context.active_object
    obj.name = name
    
    # Scale: thin cross-section (1x1) with proper length
    obj.scale = (0.5, 0.5, length/2)  # 1x1 cross-section, length along Z
    
    # Rotate to align with direction vector
    if direction.length > 0:
        z_axis = mathutils.Vector((0, 0, 1))
        rot_quat = z_axis.rotation_difference(direction)
        obj.rotation_euler = rot_quat.to_euler()
    
    # Add rigid body
    bpy.ops.rigidbody.object_add()
    obj.rigid_body.linear_damping = rigid_body_damping
    obj.rigid_body.angular_damping = rigid_body_damping
    return obj

def create_fixed_constraint(obj_a, obj_b):
    """Create fixed constraint between two objects"""
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=obj_a.location)
    empty = bpy.context.active_object
    empty.name = f"Constraint_{obj_a.name}_{obj_b.name}"
    
    bpy.ops.rigidbody.constraint_add()
    empty.rigid_body_constraint.type = 'FIXED'
    empty.rigid_body_constraint.object1 = obj_a
    empty.rigid_body_constraint.object2 = obj_b

def create_hinge_constraint(obj_a, obj_b, location, axis='Z'):
    """Create hinge constraint at specified location"""
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=location)
    empty = bpy.context.active_object
    empty.name = f"Hinge_{obj_a.name}_{obj_b.name}"
    
    bpy.ops.rigidbody.constraint_add()
    empty.rigid_body_constraint.type = 'HINGE'
    empty.rigid_body_constraint.object1 = obj_a
    empty.rigid_body_constraint.object2 = obj_b
    empty.rigid_body_constraint.use_limit_ang_z = True
    empty.rigid_body_constraint.limit_ang_z_lower = hinge_limits[0]
    empty.rigid_body_constraint.limit_ang_z_upper = hinge_limits[1]

# ========== BUILD STRUCTURE ==========
objects_by_bay = {}
flexible_verticals = {}  # bay_index: [NW, NE, SW, SE]

# Create bays
for i, base_z in enumerate(base_z_positions):
    bay_index = i + 1
    center_z = base_z + bay_height/2
    
    if bay_index in [1, 3, 5]:  # Rigid bays
        rigid = create_cube(
            f"RigidBay{bay_index}",
            (0, 0, center_z),
            rigid_bay_dim,
            mass=100.0  # Heavy for stability
        )
        objects_by_bay[bay_index] = [rigid]
        
        # First bay should be passive (fixed to ground)
        if bay_index == 1:
            rigid.rigid_body.type = 'PASSIVE'
    
    else:  # Flexible bays (2, 4, 6)
        # Four vertical members
        verticals = []
        positions = [
            (-cross_section_offset, -cross_section_offset, center_z),  # SW
            (-cross_section_offset, cross_section_offset, center_z),   # NW
            (cross_section_offset, cross_section_offset, center_z),    # NE
            (cross_section_offset, -cross_section_offset, center_z),   # SE
        ]
        
        for j, pos in enumerate(positions):
            vert = create_cube(
                f"FlexBay{bay_index}_Vert{j}",
                pos,
                flexible_vert_dim,
                mass=5.0  # Lighter for flexibility
            )
            verticals.append(vert)
        
        # Two diagonal cross-braces
        # SW to NE diagonal
        diag1_start = (-cross_section_offset, -cross_section_offset, base_z)
        diag1_end = (cross_section_offset, cross_section_offset, base_z + bay_height)
        diag1 = create_diagonal_brace(
            f"FlexBay{bay_index}_Diag1",
            diag1_start,
            diag1_end,
            dim_z=1.0
        )
        diag1.rigid_body.mass = 3.0
        
        # NW to SE diagonal
        diag2_start = (-cross_section_offset, cross_section_offset, base_z)
        diag2_end = (cross_section_offset, -cross_section_offset, base_z + bay_height)
        diag2 = create_diagonal_brace(
            f"FlexBay{bay_index}_Diag2",
            diag2_start,
            diag2_end,
            dim_z=1.0
        )
        diag2.rigid_body.mass = 3.0
        
        objects_by_bay[bay_index] = verticals + [diag1, diag2]
        flexible_verticals[bay_index] = verticals

# ========== CREATE CONSTRAINTS ==========
# Inter-bay fixed constraints
for bay in range(1, 6):  # Connect bay N to bay N+1
    current_bay = objects_by_bay[bay]
    next_bay = objects_by_bay[bay + 1]
    
    if bay in [1, 3, 5]:  # Current is rigid
        rigid_cube = current_bay[0]
        if bay + 1 in flexible_verticals:  # Next is flexible
            for vert in flexible_verticals[bay + 1]:
                create_fixed_constraint(rigid_cube, vert)
    else:  # Current is flexible
        if bay + 1 in [1, 3, 5]:  # Next is rigid
            rigid_cube = next_bay[0]
            for vert in flexible_verticals[bay]:
                create_fixed_constraint(vert, rigid_cube)

# Intra-bay hinge constraints for flexible bays
for bay_index in [2, 4, 6]:
    verticals = flexible_verticals[bay_index]
    base_z = base_z_positions[bay_index - 1]
    
    # Connect verticals at top and bottom corners
    # Bottom corners
    create_hinge_constraint(verticals[0], verticals[1],  # SW-NW
                           (-cross_section_offset, 0, base_z))
    create_hinge_constraint(verticals[1], verticals[2],  # NW-NE
                           (0, cross_section_offset, base_z))
    create_hinge_constraint(verticals[2], verticals[3],  # NE-SE
                           (cross_section_offset, 0, base_z))
    create_hinge_constraint(verticals[3], verticals[0],  # SE-SW
                           (0, -cross_section_offset, base_z))
    
    # Top corners
    top_z = base_z + bay_height
    create_hinge_constraint(verticals[0], verticals[1],  # SW-NW
                           (-cross_section_offset, 0, top_z))
    create_hinge_constraint(verticals[1], verticals[2],  # NW-NE
                           (0, cross_section_offset, top_z))
    create_hinge_constraint(verticals[2], verticals[3],  # NE-SE
                           (cross_section_offset, 0, top_z))
    create_hinge_constraint(verticals[3], verticals[0],  # SE-SW
                           (0, -cross_section_offset, top_z))

# ========== LOAD PLATE ==========
load_plate = create_cube(
    "LoadPlate",
    (0, 0, load_plate_z),
    load_plate_dim,
    mass=load_mass
)

# Connect load plate to top flexible bay (bay6)
top_verticals = flexible_verticals[6]
for vert in top_verticals:
    create_fixed_constraint(vert, load_plate)

# ========== FINAL SETUP ==========
# Ensure all objects have collision shapes
for obj in bpy.data.objects:
    if obj.rigid_body:
        obj.rigid_body.collision_shape = 'BOX'

print("Structure built. Run simulation for 100 frames to observe deflection.")