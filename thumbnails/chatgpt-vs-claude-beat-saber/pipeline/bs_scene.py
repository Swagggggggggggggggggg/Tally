"""Beat Saber thumbnail scene, one shared layout rendered two ways.
  mode 'crude': ChatGPT's decent-but-flat build (Unity default sky, matte cubes, unlit saber sticks, grey arches)
  mode 'real' : Claude's neon build (dark fog, glowing sabers + trail, sliced cube with sparks, lit arches, glossy track)
Both modes use the same camera and geometry positions, so the halves meet at the thumbnail divider.
Usage: blender -b -P bs_scene.py -- '<json config>'
"""
import bpy, bmesh, sys, json, math, random
from mathutils import Vector, Matrix, Euler

cfg = json.loads(sys.argv[sys.argv.index('--') + 1])
MODE = cfg.get('mode', 'real')
REAL = MODE == 'real'
rnd = random.Random(cfg.get('seed', 7))
bpy.ops.wm.read_factory_settings(use_empty=True)
scn = bpy.context.scene
COL = bpy.context.scene.collection


def srgb(h):
    h = h.lstrip('#')
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c) + (1.0,)


def link(o):
    COL.objects.link(o)
    return o


# ------------------------------------------------------------------ materials
def mat_flat(name, hx, rough=0.6, metal=0.0, spec=0.4):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = srgb(hx)
    b.inputs['Roughness'].default_value = rough
    b.inputs['Metallic'].default_value = metal
    b.inputs['Specular IOR Level'].default_value = spec
    return m


def mat_emit(name, hx, strength, base='#000000'):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = srgb(base)
    b.inputs['Emission Color'].default_value = srgb(hx)
    b.inputs['Emission Strength'].default_value = strength
    b.inputs['Roughness'].default_value = 0.3
    return m


def mat_glow_fade(name, hx, strength, axis='X'):
    """Emissive ribbon that fades to transparent along UV.x (saber trails)."""
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    em = nt.nodes.new('ShaderNodeEmission')
    em.inputs['Color'].default_value = srgb(hx)
    em.inputs['Strength'].default_value = strength
    tr = nt.nodes.new('ShaderNodeBsdfTransparent')
    mix = nt.nodes.new('ShaderNodeMixShader')
    uv = nt.nodes.new('ShaderNodeTexCoord')
    sep = nt.nodes.new('ShaderNodeSeparateXYZ')
    ramp = nt.nodes.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].position = 0.0
    ramp.color_ramp.elements[0].color = (0.35, 0.35, 0.35, 1)
    ramp.color_ramp.elements[1].position = 1.0
    ramp.color_ramp.elements[1].color = (0, 0, 0, 1)
    nt.links.new(uv.outputs['UV'], sep.inputs[0])
    nt.links.new(sep.outputs[axis], ramp.inputs['Fac'])
    nt.links.new(ramp.outputs['Color'], mix.inputs['Fac'])
    nt.links.new(tr.outputs[0], mix.inputs[1])
    nt.links.new(em.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], out.inputs['Surface'])
    m.blend_method = 'BLEND'
    return m


C = cfg.get('colors', {})
RED, BLUE = C.get('red', '#FF1F2D'), C.get('blue', '#1F7BFF')
if REAL:
    M = dict(
        track=mat_flat('track', '#06070B', rough=0.12, metal=0.6, spec=0.8),
        arch=mat_flat('arch', '#0B0D14', rough=0.25, metal=0.8),
        neon_blue=mat_emit('neon_b', '#2E8BFF', cfg.get('neon', 18)),
        neon_red=mat_emit('neon_r', '#FF2846', cfg.get('neon', 18)),
        neon_white=mat_emit('neon_w', '#CFE6FF', cfg.get('neon', 18) * 0.8),
        cube_red=mat_emit('cube_r', '#C00010', cfg.get('cube_glow', 0.35), base='#B0000E'),
        cube_blue=mat_emit('cube_b', '#0A4FE0', cfg.get('cube_glow', 0.35), base='#0038B0'),
        frame_red=mat_emit('frame_r', '#FF3341', 2.5, base='#5A0006'),
        frame_blue=mat_emit('frame_b', '#3C8CFF', 2.5, base='#001A55'),
        arrow=mat_emit('arrow', '#FFFFFF', cfg.get('arrow', 9)),
        cut_blue=mat_emit('cut_b', '#4FA0FF', cfg.get('cut', 14)),
        saber_red=mat_emit('saber_r', '#FF2B3A', cfg.get('saber', 12)),
        saber_blue=mat_emit('saber_b', '#2F86FF', cfg.get('saber', 12)),
        core=mat_emit('core', '#E8F3FF', cfg.get('core', 22)),
        hilt=mat_flat('hilt', '#1B1D22', rough=0.35, metal=0.9),
        spark=mat_emit('spark', '#CFE8FF', cfg.get('spark', 25)),
        trail=mat_glow_fade('trail', '#2F86FF', cfg.get('trail', 3)),
        laser_blue=mat_emit('laser_b', '#2E8BFF', cfg.get('laser', 25)),
        laser_pink=mat_emit('laser_p', '#FF2EA6', cfg.get('laser', 25)),
    )
