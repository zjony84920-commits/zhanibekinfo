import bpy
import math
from mathutils import Vector

# Очистка сцены
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Профиль полого стакана: (радиус, высота)
profile = [
    (0.00, 0.08), (0.26, 0.08), (0.32, 0.10),
    (0.36, 0.16), (0.38, 0.35), (0.42, 0.75),
    (0.46, 1.15), (0.48, 1.48), (0.48, 1.52),
    (0.45, 1.52), (0.45, 1.48), (0.43, 1.15),
    (0.39, 0.75), (0.35, 0.35), (0.32, 0.19),
    (0.28, 0.15), (0.00, 0.15)
]

segments = 96
verts = []
faces = []

for radius, z in profile:
    for i in range(segments):
        angle = 2.0 * math.pi * i / segments
        verts.append((radius * math.cos(angle), radius * math.sin(angle), z))

for j in range(len(profile) - 1):
    for i in range(segments):
        a = j * segments + i
        b = j * segments + (i + 1) % segments
        c = (j + 1) * segments + (i + 1) % segments
        d = (j + 1) * segments + i
        faces.append((a, b, c, d))

mesh = bpy.data.meshes.new("GlassMesh")
mesh.from_pydata(verts, [], faces)
mesh.update()

glass = bpy.data.objects.new("Drinking Glass", mesh)
bpy.context.collection.objects.link(glass)

for polygon in mesh.polygons:
    polygon.use_smooth = True

bevel = glass.modifiers.new("Rounded Edges", 'BEVEL')
bevel.width = 0.006
bevel.segments = 3

# Стеклянный материал
material = bpy.data.materials.new("Clear Glass")
material.use_nodes = True
material.diffuse_color = (0.75, 0.90, 1.0, 0.25)

nodes = material.node_tree.nodes
nodes.clear()
output = nodes.new("ShaderNodeOutputMaterial")
glass_shader = nodes.new("ShaderNodeBsdfGlass")
glass_shader.inputs["Color"].default_value = (0.82, 0.94, 1.0, 1.0)
glass_shader.inputs["Roughness"].default_value = 0.03
glass_shader.inputs["IOR"].default_value = 1.46
material.node_tree.links.new(glass_shader.outputs["BSDF"], output.inputs["Surface"])
glass.data.materials.append(material)

# Пол
bpy.ops.mesh.primitive_plane_add(size=200, location=(0, 0, 0))
floor = bpy.context.object
floor.name = "Studio Floor"

floor_material = bpy.data.materials.new("Floor Material")
floor_material.diffuse_color = (0.22, 0.25, 0.29, 1.0)
floor_material.use_nodes = True
floor_bsdf = floor_material.node_tree.nodes.get("Principled BSDF")
floor_bsdf.inputs["Base Color"].default_value = (0.22, 0.25, 0.29, 1.0)
floor_bsdf.inputs["Roughness"].default_value = 0.75
floor.data.materials.append(floor_material)

# Свет
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

add_area_light("Softbox Left", (-3.5, -2.5, 4.0), 500, 3.0, (0.78, 0.88, 1.0))
add_area_light("Softbox Right", (3.0, 1.0, 3.0), 650, 2.5, (1.0, 0.88, 0.72))
add_area_light("Rim Light", (0.0, 2.5, 3.5), 800, 2.0, (0.75, 0.88, 1.0))

# Камера
bpy.ops.object.camera_add(location=(3.2, -5.2, 2.55))
camera = bpy.context.object
camera.name = "Product Camera"
target = Vector((0, 0, 0.78))
camera.rotation_euler = (target - camera.location).to_track_quat('-Z', 'Y').to_euler()
camera.data.type = 'ORTHO'
camera.data.ortho_scale = 3.25
bpy.context.scene.camera = camera

# Настройки рендера
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.samples = 64
scene.render.resolution_x = 900
scene.render.resolution_y = 900
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'
scene.render.filepath = "//glass_render.png"

# Выбрать стакан
bpy.ops.object.select_all(action='DESELECT')
glass.select_set(True)
bpy.context.view_layer.objects.active = glass

print("Стакан создан! Сохраните проект через File > Save As.")
