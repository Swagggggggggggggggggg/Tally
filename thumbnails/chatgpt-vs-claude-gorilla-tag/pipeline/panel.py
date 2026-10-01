"""Render one thumbnail panel: a posed Gorilla Tag monke in a stylised GT forest.
Usage: blender -b -P panel.py -- '<json config>'
"""
import bpy, sys, json, math, random
from mathutils import Vector, Euler, Matrix

sys.path.insert(0, '/tmp/claude-0/-home-user-Tally/702e814a-b90a-5d68-bc9a-bc92c217492c/scratchpad/blender')
import gt

cfg = json.loads(sys.argv[sys.argv.index('--') + 1])
side = cfg.get('side', 'left')          # which panel; monke faces toward the divider
sgn = 1 if side == 'left' else -1       # +1: face screen-right
rnd = random.Random(cfg.get('seed', 7))

bpy.ops.wm.read_factory_settings(use_empty=True)
scn = bpy.context.scene

# ---------------------------------------------------------------- monke
M = gt.append_rig(side)
gt.set_look(M, cfg['fur'], emission=cfg.get('fur_emission', 0.05), subsurface=cfg.get('subsurface', 0.1),
            glossy=cfg.get('glossy'), glossy_color=cfg.get('glossy_color'))
gt.set_name(M, cfg.get('name', 'GORILLA'))
if cfg.get('face'):
    n = gt.set_face_image(M, cfg['face'])
    print('face textures replaced:', n)
ROOT = Vector(cfg.get('root', (0, 0, 0)))
gt.place(M, tuple(ROOT), rot_z_deg=sgn * cfg.get('turn', 28))

# pose ----------------------------------------------------------------
P = cfg.get('pose', {})
gt.rot_bone(M, 'torso', P.get('torso', (18, 0, 0)))
gt.rot_bone(M, 'head', P.get('head', (8, 0, 0)))
arm = M['arm']
mw = arm.matrix_world
# lead hand = the hand on the divider side. Left panel monke faces screen-right, so its own left (L, +x) leads.
lead_side, rear_side = ('L', 'R') if side == 'left' else ('R', 'L')
mx = 1 if lead_side == 'L' else -1   # mirror x for the right-panel monke


def lw(v):
    return mw @ Vector((v[0] * mx, v[1], v[2]))


def ld(v):
    return mw.to_3x3() @ Vector((v[0] * mx, v[1], v[2]))


if 'hands_world' in P:
    # explicit pose: hand targets relative to the monke root (world axes), elbow directions, finger curls
    for sd, hp in P['hands_world'].items():
        gt.set_hand_world(M, sd, ROOT + Vector(hp), rot_deg=P.get('hand_rot', {}).get(sd))
    for sd, ed in P.get('elbows_world', {}).items():
        print('elbow', sd, gt.aim_elbow(M, sd, Vector(ed)))
    for sd, cv in P.get('curls', {}).items():
        gt.curl(M, sd, *cv)
    bpy.context.view_layer.update()
    for sd, hp in P['hands_world'].items():
        print('HAND', sd, 'target', tuple(round(v, 3) for v in (ROOT + Vector(hp))), 'got', tuple(round(v, 3) for v in gt.bone_world(M, 'hand.' + sd)),
              'ctrl', tuple(round(v, 3) for v in gt.bone_world(M, 'hand_controller.' + sd)))
elif 'lead_world' in P:
    lwp = P['lead_world']
    gt.set_hand_world(M, lead_side, Vector((lwp[0] * sgn, lwp[1], lwp[2])), rot_deg=P.get('lead_rot'))
else:
    gt.set_hand_world(M, lead_side, lw(P.get('lead', (0.32, -0.62, 0.32))), rot_deg=P.get('lead_rot'))
