import math
import os
import sys

import bpy


def parse_args():
    argv = sys.argv
    defaults = {
        "blend_path": os.path.abspath("point_cloud_blob.blend"),
        "render_path": os.path.abspath("render\\point_cloud_blob.png"),
        "animation_path": os.path.abspath("render\\animation\\frame_"),
        "render": False,
        "animate": False,
        "frames": 96,
        "fps": 24,
    }
    if "--" not in argv:
        return defaults

    user_args = argv[argv.index("--") + 1 :]
    args = defaults.copy()

    i = 0
    while i < len(user_args):
        arg = user_args[i]
        if arg == "--blend" and i + 1 < len(user_args):
            args["blend_path"] = os.path.abspath(user_args[i + 1])
            i += 2
            continue
        if arg == "--render" and i + 1 < len(user_args):
            args["render_path"] = os.path.abspath(user_args[i + 1])
            args["render"] = True
            i += 2
            continue
        if arg == "--animate" and i + 1 < len(user_args):
            args["animation_path"] = os.path.abspath(user_args[i + 1])
            args["animate"] = True
            i += 2
            continue
        if arg == "--frames" and i + 1 < len(user_args):
            args["frames"] = int(user_args[i + 1])
            i += 2
            continue
        if arg == "--fps" and i + 1 < len(user_args):
            args["fps"] = int(user_args[i + 1])
            i += 2
            continue
        i += 1

    return args


def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.world = bpy.data.worlds.new("World")
    scene.world.use_nodes = True
    bg = scene.world.node_tree.nodes["Background"]
    bg.inputs[0].default_value = (0.0, 0.0, 0.0, 1.0)
    bg.inputs[1].default_value = 0.0
    return scene


def configure_render(scene, fps):
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
    scene.view_settings.exposure = -1.0
    scene.frame_start = 1
    scene.render.fps = fps

    if hasattr(scene, "eevee"):
        scene.eevee.taa_render_samples = 128
        if hasattr(scene.eevee, "use_bloom"):
            scene.eevee.use_bloom = True
            scene.eevee.bloom_intensity = 0.035
            scene.eevee.bloom_radius = 4.8
            scene.eevee.bloom_threshold = 0.55


def create_dot_instance():
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=0.0105, location=(0, 0, 0))
    dot = bpy.context.active_object
    dot.name = "DotInstance"
    dot.hide_render = False
    dot.hide_set(True)
    return dot


def create_blob_source():
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=160,
        ring_count=112,
        radius=1.15,
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
    map_range.location = (-520, 0)
    noise.location = (-700, -220)
    math_noise.location = (-500, -220)
    add.location = (-260, -40)
    ramp.location = (-40, 0)
    emission.location = (180, 0)
    output.location = (420, 0)
    value.location = (180, -180)

    map_range.inputs["From Min"].default_value = -1.2
    map_range.inputs["From Max"].default_value = 1.2
    map_range.inputs["To Min"].default_value = 0.0
    map_range.inputs["To Max"].default_value = 1.0
    map_range.clamp = True

    noise.inputs["Scale"].default_value = 2.1
    noise.inputs["Detail"].default_value = 5.0
    noise.inputs["Roughness"].default_value = 0.38

    math_noise.operation = "MULTIPLY"
    math_noise.inputs[1].default_value = 0.07
    add.operation = "ADD"
    add.use_clamp = True

    ramp.color_ramp.elements[0].position = 0.08
    ramp.color_ramp.elements[0].color = (0.90, 0.40, 1.0, 1.0)
    ramp.color_ramp.elements[1].position = 0.92
    ramp.color_ramp.elements[1].color = (0.22, 0.74, 1.0, 1.0)

    value.outputs[0].default_value = 2.3

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
    scale_a.inputs[3].default_value = 1.45
    scale_b.inputs[3].default_value = 3.2

    noise_a.noise_dimensions = "4D"
    noise_a.inputs["Scale"].default_value = 1.0
    noise_a.inputs["Detail"].default_value = 8.0
    noise_a.inputs["Roughness"].default_value = 0.4
    noise_a.inputs["W"].default_value = 0.0

    noise_b.noise_dimensions = "4D"
    noise_b.inputs["Scale"].default_value = 1.0
    noise_b.inputs["Detail"].default_value = 3.0
    noise_b.inputs["Roughness"].default_value = 0.54
    noise_b.inputs["W"].default_value = 3.8

    math_a.operation = "MULTIPLY"
    math_a.inputs[1].default_value = 0.34
    math_b.operation = "MULTIPLY"
    math_b.inputs[1].default_value = 0.13
    add.operation = "ADD"

    map_range.inputs["From Min"].default_value = 0.0
    map_range.inputs["From Max"].default_value = 0.52
    map_range.inputs["To Min"].default_value = -0.16
    map_range.inputs["To Max"].default_value = 0.29
    map_range.clamp = False

    multiply.operation = "SCALE"
    mesh_to_points.mode = "VERTICES"
    mesh_to_points.inputs["Radius"].default_value = 0.017

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

    return {
        "noise_a": noise_a,
        "noise_b": noise_b,
        "amplitude": map_range,
    }


