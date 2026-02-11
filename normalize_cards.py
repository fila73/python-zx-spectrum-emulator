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

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    card_contours = []
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if 20000 < area < 200000:
            card_contours.append(cnt)

    boxes = [cv2.boundingRect(cnt) for cnt in card_contours]
    boxes.sort(key=lambda b: b[1])
    
    rows = []
    if boxes:
        current_row = [boxes[0]]
        for i in range(1, len(boxes)):
            if boxes[i][1] - current_row[-1][1] < 100:
                current_row.append(boxes[i])
            else:
                current_row.sort(key=lambda b: b[0])
                rows.append(current_row)
                current_row = [boxes[i]]
        current_row.sort(key=lambda b: b[0])
        rows.append(current_row)

    # Calculate standard target size (median of standard card dimensions)
    std_widths = []
    std_heights = []
    for r_idx in range(min(len(rows), 4)):
        for x, y, w, h in rows[r_idx]:
            std_widths.append(w)
            std_heights.append(h)
    
    target_w = int(np.median(std_widths))
    target_h = int(np.median(std_heights))
    print(f"Target size: {target_w}x{target_h}")

    suits = ["hearts", "diamonds", "clubs", "spades"]
    ranks = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "j", "q", "k", "a"]
    
    for row_idx, row in enumerate(rows):
        if row_idx < 4: # Standard suit rows
            for col_idx, (x, y, w, h) in enumerate(row):
                if col_idx < 13:
                    card_img = img[y:y+h, x:x+w]
                    resized = cv2.resize(card_img, (target_w, target_h), interpolation=cv2.INTER_LANCZOS4)
                    name = f"{suits[row_idx]}_{ranks[col_idx]}.png"
                    cv2.imwrite(os.path.join(output_dir, name), resized)
        else: # Bottom row for specials
            special_names = ["joker", "blue_revers", "red_revers"]
            for col_idx, (x, y, w, h) in enumerate(row):
                if col_idx < len(special_names):
                    card_img = img[y:y+h, x:x+w]
                    # Resize to match standard cards
                    resized = cv2.resize(card_img, (target_w, target_h), interpolation=cv2.INTER_LANCZOS4)
                    cv2.imwrite(os.path.join(output_dir, f"{special_names[col_idx]}.png"), resized)

    print(f"Processed and normalized {len(rows)*13 if len(rows)<5 else 52+len(rows[4])} cards.")

if __name__ == "__main__":
    process_cards()