if 'hands_world' not in P:
    gt.set_hand_world(M, rear_side, lw(P.get('rear', (-0.34, -0.10, -0.28))), rot_deg=P.get('rear_rot'))
    print('elbow lead', gt.aim_elbow(M, lead_side, ld(P.get('lead_elbow', (0.7, 0.1, -0.7)))))
    print('elbow rear', gt.aim_elbow(M, rear_side, ld(P.get('rear_elbow', (-0.8, 0.2, -0.4)))))
    gt.curl(M, lead_side, *P.get('lead_curl', (12, 18, 0)))
    gt.curl(M, rear_side, *P.get('rear_curl', (40, 45, 20)))
bpy.context.view_layer.update()
print('lead hand world', gt.bone_world(M, 'hand.' + lead_side))

# ---------------------------------------------------------------- world / sky
world = bpy.data.worlds.new('sky')
scn.world = world
world.use_nodes = True
wn = world.node_tree.nodes
wl = world.node_tree.links
for n in list(wn):
    wn.remove(n)
out = wn.new('ShaderNodeOutputWorld')
bg = wn.new('ShaderNodeBackground')
tc = wn.new('ShaderNodeTexCoord')
sep = wn.new('ShaderNodeSeparateXYZ')
ramp = wn.new('ShaderNodeValToRGB')
wl.new(tc.outputs['Generated'], sep.inputs[0])
mp = wn.new('ShaderNodeMapRange')
mp.inputs['From Min'].default_value = cfg.get('sky_min', 0.0)
mp.inputs['From Max'].default_value = cfg.get('sky_max', 1.0)
wl.new(tc.outputs['Window'], sep.inputs[0]) if cfg.get('sky_screen', True) else None
wl.new(sep.outputs['Y'], mp.inputs['Value'])
wl.new(mp.outputs['Result'], ramp.inputs['Fac'])
cr = ramp.color_ramp
stops = cfg['sky']  # list of [pos, hex]
while len(cr.elements) < len(stops):
    cr.elements.new(0.5)
for el, (pos, hx) in zip(cr.elements, stops):
    el.position = pos
    el.color = gt.srgb(hx)
wl.new(ramp.outputs['Color'], bg.inputs['Color'])
bg.inputs['Strength'].default_value = cfg.get('sky_strength', 1.0)
wl.new(bg.outputs['Background'], out.inputs['Surface'])

# a separate, dimmer world light for illumination so the bright backdrop doesn't flatten the monke
lp = wn.new('ShaderNodeLightPath')
mix = wn.new('ShaderNodeMixShader')
amb = wn.new('ShaderNodeBackground')
amb.inputs['Color'].default_value = gt.srgb(cfg.get('ambient', '#8AA4C8'))
amb.inputs['Strength'].default_value = cfg.get('ambient_strength', 0.6)
wl.new(lp.outputs['Is Camera Ray'], mix.inputs['Fac'])
wl.new(amb.outputs['Background'], mix.inputs[1])
wl.new(bg.outputs['Background'], mix.inputs[2])
wl.new(mix.outputs['Shader'], out.inputs['Surface'])