else:
    M = dict(
        track=mat_flat('track', '#8E949B', rough=0.8), arch=mat_flat('arch', '#B9BEC4', rough=0.7),
        neon_blue=mat_flat('edge', '#EDEDED', rough=0.7), neon_red=mat_flat('edge', '#EDEDED', rough=0.7),
        neon_white=mat_flat('edge_w', '#EDEDED', rough=0.7),
        cube_red=mat_flat('cube_r', '#D6262E', rough=0.55), cube_blue=mat_flat('cube_b', '#2E62D6', rough=0.55),
        frame_red=mat_flat('frame_r', '#D6262E', rough=0.55), frame_blue=mat_flat('frame_b', '#2E62D6', rough=0.55),
        arrow=mat_flat('arrow', '#FFFFFF', rough=0.5), cut_blue=mat_flat('cut', '#FFFFFF'),
        saber_red=mat_emit('saber_r', '#FF3B45', cfg.get('crude_saber', 1.6), base='#E0303A'),
        saber_blue=mat_emit('saber_b', '#3B78FF', cfg.get('crude_saber', 1.6), base='#2E62D6'),
        core=mat_flat('core', '#FFFFFF'), hilt=mat_flat('hilt', '#6E737A', rough=0.6),
        spark=mat_flat('spark', '#FFFFFF'), trail=mat_flat('trail', '#FFFFFF'),
        laser_blue=None, laser_pink=None,
    )


# ------------------------------------------------------------------ geometry helpers
def box(size, loc, rot=(0, 0, 0), mat=None, bevel=0.0, name='box'):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot)
    o = bpy.context.object
    o.name = name
    o.scale = size
    if bevel:
        bpy.ops.object.transform_apply(scale=True, location=False, rotation=False)
        bv = o.modifiers.new('bev', 'BEVEL')
        bv.width = bevel
        bv.segments = 3
    if mat:
        o.data.materials.append(mat)
    return o


def beam(p0, p1, r, mat, verts=16, name='beam'):
    p0, p1 = Vector(p0), Vector(p1)
    d = p1 - p0
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r, depth=d.length, location=(p0 + p1) / 2)
    o = bpy.context.object
    o.name = name
    o.rotation_euler = d.to_track_quat('Z', 'Y').to_euler()
    if mat:
        o.data.materials.append(mat)
    for p in o.data.polygons:
        p.use_smooth = True
    return o


# ------------------------------------------------------------------ shared layout
L = cfg.get('layout', {})
TRACK_W = L.get('track_w', 3.2)
ARCH_Y = L.get('arch_y', [7, 14, 21, 28, 35, 42, 49, 56, 63, 70])
ARCH_W, ARCH_H, ARCH_T = L.get('arch_w', 9.0), L.get('arch_h', 7.0), L.get('arch_t', 0.35)

# track: a long platform down the middle
box((TRACK_W, 120, 0.3), (0, 55, -0.15), mat=M['track'], name='track')
for sx in (-1, 1):
    box((0.06, 120, 0.06), (sx * (TRACK_W / 2 - 0.03), 55, 0.01), mat=M['neon_red' if sx < 0 else 'neon_blue'], name='edge')
