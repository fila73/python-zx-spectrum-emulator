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

    # Improved sorting: Group by Y (rows) then X
    # We find typical row Y coordinates by clustering or rounding
    boxes = [cv2.boundingRect(cnt) for cnt in card_contours]
    
    # Sort boxes by Y
    boxes.sort(key=lambda b: b[1])
    
    # Simple row grouping: if Y is within 50px, it's the same row
    rows = []
    if boxes:
        current_row = [boxes[0]]
        for i in range(1, len(boxes)):
            if boxes[i][1] - current_row[-1][1] < 100: # 100px tolerance for row
                current_row.append(boxes[i])
            else:
                current_row.sort(key=lambda b: b[0]) # Sort row by X
                rows.append(current_row)
                current_row = [boxes[i]]
        current_row.sort(key=lambda b: b[0])
        rows.append(current_row)

    # Flatten the rows back into a list of sorted boxes
    sorted_boxes = [box for row in rows for box in row]

    print(f"Found {len(sorted_boxes)} cards across {len(rows)} rows.")

    suits = ["hearts", "diamonds", "clubs", "spades"]
    ranks = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "j", "q", "k", "a"]
    
    # First 4 rows (13 cards each) should be standard cards
    count = 0
    for row_idx, row in enumerate(rows):
        if row_idx < 4: # Standard suit rows
            for col_idx, (x, y, w, h) in enumerate(row):
                if col_idx < 13:
                    card_img = img[y:y+h, x:x+w]
                    name = f"{suits[row_idx]}_{ranks[col_idx]}.png"
                    cv2.imwrite(os.path.join(output_dir, name), card_img)
                    count += 1
        else: # Bottom row for specials
            special_names = ["joker", "blue_revers", "red_revers"]
            for col_idx, (x, y, w, h) in enumerate(row):
                if col_idx < len(special_names):
                    card_img = img[y:y+h, x:x+w]
                    cv2.imwrite(os.path.join(output_dir, f"{special_names[col_idx]}.png"), card_img)

    print(f"Saved {count} standard cards and special cards.")

if __name__ == "__main__":
    process_cards()
