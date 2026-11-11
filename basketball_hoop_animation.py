import bpy
import math
from mathutils import Vector

# ============================================================
# BASKETBALL HOOP + BALL ANIMATION
# Blender 3.6+ / 4.x / 5.x
# Run from Scripting > Open > Run Script (or Alt+P).
# ============================================================

# Delete scene objects directly (works even if Blender was in Edit Mode).
for obj in list(bpy.data.objects):
    bpy.data.objects.remove(obj, do_unlink=True)


# -------------------- MATERIALS --------------------
def make_material(name, color, metallic=0.0, roughness=0.45):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1.0)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (*color, 1.0)
        bsdf.inputs["Metallic"].default_value = metallic
        bsdf.inputs["Roughness"].default_value = roughness
    return mat

mat_ball = make_material("Basketball - Orange Leather", (0.95, 0.20, 0.025), 0.0, 0.34)
mat_seams = make_material("Ball Seams - Dark Rubber", (0.035, 0.018, 0.012), 0.0, 0.65)
mat_rim = make_material("Rim - Red Metal", (0.80, 0.035, 0.018), 0.72, 0.25)
mat_board = make_material("Backboard - Frosted Acrylic", (0.82, 0.90, 0.96), 0.12, 0.22)
mat_white = make_material("Net and Markings - White", (0.92, 0.94, 0.96), 0.0, 0.5)
mat_pole = make_material("Support - Graphite Steel", (0.12, 0.15, 0.19), 0.78, 0.28)
mat_floor = make_material("Court - Warm Wood", (0.42, 0.22, 0.09), 0.0, 0.62)
mat_lines = make_material("Court Lines", (0.94, 0.82, 0.61), 0.0, 0.55)


