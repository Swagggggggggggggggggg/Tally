"""The 'bad AI build' panel: a primitive-shape Gorilla Tag monke in a Unity-default prototype scene.
Usage: blender -b -P crude.py -- '<json config>'
"""
import bpy, sys, json, math, random
from mathutils import Vector, Euler

sys.path.insert(0, '/tmp/claude-0/-home-user-Tally/702e814a-b90a-5d68-bc9a-bc92c217492c/scratchpad/blender')
import gt

cfg = json.loads(sys.argv[sys.argv.index('--') + 1])
rnd = random.Random(cfg.get('seed', 3))
bpy.ops.wm.read_factory_settings(use_empty=True)
scn = bpy.context.scene
OX, OY, OZ = cfg.get('offset', (0.0, 0.0, 0.0))   # whole-monke offset to line up with the hero framing


def flat(name, hx, rough=0.55, spec=0.35):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = gt.srgb(hx)
    b.inputs['Roughness'].default_value = rough
    b.inputs['Specular IOR Level'].default_value = spec
    return m


M_BODY = flat('body', cfg.get('body', '#2B2B2B'))
M_FACE = flat('face', cfg.get('face_col', '#9C9C9C'))
M_EYE = flat('eye', '#0A0A0A', rough=0.2)
M_WHITE = flat('eyewhite', '#F2F2F2', rough=0.3)
M_MISSING = bpy.data.materials.new('missing')
M_MISSING.use_nodes = True
_nt = M_MISSING.node_tree
_b = _nt.nodes['Principled BSDF']
_ck = _nt.nodes.new('ShaderNodeTexChecker')
_ck.inputs['Color1'].default_value = gt.srgb('#FF00DC')
_ck.inputs['Color2'].default_value = gt.srgb('#111111')
_ck.inputs['Scale'].default_value = cfg.get('missing_scale', 6.0)
_tc = _nt.nodes.new('ShaderNodeTexCoord')
_nt.links.new(_tc.outputs['Object'], _ck.inputs['Vector'])
_nt.links.new(_ck.outputs['Color'], _b.inputs['Base Color'])
_b.inputs['Roughness'].default_value = 0.6

monke = []


def add(o, mat, smooth=False):
    o.data.materials.append(mat)
    for p in o.data.polygons:
        p.use_smooth = smooth
    monke.append(o)
    return o


def sphere(r, loc, mat, seg=12, rings=8, scale=(1, 1, 1)):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=seg, ring_count=rings, radius=r, location=loc)
    o = bpy.context.object
    o.scale = scale
    return add(o, mat)


def cyl(r, depth, loc, rot, mat, verts=10):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r, depth=depth, location=loc, rotation=rot)
    return add(bpy.context.object, mat)


def box(size, loc, rot, mat):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot)
    o = bpy.context.object
    o.scale = size
    return add(o, mat)


# ---- body: a Unity-style capsule, a bit too stiff and too narrow at the shoulders
BR = cfg.get('body_r', 0.27)
BH = cfg.get('body_h', 0.18)          # straight section of the capsule (real GT torsos are short)
cyl(BR, BH, (0, 0, 0.15 - BH / 2), (0, 0, 0), M_BODY, verts=12)
sphere(BR, (0, 0, 0.15), M_BODY, seg=12, rings=8)
sphere(BR, (0, 0, 0.15 - BH), M_BODY, seg=12, rings=8)
for o in monke[-3:]:
    o.scale = (1.0, 0.78, 1.0)
# ---- head: low-poly sphere sunk into the body, slightly off-centre
H = cfg.get('head', {})
hx, hz, hr = H.get('x', 0.015), H.get('z', 0.49), H.get('r', 0.155)
sphere(hr, (hx, -0.02, hz), M_BODY, seg=10, rings=7)
# face: a flat grey disc stuck on the front, crooked
fd = cyl(hr * 0.74, 0.03, (hx - 0.008, -0.02 - hr - 0.012, hz - 0.015), (math.radians(90), math.radians(cfg.get('face_tilt', 9)), 0), M_FACE, verts=14)
# eyes: mismatched sizes and heights (the 'AI made it' tell)
E = cfg.get('eyes', {})
fy = -0.02 - hr - 0.012 - 0.018
for ex, ez, er, pr, pdx, pdz in ((-0.045, 0.025, 0.034, 0.016, -0.012, 0.010), (0.050, 0.008, 0.026, 0.013, 0.010, -0.004)):
    sphere(er, (hx + ex, fy, hz + ez), M_WHITE, seg=10, rings=6, scale=(1, 0.45, 1))
    sphere(pr, (hx + ex + pdx, fy - 0.010, hz + ez + pdz), M_EYE, seg=8, rings=6, scale=(1, 0.5, 1))
