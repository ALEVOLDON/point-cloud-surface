import math
import os
import sys

import bpy


def parse_args():
    argv = sys.argv
    if "--" not in argv:
        return {
            "blend_path": os.path.abspath("point_cloud_blob.blend"),
            "render_path": os.path.abspath("render\\point_cloud_blob.png"),
            "render": False,
        }

    user_args = argv[argv.index("--") + 1 :]
    blend_path = os.path.abspath("point_cloud_blob.blend")
    render_path = os.path.abspath("render\\point_cloud_blob.png")
    render = False

    i = 0
    while i < len(user_args):
        arg = user_args[i]
        if arg == "--blend" and i + 1 < len(user_args):
            blend_path = os.path.abspath(user_args[i + 1])
            i += 2
            continue
        if arg == "--render" and i + 1 < len(user_args):
            render_path = os.path.abspath(user_args[i + 1])
            render = True
            i += 2
            continue
        i += 1

    return {
        "blend_path": blend_path,
        "render_path": render_path,
        "render": render,
    }


def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.world = bpy.data.worlds.new("World")
    scene.world.use_nodes = True
    bg = scene.world.node_tree.nodes["Background"]
    bg.inputs[0].default_value = (0.0, 0.0, 0.0, 1.0)
    bg.inputs[1].default_value = 0.0
    return scene


def configure_render(scene):
    try:
        scene.render.engine = "BLENDER_EEVEE_NEXT"
    except TypeError:
        scene.render.engine = "BLENDER_EEVEE"

    scene.render.resolution_x = 1536
    scene.render.resolution_y = 1536
    scene.render.resolution_percentage = 100
    scene.render.film_transparent = False
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.view_settings.view_transform = "Standard"
    scene.view_settings.look = "None"
    scene.view_settings.exposure = -1.2

    if hasattr(scene, "eevee"):
        scene.eevee.taa_render_samples = 128
        if hasattr(scene.eevee, "use_bloom"):
            scene.eevee.use_bloom = True
            scene.eevee.bloom_intensity = 0.03
            scene.eevee.bloom_radius = 4.5
            scene.eevee.bloom_threshold = 0.6


def create_dot_instance():
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=0.012, location=(0, 0, 0))
    dot = bpy.context.active_object
    dot.name = "DotInstance"
    dot.hide_render = False
    dot.hide_set(True)
    return dot


def create_blob_source():
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=132,
        ring_count=96,
        radius=1.18,
        location=(0, 0, 0),
    )
    source = bpy.context.active_object
    source.name = "BlobSurface"
    bpy.ops.object.shade_smooth()
    return source


def build_emission_material():
    material = bpy.data.materials.new("PointGlow")
    material.use_nodes = True
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    nodes.clear()

    output = nodes.new("ShaderNodeOutputMaterial")
    emission = nodes.new("ShaderNodeEmission")
    geometry = nodes.new("ShaderNodeNewGeometry")
    separate = nodes.new("ShaderNodeSeparateXYZ")
    map_range = nodes.new("ShaderNodeMapRange")
    ramp = nodes.new("ShaderNodeValToRGB")
    noise = nodes.new("ShaderNodeTexNoise")
    math_noise = nodes.new("ShaderNodeMath")
    add = nodes.new("ShaderNodeMath")
    value = nodes.new("ShaderNodeValue")

    geometry.location = (-900, 0)
    separate.location = (-700, 0)
    map_range.location = (-500, 0)
    noise.location = (-700, -220)
    math_noise.location = (-500, -220)
    add.location = (-260, -40)
    ramp.location = (-40, 0)
    emission.location = (180, 0)
    output.location = (420, 0)
    value.location = (-260, -260)

    map_range.inputs["From Min"].default_value = -1.4
    map_range.inputs["From Max"].default_value = 1.4
    map_range.inputs["To Min"].default_value = 0.0
    map_range.inputs["To Max"].default_value = 1.0
    map_range.clamp = True

    noise.inputs["Scale"].default_value = 1.8
    noise.inputs["Detail"].default_value = 5.4
    noise.inputs["Roughness"].default_value = 0.45

    math_noise.operation = "MULTIPLY"
    math_noise.inputs[1].default_value = 0.12
    add.operation = "ADD"
    add.use_clamp = True

    ramp.color_ramp.elements[0].position = 0.12
    ramp.color_ramp.elements[0].color = (0.9, 0.28, 1.0, 1.0)
    ramp.color_ramp.elements[1].position = 0.9
    ramp.color_ramp.elements[1].color = (0.16, 0.58, 1.0, 1.0)

    value.outputs[0].default_value = 2.8

    links.new(geometry.outputs["Position"], separate.inputs["Vector"])
    links.new(separate.outputs["Z"], map_range.inputs["Value"])
    links.new(geometry.outputs["Position"], noise.inputs["Vector"])
    links.new(noise.outputs["Fac"], math_noise.inputs[0])
    links.new(map_range.outputs["Result"], add.inputs[0])
    links.new(math_noise.outputs["Value"], add.inputs[1])
    links.new(add.outputs["Value"], ramp.inputs["Fac"])
    links.new(ramp.outputs["Color"], emission.inputs["Color"])
    links.new(value.outputs["Value"], emission.inputs["Strength"])
    links.new(emission.outputs["Emission"], output.inputs["Surface"])

    return material


