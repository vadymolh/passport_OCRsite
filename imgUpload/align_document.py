import os

import numpy as np
import imutils
import cv2

from .alignment.align_images import align_images


def align_image(image_path, template_path, output_folder, maxFeatures=15000, keepPercent=0.28, debug=False):
    """
    Perform image alignment using an input image and a template.

    Parameters:
        image_path (str): Path to the input image file.
        template_path (str): Path to the template image file.
        output_folder (str): Path to the output folder.

    Returns:
        Aligned image
    """
    
    # Load the input image and template from disk.
    print("\nLoading images...")
    image = cv2.imread(image_path)
    template = cv2.imread(template_path)

    # Create the "Output" folder if it doesn't exist.
    os.makedirs(output_folder, exist_ok=True)

    print("Aligning images...")
    aligned = align_images(image, template, maxFeatures=maxFeatures, keepPercent=keepPercent, debug=debug)
    result = aligned.copy()

    # cv2.imwrite(os.path.join(output_folder, os.path.splitext(os.path.basename(image_path))[0] + "_aligned.jpg"), aligned)

    # Resize both the aligned and template images so we can easily
    # visualize them on our screen.
    aligned = imutils.resize(aligned, width=800)
    template = imutils.resize(template, width=800)

    # Our first output visualization of the image alignment is a
    # side-by-side comparison of the output aligned image and the
    # template.
    stacked = np.hstack([aligned, template])

    # Our second image alignment visualization is *overlaying* the
    # aligned image on the template, that way we can obtain an idea of
    # how good our image alignment is.
    overlay = template.copy()
    output = aligned.copy()
    cv2.addWeighted(overlay, 0.5, output, 0.5, 0, output)

    if debug:
        # Show the two output image alignment visualizations.
        cv2.imshow("Image Alignment Stacked", stacked)
        cv2.imshow("Image Alignment Overlay", output)
        cv2.waitKey(0)

    return result