# mouth: a thin black bar, tilted
box((0.070, 0.010, 0.010), (hx + 0.006, fy + 0.004, hz - 0.068), (0, math.radians(-8), 0), M_EYE)
# ears: different sizes
sphere(0.045, (hx - hr - 0.005, -0.01, hz + 0.01), M_FACE, seg=8, rings=6, scale=(0.5, 1, 1))
sphere(0.034, (hx + hr + 0.002, -0.01, hz + 0.03), M_FACE, seg=8, rings=6, scale=(0.5, 1, 1))
# chest patch: a flat box slapped on the front
box((0.23, 0.02, 0.24), (0.0, -0.215, 0.07), (0, math.radians(2), 0), M_FACE)
# name tag in Blender's default font (no pixel font: another tell)
bpy.ops.object.text_add(location=(-0.097, -0.228, 0.13), rotation=(math.radians(90), math.radians(-3), 0))
t = bpy.context.object
t.data.body = cfg.get('name', 'CHATGPT')
t.data.size = 0.050
t.data.extrude = 0.002
t.data.materials.append(M_EYE)
monke.append(t)
# arms: stiff straight cylinders in an A-pose, ball hands
A = cfg.get('arm_deg', 28)
for sx in (-1, 1):
    sh = Vector((sx * 0.25, 0, cfg.get('shoulder_z', 0.27)))
    arm_mat = M_MISSING if (cfg.get('missing_arm') and sx == -1) else M_BODY
    ang = math.radians(cfg.get('arm_deg_side', {}).get(str(sx), A))
    L = 0.80
    d = Vector((sx * math.sin(ang), -0.06, -math.cos(ang))).normalized()
    mid = sh + d * (L / 2)
    rot = d.to_track_quat('Z', 'Y').to_euler()
    cyl(0.062, L, tuple(mid), tuple(rot), arm_mat, verts=8)
    sphere(0.085, tuple(sh + d * L), arm_mat, seg=8, rings=6)
    sphere(0.072, tuple(sh), M_BODY, seg=8, rings=6)

# group the whole crude monke under one root so it can be scaled/placed to match the real model
bpy.ops.object.empty_add(location=(0, 0, 0))
CR = bpy.context.object
CR.name = 'crude_root'
for o in monke:
    o.parent = CR
SC = cfg.get('scale', 1.0)
CR.scale = (SC, SC, SC)
CR.location = (OX, OY, OZ)
CR.rotation_euler = (0, 0, math.radians(cfg.get('turn', 0.0)))
bpy.context.view_layer.update()

# ---------------------------------------------------------------- Unity-default style world
world = bpy.data.worlds.new('sky')
scn.world = world
world.use_nodes = True
wn, wl = world.node_tree.nodes, world.node_tree.links
for n in list(wn):
    wn.remove(n)
out = wn.new('ShaderNodeOutputWorld')
bg = wn.new('ShaderNodeBackground')
tc = wn.new('ShaderNodeTexCoord')
sep = wn.new('ShaderNodeSeparateXYZ')
ramp = wn.new('ShaderNodeValToRGB')
wl.new(tc.outputs['Generated'], sep.inputs[0])
mr = wn.new('ShaderNodeMapRange')
mr.inputs['From Min'].default_value = -1.0
mr.inputs['From Max'].default_value = 1.0
wl.new(sep.outputs['Z'], mr.inputs['Value'])
wl.new(mr.outputs['Result'], ramp.inputs['Fac'])
cr = ramp.color_ramp
stops = cfg.get('sky', [[0.0, '#6A6A6A'], [0.495, '#8A8F94'], [0.505, '#D9E1E8'], [0.62, '#A9C3E2'], [1.0, '#5F8FCB']])
while len(cr.elements) < len(stops):
    cr.elements.new(0.5)
for el, (pos, hx_) in zip(cr.elements, stops):
    el.position = pos
    el.color = gt.srgb(hx_)
wl.new(ramp.outputs['Color'], bg.inputs['Color'])
bg.inputs['Strength'].default_value = cfg.get('sky_strength', 1.0)
wl.new(bg.outputs['Background'], out.inputs['Surface'])