def build_geometry_nodes(source, dot, material):
    modifier = source.modifiers.new(name="PointCloudBlob", type="NODES")
    node_group = bpy.data.node_groups.new("PointCloudBlobNodes", "GeometryNodeTree")
    modifier.node_group = node_group

    nodes = node_group.nodes
    links = node_group.links

    group_input = nodes.new("NodeGroupInput")
    group_output = nodes.new("NodeGroupOutput")
    set_position = nodes.new("GeometryNodeSetPosition")
    normal = nodes.new("GeometryNodeInputNormal")
    position = nodes.new("GeometryNodeInputPosition")
    scale_a = nodes.new("ShaderNodeVectorMath")
    scale_b = nodes.new("ShaderNodeVectorMath")
    noise_a = nodes.new("ShaderNodeTexNoise")
    noise_b = nodes.new("ShaderNodeTexNoise")
    math_a = nodes.new("ShaderNodeMath")
    math_b = nodes.new("ShaderNodeMath")
    add = nodes.new("ShaderNodeMath")
    map_range = nodes.new("ShaderNodeMapRange")
    multiply = nodes.new("ShaderNodeVectorMath")
    mesh_to_points = nodes.new("GeometryNodeMeshToPoints")
    object_info = nodes.new("GeometryNodeObjectInfo")
    instance_on_points = nodes.new("GeometryNodeInstanceOnPoints")
    realize = nodes.new("GeometryNodeRealizeInstances")
    set_material = nodes.new("GeometryNodeSetMaterial")

    node_group.interface.new_socket(name="Geometry", in_out="INPUT", socket_type="NodeSocketGeometry")
    node_group.interface.new_socket(name="Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry")

    group_input.location = (-1700, 0)
    position.location = (-1500, -240)
    normal.location = (-860, 20)
    scale_a.location = (-1280, -120)
    noise_a.location = (-1080, -120)
    scale_b.location = (-1280, -420)
    noise_b.location = (-1080, -420)
    math_a.location = (-860, -160)
    math_b.location = (-860, -420)
    add.location = (-660, -300)
    map_range.location = (-460, -300)
    multiply.location = (-260, -80)
    set_position.location = (-40, 40)
    mesh_to_points.location = (220, 40)
    object_info.location = (220, -220)
    instance_on_points.location = (500, 40)
    realize.location = (760, 40)
    set_material.location = (980, 40)
    group_output.location = (1220, 40)

    scale_a.operation = "SCALE"
    scale_b.operation = "SCALE"
    scale_a.inputs[3].default_value = 1.65
    scale_b.inputs[3].default_value = 3.6

    noise_a.noise_dimensions = "4D"
    noise_a.inputs["Scale"].default_value = 1.0
    noise_a.inputs["Detail"].default_value = 7.0
    noise_a.inputs["Roughness"].default_value = 0.42
    noise_a.inputs["W"].default_value = 0.18

    noise_b.noise_dimensions = "4D"
    noise_b.inputs["Scale"].default_value = 1.0
    noise_b.inputs["Detail"].default_value = 3.0
    noise_b.inputs["Roughness"].default_value = 0.55
    noise_b.inputs["W"].default_value = 4.7

    math_a.operation = "MULTIPLY"
    math_a.inputs[1].default_value = 0.42
    math_b.operation = "MULTIPLY"
    math_b.inputs[1].default_value = 0.16
    add.operation = "ADD"

    map_range.inputs["From Min"].default_value = 0.0
    map_range.inputs["From Max"].default_value = 0.58
    map_range.inputs["To Min"].default_value = -0.24
    map_range.inputs["To Max"].default_value = 0.36
    map_range.clamp = False

    multiply.operation = "SCALE"
    mesh_to_points.mode = "VERTICES"
    mesh_to_points.inputs["Radius"].default_value = 0.018

    object_info.transform_space = "RELATIVE"
    object_info.inputs["Object"].default_value = dot

    set_material.inputs["Material"].default_value = material

    links.new(group_input.outputs["Geometry"], set_position.inputs["Geometry"])
    links.new(position.outputs["Position"], scale_a.inputs[0])
    links.new(position.outputs["Position"], scale_b.inputs[0])
    links.new(scale_a.outputs["Vector"], noise_a.inputs["Vector"])
    links.new(scale_b.outputs["Vector"], noise_b.inputs["Vector"])
    links.new(noise_a.outputs["Fac"], math_a.inputs[0])
    links.new(noise_b.outputs["Fac"], math_b.inputs[0])
    links.new(math_a.outputs["Value"], add.inputs[0])
    links.new(math_b.outputs["Value"], add.inputs[1])
    links.new(add.outputs["Value"], map_range.inputs["Value"])
    links.new(normal.outputs["Normal"], multiply.inputs[0])
    links.new(map_range.outputs["Result"], multiply.inputs[3])
    links.new(multiply.outputs["Vector"], set_position.inputs["Offset"])
    links.new(set_position.outputs["Geometry"], mesh_to_points.inputs["Mesh"])
    links.new(mesh_to_points.outputs["Points"], instance_on_points.inputs["Points"])
    links.new(object_info.outputs["Geometry"], instance_on_points.inputs["Instance"])
    links.new(instance_on_points.outputs["Instances"], realize.inputs["Geometry"])
    links.new(realize.outputs["Geometry"], set_material.inputs["Geometry"])
    links.new(set_material.outputs["Geometry"], group_output.inputs["Geometry"])


