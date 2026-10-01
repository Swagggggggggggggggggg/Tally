"""Gorilla Tag rig helpers built on NachoEngine's Gorilla_IK_Rig.blend (Blender 4.5, run inside Blender)."""
import bpy, math, os
from mathutils import Vector, Matrix, Euler

RIG_BLEND = "/tmp/claude-0/-home-user-Tally/702e814a-b90a-5d68-bc9a-bc92c217492c/scratchpad/nacho/rig/GorillaTag_IK_Rig.blend"


def srgb(h):
    """'#RRGGBB' -> linear RGBA tuple."""
    h = h.lstrip('#')
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    lin = [x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
    return (lin[0], lin[1], lin[2], 1.0)


def append_rig(tag):
    """Append the Gorilla_IK_Rig collection and return its objects (armature, mesh, nametag)."""
    before = set(bpy.data.objects)
    with bpy.data.libraries.load(RIG_BLEND, link=False) as (src, dst):
        dst.collections = ["Gorilla_IK_Rig"]
    col = dst.collections[0]
    col.name = "GT_" + tag
    bpy.context.scene.collection.children.link(col)
    new = [o for o in bpy.data.objects if o not in before]
    arm = next(o for o in new if o.type == 'ARMATURE')
    mesh = next(o for o in new if o.type == 'MESH' and o.parent == arm)
    text = next((o for o in new if o.type == 'FONT'), None)
    arm.name, mesh.name = "Rig_" + tag, "Monke_" + tag
    if text:
        text.name = "Tag_" + tag
    # bone custom shapes come along as extra objects; hide them from render
    for o in new:
        if o not in (arm, mesh, text):
            o.hide_render = True
    # single-user materials so each monke has its own colour
    for slot in mesh.material_slots:
        if slot.material:
            slot.material = slot.material.copy()
            nt = slot.material.node_tree
            for n in nt.nodes:
                if n.type == 'GROUP' and n.node_tree and n.node_tree.name.startswith('GorillaTagColorShader'):
                    n.node_tree = n.node_tree.copy()
    if text:
        for slot in text.material_slots:
            if slot.material:
                slot.material = slot.material.copy()
    return {"arm": arm, "mesh": mesh, "text": text, "col": col, "all": new}


def shader_group_node(mesh):
    for slot in mesh.material_slots:
        for n in slot.material.node_tree.nodes:
            if n.type == 'GROUP' and n.node_tree and n.node_tree.name.startswith('GorillaTagColorShader'):
                return n
    return None


def set_look(r, color_hex=None, lava=0.0, ice=0.0, emission=None, lava_emission=None, subsurface=None,
             glossy=None, glossy_color=None):
    g = shader_group_node(r["mesh"])
    if color_hex:
        g.inputs['PrimaryColor'].default_value = srgb(color_hex)
    g.inputs['Lava'].default_value = lava
    g.inputs['Ice'].default_value = ice
    if emission is not None:
        g.inputs['Color Emission'].default_value = emission
    if lava_emission is not None and 'Lava Emission' in g.inputs:
        g.inputs['Lava Emission'].default_value = lava_emission
    if subsurface is not None:
        g.inputs['Subsurface'].default_value = subsurface
    if glossy is not None and 'Glossy Strength' in g.inputs:
        g.inputs['Glossy Strength'].default_value = glossy
    if glossy_color and 'Glossy Color' in g.inputs:
        g.inputs['Glossy Color'].default_value = srgb(glossy_color)
    return g


def set_face_image(r, path):
    """Replace the face texture image (64x65 pixel-art face) used by this monke's shader copies."""
    img = bpy.data.images.load(path, check_existing=False)
    img.colorspace_settings.name = 'sRGB'
    replaced = 0

    def walk(tree, seen):
        nonlocal replaced
        for n in tree.nodes:
            if n.type == 'TEX_IMAGE' and n.image and n.image.name.startswith('gorillatexture'):
                n.image = img
                replaced += 1
            if n.type == 'GROUP' and n.node_tree and n.node_tree not in seen:
                seen.add(n.node_tree)
                walk(n.node_tree, seen)

    # make nested groups single-user first so the swap only affects this monke
    g = shader_group_node(r["mesh"])

    def localize(tree):
        for n in tree.nodes:
            if n.type == 'GROUP' and n.node_tree:
                n.node_tree = n.node_tree.copy()
                localize(n.node_tree)

    localize(g.node_tree)
    walk(g.node_tree, set())
    return replaced


def set_name(r, text):
    if r["text"]:
        r["text"].data.body = text


def place(r, loc=(0, 0, 0), rot_z_deg=0.0, scale=1.0, rot_xyz_deg=None):
    a = r["arm"]
    a.location = loc
    if rot_xyz_deg:
        a.rotation_euler = Euler([math.radians(v) for v in rot_xyz_deg], 'XYZ')
    else:
        a.rotation_euler = Euler((0, 0, math.radians(rot_z_deg)), 'XYZ')
    a.scale = (scale, scale, scale)
    bpy.context.view_layer.update()


def pb(r, name):
    return r["arm"].pose.bones[name]


def set_hand_world(r, side, world_pos, rot_deg=None):
    """Move the IK hand controller ('L' or 'R') to a world-space position. rot_deg: optional XYZ euler (deg)
    applied on top of the rest orientation in armature space."""
    a = r["arm"]
    b = a.pose.bones["hand_controller." + side]
    bpy.context.view_layer.update()
    rest = a.matrix_world @ b.bone.matrix_local
    target = Matrix.Translation(Vector(world_pos)) @ rest.to_3x3().to_4x4()
    if rot_deg:
        target = Matrix.Translation(Vector(world_pos)) @ (
            a.matrix_world.to_3x3() @ Euler([math.radians(v) for v in rot_deg], 'XYZ').to_matrix()
            @ (a.matrix_world.to_3x3().inverted() @ rest.to_3x3())).to_4x4()
    b.matrix = a.matrix_world.inverted() @ target
    bpy.context.view_layer.update()


def hand_rest_world(r, side):
    a = r["arm"]
    bpy.context.view_layer.update()
    return (a.matrix_world @ a.pose.bones["hand_controller." + side].bone.matrix_local).translation.copy()


def rot_bone(r, name, xyz_deg):
    b = pb(r, name)
    b.rotation_mode = 'XYZ'
    b.rotation_euler = Euler([math.radians(v) for v in xyz_deg], 'XYZ')
    bpy.context.view_layer.update()


def curl(r, side, index=0.0, middle=0.0, thumb=0.0):
    """Finger curl via the control bones (degrees around local X)."""
    for nm, v in (("f_index_control", index), ("f_middle_control", middle), ("thumb_control", thumb)):
        b = pb(r, f"{nm}.{side}")
        b.rotation_mode = 'XYZ'
        b.rotation_euler = Euler((math.radians(v), 0, 0), 'XYZ')
    bpy.context.view_layer.update()


def bone_world(r, name, tail=False):
    a = r["arm"]
    bpy.context.view_layer.update()
    b = a.pose.bones[name]
    return a.matrix_world @ (b.tail if tail else b.head)


BRAND = "/tmp/claude-0/-home-user-Tally/702e814a-b90a-5d68-bc9a-bc92c217492c/scratchpad/research/brand/"


def import_logo(svg, name, width=1.0, depth=0.08, bevel=0.012, mat=None):
    """Import an SVG logo as a single extruded, bevelled mesh centred at origin, facing -Y (readable from front)."""
    before = set(bpy.data.objects)
    bpy.ops.import_curve.svg(filepath=svg)
    new = [o for o in bpy.data.objects if o not in before]
    bpy.ops.object.select_all(action='DESELECT')
    for o in new:
        o.select_set(True)
    bpy.context.view_layer.objects.active = new[0]
    if len(new) > 1:
        bpy.ops.object.join()
    ob = bpy.context.view_layer.objects.active
    ob.name = name
    cu = ob.data
    cu.dimensions = '2D'
    cu.fill_mode = 'BOTH'
    # normalise size first (svg import is tiny)
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
    ob.location = (0, 0, 0)
    w = ob.dimensions.x
    s = width / w
    cu.extrude = depth / 2 / s
    cu.bevel_depth = bevel / s
    cu.bevel_resolution = 3
    cu.offset = -bevel / s
    cu.resolution_u = 24
    ob.scale = (s, s, s)
    bpy.context.view_layer.update()
    bpy.ops.object.convert(target='MESH')
    ob = bpy.context.view_layer.objects.active
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    # stand it up: SVG lies in XY plane -> rotate to XZ facing -Y
    ob.rotation_euler = (math.radians(90), 0, 0)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
    ob.location = (0, 0, 0)
    ob.data.materials.clear()
    if mat:
        ob.data.materials.append(mat)
    for p in ob.data.polygons:
        p.use_smooth = False
    return ob


def emissive_mat(name, hex_col, strength=1.0, base_hex=None, rough=0.35):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = srgb(base_hex or hex_col)
    b.inputs['Roughness'].default_value = rough
    b.inputs['Emission Color'].default_value = srgb(hex_col)
    b.inputs['Emission Strength'].default_value = strength
    return m


def plain_mat(name, hex_col, rough=0.5, metal=0.0, coat=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = srgb(hex_col)
    b.inputs['Roughness'].default_value = rough
    b.inputs['Metallic'].default_value = metal
    b.inputs['Coat Weight'].default_value = coat
    return m


def aim_elbow(r, side, desired_world_dir, step=3):
    """Pick the IK pole angle that puts the elbow closest to a desired direction (world space, from the shoulder)."""
    a = r["arm"]
    con = a.pose.bones['forearm.' + side].constraints[0]
    d = Vector(desired_world_dir).normalized()
    best = None
    for deg in range(-180, 180, step):
        con.pole_angle = math.radians(deg)
        bpy.context.view_layer.update()
        sh = bone_world(r, 'upper_arm.' + side)
        e = bone_world(r, 'forearm.' + side)
        sc = (e - sh).normalized().dot(d)
        if best is None or sc > best[0]:
            best = (sc, deg)
    con.pole_angle = math.radians(best[1])
    bpy.context.view_layer.update()
    return best
