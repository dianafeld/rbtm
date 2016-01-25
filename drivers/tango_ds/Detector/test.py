from xiApi import Detector
import PyTango


d = Detector()
d.set_roi(0, 2900, 0, 2600)
d.set_exposure(100)
d.get_image(100)
