"""ChatGPT's 'decent but not Claude' Gorilla Tag monke: a from-scratch low-poly gorilla.
Skin-modifier body with long arms, round head with brow ridge, curved GT-style face plate,
flat brand-coloured fur. Same local frame as crude.py (faces -y, head centre z~0.5).
"""
import bpy, bmesh, math
from mathutils import Vector, Matrix


def _obj(name, me):
    o = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(o)
    return o


def _apply(o):
    bpy.context.view_layer.objects.active = o
    for m in list(o.modifiers):
        bpy.ops.object.modifier_apply(modifier=m.name)


def _flat(o):
    for p in o.data.polygons:
        p.use_smooth = False


def _skin_body(G, mat):
    """Torso + arms as one skinned skeleton (gives a chunky organic low-poly mesh)."""
    sx_raise = G.get('raise_side', -1)          # which arm does the peace sign (-1 = screen left)
    hx, hz = G.get('wrist_x', 0.25), G.get('wrist_z', 0.60)
    V = [  # (pos, radius_x, radius_y)
        ((0, 0.03, -0.30), 0.23, 0.19),   # 0 hips
        ((0, 0.01, -0.05), 0.27, 0.22),   # 1 belly
        ((0, 0.00, 0.15), 0.28, 0.22),    # 2 chest
        ((0, 0.02, G.get('neck_z', 0.36)), 0.17, 0.15),    # 3 neck
    ]
    E = [(0, 1), (1, 2), (2, 3)]
    for sx in (-1, 1):
        base = len(V)
        if sx == sx_raise:
            arm = [((sx * 0.29, 0.03, 0.25), 0.105, 0.10),          # shoulder
                   ((sx * 0.43, -0.03, 0.22), 0.085, 0.08),         # elbow out to the side
                   ((sx * hx, -0.10, hz), 0.07, 0.065)]             # wrist up beside the head
        else:
            arm = [((sx * 0.29, 0.03, 0.25), 0.105, 0.10),
                   ((sx * 0.40, -0.04, -0.05), 0.085, 0.08),
                   ((sx * 0.42, -0.10, -0.36), 0.07, 0.065),
                   ((sx * 0.42, -0.13, -0.47), 0.095, 0.085)]      # knuckle fist
        V += arm
        E.append((2, base))
        E += [(base + i, base + i + 1) for i in range(len(arm) - 1)]
    me = bpy.data.meshes.new('g_body')
    me.from_pydata([v[0] for v in V], E, [])
    o = _obj('g_body', me)
    sk = o.modifiers.new('skin', 'SKIN')
    sk.use_smooth_shade = False
    for i, (_, rx, ry) in enumerate(V):
        o.data.skin_vertices[0].data[i].radius = (rx, ry)
    o.data.skin_vertices[0].data[0].use_root = True
    sub = o.modifiers.new('sub', 'SUBSURF')
    sub.levels = sub.render_levels = G.get('body_subd', 1)
    _apply(o)
    _flat(o)
    o.data.materials.append(mat)
    return o, Vector((sx_raise * hx, -0.10, hz))


def _head(G, M):
    hr = G.get('head_r', 0.17)
    c = Vector((0, -0.03, G.get('head_z', 0.53)))
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=16, v_segments=11, radius=hr)
    me = bpy.data.meshes.new('g_head')
    bm.to_mesh(me); bm.free()
    head = _obj('g_head', me)
    head.location = c
    head.scale = (1.06, 0.97, 0.96)
    _flat(head); head.data.materials.append(M['fur'])
    parts = [head]
    # brow ridge: a squashed bar across the top of the face
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=12, v_segments=6, radius=1.0)
    me = bpy.data.meshes.new('g_brow'); bm.to_mesh(me); bm.free()
    brow = _obj('g_brow', me)
    brow.location = c + Vector((0, -hr * 0.84, hr * 0.40))
    brow.scale = (hr * G.get('brow_w', 0.70), hr * 0.20, hr * 0.13)
    _flat(brow); brow.data.materials.append(M['fur'])
    if G.get('brow_w', 0.70) > 0:
        parts.append(brow)
    else:
        bpy.data.objects.remove(brow)
    # face plate: GT-style outline (wide eye band, narrowing muzzle) cut out of a slightly larger sphere
    outline = [(-0.118, 0.095), (-0.04, 0.085), (0.0, 0.065), (0.04, 0.085), (0.118, 0.095), (0.128, 0.03),
               (0.112, -0.03), (0.082, -0.085), (0.055, -0.13), (0.0, -0.148), (-0.055, -0.13), (-0.082, -0.085),
               (-0.112, -0.03), (-0.128, 0.03)]
    k = hr / 0.165 * G.get('plate_scale', 0.88)
    bm = bmesh.new()
    vf = [bm.verts.new((x * k, -0.6, z * k)) for x, z in outline]
    vb = [bm.verts.new((x * k, 0.0, z * k)) for x, z in outline]
    bm.faces.new(vf); bm.faces.new(list(reversed(vb)))
    n = len(outline)
    for i in range(n):
        bm.faces.new((vf[i], vf[(i + 1) % n], vb[(i + 1) % n], vb[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new('g_faceprism'); bm.to_mesh(me); bm.free()
    prism = _obj('g_faceprism', me)
    prism.location = c
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=40, v_segments=24, radius=hr * 1.035)
    me = bpy.data.meshes.new('g_face'); bm.to_mesh(me); bm.free()
    face = _obj('g_face', me)
    face.location = c
    face.scale = (1.06, 0.97, 0.96)
    bo = face.modifiers.new('cut', 'BOOLEAN')
    bo.operation = 'INTERSECT'
    bo.object = prism
    _apply(face)
    bpy.data.objects.remove(prism)
    face.data.materials.append(M['plate'])
    parts.append(face)
    fy = c.y - hr * 0.97 * 1.035          # front surface of the plate
    # eyes: decent, symmetric, a bit too big and glossy (the 'AI cartoon' tell)
    er = G.get('eye_r', 0.034) * k
    for sx in (-1, 1):
        ex, ez = sx * 0.050 * k, c.z + 0.030 * k
        for r, mat, dy, sc in ((er, M['white'], 0.004, (1, 0.5, 1)), (er * 0.55, M['black'], -0.010, (1, 0.45, 1)),
                               (er * 0.16, M['white'], -0.017, (1, 0.4, 1))):
            bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=14, v_segments=9, radius=r)
            me = bpy.data.meshes.new('g_eye'); bm.to_mesh(me); bm.free()
            e = _obj('g_eye', me)
            off = (sx * -0.004 * k, 0, 0.007 * k) if r < er * 0.3 else (0, 0, 0)
            e.location = (ex + off[0], fy + dy, ez + off[2])
            e.scale = sc
            e.data.materials.append(mat)
            parts.append(e)
    # nostrils + mouth
    for sx in (-1, 1):
        bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=10, v_segments=6, radius=0.011 * k)
        me = bpy.data.meshes.new('g_nos'); bm.to_mesh(me); bm.free()
        nn = _obj('g_nos', me)
        nn.location = (sx * 0.018 * k, fy + 0.006, c.z - 0.050 * k)
        nn.scale = (1.2, 0.5, 0.8)
        nn.data.materials.append(M['black'])
        parts.append(nn)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, fy + 0.004, c.z - 0.098 * k))
    mo = bpy.context.object
    mo.scale = (0.060 * k, 0.012, 0.008 * k)
    mo.data.materials.append(M['black'])
    parts.append(mo)
    # ears
    for sx in (-1, 1):
        bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=10, v_segments=7, radius=0.042 * k)
        me = bpy.data.meshes.new('g_ear'); bm.to_mesh(me); bm.free()
        ea = _obj('g_ear', me)
        ea.location = (sx * hr * 1.04, c.y + 0.01, c.z + 0.015)
        ea.scale = (0.45, 0.9, 1.0)
        _flat(ea); ea.data.materials.append(M['plate'])
        parts.append(ea)
    return parts


