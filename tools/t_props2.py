"""Preview props: python3 t_props2.py name[,name...] -> out/p2_<first>.png"""
import sys, time, numpy as np
from PIL import Image
from sdf import *
import props2 as P2
SIZES = dict(streetlamp=(40, 140), balloons=(50, 100), carousel=(70, 130), cotton=(70, 80), hydrant=(26, 34), trashcan=(34, 44),
             wreck=(96, 56), bulbs=(110, 100), clownhead=(70, 82), strongman=(56, 140), candelabra=(40, 100), coffin=(44, 92),
             cypress=(100, 150), tesla=(50, 100), tank=(50, 104), knight=(56, 130), cage=(40, 104), brazier=(36, 90), reeds=(44, 66),
             gargoyle=(56, 100), butch=(84, 150), pk_head=(52, 50), kid=(40, 56), clown_car=(64, 50), balloon=(20, 40),
             count_bat=(70, 54), star=(20, 24), skel_dead=(80, 30), skel_fall=(100, 100), bat_dead=(70, 30), vamp_dead=(60, 30),
             vamp_fall=(84, 104), count_dead=(80, 34), giggles_dead=(210, 70), giggles_fall=(190, 170), count_fall=(170, 140))
names = sys.argv[1].split(',')
arg = sys.argv[2] if len(sys.argv) > 2 else None
ims = []
t = time.time()
for n in names:
    W, H = SIZES[n]
    fn = getattr(P2, n)
    ps = fn(arg) if arg and n == 'butch' else fn()
    im = render(ps, W, H, cam_y=H / 96 / 2 - 0.01, cam_h=H / 96, ss=1)
    a = to_rgba(im); a[im.glow, :3] = np.minimum(255, a[im.glow, :3].astype(int) + 40)
    ims.append(a)
print('%.1fs' % (time.time() - t))
Wt = sum(a.shape[1] + 4 for a in ims); Ht = max(a.shape[0] for a in ims)
sh = Image.new('RGBA', (Wt, Ht), (40, 30, 50, 255)); x = 0
for a in ims:
    sh.alpha_composite(Image.fromarray(a, 'RGBA'), (x, Ht - a.shape[0])); x += a.shape[1] + 4
sh.resize((sh.width * 2, sh.height * 2), Image.NEAREST).save('out/p2_%s.png' % names[0])
