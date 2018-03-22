import cap as cap
import cv2
import zbar
from PIL import Image

scanner = zbar.ImageScanner()
scanner.parse_config('enable')
font = cv2.FONT_HERSHEY_SIMPLEX
camera = cv2.VideoCapture(0)

while (True):
	grabbed, frame = camera.read()
	if not grabbed:
		break
	pil = Image.fromarray(frame).convert('L')
	width, height = pil.size
	raw = pil.tobytes()
	zarimage = zbar.Image(width, height, 'Y800', raw)
	scanner.scan(zarimage)
	for symbol in zarimage:
		if not symbol.count:
			print 'decoded', symbol.type, 'symbol', '"%s"' % symbol.data
		cv2.putText(frame, symbol.data, (20, 100), font, 1, (0, 255, 0), 4)
	cv2.imshow('frame', frame)
	if cv2.waitKey(1) & 0xFF == ord('q'):
		break
cap.release()
cv2.destroyAllWindows()