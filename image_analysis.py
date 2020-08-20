import base64, logging, cv2
import numpy as np

logging.basicConfig(level=logging.WARNING)

def readb64(uri):
	try:
	   encoded_data = uri.split(',')[1]
	   nparr = np.fromstring(base64.b64decode(encoded_data), np.uint8)
	   img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
	   return img
	except:
		return cv2.imread(uri)

"""
	Method used to minimally filter logo images: since these include at least one color,
	this is a fast and easy way to avoid most false negatives from Google Image Search.
"""
def isgray(src):
	img = readb64(src)
	if img is None:
		logging.error("Could not decode image {}".format(src))
		return None
	if len(img.shape) < 3: return True
	if img.shape[2]  == 1: return True
	b,g,r = img[:,:,0], img[:,:,1], img[:,:,2]
	assert b.size == g.size
	ratio_bg = float(np.sum(b == g))  / b.size
	assert b.size == r.size
	ratio_br = float(np.sum(b == r))  / b.size
	return ratio_bg > .9 and ratio_br > .9

FACE_CASCADE = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")

"""
	Method used to minimally filter author pictures images: results from Google Image Search
	often include group pictures (in which case more than one face will be detected) or book
	covers (and thus zero face). 
"""
def face_count(src):
	img = readb64(src)
	if img is None:
		logging.error("Could not decode image", src)
		return None
	grayscale = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
	faces = FACE_CASCADE.detectMultiScale(grayscale, 
		scaleFactor=1.1, 
		minNeighbors=5, 
		minSize=(30, 30), 
		flags=cv2.CASCADE_SCALE_IMAGE)
	return len(faces)
