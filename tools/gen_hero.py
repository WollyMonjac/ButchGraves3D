import numpy as np
from PIL import Image
from sdf import *
import hero
FL=[Light((-0.45,0.6,0.75),(1.05,0.95,0.85),'dir',True),Light((0.8,0.2,-0.5),(0.5,0.65,1.1),'rim'),Light((0.2,-0.9,0.5),(0.35,0.18,0.08),'dir')]
for nm,ex,bl in hero.FACES:
    for sz in (24,36):
        im=render(hero.head(ex,bl),sz,sz,cam_y=-0.035,cam_h=0.24,ss=4,lights=FL,ambient=0.3)
        Image.fromarray(to_rgba(im),'RGBA').save('spr/hero_%s_%d.png'%(nm,sz))
TL=[Light((-0.6,0.4,0.6),(0.55,0.5,0.6),'dir',True),Light((0.7,0.3,-0.6),(0.9,1.0,1.4),'rim'),Light((0.3,-0.8,0.6),(0.9,0.4,0.1),'dir')]
im=render(hero.bust(),120,150,cam_y=-0.16,cam_h=0.66,ss=3,lights=TL,ambient=0.18)
Image.fromarray(to_rgba(im),'RGBA').save('spr/hero_bust.png')
print('ok')
