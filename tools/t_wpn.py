import sys, time, numpy as np
from PIL import Image
from sdf import *
import weapons as WP
items = [('revolver',0),('revolver',1),('shotgun',0),('shotgun',1),('shotgun',2),('tommy',0),('tommy',1),('launcher',0),('launcher',1),('shovel',0),('shovel',1),('shovel',2)]
sel = [int(a) for a in sys.argv[1].split(',')] if len(sys.argv)>1 else range(len(items))
W,H=160,96
ims=[]
t=time.time()
for i in sel:
    fn,fr=items[i]
    # view plane y in [-0.6, 0.36]
    im=render(WP.weapon(fn,fr),W,H,cam_y=-0.12,cam_h=0.96,ss=int(__import__("os").environ.get("SS","2")),fov_dist=1.0,cam_z_tilt=0.12,lights=WP.WEAPON_LIGHTS,tstart=0.05,tspan=3.0)
    ims.append(to_rgba(im)); print(i, time.time()-t, flush=True)
cols=4
sheet=Image.new('RGBA',(W*cols,H*((len(ims)+cols-1)//cols)),(70,60,80,255))
for k,a in enumerate(ims): sheet.alpha_composite(Image.fromarray(a,'RGBA'),((k%cols)*W,(k//cols)*H))
sheet.resize((sheet.width*2,sheet.height*2),Image.NEAREST).save('out/weapons.png')
