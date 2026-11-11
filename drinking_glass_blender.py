import bpy
import math

# Clear the scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create a hollow drinking glass by revolving a profile around the Z axis
profile = [
    (0.00, 0.08), (0.28, 0.08), (0.34, 0.10),
    (0.37, 0.16), (0.39, 0.35), (0.43, 0.75),
    (0.47, 1.15), (0.49, 1.48), (0.485, 1.53),  # outer rim
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

mesh = bpy.data.meshes.new("GlassMesh")
mesh.from_pydata(verts, [], faces)
mesh.update()
glass = bpy.data.objects.new("Clear Drinking Glass", mesh)
bpy.context.collection.objects.link(glass)

# Smooth shading and a small bevel for realistic highlights
for poly in mesh.polygons:
    poly.use_smooth = True
bevel = glass.modifiers.new("Soft glass edges", 'BEVEL')
bevel.width = 0.008
bevel.segments = 3
solidify = glass.modifiers.new("Glass thickness", 'SOLIDIFY')
solidify.thickness = 0.012
solidify.offset = 0

# Transparent glass material
mat = bpy.data.materials.new("Clear Glass")
mat.use_nodes = True
mat.diffuse_color = (0.82, 0.94, 1.0, 0.22)
nodes = mat.node_tree.nodes
nodes.clear()
out = nodes.new("ShaderNodeOutputMaterial")
glass_bsdf = nodes.new("ShaderNodeBsdfGlass")
glass_bsdf.inputs["Color"].default_value = (0.88, 0.97, 1.0, 1)
glass_bsdf.inputs["Roughness"].default_value = 0.025
glass_bsdf.inputs["IOR"].default_value = 1.46
mat.node_tree.links.new(glass_bsdf.outputs["BSDF"], out.inputs["Surface"])
glass.data.materials.append(mat)

# Ground plane
bpy.ops.mesh.primitive_plane_add(size=200, location=(0, 0, 0))
ground = bpy.context.object
ground.name = "Matte Studio Floor"
floor_mat = bpy.data.materials.new("Warm Light Gray")
floor_mat.diffuse_color = (0.34, 0.37, 0.40, 1)
floor_mat.use_nodes = True
floor_mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.34, 0.37, 0.40, 1)
floor_mat.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.72
ground.data.materials.append(floor_mat)

# Studio lighting
def area_light(name, location, energy, size, color):
    bpy.ops.object.light_add(type='AREA', location=location)
    light = bpy.context.object
    light.name = name
    light.data.energy = energy
    light.data.shape = 'DISK'
    light.data.size = size
    light.data.color = color
    direction = (0 - location[0], 0 - location[1], 0.8 - location[2])
    light.rotation_euler = direction_to_euler(direction)
    return light

def direction_to_euler(direction):
    from mathutils import Vector
    return Vector(direction).to_track_quat('-Z', 'Y').to_euler()

area_light("Large softbox left", (-3.5, -2.5, 4.0), 500, 3.0, (0.78, 0.88, 1.0))
area_light("Softbox right", (3.0, 1.0, 3.0), 650, 2.5, (1.0, 0.88, 0.72))
area_light("Rim light", (0.0, 2.5, 3.5), 800, 2.0, (0.75, 0.88, 1.0))

# Camera
from mathutils import Vector
bpy.ops.object.camera_add(location=(3.2, -5.2, 2.55))
camera = bpy.context.object
camera.name = "Product Camera"
target = Vector((0, 0, 0.78))
camera.rotation_euler = (target - camera.location).to_track_quat('-Z', 'Y').to_euler()
camera.data.type = 'ORTHO'
camera.data.ortho_scale = 3.25
bpy.context.scene.camera = camera

# Render settings
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.samples = 64
scene.render.resolution_x = 900
scene.render.resolution_y = 900
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'
scene.render.filepath = "//glass_render.png"
scene.world.color = (0.12, 0.12, 0.12)

# Select the glass for convenient editing
bpy.ops.object.select_all(action='DESELECT')
glass.select_set(True)
bpy.context.view_layer.objects.active = glass

# Save the Blender project beside this script when run from Blender
bpy.ops.wm.save_as_mainfile(filepath="//drinking_glass.blend")
# Render a preview
bpy.ops.render.render(write_still=True)
