import cv2
import numpy as np
import os

def fix_reverses_shifted():
    img_path = "/home/fila/Downloads/Gemini_Generated_Image_bdc6kubdc6kubdc6.png"
    output_dir = "/home/fila/projects/android/zoliky/src/main/res/drawable"
    
    img = cv2.imread(img_path)
    if img is None:
        return

    target_w, target_h = 172, 280

    # Reference: Joker position from previous successful detection
    # From previous logs: ((551, 1338, 207, 317), 64779.0)
    j_x, j_y, j_w, j_h = 551, 1338, 207, 317
    
    # Increase shift to the right to avoid the "white spots" (bits of previous cards)
    # Original spacing was 260. Let's try 265 or similar.
    # Actually, looking at the image, there's quite a gap.
    blue_x = 817 # Shifted slightly right from 815
    red_x = 1100  # Shifted slightly right from 1095
    
    # Width of the crop on original image before resizing
    # Joker width was 207, let's use a slightly narrower crop if needed, 
    # but the main issue is the X start.
    crop_w = 200 
    
    blue_back = img[j_y:j_y+j_h, blue_x:blue_x+crop_w]
    red_back = img[j_y:j_y+j_h, red_x:red_x+crop_w]
    
    cv2.imwrite(os.path.join(output_dir, "blue_revers.png"), cv2.resize(blue_back, (target_w, target_h), interpolation=cv2.INTER_LANCZOS4))
    cv2.imwrite(os.path.join(output_dir, "red_revers.png"), cv2.resize(red_back, (target_w, target_h), interpolation=cv2.INTER_LANCZOS4))

    print("Fixed reverses with right shift.")

if __name__ == "__main__":
    fix_reverses_shifted()
