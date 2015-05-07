from xiApi import Detector

import numpy as np
import pylab as plt
d = Detector()

d.set_exposure(1000)
d.enable_cooling()
res = d.get_image()


plt.figure()
plt.imshow(res, cmap=plt.cm.gray)
plt.colorbar()
plt.show()
