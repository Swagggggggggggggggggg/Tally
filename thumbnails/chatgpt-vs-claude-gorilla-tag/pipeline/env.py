"""Gorilla Tag-style treehouse + forest environment, built two ways from ONE layout:
  build(scn, cfg, mode='real')  -> PBR wood treehouse, real fir trees, ferns, rocks, HDRI + golden-hour sun
  build(scn, cfg, mode='crude') -> the same layout as flat untextured primitives (an AI's day-one prototype)
World coordinates: monke at origin facing -Y (toward the camera); everything here sits behind it (+Y).
"""
import bpy, math, os, random
from mathutils import Vector, Euler

PH = os.environ.get("PH_DIR", os.path.join(os.path.dirname(os.path.abspath(__file__)), "ph")) + "/"  # filled by ph_get.py
GROUND_Z = -0.2

# ------------------------------------------------------------------ layout (shared by both modes)
TH = dict(x=1.75, y=5.2, deck_z=1.05, deck_w=2.4, deck_d=2.1, hut_w=1.6, hut_d=1.3, hut_h=1.05, rot=-18)
LEFT_TRUNK = dict(x=-1.55, y=4.4, deck_z=1.35, deck_r=0.85)
INNER = 1.0   # +1: divider is toward +x (left panel), -1: toward -x (right panel)


def set_layout(cfg, mode):
    """inner = direction of the thumbnail divider in world x. Treehouse goes on the inner side, trunk platform outer."""
    global INNER
    L = cfg.get('layout', {})
    INNER = L.get('inner', 1.0 if mode == 'crude' else -1.0)
    TH.update(x=INNER * L.get('th_x', 1.25), y=L.get('th_y', 4.2), deck_z=L.get('deck_z', 0.55),
              rot=-INNER * L.get('th_rot', 14))
    LEFT_TRUNK.update(x=-INNER * L.get('trunk_x', 1.6), y=L.get('trunk_y', 5.6), deck_z=L.get('trunk_deck_z', 0.85))


def srgb(h):
    h = h.lstrip('#')
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple([x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c] + [1.0])


# ------------------------------------------------------------------ materials
def pbr(name, folder, scale=1.0, tint=None, rough_mul=1.0, bump=1.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes['Principled BSDF']
    tc = nt.nodes.new('ShaderNodeTexCoord')
    mp = nt.nodes.new('ShaderNodeMapping')
    mp.inputs['Scale'].default_value = (scale, scale, scale)
    nt.links.new(tc.outputs['UV'], mp.inputs['Vector'])

    def img(fn, cs):
        n = nt.nodes.new('ShaderNodeTexImage')
        n.image = bpy.data.images.load(PH + f"tex/{folder}/{fn}", check_existing=True)
        n.image.colorspace_settings.name = cs
        n.projection = 'BOX'
        n.projection_blend = 0.25
        nt.links.new(mp.outputs['Vector'], n.inputs['Vector'])
        return n
    d = img('Diffuse.jpg', 'sRGB')
    col = d.outputs['Color']
    if tint:
        mx = nt.nodes.new('ShaderNodeMix')
        mx.data_type = 'RGBA'
        mx.blend_type = 'MULTIPLY'
        mx.inputs['Factor'].default_value = 1.0
        nt.links.new(col, mx.inputs['A'])
        mx.inputs['B'].default_value = srgb(tint)
        col = mx.outputs['Result']
    nt.links.new(col, b.inputs['Base Color'])
    r = img('Rough.jpg', 'Non-Color')
    if rough_mul != 1.0:
        mm = nt.nodes.new('ShaderNodeMath')
        mm.operation = 'MULTIPLY'
        mm.inputs[1].default_value = rough_mul
        nt.links.new(r.outputs['Color'], mm.inputs[0])
        nt.links.new(mm.outputs['Value'], b.inputs['Roughness'])
    else:
        nt.links.new(r.outputs['Color'], b.inputs['Roughness'])
    n = img('nor_gl.jpg', 'Non-Color')
    nm = nt.nodes.new('ShaderNodeNormalMap')
    nm.inputs['Strength'].default_value = bump
    nt.links.new(n.outputs['Color'], nm.inputs['Color'])
    nt.links.new(nm.outputs['Normal'], b.inputs['Normal'])
    return m


def flat(name, hx, rough=0.6):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = srgb(hx)
    b.inputs['Roughness'].default_value = rough
    return m


def mats(mode):
    if mode == 'real':
        return dict(
            deck=pbr('deck', 'weathered_planks', 1.0, tint='#E2C49A'),
            wall=pbr('wall', 'brown_planks_05', 1.0, tint='#F0D2A8'),
            roof=pbr('roof', 'roof_planks', 1.0, tint='#C8A27A'),
            post=pbr('post', 'pine_bark', 1.5),
            trim=pbr('trim', 'weathered_planks', 2.0, tint='#B98A5C'),
            slide=pbr('slide', 'weathered_planks', 1.0, tint='#D9B48A', rough_mul=0.7),
            rope=flat('rope', '#B79A6B', 0.9),
            ground=pbr('ground', 'forest_leaves_02', 0.6, tint='#6A5C48', bump=1.2),
        )
    # crude: Unity-default-ish flat greys with a faint blue cast
    return dict(
        deck=flat('deck', '#A9B2BC'), wall=flat('wall', '#C9D0D8'), roof=flat('roof', '#8A949F'),
        post=flat('post', '#9CA5AF'), trim=flat('trim', '#B3BBC4'), slide=flat('slide', '#B7C4D3'),
        rope=flat('rope', '#9CA5AF'), ground=None,
    )


# ------------------------------------------------------------------ primitives
def box(size, loc, rot, mat, parent=None, bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot)
    o = bpy.context.object
    o.scale = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if bevel:
        bv = o.modifiers.new('bv', 'BEVEL')
        bv.width = bevel
        bv.segments = 2
    o.data.materials.append(mat)
    bpy.ops.object.shade_flat()
    if parent:
        o.parent = parent
    return o


def cylinder(r, depth, loc, rot, mat, verts=12, parent=None):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r, depth=depth, location=loc, rotation=rot)
    o = bpy.context.object
    o.data.materials.append(mat)
    if parent:
        o.parent = parent
    return o