# -------------------- MESH HELPERS --------------------
def create_mesh_object(name, verts, faces, material=None, smooth=False):
    mesh = bpy.data.meshes.new(name + " Mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    if material:
        obj.data.materials.append(material)
    if smooth:
        for poly in mesh.polygons:
            poly.use_smooth = True
    return obj


def create_box(name, center, dimensions, material):
    x, y, z = (dimensions[0] / 2, dimensions[1] / 2, dimensions[2] / 2)
    cx, cy, cz = center
    verts = [
        (cx-x, cy-y, cz-z), (cx+x, cy-y, cz-z),
        (cx+x, cy+y, cz-z), (cx-x, cy+y, cz-z),
        (cx-x, cy-y, cz+z), (cx+x, cy-y, cz+z),
        (cx+x, cy+y, cz+z), (cx-x, cy+y, cz+z)
    ]
    faces = [
        (0, 3, 2, 1), (4, 5, 6, 7),
        (0, 1, 5, 4), (1, 2, 6, 5),
        (2, 3, 7, 6), (3, 0, 4, 7)
    ]
    obj = create_mesh_object(name, verts, faces, material)
    bevel = obj.modifiers.new("Small Rounded Edges", 'BEVEL')
    bevel.width = 0.025
    bevel.segments = 3
    return obj


def create_vertical_cylinder(name, center, radius, depth, material, segments=48):
    cx, cy, cz = center
    verts = []
    for z in (cz - depth / 2, cz + depth / 2):
        for i in range(segments):
            a = 2 * math.pi * i / segments
            verts.append((cx + radius * math.cos(a), cy + radius * math.sin(a), z))
    faces = []
    for i in range(segments):
        j = (i + 1) % segments
        faces.append((i, j, segments + j, segments + i))
    faces.append(tuple(range(segments - 1, -1, -1)))
    faces.append(tuple(range(segments, 2 * segments)))
    obj = create_mesh_object(name, verts, faces, material, smooth=True)
    return obj


def create_torus(name, center, major_radius, minor_radius, material,
                 major_segments=96, minor_segments=16):
    cx, cy, cz = center
    verts, faces = [], []
    for i in range(major_segments):
        a = 2 * math.pi * i / major_segments
        for j in range(minor_segments):
            b = 2 * math.pi * j / minor_segments
            r = major_radius + minor_radius * math.cos(b)
            verts.append((cx + r * math.cos(a),
                          cy + r * math.sin(a),
                          cz + minor_radius * math.sin(b)))
    for i in range(major_segments):
        for j in range(minor_segments):
            a = i * minor_segments + j
            b = i * minor_segments + (j + 1) % minor_segments
            c = ((i + 1) % major_segments) * minor_segments + (j + 1) % minor_segments
            d = ((i + 1) % major_segments) * minor_segments + j
            faces.append((a, b, c, d))
    return create_mesh_object(name, verts, faces, material, smooth=True)


def create_uv_sphere(name, radius, material, rings=28, segments=48):
    verts, faces = [], []
    for j in range(rings + 1):
        phi = math.pi * j / rings
        for i in range(segments):
            theta = 2 * math.pi * i / segments
            verts.append((radius * math.sin(phi) * math.cos(theta),
                          radius * math.sin(phi) * math.sin(theta),
                          radius * math.cos(phi)))
    for j in range(rings):
        for i in range(segments):
            a = j * segments + i
            b = j * segments + (i + 1) % segments
            c = (j + 1) * segments + (i + 1) % segments
            d = (j + 1) * segments + i
            faces.append((a, b, c, d))
    return create_mesh_object(name, verts, faces, material, smooth=True)


def create_curve_object(name, splines_points, bevel_depth, material, cyclic_flags=None):
    curve = bpy.data.curves.new(name + " Curve", 'CURVE')
    curve.dimensions = '3D'
    curve.resolution_u = 16
    curve.bevel_depth = bevel_depth
    curve.bevel_resolution = 3
    for idx, points in enumerate(splines_points):
        if len(points) < 2:
            continue
        spline = curve.splines.new('POLY')
        spline.points.add(len(points) - 1)
        for p, co in zip(spline.points, points):
            p.co = (co[0], co[1], co[2], 1.0)
        if cyclic_flags and idx < len(cyclic_flags):
            spline.use_cyclic_u = cyclic_flags[idx]
    obj = bpy.data.objects.new(name, curve)
    bpy.context.scene.collection.objects.link(obj)
    if material:
        obj.data.materials.append(material)
    return obj


def create_beam_between(name, start, end, radius, material, segments=24):
    a = Vector(start)
    b = Vector(end)
    axis = (b - a).normalized()
    helper = Vector((0, 0, 1))
    if abs(axis.dot(helper)) > 0.95:
        helper = Vector((1, 0, 0))
    u = axis.cross(helper).normalized()
    v = axis.cross(u).normalized()
    verts = []
    for point in (a, b):
        for i in range(segments):
            angle = 2 * math.pi * i / segments
            pos = point + radius * (math.cos(angle) * u + math.sin(angle) * v)
            verts.append(tuple(pos))
    faces = []
    for i in range(segments):
        j = (i + 1) % segments
        faces.append((i, j, segments + j, segments + i))
    faces.append(tuple(range(segments - 1, -1, -1)))
    faces.append(tuple(range(segments, 2 * segments)))
    return create_mesh_object(name, verts, faces, material, smooth=True)


# -------------------- COURT --------------------
create_box("Basketball Court Floor", (0, 0, -0.12), (18, 16, 0.22), mat_floor)

# A few simple court markings in front of the hoop.
court_lines = [
    [(-5.0, -4.8, 0.005), (5.0, -4.8, 0.005)],
    [(-5.0, -4.8, 0.005), (-5.0, 4.0, 0.005)],
    [(5.0, -4.8, 0.005), (5.0, 4.0, 0.005)],
]
create_curve_object("Court Boundary Lines", court_lines, 0.018, mat_lines)


# -------------------- HOOP AND BACKBOARD --------------------
# Main support pole behind the board.
create_vertical_cylinder("Basket Support Pole", (0, 1.45, 1.78), 0.085, 3.56, mat_pole)

# Backboard: front side faces the camera (negative Y).
board = create_box("Backboard", (0, 0.78, 3.88), (1.85, 0.13, 1.12), mat_board)

# Board target rectangle on its front surface.
target_y = 0.705
target_points = [
    [(-0.31, target_y, 3.56), (0.31, target_y, 3.56),
     (0.31, target_y, 4.16), (-0.31, target_y, 4.16)]
]
create_curve_object("Backboard Target Square", target_points, 0.014, mat_rim, [True])

# Backboard support brackets.
create_beam_between("Upper Board Brace", (0, 1.40, 3.50), (0, 0.80, 4.12), 0.045, mat_pole)
create_beam_between("Lower Board Brace", (0, 1.40, 3.05), (0, 0.80, 3.55), 0.045, mat_pole)

# Hoop ring and its support arm.
rim_z = 3.12
rim_center_y = 0.05
create_torus("Basketball Rim", (0, rim_center_y, rim_z), 0.43, 0.027, mat_rim)
create_beam_between("Rim Mount", (0, 0.73, 3.28), (0, 0.39, rim_z), 0.045, mat_pole)

# Net: twelve gently sloping white cords and a small bottom ring.
net_top_r = 0.375
net_bottom_r = 0.17
net_bottom_z = 2.48
net_top_z = 3.10
net_paths = []
net_count = 12
for i in range(net_count):
    angle1 = 2 * math.pi * i / net_count
    angle2 = 2 * math.pi * (i + 0.5) / net_count
    top = (net_top_r * math.cos(angle1), rim_center_y + net_top_r * math.sin(angle1), net_top_z)
    middle = (0.27 * math.cos(angle2), rim_center_y + 0.27 * math.sin(angle2), 2.78)
    bottom = (net_bottom_r * math.cos(angle1), rim_center_y + net_bottom_r * math.sin(angle1), net_bottom_z)
    net_paths.append([top, middle, bottom])
create_curve_object("White Basketball Net", net_paths, 0.009, mat_white)

bottom_ring_points = []
for i in range(64):
    a = 2 * math.pi * i / 64
    bottom_ring_points.append((net_bottom_r * math.cos(a),
                               rim_center_y + net_bottom_r * math.sin(a),
                               net_bottom_z))
create_curve_object("Net Bottom Ring", [bottom_ring_points], 0.009, mat_white, [True])


# -------------------- BASKETBALL --------------------
ball_radius = 0.235
ball = create_uv_sphere("Basketball", ball_radius, mat_ball)
ball.location = (-2.25, -0.15, 4.75)

# Classic dark curved seams on the ball, built in the ball's local coordinates.
seam_splines = []
samples = 100
# Three great circles in different planes.
for plane in range(3):
    pts = []
    for i in range(samples):
        t = 2 * math.pi * i / samples
        if plane == 0:
            p = (0, ball_radius * math.cos(t), ball_radius * math.sin(t))
        elif plane == 1:
            p = (ball_radius * math.cos(t), 0, ball_radius * math.sin(t))
        else:
            p = (ball_radius * math.cos(t), ball_radius * math.sin(t), 0)
        pts.append(p)
    seam_splines.append(pts)

seams = create_curve_object("Basketball Seams", seam_splines, 0.008, mat_seams, [True, True, True])
seams.parent = ball
seams.location = (0, 0, 0)


# -------------------- BALL ANIMATION --------------------
# The ball arcs toward the hoop, passes through the center, then drops to the floor.
# Keyframes are spaced to make the shot easy to see in the timeline.
animation_keys = [
    (1,   (-2.25, -0.15, 4.75), (0.00, 0.00, 0.00)),
    (22,  (-1.55, -0.12, 4.62), (0.00, 0.65, 0.00)),
    (40,  (-0.78, -0.06, 4.03), (0.00, 1.40, 0.00)),
    (52,  (-0.25,  0.00, 3.42), (0.00, 1.95, 0.00)),
    (58,  ( 0.00,  0.05, 3.10), (0.00, 2.20, 0.00)),
    (66,  ( 0.02,  0.06, 2.55), (0.00, 2.65, 0.00)),
    (80,  ( 0.06,  0.10, 1.45), (0.00, 3.35, 0.00)),
    (91,  ( 0.12,  0.14, ball_radius), (0.00, 3.80, 0.00)),
    (98,  ( 0.12,  0.14, 0.42), (0.00, 4.05, 0.00)),
    (106, ( 0.12,  0.14, ball_radius), (0.00, 4.35, 0.00)),
    (120, ( 0.12,  0.14, ball_radius), (0.00, 4.55, 0.00)),
]
for frame, location, rotation in animation_keys:
    ball.location = location
    ball.rotation_euler = rotation
    ball.keyframe_insert(data_path="location", frame=frame)
    ball.keyframe_insert(data_path="rotation_euler", frame=frame)

# Keep the animated curves smooth in Blender versions exposing classic F-curves.
try:
    action = ball.animation_data.action
    for fcurve in action.fcurves:
        for key in fcurve.keyframe_points:
            key.interpolation = 'BEZIER'
except Exception:
    pass


# -------------------- LIGHTS AND CAMERA --------------------
def add_area_light(name, location, energy, size, color):
    light_data = bpy.data.lights.new(name, 'AREA')
    light_data.energy = energy
    light_data.shape = 'DISK'
    light_data.size = size
    light_data.color = color
    light_obj = bpy.data.objects.new(name, light_data)
    bpy.context.scene.collection.objects.link(light_obj)
    light_obj.location = location
    direction = Vector((0, 0.8, 2.2)) - light_obj.location
    light_obj.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
    return light_obj

add_area_light("Large Softbox", (-4, -5, 7), 950, 5, (1.0, 0.86, 0.72))
add_area_light("Cool Fill", (4, -2, 5), 700, 4, (0.72, 0.84, 1.0))
add_area_light("Back Rim Light", (0, 4, 6), 1100, 3, (1.0, 0.72, 0.52))

camera_data = bpy.data.cameras.new("Basketball Camera")
camera = bpy.data.objects.new("Basketball Camera", camera_data)
bpy.context.scene.collection.objects.link(camera)
camera.location = (4.8, -10.5, 5.0)
look_at = Vector((0, 0.25, 2.25))
camera.rotation_euler = (look_at - camera.location).to_track_quat('-Z', 'Y').to_euler()
camera_data.type = 'ORTHO'
camera_data.ortho_scale = 8.6
bpy.context.scene.camera = camera


# -------------------- SCENE / RENDER SETTINGS --------------------
scene = bpy.context.scene
scene.frame_start = 1
scene.frame_end = 120
scene.render.fps = 30
scene.render.engine = 'BLENDER_EEVEE_NEXT'
scene.render.resolution_x = 1280
scene.render.resolution_y = 720
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'
scene.render.filepath = "//basketball_frame_"

# World background.
world = bpy.data.worlds.new("Basketball Studio World") if not bpy.data.worlds else bpy.data.worlds[0]
scene.world = world
world.use_nodes = True
world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.055, 0.065, 0.085, 1)
world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.45

# Set a useful opening frame and camera view.
scene.frame_set(1)
for obj in bpy.context.selected_objects:
    obj.select_set(False)
ball.select_set(True)
bpy.context.view_layer.objects.active = ball

print("Готово! Созданы баскетбольное кольцо, щит, сетка и мяч с анимацией попадания.")
print("Нажми Space, чтобы посмотреть анимацию. Ctrl+Shift+S — сохранить .blend.")
print("Для рендера анимации нажми Ctrl+F12 (будут сохранены PNG-кадры).")