# ---------------------------------------------------------------- environment (stylised GT forest)
def pix_noise_mat(name, c1, c2, scale=18.0, snap=0.05, rough=0.9):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes['Principled BSDF']
    b.inputs['Roughness'].default_value = rough
    t = nt.nodes.new('ShaderNodeTexCoord')
    vm = nt.nodes.new('ShaderNodeVectorMath')
    vm.operation = 'SNAP'
    vm.inputs[1].default_value = (snap, snap, snap)
    nz = nt.nodes.new('ShaderNodeTexNoise')
    nz.inputs['Scale'].default_value = scale
    nz.inputs['Detail'].default_value = 3
    rp = nt.nodes.new('ShaderNodeValToRGB')
    rp.color_ramp.elements[0].color = gt.srgb(c1)
    rp.color_ramp.elements[1].color = gt.srgb(c2)
    rp.color_ramp.elements[0].position = 0.3
    rp.color_ramp.elements[1].position = 0.7
    nt.links.new(t.outputs['Object'], vm.inputs[0])
    nt.links.new(vm.outputs['Vector'], nz.inputs['Vector'])
    nt.links.new(nz.outputs['Fac'], rp.inputs['Fac'])
    nt.links.new(rp.outputs['Color'], b.inputs['Base Color'])
    fog = cfg.get('fog')
    if fog:
        # aerial perspective: blend toward the panel's sky colour with camera distance
        out_n = nt.nodes['Material Output']
        lp = nt.nodes.new('ShaderNodeLightPath')
        mr = nt.nodes.new('ShaderNodeMapRange')
        mr.inputs['From Min'].default_value = fog.get('near', 3.0)
        mr.inputs['From Max'].default_value = fog.get('far', 25.0)
        mr.inputs['To Max'].default_value = fog.get('max', 0.75)
        em = nt.nodes.new('ShaderNodeEmission')
        em.inputs['Color'].default_value = gt.srgb(fog.get('color', '#BFE9FF'))
        em.inputs['Strength'].default_value = fog.get('strength', 1.0)
        mx = nt.nodes.new('ShaderNodeMixShader')
        nt.links.new(lp.outputs['Ray Length'], mr.inputs['Value'])
        nt.links.new(mr.outputs['Result'], mx.inputs['Fac'])
        nt.links.new(b.outputs['BSDF'], mx.inputs[1])
        nt.links.new(em.outputs['Emission'], mx.inputs[2])
        nt.links.new(mx.outputs['Shader'], out_n.inputs['Surface'])
    return m


bark = pix_noise_mat('bark', cfg.get('bark1', '#3A2A1E'), cfg.get('bark2', '#6B4A30'), 8, 0.06)
leaf = pix_noise_mat('leaf', cfg.get('leaf1', '#123A1E'), cfg.get('leaf2', '#2F6B2A'), 6, 0.08)
wood = pix_noise_mat('wood', '#6A4428', '#9B6A3E', 5, 0.05)
grass = pix_noise_mat('grass', cfg.get('grass1', '#2E5A1E'), cfg.get('grass2', '#5E8F2E'), 2.5, 0.12)
rock = pix_noise_mat('rock', cfg.get('rock1', '#5A5550'), cfg.get('rock2', '#8C847A'), 1.2, 0.2)


def link(o):
    scn.collection.objects.link(o)
    return o


def cyl(name, r1, r2, h, loc, mat, verts=8):
    bpy.ops.mesh.primitive_cone_add(vertices=verts, radius1=r1, radius2=r2, depth=h, location=loc)
    o = bpy.context.object
    o.name = name
    o.data.materials.append(mat)
    return o


def pine(x, y, h, r, z0=-0.62):
    cyl('trunk', r * 0.16, r * 0.10, h, (x, y, z0 + h / 2), bark)
    layers = 6
    for i in range(layers):
        t = i / layers
        zz = z0 + h * (0.35 + 0.62 * t)
        rr = r * (1.0 - 0.75 * t) * rnd.uniform(0.85, 1.1)
        cyl('foliage', rr, rr * 0.15, h * 0.22, (x + rnd.uniform(-.05, .05), y, zz), leaf, verts=7)


# ground
bpy.ops.mesh.primitive_plane_add(size=80, location=(0, 10, -0.62))
bpy.context.object.data.materials.append(grass)