def beam(p0, p1, r, mat, verts=8, parent=None, square=False):
    p0, p1 = Vector(p0), Vector(p1)
    d = p1 - p0
    mid = (p0 + p1) / 2
    rot = d.to_track_quat('Z', 'Y').to_euler()
    if square:
        o = box((r * 2, r * 2, d.length), mid, rot, mat, parent)
    else:
        o = cylinder(r, d.length, mid, rot, mat, verts, parent)
    return o


def uv_unwrap(o):
    """Cube-project UVs so PBR textures sit at a sane real-world scale."""
    bpy.context.view_layer.objects.active = o
    o.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.cube_project(cube_size=1.0)
    bpy.ops.object.mode_set(mode='OBJECT')
    o.select_set(False)


# ------------------------------------------------------------------ treehouse (shared layout)
def treehouse(M, mode):
    root = bpy.data.objects.new('treehouse', None)
    bpy.context.scene.collection.objects.link(root)
    root.location = (TH['x'], TH['y'], GROUND_Z)
    root.rotation_euler = (0, 0, math.radians(TH['rot']))
    W, D, Z = TH['deck_w'], TH['deck_d'], TH['deck_z'] - GROUND_Z
    parts = []
    crude = mode == 'crude'
    # deck: planks (real) or one slab (crude)
    if crude:
        parts.append(box((W, D, 0.12), (0, 0, Z), (0, 0, 0), M['deck'], root))
    else:
        n = 14
        for i in range(n):
            x = -W / 2 + (i + 0.5) * W / n
            parts.append(box((W / n - 0.012, D, 0.07), (x, 0, Z + 0.03), (0, 0, 0), M['deck'], root, 0.008))
        for yy in (-D / 2 + 0.1, D / 2 - 0.1):
            parts.append(box((W, 0.1, 0.12), (0, yy, Z - 0.06), (0, 0, 0), M['trim'], root, 0.01))
    # posts
    for sx in (-1, 1):
        for sy in (-1, 1):
            p = (sx * (W / 2 - 0.12), sy * (D / 2 - 0.12), 0)
            if crude:
                parts.append(box((0.16, 0.16, Z), (p[0], p[1], Z / 2), (0, 0, 0), M['post'], root))
            else:
                parts.append(beam((p[0], p[1], -0.2), (p[0], p[1], Z), 0.075, M['post'], 10, root))
    # diagonal braces (real only)
    if not crude:
        for sx in (-1, 1):
            parts.append(beam((sx * (W / 2 - 0.12), -D / 2 + 0.12, Z * 0.35), (sx * 0.2, -D / 2 + 0.12, Z - 0.05), 0.035,
                              M['trim'], 6, root, square=True))
    # hut
    hw, hd, hh = TH['hut_w'], TH['hut_d'], TH['hut_h']
    hz = Z + 0.06
    if crude:
        parts.append(box((hw, hd, hh), (0.15, 0.2, hz + hh / 2), (0, 0, 0), M['wall'], root))
        # door hole faked with a darker box
        parts.append(box((0.42, 0.02, 0.7), (0.15, 0.2 - hd / 2 - 0.01, hz + 0.35), (0, 0, 0), flat('door', '#5E6670'), root))
    else:
        # vertical plank walls: front (with door gap), back, sides
        def wall(x0, x1, y, rot_z=0.0, door=None):
            n = max(3, int(abs(x1 - x0) / 0.16))
            for i in range(n):
                x = x0 + (i + 0.5) * (x1 - x0) / n
                if door and door[0] < x < door[1]:
                    top = hz + 0.82
                    parts.append(box((abs(x1 - x0) / n - 0.01, 0.05, hh - 0.82), (x, y, (top + hz + hh) / 2), (0, 0, rot_z), M['wall'], root, 0.006))
                    continue
                parts.append(box((abs(x1 - x0) / n - 0.01, 0.05, hh * (1 + 0.04 * ((i * 7) % 3 - 1))), (x, y, hz + hh / 2), (0, 0, rot_z), M['wall'], root, 0.006))
        cx, cy = 0.15, 0.2
        wall(cx - hw / 2, cx + hw / 2, cy - hd / 2, door=(cx - 0.25, cx + 0.25))
        wall(cx - hw / 2, cx + hw / 2, cy + hd / 2)
        for sx in (-1, 1):
            n = 8
            for i in range(n):
                y = cy - hd / 2 + (i + 0.5) * hd / n
                parts.append(box((0.05, hd / n - 0.01, hh), (cx + sx * hw / 2, y, hz + hh / 2), (0, 0, 0), M['wall'], root, 0.006))
        # dark interior so the doorway reads
        parts.append(box((hw - 0.12, hd - 0.12, hh - 0.05), (cx, cy, hz + hh / 2), (0, 0, 0), flat('interior', '#120C08', 1.0), root))
        # window cut-out look: dark square with frame on the side
        parts.append(box((0.03, 0.42, 0.34), (cx + hw / 2 + 0.03, cy, hz + 0.62), (0, 0, 0), flat('win', '#1A120C', 1.0), root))
    # gabled roof
    rz = hz + hh
    span = hw / 2 + 0.25
    ang = math.radians(32)
    L = span / math.cos(ang)
    for sx in (-1, 1):
        parts.append(box((L, hd + 0.5, 0.07), (0.15 + sx * span / 2, 0.2, rz + span * math.tan(ang) / 2),
                         (0, sx * ang, 0), M['roof'], root, 0.01))
    if crude:
        pass
    else:
        # ridge beam + gable triangles
        parts.append(beam((0.15, 0.2 - hd / 2 - 0.25, rz + span * math.tan(ang) + 0.02), (0.15, 0.2 + hd / 2 + 0.25, rz + span * math.tan(ang) + 0.02),
                          0.05, M['trim'], 6, root, square=True))
        # closed gable ends (planked triangles front and back)
        peak = (hw / 2) * math.tan(ang)
        for gy in (0.2 - hd / 2, 0.2 + hd / 2):
            me = bpy.data.meshes.new('gable')
            t = 0.025
            vs = [(0.15 - hw / 2, gy - t, rz), (0.15 + hw / 2, gy - t, rz), (0.15, gy - t, rz + peak),
                  (0.15 - hw / 2, gy + t, rz), (0.15 + hw / 2, gy + t, rz), (0.15, gy + t, rz + peak)]
            me.from_pydata(vs, [], [(0, 1, 2), (5, 4, 3), (0, 3, 4, 1), (1, 4, 5, 2), (2, 5, 3, 0)])
            me.update()
            g = bpy.data.objects.new('gable', me)
            bpy.context.scene.collection.objects.link(g)
            g.parent = root
            g.data.materials.append(M['wall'])
            parts.append(g)
    # railings on the deck front/sides
    rail_h = 0.55
    if crude:
        parts.append(box((W, 0.08, 0.08), (0, -D / 2 + 0.05, Z + rail_h), (0, 0, 0), M['trim'], root))
    else:
        for i in range(9):
            x = -W / 2 + 0.1 + i * (W - 0.2) / 8
            if -0.75 < -INNER * x < -0.2:
                continue  # gap where the slide starts
            parts.append(beam((x, -D / 2 + 0.06, Z), (x, -D / 2 + 0.06, Z + rail_h), 0.025, M['trim'], 6, root, square=True))
        parts.append(beam((-INNER * W / 2, -D / 2 + 0.06, Z + rail_h), (-INNER * 0.75, -D / 2 + 0.06, Z + rail_h), 0.035, M['trim'], 6, root, square=True))
        parts.append(beam((-INNER * 0.2, -D / 2 + 0.06, Z + rail_h), (INNER * W / 2, -D / 2 + 0.06, Z + rail_h), 0.035, M['trim'], 6, root, square=True))
        for sx in (-1, 1):
            parts.append(beam((sx * (W / 2 - 0.05), -D / 2, Z + rail_h), (sx * (W / 2 - 0.05), D / 2, Z + rail_h), 0.035, M['trim'], 6, root, square=True))
    # slide from the deck front-left down toward the camera
    s0 = Vector((-INNER * 0.48, -D / 2, Z + 0.05))
    s1 = Vector((-INNER * 1.15, -D / 2 - 1.6, 0.12))
    sl = beam(s0, s1, 0.24 if not crude else 0.26, M['slide'], 6, root, square=True)
    sl.scale = (1.0, 0.18, 1.0) if not crude else (1.0, 0.25, 1.0)
    parts.append(sl)
    if not crude:
        for sx in (-1, 1):
            off = Vector((sx * 0.27, 0, 0.09))
            parts.append(beam(s0 + off, s1 + off, 0.03, M['trim'], 6, root, square=True))
    # ladder on the right side
    lx = INNER * (W / 2 + 0.02)
    if crude:
        parts.append(box((0.05, 0.5, Z), (lx, 0.2, Z / 2), (0, 0, 0), M['post'], root))
    else:
        for yy in (0.0, 0.42):
            parts.append(beam((lx, yy, 0), (lx, yy, Z + 0.4), 0.025, M['trim'], 6, root, square=True))
        for k in range(6):
            zz = 0.15 + k * (Z / 6)
            parts.append(beam((lx, 0.0, zz), (lx, 0.42, zz), 0.018, M['trim'], 6, root))
    if not crude:
        for o in parts:
            if o.type == 'MESH':
                uv_unwrap(o)
    return root


