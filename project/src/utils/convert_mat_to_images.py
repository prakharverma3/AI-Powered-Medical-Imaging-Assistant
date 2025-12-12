import os
import h5py
import numpy as np
import cv2
from tqdm import tqdm

RAW_DIR = "data/raw"     
OUT_IMG_DIR = "data/Images/images"
OUT_MASK_DIR = "data/Images/masks"

os.makedirs(OUT_IMG_DIR, exist_ok=True)
os.makedirs(OUT_MASK_DIR, exist_ok=True)

def normalize(img):
    img = img.astype(np.float32)
    img = (img - img.min()) / (img.max() - img.min() + 1e-8)
    img = (img * 255).astype(np.uint8)
    return img

def main():
    files = [f for f in os.listdir(RAW_DIR) if f.endswith(".mat")]

    for f in tqdm(files):
        path = os.path.join(RAW_DIR, f)

        # ---- load .mat v7.3 using h5py ----
        try:
            file = h5py.File(path, 'r')
        except:
            print("Cannot open:", path)
            continue

        cjdata = file["cjdata"]

        # v7.3 encoding requires indexing like this:
        img = np.array(cjdata['image'])
        img = np.rot90(img)  # orient correctly

        mask = np.array(cjdata['tumorMask'])
        mask = np.rot90(mask)

        # label stored differently
        label = int(np.array(cjdata["label"])[0][0])

        # normalize image
        img = normalize(img)
        mask = (mask > 0).astype(np.uint8) * 255

        img_name = f.replace(".mat", ".png")

        # create class folder
        class_dir = os.path.join(OUT_IMG_DIR, str(label))
        os.makedirs(class_dir, exist_ok=True)

        # save files
        cv2.imwrite(os.path.join(class_dir, img_name), img)
        cv2.imwrite(os.path.join(OUT_MASK_DIR, img_name), mask)

    print("\nConversion complete!")

if __name__ == "__main__":
    main()
