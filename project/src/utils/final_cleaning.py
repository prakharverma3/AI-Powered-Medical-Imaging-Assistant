import os
import cv2
import shutil
import numpy as np
from tqdm import tqdm
from sklearn.model_selection import train_test_split

IMG_DIR = "data/Images/images"
MASK_DIR = "data/Images/masks"

FINAL_DIR = "data/cleaned"

CLASSES = ["1", "2", "3", "no_tumor"]  # your actual folders

# Create final directories
for split in ["train", "val", "test"]:
    for cls in CLASSES:
        os.makedirs(f"{FINAL_DIR}/{split}/images/{cls}", exist_ok=True)

    # masks only for tumor classes 1,2,3
    for cls in ["1", "2", "3"]:
        os.makedirs(f"{FINAL_DIR}/{split}/masks/{cls}", exist_ok=True)


def load_image(path):
    img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        return None
    img = cv2.resize(img, (224, 224))
    img = img.astype(np.float32)
    img = (img - img.min()) / (img.max() - img.min() + 1e-8)
    img = (img * 255).astype(np.uint8)
    return img


def load_mask(path):
    if not os.path.exists(path):
        return None
    mask = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    if mask is None:
        return None
    mask = cv2.resize(mask, (224, 224))
    mask = (mask > 0).astype(np.uint8) * 255
    return mask


def main():

    all_items = []  # list of tuples (img_path, mask_path or None, class)

    for cls in CLASSES:
        class_folder = os.path.join(IMG_DIR, cls)

        for fname in os.listdir(class_folder):
            img_path = os.path.join(class_folder, fname)

            if cls == "no_tumor":
                mask_path = None  # no tumor → no mask
            else:
                mask_path = os.path.join(MASK_DIR, fname)

            all_items.append((img_path, mask_path, cls))

    # Train/Val/Test split (70/20/10)
    train, temp = train_test_split(all_items, test_size=0.3, random_state=42)
    val, test = train_test_split(temp, test_size=0.33, random_state=42)

    splits = {"train": train, "val": val, "test": test}

    # Process data
    for split, items in splits.items():
        print(f"\nProcessing {split} set...")

        for img_path, mask_path, cls in tqdm(items):

            # Load image
            img = load_image(img_path)
            if img is None:
                continue

            filename = os.path.basename(img_path)

            # Save image
            cv2.imwrite(f"{FINAL_DIR}/{split}/images/{cls}/{filename}", img)

            # Save mask *only for tumor classes*
            if cls in ["1", "2", "3"]:
                mask = load_mask(mask_path)
                if mask is not None:
                    cv2.imwrite(f"{FINAL_DIR}/{split}/masks/{cls}/{filename}", mask)

    print("\n✅ FINAL CLEANING COMPLETE!")
    print(f"Cleaned dataset saved to: {FINAL_DIR}")


if __name__ == "__main__":
    main()