def create_camera():
    bpy.ops.object.camera_add(location=(0.0, -6.4, 0.9), rotation=(math.radians(82), 0.0, 0.0))
    camera = bpy.context.active_object
    camera.name = "Camera"
    camera.data.lens = 62
    camera.data.dof.use_dof = True
    camera.data.dof.focus_distance = 6.1
    camera.data.dof.aperture_fstop = 2.8

    bpy.ops.object.empty_add(type="PLAIN_AXES", location=(0.0, 0.0, 0.0))
    target = bpy.context.active_object
    target.name = "CameraTarget"
    target.location = (0.0, 0.0, 0.08)

    constraint = camera.constraints.new(type="TRACK_TO")
    constraint.target = target
    constraint.track_axis = "TRACK_NEGATIVE_Z"
    constraint.up_axis = "UP_Y"

    bpy.context.scene.camera = camera
    return camera


def create_rim_lights():
    bpy.ops.object.light_add(type="AREA", location=(1.8, -1.4, 1.5))
    key = bpy.context.active_object
    key.data.energy = 3000
    key.data.shape = "DISK"
    key.data.size = 3.2
    key.data.color = (0.62, 0.83, 1.0)

    bpy.ops.object.light_add(type="AREA", location=(-1.8, 1.2, -1.3))
    fill = bpy.context.active_object
    fill.data.energy = 1800
    fill.data.shape = "DISK"
    fill.data.size = 3.8
    fill.data.color = (0.84, 0.58, 1.0)


def pose_blob(source):
    source.rotation_euler = (
        math.radians(18),
        math.radians(-14),
        math.radians(22),
    )
    source.scale = (1.08, 1.0, 1.04)


def ensure_parent_dir(path):
    directory = os.path.dirname(path)
    if directory:
        os.makedirs(directory, exist_ok=True)


def main():
    args = parse_args()
    scene = reset_scene()
    configure_render(scene)

    dot = create_dot_instance()
    source = create_blob_source()
    material = build_emission_material()
    build_geometry_nodes(source, dot, material)
    pose_blob(source)
    create_camera()
    ensure_parent_dir(args["blend_path"])
    bpy.ops.wm.save_as_mainfile(filepath=args["blend_path"])

    if args["render"]:
        ensure_parent_dir(args["render_path"])
        scene.render.filepath = args["render_path"]
        bpy.ops.render.render(write_still=True)


if __name__ == "__main__":
    main()
