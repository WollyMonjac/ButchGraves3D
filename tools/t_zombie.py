import time, numpy as np
from PIL import Image
from sdf import *
from monsters import *
t=time.time()
W,H=64,84
ims=[]
for pose in ('walk1','walk2','attack','pain'):
    ps=zombie(pose)
    im=render(ps,W,H,cam_y=H/96/2-0.01,cam_h=H/96,ss=3)
    ims.append(to_rgba(im))
    print(pose, time.time()-t)
sheet=Image.new('RGBA',(W*len(ims),H),(40,30,50,255))
for i,a in enumerate(ims): sheet.alpha_composite(Image.fromarray(a,'RGBA'),(i*W,0))
sheet.resize((sheet.width*4,sheet.height*4),Image.NEAREST).save('out/zombie.png')