# prototype grid floor
gm = bpy.data.materials.new('grid')
gm.use_nodes = True
nt = gm.node_tree
b = nt.nodes['Principled BSDF']
ck = nt.nodes.new('ShaderNodeTexBrick')
ck.inputs['Color1'].default_value = gt.srgb('#BDBDBD')
ck.inputs['Color2'].default_value = gt.srgb('#B4B4B4')
ck.inputs['Mortar'].default_value = gt.srgb('#8E8E8E')
ck.inputs['Scale'].default_value = 1.0
ck.inputs['Mortar Size'].default_value = 0.012
ck.offset = 0.0
ck.inputs['Brick Width'].default_value = 1.0
ck.inputs['Row Height'].default_value = 1.0
tcc = nt.nodes.new('ShaderNodeTexCoord')
nt.links.new(tcc.outputs['Object'], ck.inputs['Vector'])
nt.links.new(ck.outputs['Color'], b.inputs['Base Color'])
b.inputs['Roughness'].default_value = 0.8
bpy.ops.mesh.primitive_plane_add(size=120, location=(0, 10, -0.62))
bpy.context.object.data.materials.append(gm)

# primitive 'trees' in an unnaturally even row, one floating
M_TRUNK = flat('trunk', '#7A5230', spec=0.2)
M_LEAF = flat('leafy', '#3FA23A', spec=0.2)
for i, x in enumerate(cfg.get('tree_x', [-4.5, -2.5, -0.5, 1.5, 3.5, 5.5])):
    y = cfg.get('tree_y', 10.0)
    fl = cfg.get('float_tree', 3)
    z0 = -0.62 + (0.6 if i == fl else 0.0)
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.18, depth=2.2, location=(x, y, z0 + 1.1))
    bpy.context.object.data.materials.append(M_TRUNK)
    bpy.ops.mesh.primitive_cone_add(vertices=8, radius1=1.1, depth=2.6, location=(x, y, z0 + 3.2))
    bpy.context.object.data.materials.append(M_LEAF)
# placeholder cube
if cfg.get('cube', True):
    bpy.ops.mesh.primitive_cube_add(size=1.4, location=(cfg.get('cube_x', -2.2), 6.0, 0.08))
    bpy.context.object.data.materials.append(flat('cubeg', '#CFCFCF'))

# ---------------------------------------------------------------- default-ish lighting: one hard sun + flat ambient
sun = bpy.data.lights.new('sun', 'SUN')
sun.energy = cfg.get('sun', 3.2)
sun.angle = math.radians(1.0)
so = bpy.data.objects.new('sun', sun)
scn.collection.objects.link(so)
so.rotation_euler = Euler([math.radians(v) for v in cfg.get('sun_rot', (50, 0, -30))], 'XYZ')
# fill so the black body isn't a void
fill = bpy.data.lights.new('fill', 'AREA')
fill.energy = cfg.get('fill', 120)
fill.size = 3
fo = bpy.data.objects.new('fill', fill)
scn.collection.objects.link(fo)
fo.location = (0.6, -2.4, 0.9)
fo.rotation_euler = (Vector((0, 0, 0.3)) - fo.location).to_track_quat('-Z', 'Y').to_euler()

# ---------------------------------------------------------------- camera (same as the hero's left panel)
C = cfg.get('cam', {})
cam = bpy.data.cameras.new('cam')
co = bpy.data.objects.new('cam', cam)
scn.collection.objects.link(co)
co.location = Vector(C.get('loc', (0.32, -1.40, 0.13)))
tgt = Vector(C.get('target', (0.32, 0, 0.49)))
co.rotation_euler = (tgt - co.location).to_track_quat('-Z', 'Y').to_euler()
cam.lens = C.get('lens', 34)
cam.dof.use_dof = False          # everything flat and sharp: cheap look
cam.shift_x = C.get('shift_x', 0.0)
cam.shift_y = C.get('shift_y', 0.0)
scn.camera = co

R = cfg.get('render', {})
scn.render.engine = 'CYCLES'
scn.cycles.device = 'CPU'
scn.cycles.samples = R.get('samples', 32)
scn.cycles.use_denoising = True
scn.render.resolution_x = R.get('w', 1280)
scn.render.resolution_y = R.get('h', 720)
scn.view_settings.view_transform = R.get('view', 'Standard')
scn.view_settings.look = 'None'
scn.render.image_settings.file_format = 'PNG'
scn.render.image_settings.color_depth = '16'
scn.render.filepath = cfg['out']
if cfg.get('save_blend'):
    bpy.ops.file.pack_all()
    bpy.ops.wm.save_as_mainfile(filepath=cfg['save_blend'], compress=True)
bpy.ops.render.render(write_still=True)
print('DONE', cfg['out'])
if cfg.get('mask_out'):
    keep = set(monke)
    for o in scn.objects:
        if o.type in ('MESH', 'FONT', 'CURVE') and o not in keep:
            o.hide_render = True
    scn.render.film_transparent = True
    scn.cycles.samples = 4
    scn.cycles.use_denoising = False
    scn.render.image_settings.color_mode = 'RGBA'
    scn.render.filepath = cfg['mask_out']
    bpy.ops.render.render(write_still=True)
    print('MASK', cfg['mask_out'])
