import cv2

cap = cv2.VideoCapture('road.mp4')
ret, frame = cap.read()
cap.release()

print(f"Frame read OK: {ret}, shape: {frame.shape}")

gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
blur = cv2.GaussianBlur(gray, (5, 5), 0)
edges = cv2.Canny(blur, 50, 150)

cv2.imshow('original', frame)
cv2.imshow('edges', edges)
cv2.waitKey(0)
cv2.destroyAllWindows()
