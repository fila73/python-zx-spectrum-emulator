import cv2
import numpy as np
import os

def round_corners():
    directory = "/home/fila/projects/android/zoliky/src/main/res/drawable"
    # Radius for the rounded corners (pixels)
    radius = 18 
    
    for filename in os.listdir(directory):
        if filename.endswith(".png") and ("_" in filename or filename in ["joker.png", "red_revers.png", "blue_revers.png"]):
            path = os.path.join(directory, filename)
            # Load with alpha channel
            img = cv2.imread(path, cv2.IMREAD_UNCHANGED)
            if img is None: continue
            
            # Ensure 4 channels (BGRA)
            if img.shape[2] == 3:
                img = cv2.cvtColor(img, cv2.COLOR_BGR2BGRA)
            
            h, w = img.shape[:2]
            
            # Create a mask with white rounded rectangle on black background
            mask = np.zeros((h, w), dtype=np.uint8)
            # Draw a filled rounded rectangle
            # Using polylines/contours to get smooth rounded corners
            cv2.rectangle(mask, (radius, 0), (w - radius, h), 255, -1)
            cv2.rectangle(mask, (0, radius), (w, h - radius), 255, -1)
            cv2.circle(mask, (radius, radius), radius, 255, -1)
            cv2.circle(mask, (w - radius, radius), radius, 255, -1)
            cv2.circle(mask, (radius, h - radius), radius, 255, -1)
            cv2.circle(mask, (w - radius, h - radius), radius, 255, -1)
            
            # Apply mask to alpha channel
            img[:, :, 3] = cv2.bitwise_and(img[:, :, 3], mask)
            
            cv2.imwrite(path, img)
            print(f"Rounded corners for {filename}")

if __name__ == "__main__":
    round_corners()
