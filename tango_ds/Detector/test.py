from xiApi import Detector
import PyTango


d = Detector()

d.set_exposure(100)
d.get_image()