def left_platform(M, mode, tree_coll=None):
    """Ring deck around a trunk on the left + rope bridge to the treehouse."""
    crude = mode == 'crude'
    x, y, z, r = LEFT_TRUNK['x'], LEFT_TRUNK['y'], LEFT_TRUNK['deck_z'], LEFT_TRUNK['deck_r']
    if crude:
        cylinder(0.32, 6.0, (x, y, GROUND_Z + 3.0), (0, 0, 0), M['post'], 8)
        cylinder(r, 0.12, (x, y, z), (0, 0, 0), M['deck'], 10)
    else:
        bpy.ops.mesh.primitive_cylinder_add(vertices=48, radius=r, depth=0.08, location=(x, y, z))
        dk = bpy.context.object
        dk.data.materials.append(M['deck'])
        uv_unwrap(dk)
        for k in range(10):
            a = k / 10 * 2 * math.pi
            beam((x + 0.3 * math.cos(a), y + 0.3 * math.sin(a), z - 0.04), (x + (r - 0.05) * math.cos(a), y + (r - 0.05) * math.sin(a), z - 0.5),
                 0.03, M['trim'], 6, square=True)
    # rope bridge: from left deck edge to treehouse deck left edge
    th = bpy.data.objects['treehouse']
    a = Vector((x + INNER * r * 0.9, y + 0.1, z))
    b = th.matrix_world @ Vector((-INNER * TH['deck_w'] / 2, 0.2, TH['deck_z'] - GROUND_Z))
    n = 16 if not crude else 5
    sag = 0.35
    pts = []
    for i in range(n + 1):
        t = i / n
        p = a.lerp(b, t)
        p.z -= sag * 4 * t * (1 - t)
        pts.append(p)
    d = (b - a).normalized()
    side = d.cross(Vector((0, 0, 1))).normalized()
    for i in range(n):
        p = (pts[i] + pts[i + 1]) / 2
        seg = pts[i + 1] - pts[i]
        if crude:
            box((seg.length * 0.98, 0.5, 0.06), p, (0, -math.atan2(seg.z, seg.xy.length), math.atan2(d.y, d.x)), M['deck'])
        else:
            pl = box((0.11, 0.55, 0.04), p, (0, -math.atan2(seg.z, seg.xy.length), math.atan2(d.y, d.x)), M['deck'], None, 0.006)
            uv_unwrap(pl)
    if not crude:
        for s in (-1, 1):
            for i in range(n):
                p0 = pts[i] + side * s * 0.3 + Vector((0, 0, 0.55))
                p1 = pts[i + 1] + side * s * 0.3 + Vector((0, 0, 0.55))
                beam(p0, p1, 0.012, M['rope'], 6)
                if i % 2 == 0:
                    beam(pts[i] + side * s * 0.28, p0, 0.008, M['rope'], 5)


