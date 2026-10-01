"""Make a GitHub-sized editable copy of a heavy scene: decimate huge meshes, downscale packed textures."""
import bpy, bmesh, sys
out = sys.argv[-1]
import os
TMP = os.path.join(os.path.dirname(out), 'lite_tex')
os.makedirs(TMP, exist_ok=True)
dg = bpy.context.evaluated_depsgraph_get()
for me in [m for m in bpy.data.meshes if len(m.polygons) > 200000]:
    tmp = bpy.data.objects.new('tmp_dec', me)
    bpy.context.scene.collection.objects.link(tmp)
    d = tmp.modifiers.new('dec', 'DECIMATE')
    d.ratio = 60000 / len(me.polygons)
    dg = bpy.context.evaluated_depsgraph_get()
    new = bpy.data.meshes.new_from_object(tmp.evaluated_get(dg))
    bm = bmesh.new(); bm.from_mesh(new)
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context='VERTS')
    bm.to_mesh(new); bm.free()
    print('decimated', me.name, len(me.polygons), '->', len(new.polygons))
    for o in bpy.data.objects:
        if o.data == me and o is not tmp:
            o.data = new
    bpy.data.objects.remove(tmp)
    bpy.data.meshes.remove(me)
keep = ('gorilla', 'GorillaEyeMask', 'lightfur', 'lavasmall', 'iceberg', 'chest', 'face')
for im in bpy.data.images:
    if not im.packed_file or any(k.lower() in im.name.lower() for k in keep):
        continue
    w, h = im.size
    cap = 2048 if im.name.endswith('.hdr') else 1024
    if max(w, h) > cap:
        s = cap / max(w, h)
        im.scale(int(w * s), int(h * s))
    hdr = im.name.endswith('.hdr')
    im.file_format = 'HDR' if hdr else 'JPEG'
    p = TMP + '/' + bpy.path.clean_name(im.name) + ('.hdr' if hdr else '.jpg')
    im.save(filepath=p, quality=88)
    im.unpack(method='REMOVE') if im.packed_file else None
    im.filepath = p
    im.source = 'FILE'
    im.reload()
    im.pack()
bpy.ops.wm.save_as_mainfile(filepath=out, compress=True)
