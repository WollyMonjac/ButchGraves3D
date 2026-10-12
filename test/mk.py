"""Write a FreeJ2ME harness script: python3 mk.py out.txt EP WARP SKILL 'steps' ; steps: 'w500 s h54:400 t53 ...'
   w<ms> wait, s screenshot, t<key> tap, h<key>:<ms> hold."""
import sys
out, ep, warp, skill, steps = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), sys.argv[5]
L = ['wait 2500', 'tap 53', 'wait 300']
for k in range(ep - 1):
    L += ['tap 56', 'wait 100']
L += ['tap 53', 'wait 300']
if skill == 0: L += ['tap 50', 'wait 100']
if skill == 2: L += ['tap 56', 'wait 100']
for k in range(warp - 1):
    L += ['tap 35', 'wait 60']
L += ['tap 53', 'wait 300']
for k in range(7):
    L += ['tap 53', 'wait 800']     # story pages only take 5 once it has been let go of for half a second
n = 0
for s in steps.split():
    if s == 's':
        n += 1; L.append('shot @OUT/%02d.png' % n)
    elif s[0] == 'w': L.append('wait ' + s[1:])
    elif s[0] == 't': L.append('tap ' + s[1:])
    elif s[0] == 'h':
        k, ms = s[1:].split(':'); L.append('hold %s %s' % (k, ms))
L.append('quit')
open(out, 'w').write('\n'.join(L) + '\n')