# lane lines (four lanes)
for lx in (-0.8, 0.0, 0.8):
    box((0.012, 120, 0.004), (lx, 55, 0.002), mat=M['neon_white'] if REAL else M['arch'], name='lane')
# arches over the track, receding to the vanishing point (they straddle the divider)
for i, y in enumerate(ARCH_Y):
    for sx in (-1, 1):
        box((ARCH_T, ARCH_T, ARCH_H), (sx * ARCH_W / 2, y, ARCH_H / 2 - 0.3), mat=M['arch'], name='arch_leg')
    box((ARCH_W + ARCH_T * 1.08, ARCH_T * 1.04, ARCH_T), (0, y, ARCH_H - 0.3), mat=M['arch'], name='arch_top')   # overhangs the legs: no coplanar faces
    if REAL:
        # neon tube on the inner edge of each arch, alternating colours
        nm = M['neon_blue'] if i % 2 == 0 else M['laser_pink']
        h = ARCH_H - 0.3 - ARCH_T / 2 - 0.05
        w = ARCH_W / 2 - ARCH_T / 2 - 0.05
        y0 = y - ARCH_T / 2 - 0.02
        for a, b in (((-w, y0, 0), (-w, y0, h)), ((w, y0, 0), (w, y0, h)), ((-w, y0, h), (w, y0, h))):
            beam(a, b, 0.035, nm, verts=8, name='arch_neon')
# side towers beyond the arches
for sx in (-1, 1):
    for y in L.get('tower_y', [10, 24, 38, 52]):
        box((1.2, 1.2, 18), (sx * 9.5, y, 8.7), mat=M['arch'], name='tower')
        if REAL:
            beam((sx * 8.88, y - 0.61, 0.5), (sx * 8.88, y - 0.61, 16), 0.04, M['neon_blue'], 8, 'tower_neon')

# far notes coming down the track (same spots in both modes)
NOTE = L.get('note', 0.5)


def note(loc, colour, rot_deg=(0, 0, 0), arrow=True, name='note'):
    """Beat Saber note: bevelled cube, lighter frame, white chevron arrow on the camera-facing side."""
    rot = Euler([math.radians(v) for v in rot_deg], 'XYZ')
    root = bpy.data.objects.new(name, None)
    link(root)
    root.location = loc
    root.rotation_euler = rot
    parts = []
    c = box((NOTE, NOTE, NOTE), (0, 0, 0), mat=M['cube_' + colour], bevel=NOTE * 0.12 if REAL else 0.0, name=name + '_cube')
    parts.append(c)
    if REAL:
        # glowing frame lines on the front face edges
        f = NOTE / 2 - NOTE * 0.07
        y = -NOTE / 2 - 0.004
        for a, b in (((-f, y, -f), (f, y, -f)), ((-f, y, f), (f, y, f)), ((-f, y, -f), (-f, y, f)), ((f, y, -f), (f, y, f))):
            parts.append(beam(a, b, NOTE * 0.018, M['frame_' + colour], 6, name + '_frame'))
    if arrow:
        # chevron pointing down (down-cut note)
        w, h, t = NOTE * 0.62, NOTE * 0.22, 0.012
        me = bpy.data.meshes.new(name + '_arrow')
        y = -NOTE / 2 - 0.006
        vz = NOTE * 0.18
        verts = [(-w / 2, y, vz), (w / 2, y, vz), (0, y, vz - h)]
        me.from_pydata(verts, [], [(0, 1, 2)])
        ao = bpy.data.objects.new(name + '_arrow', me)
        link(ao)
        ao.data.materials.append(M['arrow'])
        parts.append(ao)
    for p in parts:
        p.parent = root
    return root, parts


for (x, y, z, col) in L.get('far_notes', [(-0.4, 9.0, 0.9, 'red'), (0.4, 9.0, 0.9, 'blue'), (-1.2, 15.0, 1.5, 'red'),
                                          (1.2, 15.0, 1.5, 'blue'), (0.4, 21.0, 0.5, 'blue'), (-0.4, 25.0, 1.4, 'red')]):
    note((x, y, z), col, name='far')

# ------------------------------------------------------------------ hero hits
H = cfg.get('hero', {})