# ------------------------------------------------------------------ real forest dressing
def import_gltf(name):
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=PH + f"models/{name}/{name}.gltf")
    new = [o for o in bpy.data.objects if o not in before]
    col = bpy.data.collections.new('src_' + name)
    for o in new:
        for c in o.users_collection:
            c.objects.unlink(o)
        col.objects.link(o)
    return col, [o for o in new if o.type == 'MESH']


def instance(col_obj_meshes, loc, rot_z, scale):
    """Linked duplicate of a single mesh object (shares mesh data, cheap)."""
    src = col_obj_meshes
    o = bpy.data.objects.new(src.name + '_i', src.data)
    bpy.context.scene.collection.objects.link(o)
    o.location = loc
    o.rotation_euler = (0, 0, rot_z)
    o.scale = (scale, scale, scale)
    return o


def reset_origin_to_base(o):
    """Move mesh so its lowest point sits at z=0 and centre is at x,y=0 (gltf variants are offset)."""
    import bmesh
    me = o.data
    xs = [v.co.x for v in me.vertices]
    ys = [v.co.y for v in me.vertices]
    zs = [v.co.z for v in me.vertices]
    cx, cy, mz = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2, min(zs)
    for v in me.vertices:
        v.co.x -= cx
        v.co.y -= cy
        v.co.z -= mz


