import numpy as np, time
from PIL import Image
from sdf import *
import hero
t=time.time()
FL=[Light((-0.45,0.6,0.75),(1.05,0.95,0.85),'dir',True),Light((0.8,0.2,-0.5),(0.5,0.65,1.1),'rim'),Light((0.2,-0.9,0.5),(0.35,0.18,0.08),'dir')]
ims=[]
for nm,ex,bl in hero.FACES:
    im=render(hero.head(ex,bl),48,48,cam_y=-0.02,cam_h=0.26,ss=3,lights=FL,ambient=0.3)
    ims.append(to_rgba(im))
print(time.time()-t)
im=render(hero.bust(),120,150,cam_y=-0.16,cam_h=0.66,ss=2,lights=FL,ambient=0.25)
b=to_rgba(im); print(time.time()-t)
sh=Image.new('RGBA',(48*5+130,150),(40,30,50,255))
for k,a in enumerate(ims): sh.alpha_composite(Image.fromarray(a,'RGBA'),(k*48,0))
sh.alpha_composite(Image.fromarray(b,'RGBA'),(250,0))
sh.resize((sh.width*3,sh.height*3),Image.NEAREST).save('out/hero.png')