def create_camera():
    bpy.ops.object.camera_add(location=(0.0, -6.8, 0.7), rotation=(math.radians(82), 0.0, 0.0))
    camera = bpy.context.active_object
    camera.name = "Camera"
    camera.data.lens = 68
    camera.data.dof.use_dof = True
    camera.data.dof.focus_distance = 6.45
    camera.data.dof.aperture_fstop = 2.2

    bpy.ops.object.empty_add(type="PLAIN_AXES", location=(0.0, 0.0, 0.0))
    target = bpy.context.active_object
    target.name = "CameraTarget"
    target.location = (0.0, 0.0, 0.06)

    constraint = camera.constraints.new(type="TRACK_TO")
    constraint.target = target
    constraint.track_axis = "TRACK_NEGATIVE_Z"
    constraint.up_axis = "UP_Y"

    bpy.context.scene.camera = camera
    return camera, target


def pose_blob(source):
    source.rotation_euler = (
        math.radians(16),
        math.radians(-18),
        math.radians(24),
    )
    source.scale = (1.12, 0.98, 1.06)


def add_animation(source, target, nodes_info, scene, frame_end):
    scene.frame_end = frame_end
    base_rot_z = source.rotation_euler.z
    base_rot_x = source.rotation_euler.x

    noise_a_w = nodes_info["noise_a"].inputs["W"]
    noise_b_w = nodes_info["noise_b"].inputs["W"]
    amp_min = nodes_info["amplitude"].inputs["To Min"]
    amp_max = nodes_info["amplitude"].inputs["To Max"]

    for frame, progress in ((1, 0.0), (frame_end // 2, 0.5), (frame_end, 1.0)):
        angle = progress * math.tau
        source.rotation_euler.z = base_rot_z + math.radians(14.0) * math.sin(angle)
        source.rotation_euler.x = base_rot_x + math.radians(5.0) * math.cos(angle)
        source.scale = (
            1.12 + 0.03 * math.sin(angle),
            0.98 + 0.02 * math.cos(angle * 2.0),
            1.06 + 0.025 * math.cos(angle),
        )
        target.location.z = 0.06 + 0.05 * math.sin(angle)

        noise_a_w.default_value = progress * 1.4
        noise_b_w.default_value = 3.8 + progress * 2.2
        amp_min.default_value = -0.16 - 0.02 * math.sin(angle)
        amp_max.default_value = 0.29 + 0.035 * math.cos(angle)

        source.keyframe_insert(data_path="rotation_euler", frame=frame)
        source.keyframe_insert(data_path="scale", frame=frame)
        target.keyframe_insert(data_path="location", frame=frame)
        noise_a_w.keyframe_insert(data_path="default_value", frame=frame)
        noise_b_w.keyframe_insert(data_path="default_value", frame=frame)
        amp_min.keyframe_insert(data_path="default_value", frame=frame)
        amp_max.keyframe_insert(data_path="default_value", frame=frame)

def configure_animation_output(scene, output_path):
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.filepath = output_path


def ensure_parent_dir(path):
    directory = os.path.dirname(path)
    if directory:
        os.makedirs(directory, exist_ok=True)


def main():
    args = parse_args()
    scene = reset_scene()
    configure_render(scene, args["fps"])

    dot = create_dot_instance()
    source = create_blob_source()
    material = build_emission_material()
    nodes_info = build_geometry_nodes(source, dot, material)
    pose_blob(source)
    camera, target = create_camera()

    if args["animate"]:
        add_animation(source, target, nodes_info, scene, args["frames"])

    ensure_parent_dir(args["blend_path"])
    bpy.ops.wm.save_as_mainfile(filepath=args["blend_path"])

    if args["render"]:
        ensure_parent_dir(args["render_path"])
        scene.render.image_settings.file_format = "PNG"
        scene.render.filepath = args["render_path"]
        bpy.ops.render.render(write_still=True)

    if args["animate"]:
        ensure_parent_dir(args["animation_path"])
        configure_animation_output(scene, args["animation_path"])
        bpy.ops.render.render(animation=True)


if __name__ == "__main__":
    main()