def forest_real(cfg, rnd):
    _, firs = import_gltf('fir_tree_01')
    for f in firs:
        f.matrix_world.identity()
        reset_origin_to_base(f)
        f.hide_render = True
    _, ferns = import_gltf('fern_02')
    for f in ferns:
        f.matrix_world.identity()
        reset_origin_to_base(f)
        f.hide_render = True
    _, rocks = import_gltf('rock_moss_set_01')
    for f in rocks:
        f.matrix_world.identity()
        reset_origin_to_base(f)
        f.hide_render = True
    # the trunk the left platform wraps around + firs framing the treehouse
    spots = [(LEFT_TRUNK['x'], LEFT_TRUNK['y'], 1.0), (TH['x'] + INNER * 0.9, TH['y'] + 1.2, 1.05)] + cfg.get('firs', [
        (0.6, 9.0, 0.95), (-3.6, 8.2, 1.1), (4.2, 10.5, 1.0), (-1.8, 13.0, 1.05),
        (2.6, 15.0, 1.0), (-5.5, 11.0, 0.95), (6.5, 8.0, 1.1), (-0.9, 18.0, 1.0), (4.0, 20.0, 1.0)])
    for i, (x, y, s) in enumerate(spots):
        instance(firs[i % len(firs)], (x, y, GROUND_Z - 0.05), rnd.uniform(0, 6.28), s)
    # ferns scattered in the mid-ground, kept out of the monke/face silhouette
    for i in range(cfg.get('ferns', 70)):
        x = rnd.uniform(-6.5, 6.5)
        y = rnd.uniform(1.2, 14.0)
        if abs(x) < 0.7 and y < 2.5:
            continue
        instance(ferns[rnd.randrange(len(ferns))], (x, y, GROUND_Z), rnd.uniform(0, 6.28), rnd.uniform(1.0, 1.8))
    for i in range(cfg.get('rocks', 8)):
        x = rnd.uniform(-4, 5)
        y = rnd.uniform(2.0, 8.0)
        if abs(x) < 0.8 and y < 3:
            continue
        instance(rocks[rnd.randrange(len(rocks))], (x, y, GROUND_Z - 0.05), rnd.uniform(0, 6.28), rnd.uniform(0.25, 0.5))