def saber(hilt_pos, tip_dir, colour, length=1.05):
    hp, d = Vector(hilt_pos), Vector(tip_dir).normalized()
    parts = [beam(hp - d * 0.22, hp, 0.028, M['hilt'], 16, 'hilt')]
    if REAL:
        parts.append(beam(hp, hp + d * length, 0.010, M['core'], 16, 'blade_core'))
        parts.append(beam(hp, hp + d * length, 0.022, M['saber_' + colour], 16, 'blade_glow'))
    else:
        parts.append(beam(hp, hp + d * length, 0.022, M['saber_' + colour], 10, 'blade'))
    return parts


# LEFT (ChatGPT side): red note, red saber clipping straight through it (no cut, no effects)
LN = H.get('left_note', [-0.62, 0.45, 1.18])
LR = H.get('left_note_rot', [8, 10, -8])
note(LN, 'red', LR, name='heroL')
saber(H.get('left_hilt', [-0.30, -0.55, 0.78]), H.get('left_dir', [-0.42, 1.0, 0.55]), 'red', H.get('left_len', 1.05))

# RIGHT (Claude side): blue note sliced in two along the saber's swing plane
RN = Vector(H.get('right_note', [0.62, 0.45, 1.18]))
RR = H.get('right_note_rot', [8, -10, 8])
cut_n = Vector(H.get('cut_normal', [0.55, -0.15, 0.82])).normalized()   # normal of the slice plane (world)
gap = H.get('cut_gap', 0.11)
if REAL:
    root, parts = note(tuple(RN), 'blue', RR, name='heroR')
    bpy.context.view_layer.update()
    # bake each part to world space, then split every part by the slice plane into two halves
    halves = {+1: [], -1: []}
    for p in parts:
        mw = p.matrix_world.copy()
        dg = bpy.context.evaluated_depsgraph_get()
        me = bpy.data.meshes.new_from_object(p.evaluated_get(dg))
        me.transform(mw)
        mats = list(p.data.materials)
        for side in (+1, -1):
            bm = bmesh.new()
            bm.from_mesh(me)
            geom = bm.verts[:] + bm.edges[:] + bm.faces[:]
            res = bmesh.ops.bisect_plane(bm, geom=geom, plane_co=RN, plane_no=cut_n,
                                         clear_inner=(side == +1), clear_outer=(side == -1))
            cut_edges = [e for e in res['geom_cut'] if isinstance(e, bmesh.types.BMEdge)]
            nf_before = len(bm.faces)
            if cut_edges:
                bmesh.ops.holes_fill(bm, edges=cut_edges, sides=0)
            if not bm.verts:
                bm.free()
                continue
            hm = bpy.data.meshes.new(p.name + ('_a' if side > 0 else '_b'))
            bm.to_mesh(hm)
            bm.free()
            for mt in mats:
                hm.materials.append(mt)
            hm.materials.append(M['cut_blue'])
            # faces created by the fill are the cut faces -> glowing material
            for poly in hm.polygons[nf_before:]:
                poly.material_index = len(hm.materials) - 1
            ho = bpy.data.objects.new(hm.name, hm)
            link(ho)
            halves[side].append(ho)
        bpy.data.objects.remove(p)
    # push the halves apart along the cut normal, with a little spin
    for side, objs in halves.items():
        for o in objs:
            o.location = cut_n * gap * side * 0.5
            o.rotation_mode = 'XYZ'
        if objs:
            piv = bpy.data.objects.new('half_pivot', None)
            link(piv)
            piv.location = RN
            bpy.context.view_layer.update()
            for o in objs:
                o.parent = piv
                o.matrix_parent_inverse = piv.matrix_world.inverted()
            blade_axis = Vector(H.get('right_dir', [0.3, 1.0, 0.05])).normalized()
            piv.rotation_mode = 'QUATERNION'
            piv.rotation_quaternion = Matrix.Rotation(math.radians(side * H.get('open', 18)), 4, blade_axis).to_quaternion()
    # sparks: a few short streaks bursting from the two ends of the cut line
    bd = Vector(H.get('right_dir', [0.3, 1.0, 0.05])).normalized()
    for i in range(H.get('sparks', 14)):
        end_ = rnd.choice((-1, 1))
        base = RN + bd * end_ * NOTE * rnd.uniform(0.55, 0.75)
        d = (bd * end_ * rnd.uniform(0.3, 0.8) + cut_n * rnd.uniform(-1.0, 1.0)).normalized()
        off = base + d * rnd.uniform(0.02, 0.06)
        beam(off, off + d * rnd.uniform(0.04, 0.12), rnd.uniform(0.0025, 0.0045), M['spark'], 6, 'spark')
    # blue saber already past the cut, with a fading trail behind it
    hp = Vector(H.get('right_hilt', [0.30, -0.55, 0.78]))
    d1 = Vector(H.get('right_dir', [0.30, 1.0, 0.05])).normalized()
    saber(hp, d1, 'blue', H.get('right_len', 1.05))
    ax = Vector(H.get('trail_axis', [0.0, 0.25, 1.0])).normalized()   # swing rotation axis through the hilt
    steps, sweep = 14, math.radians(H.get('trail_deg', 35))
    vs, fs = [], []
    for k in range(steps + 1):
        R = Matrix.Rotation(-sweep * k / steps, 3, ax)
        dk = R @ d1
        vs += [tuple(hp + dk * H.get('right_len', 1.05) * H.get('trail_in', 0.62)), tuple(hp + dk * H.get('right_len', 1.05))]
    for k in range(steps):
        a = 2 * k
        fs.append((a, a + 1, a + 3, a + 2))
    me = bpy.data.meshes.new('trail')
    me.from_pydata(vs, [], fs)
    uvl = me.uv_layers.new()
    for poly in me.polygons:
        for li in poly.loop_indices:
            vi = me.loops[li].vertex_index
            uvl.data[li].uv = ((vi // 2) / steps, vi % 2)
    tr = bpy.data.objects.new('trail', me)
    link(tr)
    tr.data.materials.append(M['trail'])
else:
    # ChatGPT side builds the same right-hand hit but without slicing (only the left half of this render is used)
    note(tuple(RN), 'blue', RR, name='heroR')
    saber(H.get('right_hilt', [0.30, -0.55, 0.78]), H.get('right_dir', [0.30, 1.0, 0.05]), 'blue', H.get('right_len', 1.05))

# lasers (real only): long beams fanning from the far towers across the sky
if REAL:
    for i, (sx, y, ang, col) in enumerate(L.get('lasers', [(1, 40, 28, 'blue'), (1, 44, 40, 'pink'), (1, 48, 52, 'blue'),
                                                           (-1, 40, 28, 'pink'), (-1, 44, 40, 'blue'), (-1, 48, 52, 'pink')])):
        p0 = Vector((sx * 9.5, y, 14))
        d = Vector((-sx * math.cos(math.radians(ang)), -0.55, math.sin(math.radians(ang)) * 0.35)).normalized()
        beam(p0, p0 + d * 60, 0.05, M['laser_' + col], 8, 'laser')

# ------------------------------------------------------------------ world + lights
world = bpy.data.worlds.new('w')
scn.world = world
world.use_nodes = True
wn, wl = world.node_tree.nodes, world.node_tree.links
for n in list(wn):
    wn.remove(n)
out = wn.new('ShaderNodeOutputWorld')
bg = wn.new('ShaderNodeBackground')
tc = wn.new('ShaderNodeTexCoord')
sep = wn.new('ShaderNodeSeparateXYZ')
mr = wn.new('ShaderNodeMapRange')
mr.inputs['From Min'].default_value = -1.0
mr.inputs['From Max'].default_value = 1.0
ramp = wn.new('ShaderNodeValToRGB')
wl.new(tc.outputs['Generated'], sep.inputs[0])
wl.new(sep.outputs['Z'], mr.inputs['Value'])
wl.new(mr.outputs['Result'], ramp.inputs['Fac'])
stops = cfg.get('sky') or ([[0.0, '#020306'], [0.5, '#0A1430'], [0.62, '#060A1C'], [1.0, '#020308']] if REAL else
                           [[0.0, '#5E5E5E'], [0.495, '#7D8287'], [0.505, '#DCE3EA'], [0.56, '#B9CFE9'], [0.75, '#7FA6DA'], [1.0, '#4D7EC6']])
cr = ramp.color_ramp
while len(cr.elements) < len(stops):
    cr.elements.new(0.5)
for el, (pos, hx) in zip(cr.elements, stops):
    el.position = pos
    el.color = srgb(hx)
wl.new(ramp.outputs['Color'], bg.inputs['Color'])
bg.inputs['Strength'].default_value = cfg.get('sky_strength', 1.0)
wl.new(bg.outputs['Background'], out.inputs['Surface'])
if REAL and cfg.get('fog', 0.0):
    vs_ = wn.new('ShaderNodeVolumeScatter')
    vs_.inputs['Density'].default_value = cfg['fog']
    vs_.inputs['Color'].default_value = srgb(cfg.get('fog_col', '#9FB8FF'))
    wl.new(vs_.outputs[0], out.inputs['Volume'])

if REAL:
    # cool key from above-front so the hero cube faces read, plus coloured fills matching the sabers
    for name, loc, energy, col, size in (('key', (0.8, -1.2, 3.2), cfg.get('key', 45), '#B8D4FF', 2.0), ('fillB', (1.4, 0.6, 1.0), 40, '#2E8BFF', 1.0),
                                         ('fillR', (-1.4, 0.6, 1.0), 40, '#FF2846', 1.0)):
        l = bpy.data.lights.new(name, 'AREA')
        l.energy, l.size, l.color = energy, size, srgb(col)[:3]
        o = link(bpy.data.objects.new(name, l))
        o.location = loc
        o.rotation_euler = (Vector((0, 0.45, 1.18)) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
else:
    sun = bpy.data.lights.new('sun', 'SUN')
    sun.energy = cfg.get('sun', 3.0)
    sun.angle = math.radians(2)
    so = link(bpy.data.objects.new('sun', sun))
    so.rotation_euler = Euler([math.radians(v) for v in cfg.get('sun_rot', (50, 0, -25))], 'XYZ')

# ------------------------------------------------------------------ camera (identical in both modes)
CM = cfg.get('cam', {})
cam = bpy.data.cameras.new('cam')
co = link(bpy.data.objects.new('cam', cam))
co.location = Vector(CM.get('loc', (0, -1.7, 1.55)))
co.rotation_euler = (Vector(CM.get('target', (0, 6, 1.2))) - co.location).to_track_quat('-Z', 'Y').to_euler()
cam.lens = CM.get('lens', 24)
cam.dof.use_dof = False
scn.camera = co

R = cfg.get('render', {})
scn.render.engine = 'CYCLES'
scn.cycles.device = 'CPU'
scn.cycles.samples = R.get('samples', 32)
scn.cycles.use_denoising = True
scn.cycles.volume_step_rate = 4.0
scn.render.resolution_x = R.get('w', 1280)
scn.render.resolution_y = R.get('h', 720)
scn.view_settings.view_transform = cfg.get('view', 'AgX' if REAL else 'Standard')
scn.view_settings.look = cfg.get('look', 'AgX - Punchy' if REAL else 'None')
scn.render.image_settings.file_format = 'PNG'
scn.render.image_settings.color_depth = '16'
scn.render.filepath = cfg['out']

# bloom (real only) via the compositor glare node
if REAL and cfg.get('bloom', True):
    scn.use_nodes = True
    nt = scn.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    rl = nt.nodes.new('CompositorNodeRLayers')
    gl = nt.nodes.new('CompositorNodeGlare')
    comp = nt.nodes.new('CompositorNodeComposite')
    B = cfg.get('bloom_cfg', {})
    try:
        gl.glare_type = 'BLOOM'
    except Exception:
        gl.glare_type = 'FOG_GLOW'
    gl.quality = 'HIGH'
    for sock, val in (('Threshold', B.get('threshold', 1.5)), ('Size', B.get('size', 0.55)), ('Strength', B.get('strength', 0.6)),
                      ('Saturation', B.get('saturation', 1.25)), ('Smoothness', B.get('smooth', 0.2))):
        if sock in gl.inputs:
            gl.inputs[sock].default_value = val
    nt.links.new(rl.outputs['Image'], gl.inputs['Image'])
    nt.links.new(gl.outputs['Image'], comp.inputs['Image'])

if cfg.get('save_blend'):
    bpy.ops.file.pack_all()
    bpy.ops.wm.save_as_mainfile(filepath=cfg['save_blend'], compress=True)
bpy.ops.render.render(write_still=True)
print('DONE', cfg['out'])