def _peace_hand(wrist, sx, M, G):
    """Rounded palm + two raised fingers in a V, other fingers curled, thumb across."""
    parts = []
    up = Vector((sx * -0.10, -0.08, 1)).normalized()      # forearm direction continues up/in
    palm_c = wrist + up * G.get('palm_up', 0.035)
    bpy.ops.mesh.primitive_cube_add(size=1, location=palm_c)
    pm = bpy.context.object
    pm.scale = (0.105, 0.055, 0.10)
    pm.rotation_euler = up.to_track_quat('Z', 'Y').to_euler()
    bv = pm.modifiers.new('bev', 'BEVEL'); bv.width = 0.018; bv.segments = 2
    _apply(pm); _flat(pm); pm.data.materials.append(M['fur'])
    parts.append(pm)
    side = Vector((1, 0, 0))
    for i, (spread, ln) in enumerate(((-16, 0.15), (14, 0.14))):
        d = (Matrix.Rotation(math.radians(spread), 3, 'Y') @ up).normalized()
        base = palm_c + up * 0.045 + side * (-0.026 if i == 0 else 0.026)
        bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.022, depth=ln, location=base + d * ln / 2)
        f = bpy.context.object
        f.rotation_euler = d.to_track_quat('Z', 'Y').to_euler()
        _flat(f); f.data.materials.append(M['fur']); parts.append(f)
        bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=8, v_segments=6, radius=0.022)
        me = bpy.data.meshes.new('g_tip'); bm.to_mesh(me); bm.free()
        t = _obj('g_tip', me); t.location = base + d * ln
        _flat(t); t.data.materials.append(M['fur']); parts.append(t)
    # curled fingers: one rounded bar across the front of the palm (no separate knuckle balls)
    bpy.ops.mesh.primitive_cube_add(size=1, location=palm_c + up * 0.005 + Vector((0, -0.04, 0)))
    cf = bpy.context.object
    cf.scale = (0.10, 0.045, 0.05)
    cf.rotation_euler = up.to_track_quat('Z', 'Y').to_euler()
    bv = cf.modifiers.new('bev', 'BEVEL'); bv.width = 0.02; bv.segments = 3
    _apply(cf); _flat(cf); cf.data.materials.append(M['fur']); parts.append(cf)
    return parts


def _chest(G, M):
    bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=16, v_segments=10, radius=1.0)
    me = bpy.data.meshes.new('g_chest'); bm.to_mesh(me); bm.free()
    ch = _obj('g_chest', me)
    ch.location = (0, -0.165, 0.10)
    ch.scale = (0.19, 0.07, 0.17)
    _flat(ch); ch.data.materials.append(M['plate'])
    bpy.ops.object.text_add(location=(-0.078, -0.238, 0.12), rotation=(math.radians(84), 0, 0))
    t = bpy.context.object
    t.data.body = G.get('name', 'CHATGPT')
    t.data.size = 0.042
    t.data.extrude = 0.002
    t.data.materials.append(M['black'])
    return [ch, t]


def build(G, M):
    """M: dict of materials fur/plate/white/black. Returns all objects (unparented)."""
    body, wrist = _skin_body(G, M['fur'])
    parts = [body] + _head(G, M) + _chest(G, M)
    parts += _peace_hand(wrist, G.get('raise_side', -1), M, G)
    return parts