# trees spread behind the monke, mostly on the far side of the divider and edges
for i in range(cfg.get('trees', 26)):
    y = rnd.uniform(cfg.get('tree_ymin', 6.0), 26)
    x = rnd.uniform(-12, 12)
    # keep a window of open sky behind the monke's head (head sits near x=0)
    cxw = cfg.get('tree_clear_center', 0.0) * sgn
    if cfg.get('clear_ray'):
        # keep the sightline camera -> head clear so the head silhouettes against sky
        ccx = cfg.get('cam', {}).get('loc', (0.43, -1.83, 0.05))[0] * sgn
        ccy = cfg.get('cam', {}).get('loc', (0.43, -1.83, 0.05))[1]
        cxw = ccx + (0.0 - ccx) * (y - ccy) / (0.0 - ccy)
    half = cfg.get('tree_clear_x', 0.0) * (1 + y / 12.0)
    if abs(x - cxw) < half:
        x = cxw + math.copysign(half + rnd.uniform(0, 3), x - cxw)
    h = rnd.uniform(7, 13)
    pine(x, y, h, rnd.uniform(1.1, 2.0))

# treehouse platform + roof (Gorilla Tag landmark) placed on the far side
tx = sgn * cfg.get('treehouse_x', -2.4)
ty = cfg.get('treehouse_y', 7.5)
tz = cfg.get('treehouse_z', 2.4)
if cfg.get('treehouse', True):
  bpy.ops.mesh.primitive_cube_add(size=1, location=(tx, ty, tz))
  p = bpy.context.object
  p.scale = (2.6, 2.2, 0.12)
  p.data.materials.append(wood)
  for dx in (-1.1, 1.1):
      cyl('post', 0.09, 0.09, tz + 0.62, (tx + dx, ty - 0.9, (tz - 0.62) / 2), wood, 6)
  bpy.ops.mesh.primitive_cube_add(size=1, location=(tx, ty + 0.2, tz + 0.8))
  hut = bpy.context.object
  hut.scale = (1.6, 1.4, 1.4)
  hut.data.materials.append(wood)
  bpy.ops.mesh.primitive_cone_add(vertices=4, radius1=1.6, depth=1.0, location=(tx, ty + 0.2, tz + 2.0),
                                  rotation=(0, 0, math.radians(45)))
  bpy.context.object.data.materials.append(bark)

# distant cliffs
for i in range(cfg.get('cliffs', 7)):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=rnd.uniform(5, 9),
                                          location=(rnd.uniform(-22, 22), rnd.uniform(30, 40), rnd.uniform(-2, 3)))
    o = bpy.context.object
    o.scale = (1.4, 0.8, rnd.uniform(1.2, 2.0))
    o.data.materials.append(rock)

# ---------------------------------------------------------------- lights
def area(name, loc, target, energy, size, color):
    l = bpy.data.lights.new(name, 'AREA')
    l.energy = energy
    l.size = size
    l.color = gt.srgb(color)[:3]
    o = link(bpy.data.objects.new(name, l))
    o.location = loc
    c = o.constraints.new('TRACK_TO')
    c.target = target
    c.track_axis = 'TRACK_NEGATIVE_Z'
    c.up_axis = 'UP_Y'
    return o


aim = bpy.data.objects.new('aim', None)
link(aim)
aim.location = tuple(ROOT + Vector((0, 0, cfg.get('aim_z', 0.25))))
L = cfg.get('lights', {})
area('key', (-sgn * 1.4 + sgn * 0.0, -2.2, 1.6), aim, L.get('key', 160), 1.6, L.get('key_col', '#FFF4E6'))
area('rim', (sgn * 1.3, 1.2, 1.2), aim, L.get('rim', 260), 0.9, L.get('rim_col', '#9EE8FF'))
area('rim2', (-sgn * 1.2, 1.0, 1.0), aim, L.get('rim2', 120), 0.9, L.get('rim2_col', '#FFFFFF'))
area('fill', (sgn * 1.8, -1.6, 0.0), aim, L.get('fill', 50), 2.5, L.get('fill_col', '#CFE0FF'))
CL = cfg.get('center_light')
if CL:
    cpos = CL.get('pos', (0.80, -0.25, 0.55))
    l = bpy.data.lights.new('center', 'AREA')
    l.energy = CL.get('energy', 150)
    l.size = CL.get('size', 0.4)
    l.color = gt.srgb(CL.get('color', '#FFFFFF'))[:3]
    o = link(bpy.data.objects.new('center', l))
    o.location = (cpos[0] * sgn, cpos[1], cpos[2])
    c = o.constraints.new('TRACK_TO')
    c.target = aim
    c.track_axis = 'TRACK_NEGATIVE_Z'
    c.up_axis = 'UP_Y'
