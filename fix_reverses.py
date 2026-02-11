import cv2
import numpy as np
import os

def process_cards():
    img_path = "/home/fila/Downloads/Gemini_Generated_Image_bdc6kubdc6kubdc6.png"
    output_dir = "/home/fila/projects/android/zoliky/src/main/res/drawable"
    os.makedirs(output_dir, exist_ok=True)

    img = cv2.imread(img_path)
    if img is None:
        print("Could not open image")
        return

    # Target size for all cards
    target_w, target_h = 172, 280

    # 1. Standard Cards & Joker (White background cards)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    card_boxes = []
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if 20000 < area < 200000:
            card_boxes.append(cv2.boundingRect(cnt))
            
    card_boxes.sort(key=lambda b: b[1])
    rows = []
    if card_boxes:
        current_row = [card_boxes[0]]
        for i in range(1, len(card_boxes)):
            if card_boxes[i][1] - current_row[-1][1] < 100:
                current_row.append(card_boxes[i])
            else:
                current_row.sort(key=lambda b: b[0])
                rows.append(current_row)
                current_row = [card_boxes[i]]
        current_row.sort(key=lambda b: b[0])
        rows.append(current_row)

    suits = ["hearts", "diamonds", "clubs", "spades"]
    ranks = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "j", "q", "k", "a"]
    
    for row_idx, row in enumerate(rows):
        if row_idx < 4:
            for col_idx, (x, y, w, h) in enumerate(row):
                if col_idx < 13:
                    card_img = img[y:y+h, x:x+w]
                    resized = cv2.resize(card_img, (target_w, target_h), interpolation=cv2.INTER_LANCZOS4)
                    cv2.imwrite(os.path.join(output_dir, f"{suits[row_idx]}_{ranks[col_idx]}.png"), resized)
        elif row_idx == 4: # Joker is in the last row found by thresholding
            x, y, w, h = row[0]
            card_img = img[y:y+h, x:x+w]
            resized = cv2.resize(card_img, (target_w, target_h), interpolation=cv2.INTER_LANCZOS4)
            cv2.imwrite(os.path.join(output_dir, "joker.png"), resized)

    # 2. Reverses (Patterned/Colored backgrounds)
    # The blue and red backs are at the bottom, not white, so they need different detection.
    # Looking at original image: Joker at ~550x1338. Blue back is to its right, Red back to its right.
    # We'll use the Y from Joker and define boxes for Blue/Red based on spacing.
    
    joker_x, joker_y, joker_w, joker_h = rows[4][0]
    
    # Visual estimation of centers: Joker is at x=550.
    # Spacing between cards in that row seems to be ~260px (x-to-x)
    blue_x = joker_x + 260 
    red_x = blue_x + 260
    
    # Crop these manually with the same dimensions as the Joker
    blue_back = img[joker_y:joker_y+joker_h, blue_x:blue_x+joker_w]
    red_back = img[joker_y:joker_y+joker_h, red_x:red_x+joker_w]
    
    cv2.imwrite(os.path.join(output_dir, "blue_revers.png"), cv2.resize(blue_back, (target_w, target_h), interpolation=cv2.INTER_LANCZOS4))
    cv2.imwrite(os.path.join(output_dir, "red_revers.png"), cv2.resize(red_back, (target_w, target_h), interpolation=cv2.INTER_LANCZOS4))

    print(f"Fixed reverses. Saved to {output_dir}")

if __name__ == "__main__":
    process_cards()