def ground(M, mode):
    if mode == 'real':
        bpy.ops.mesh.primitive_plane_add(size=160, location=(0, 40, GROUND_Z))
        g = bpy.context.object
        g.data.materials.append(M['ground'])
        uv_unwrap(g)
        # gentle undulation so the ground isn't a perfect plane
        sub = g.modifiers.new('sub', 'SUBSURF')
        sub.subdivision_type = 'SIMPLE'
        sub.levels = sub.render_levels = 5
        tex = bpy.data.textures.new('gnoise', 'CLOUDS')
        tex.noise_scale = 3.0
        dp = g.modifiers.new('disp', 'DISPLACE')
        dp.texture = tex
        dp.strength = 0.25
        dp.mid_level = 0.6


# ------------------------------------------------------------------ world: HDRI + golden sun + haze
def world_real(scn, cfg):
    W = cfg.get('hdri', {})
    world = bpy.data.worlds.new('hdri')
    scn.world = world
    world.use_nodes = True
    nt = world.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new('ShaderNodeOutputWorld')
    bg = nt.nodes.new('ShaderNodeBackground')
    env = nt.nodes.new('ShaderNodeTexEnvironment')
    env.image = bpy.data.images.load(PH + f"hdri/{W.get('name', 'misty_pines')}_4k.hdr")
    tc = nt.nodes.new('ShaderNodeTexCoord')
    mp = nt.nodes.new('ShaderNodeMapping')
    mp.inputs['Rotation'].default_value = (0, 0, math.radians(W.get('rot', 0)))
    nt.links.new(tc.outputs['Generated'], mp.inputs['Vector'])
    nt.links.new(mp.outputs['Vector'], env.inputs['Vector'])
    tint = nt.nodes.new('ShaderNodeMix')
    tint.data_type = 'RGBA'
    tint.blend_type = 'MULTIPLY'
    tint.inputs['Factor'].default_value = 1.0
    tint.inputs['B'].default_value = srgb(W.get('tint', '#FFD9A6'))
    nt.links.new(env.outputs['Color'], tint.inputs['A'])
    nt.links.new(tint.outputs['Result'], bg.inputs['Color'])
    bg.inputs['Strength'].default_value = W.get('strength', 1.0)
    nt.links.new(bg.outputs['Background'], out.inputs['Surface'])
    # golden-hour sun from behind the treehouse, low, shining toward the camera
    S = cfg.get('sun', {})
    sun = bpy.data.lights.new('golden_sun', 'SUN')
    sun.energy = S.get('energy', 4.5)
    sun.angle = math.radians(S.get('angle', 3.0))
    sun.color = srgb(S.get('color', '#FFB15E'))[:3]
    so = bpy.data.objects.new('golden_sun', sun)
    scn.collection.objects.link(so)
    d = Vector(S.get('dir', (-0.25, -1.0, -0.22))).normalized()
    so.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    # atmospheric haze for light shafts
    if cfg.get('haze'):
        H = cfg['haze']
        bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 9, 3))
        hb = bpy.context.object
        hb.name = 'haze'
        hb.scale = (24, 22, 10)
        hm = bpy.data.materials.new('haze')
        hm.use_nodes = True
        hn = hm.node_tree
        hn.nodes.remove(hn.nodes['Principled BSDF'])
        pv = hn.nodes.new('ShaderNodeVolumePrincipled')
        pv.inputs['Density'].default_value = H.get('density', 0.02)
        pv.inputs['Anisotropy'].default_value = H.get('aniso', 0.7)
        pv.inputs['Color'].default_value = srgb(H.get('color', '#FFE6C8'))
        hn.links.new(pv.outputs['Volume'], hn.nodes['Material Output'].inputs['Volume'])
        hb.data.materials.append(hm)
        hb.visible_shadow = False


def world_crude(scn, cfg):
    pass  # crude.py keeps its own flat Unity sky


def build(scn, cfg, mode='real'):
    rnd = random.Random(cfg.get('seed', 11))
    set_layout(cfg, mode)
    M = mats(mode)
    treehouse(M, mode)
    left_platform(M, mode)
    if mode == 'real':
        ground(M, mode)
        forest_real(cfg, rnd)
        world_real(scn, cfg)
    return M