if L.get('sun', 0):
    s = bpy.data.lights.new('sun', 'SUN')
    s.energy = L['sun']
    s.color = gt.srgb(L.get('sun_col', '#FFE6C4'))[:3]
    so = link(bpy.data.objects.new('sun', s))
    so.rotation_euler = Euler([math.radians(v) for v in L.get('sun_rot', (55, 0, 30))], 'XYZ')

# ---------------------------------------------------------------- camera
C = cfg.get('cam', {})
cam = bpy.data.cameras.new('cam')
co = link(bpy.data.objects.new('cam', cam))
cl = C.get('loc', (0.43, -1.83, 0.05)); ct = C.get('target', (0.43, 0, 0.40))
co.location = Vector((cl[0] * sgn, cl[1], cl[2]))
tgt = Vector((ct[0] * sgn, ct[1], ct[2]))
co.rotation_euler = (tgt - co.location).to_track_quat('-Z', 'Y').to_euler()
cam.lens = C.get('lens', 42)
cam.shift_x = C.get('shift_x', 0.0)
cam.shift_y = C.get('shift_y', 0.0)
cam.dof.use_dof = True
cam.dof.focus_object = aim
cam.dof.aperture_fstop = C.get('fstop', 1.4)
scn.camera = co
scn.render.resolution_x = cfg.get('render', {}).get('w', 720)
scn.render.resolution_y = cfg.get('render', {}).get('h', 720)
bpy.context.view_layer.update()


def frame_to_world(fx, fy, dist):
    """Frame coords (fx from left, fy from top, 0..1) at a given distance in front of the camera -> world point."""
    fr = [co.matrix_world @ (v * (dist / abs(v.z))) for v in cam.view_frame(scene=scn)]
    # view_frame order: top-right, bottom-right, bottom-left, top-left
    tr, br, bl, tl = fr
    top = tl.lerp(tr, fx)
    bot = bl.lerp(br, fx)
    return top.lerp(bot, fy)


POLE = cfg.get('pole')
if POLE:
    # a white bar that IS the thumbnail divider: left edge sits exactly on frame x=0.5 (panel boundary)
    d = POLE.get('dist', 0.8)
    fr = [co.matrix_world @ (v * (d / abs(v.z))) for v in cam.view_frame(scene=scn)]
    tr, br, bl, tl = fr
    width_w = (tr - tl).length
    rad = POLE.get('frac', 0.012) * width_w        # radius as a fraction of frame width at that depth
    fx = 0.5 + rad / width_w
    mid = tl.lerp(tr, fx).lerp(bl.lerp(br, fx), 0.5)
    up = (tl - bl).normalized()
    bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=rad, depth=(tl - bl).length * 1.6, location=mid)
    po = bpy.context.object
    po.rotation_euler = up.to_track_quat('Z', 'Y').to_euler()
    pm = bpy.data.materials.new('pole')
    pm.use_nodes = True
    pb_ = pm.node_tree.nodes['Principled BSDF']
    pb_.inputs['Base Color'].default_value = (1, 1, 1, 1)
    pb_.inputs['Emission Color'].default_value = (1, 1, 1, 1)
    pb_.inputs['Emission Strength'].default_value = POLE.get('emit', 0.55)
    pb_.inputs['Roughness'].default_value = 0.4
    po.data.materials.append(pm)
    po.visible_shadow = POLE.get('shadow', True)
    print('POLE at', tuple(round(v, 3) for v in mid), 'radius', round(rad, 4))
    if POLE.get('grip'):
        gfy = POLE.get('grip_fy', 0.55)
        gp = tl.lerp(tr, fx).lerp(bl.lerp(br, fx), gfy)
        gs = POLE.get('grip_side', 'R')
        gp = gp + Vector(POLE.get('grip_offset', (0.02, 0.0, 0.0)))
        gt.set_hand_world(M, gs, gp, rot_deg=POLE.get('grip_rot'))
        if POLE.get('grip_elbow'):
            print('grip elbow', gt.aim_elbow(M, gs, Vector(POLE['grip_elbow'])))
        gt.curl(M, gs, *POLE.get('grip_curl', (75, 75, 60)))
        bpy.context.view_layer.update()
        print('GRIP at', tuple(round(v, 3) for v in gp))

