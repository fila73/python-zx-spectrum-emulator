import sys
from PIL import Image
import os

def crop_cards():
    img_path = "/home/fila/Downloads/Gemini_Generated_Image_bdc6kubdc6kubdc6.png"
    output_dir = "/home/fila/projects/android/zoliky/src/main/res/drawable"
    os.makedirs(output_dir, exist_ok=True)
    
    img = Image.open(img_path)
    w, h = img.size
    
    # Grid: 4 rows of suits, 13 columns (2-A)
    # Plus bottom row: Joker, Blue Reverse, Red Reverse
    
    cols = 13
    rows = 4
    
    # Card dimensions (approx based on image)
    # The top 4 rows are the cards. The bottom row has 3 special cards.
    # Total image 2464 x 1728
    # Top section for 4 rows: let's say 1380px high
    # Leftover for bottom row: 348px
    
    card_w = w // cols # 2464 / 13 = ~189
    card_h = 1380 // rows # 1380 / 4 = ~345
    
    suits = ["hearts", "diamonds", "clubs", "spades"]
    ranks = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "j", "q", "k", "a"]
    
    # Process standard cards
    for r in range(rows):
        for c in range(cols):
            left = c * card_w
            top = r * card_h
            right = left + card_w
            bottom = top + card_h
            
            # Crop and save
            card_img = img.crop((left, top, right, bottom))
            name = f"{suits[r]}_{ranks[c]}.png"
            card_img.save(os.path.join(output_dir, name))

    # Bottom row - manual offsets based on visual inspection of the image
    # Joker is roughly centered below the 4th column?
    # Actually, they are aligned at the bottom.
    
    # Joker: centered-ish
    # Blue: to its right
    # Red: to its right
    
    # Better: Detect bounding boxes of bottom cards
    # Or use fixed coordinates for this specific image:
    joker_box = (545, 1320, 760, 1660)
    blue_box = (810, 1320, 1045, 1660)
    red_box = (1095, 1320, 1335, 1660)
    
    img.crop(joker_box).save(os.path.join(output_dir, "joker.png"))
    img.crop(blue_box).save(os.path.join(output_dir, "blue_revers.png"))
    img.crop(red_box).save(os.path.join(output_dir, "red_revers.png"))

if __name__ == "__main__":
    crop_cards()
