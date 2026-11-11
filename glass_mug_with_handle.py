import bpy
import math
from mathutils import Vector

# Удаляем все объекты без bpy.ops, поэтому скрипт работает и из Edit Mode
for obj in list(bpy.data.objects):
    bpy.data.objects.remove(obj, do_unlink=True)

# -------------------------
# Корпус кружки (полая форма)
# -------------------------
profile = [
    (0.00, 0.08), (0.28, 0.08), (0.34, 0.10),
    (0.37, 0.16), (0.39, 0.35), (0.43, 0.75),
    (0.47, 1.15), (0.49, 1.48), (0.49, 1.53),
    (0.455, 1.53), (0.455, 1.48), (0.44, 1.15),
    (0.40, 0.75), (0.36, 0.35), (0.33, 0.19),
    (0.29, 0.15), (0.00, 0.15)
]
segments = 96
verts, faces = [], []

for radius, z in profile:
    for i in range(segments):
        angle = 2 * math.pi * i / segments
        verts.append((radius * math.cos(angle), radius * math.sin(angle), z))

for j in range(len(profile) - 1):
    for i in range(segments):
        a = j * segments + i
        b = j * segments + (i + 1) % segments
        c = (j + 1) * segments + (i + 1) % segments
        d = (j + 1) * segments + i
        faces.append((a, b, c, d))

mesh = bpy.data.meshes.new("MugBodyMesh")
mesh.from_pydata(verts, [], faces)
mesh.update()

mug = bpy.data.objects.new("Glass Mug - Body", mesh)
bpy.context.collection.objects.link(mug)

for poly in mesh.polygons:
    poly.use_smooth = True

bevel = mug.modifiers.new("Soft Edges", 'BEVEL')
bevel.width = 0.006
bevel.segments = 3

# -------------------------
# Ручка: гладкое кольцо сбоку
# -------------------------
bpy.ops.mesh.primitive_torus_add(
    major_segments=64,
    minor_segments=20,
    location=(0.58, 0, 0.82),
    major_radius=0.30,
    minor_radius=0.055,
    rotation=(math.radians(90), 0, 0)
)
handle = bpy.context.object
handle.name = "Glass Mug - Handle"

for poly in handle.data.polygons:
    poly.use_smooth = True

# Прозрачный материал для корпуса и ручки
glass_mat = bpy.data.materials.new("Transparent Glass")
glass_mat.diffuse_color = (0.72, 0.90, 1.0, 0.28)
glass_mat.use_nodes = True
nodes = glass_mat.node_tree.nodes
nodes.clear()
output = nodes.new("ShaderNodeOutputMaterial")
glass_shader = nodes.new("ShaderNodeBsdfGlass")
glass_shader.inputs["Color"].default_value = (0.82, 0.94, 1.0, 1.0)
glass_shader.inputs["Roughness"].default_value = 0.035
glass_shader.inputs["IOR"].default_value = 1.46
glass_mat.node_tree.links.new(glass_shader.outputs["BSDF"], output.inputs["Surface"])

mug.data.materials.append(glass_mat)
handle.data.materials.append(glass_mat)

# Пол для красивого вида
bpy.ops.mesh.primitive_plane_add(size=200, location=(0, 0, 0))
floor = bpy.context.object
floor.name = "Studio Floor"
floor_mat = bpy.data.materials.new("Matte Gray Floor")
floor_mat.diffuse_color = (0.22, 0.25, 0.29, 1)
floor_mat.use_nodes = True
floor_bsdf = floor_mat.node_tree.nodes.get("Principled BSDF")
floor_bsdf.inputs["Base Color"].default_value = (0.22, 0.25, 0.29, 1)
floor_bsdf.inputs["Roughness"].default_value = 0.75
floor.data.materials.append(floor_mat)

# Освещение
def add_area_light(name, location, power, size, color):
    bpy.ops.object.light_add(type='AREA', location=location)
    light = bpy.context.object
    light.name = name
    light.data.energy = power
    light.data.shape = 'DISK'
    light.data.size = size
    light.data.color = color
    direction = Vector((0, 0, 0.8)) - light.location
    light.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()

add_area_light("Softbox Left", (-3.5, -2.5, 4), 500, 3, (0.78, 0.88, 1))
add_area_light("Softbox Right", (3, 1, 3), 650, 2.5, (1, 0.88, 0.72))
add_area_light("Rim Light", (0, 2.5, 3.5), 800, 2, (0.75, 0.88, 1))

# Камера
bpy.ops.object.camera_add(location=(3.3, -5.5, 2.7))
camera = bpy.context.object
camera.name = "Mug Camera"
target = Vector((0.20, 0, 0.80))
camera.rotation_euler = (target - camera.location).to_track_quat('-Z', 'Y').to_euler()
camera.data.type = 'ORTHO'
camera.data.ortho_scale = 3.2
bpy.context.scene.camera = camera

# Скрипт завершён: кружка и ручка созданы.

print("Готово! Создана стеклянная кружка с ручкой. Нажми Ctrl+Shift+S и сохрани файл .blend.")