if 'lead_frame' in P:
    fx, fy, dist = P['lead_frame']
    if side == 'right':
        fx = 1 - fx
    wp = frame_to_world(fx, fy, dist)
    gt.set_hand_world(M, lead_side, wp, rot_deg=P.get('lead_rot'))
    sh = gt.bone_world(M, 'upper_arm.' + lead_side)
    print('lead_frame world', tuple(round(v, 3) for v in wp), 'reach', round((wp - sh).length, 3))
    print('elbow lead (re-aim)', gt.aim_elbow(M, lead_side, ld(P.get('lead_elbow', (0.7, 0.1, -0.7)))))

# environment must not bounce coloured light onto the monke (green cast on grey face/chest)
if cfg.get('no_env_bounce', True):
    keep = {M['arm'], M['mesh']} | ({M['text']} if M['text'] else set())
    for o in scn.objects:
        if o.type == 'MESH' and o not in keep:
            o.visible_diffuse = False
            o.visible_glossy = False
            o.visible_transmission = False

# ---------------------------------------------------------------- render
R = cfg.get('render', {})
scn.render.engine = 'CYCLES'
scn.cycles.device = 'CPU'
scn.cycles.samples = R.get('samples', 32)
scn.cycles.use_denoising = True
scn.render.resolution_x = R.get('w', 720)
scn.render.resolution_y = R.get('h', 720)
scn.render.film_transparent = False
scn.view_settings.view_transform = R.get('view', 'AgX')
scn.view_settings.look = R.get('look', 'AgX - Punchy')
scn.render.image_settings.file_format = 'PNG'
scn.render.image_settings.color_depth = '16'
scn.render.filepath = cfg['out']
if cfg.get('save_blend'):
    bpy.ops.file.pack_all()
    bpy.ops.wm.save_as_mainfile(filepath=cfg['save_blend'], compress=True)
bpy.ops.render.render(write_still=True)
print('DONE', cfg['out'])
if cfg.get('debug_cam'):
    DC = cfg['debug_cam']
    co.location = Vector(DC['loc']); co.rotation_euler = (Vector(DC['target']) - co.location).to_track_quat('-Z', 'Y').to_euler()
    cam.lens = DC['lens']; cam.shift_x = 0; cam.shift_y = 0; cam.dof.use_dof = False
    scn.render.filepath = cfg['out'].replace('.png', '_debug.png')
    bpy.ops.render.render(write_still=True)
if cfg.get('mask_out'):
    # silhouette pass: only the monke (and its name tag), transparent film
    keep = {M['arm'], M['mesh']} | ({M['text']} if M['text'] else set())
    for o in scn.objects:
        if o.type in ('MESH', 'CURVE', 'FONT') and o not in keep:
            o.hide_render = True
    scn.render.film_transparent = True
    scn.cycles.samples = 4
    scn.cycles.use_denoising = False
    scn.render.image_settings.color_mode = 'RGBA'
    scn.render.filepath = cfg['mask_out']
    bpy.ops.render.render(write_still=True)
    print('MASK', cfg['mask_out'])
