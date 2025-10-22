# import cv2
# import numpy as np
# import os

# def calculate_crack_area(image_path, show_result=False, pixel_to_cm_ratio=0.05):
#     """
#     Detects cracks in an image and returns the crack area and percentage.

#     Args:
#         image_path (str): Path to the image file.
#         show_result (bool): If True, displays the original image and crack mask.
#         pixel_to_cm_ratio (float): Conversion ratio (1 pixel = X cm). 
#                                    Adjust this based on your camera calibration.

#     Returns:
#         dict: {
#             'status': 'success' or 'error',
#             'crack_area_px': float (in pixels),
#             'crack_area_sqft': float (in square feet),
#             'crack_percentage': float,
#             'message': str
#         }
#     """
#     # Validate path
#     if not os.path.exists(image_path):
#         return {
#             'status': 'error',
#             'message': f"File not found: {image_path}",
#             'crack_area_px': 0.0,
#             'crack_area_sqft': 0.0,
#             'crack_percentage': 0.0
#         }

#     # Load image
#     image = cv2.imread(image_path)
#     if image is None:
#         return {
#             'status': 'error',
#             'message': f"Unable to read image (check path or format): {image_path}",
#             'crack_area_px': 0.0,
#             'crack_area_sqft': 0.0,
#             'crack_percentage': 0.0
#         }

#     # Convert to grayscale
#     gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

#     # Enhance contrast
#     gray = cv2.equalizeHist(gray)

#     # Edge detection
#     edges = cv2.Canny(gray, 50, 150)

#     # Dilate to connect cracks
#     kernel = np.ones((3, 3), np.uint8)
#     dilated = cv2.dilate(edges, kernel, iterations=2)

#     # Find contours
#     contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

#     # Compute total crack area (in pixels)
#     total_area_px = sum(cv2.contourArea(c) for c in contours)

#     # Compute image area and percentage
#     image_area = gray.shape[0] * gray.shape[1]
#     damage_percent = (total_area_px / image_area) * 100 if image_area > 0 else 0

#     # Convert pixel area → cm² → square feet
#     area_cm2 = total_area_px * (pixel_to_cm_ratio ** 2)
#     area_sqft = area_cm2 / 929.0304  # 1 sq ft = 929.0304 cm²

#     # Optional visualization
#     if show_result:
#         import matplotlib.pyplot as plt
#         crack_mask = np.zeros_like(gray)
#         cv2.drawContours(crack_mask, contours, -1, 255, -1)

#         plt.figure(figsize=(10, 5))
#         plt.subplot(1, 2, 1)
#         plt.title("Original Image")
#         plt.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
#         plt.axis('off')

#         plt.subplot(1, 2, 2)
#         plt.title(f"Detected Cracks ({damage_percent:.2f}%)")
#         plt.imshow(crack_mask, cmap='gray')
#         plt.axis('off')

#         plt.show()

#     return {
#         'status': 'success',
#         'crack_area_px': float(total_area_px),
#         'crack_area': float(area_sqft),
#         'crack_percentage': float(damage_percent),
#         'message': 'Crack area calculated successfully'
#     }




# import cv2
# import numpy as np
# import matplotlib
# matplotlib.use('Agg')  # ✅ Prevent GUI crash in Flask threads
# import matplotlib.pyplot as plt
# import os
# import random
# def calculate_crack_area(image_path, pixels_per_inch=96, save_plot=True, save_path=None):
#     """
#     Detect crack length and width, convert both to feet, calculate area (sq.ft),
#     and save a compact crack detection plot image for frontend use.
#     """
#     # --- Load Image ---
#     image = cv2.imread(image_path)
#     if image is None:
#         raise ValueError(f"❌ Image not found or unreadable: {image_path}")

#     # --- Convert to Grayscale & Enhance ---
#     gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
#     gray = cv2.equalizeHist(gray)
#     blurred = cv2.GaussianBlur(gray, (5, 5), 0)

#     # --- Edge Detection ---
#     edges = cv2.Canny(blurred, 40, 150)
#     kernel = np.ones((3, 3), np.uint8)
#     dilated = cv2.dilate(edges, kernel, iterations=2)

#     # --- Find Contours ---
#     contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
#     if not contours:
#         return {'status': 'error', 'message': 'No cracks detected'}

#     # --- Largest Contour (main crack) ---
#     largest_contour = max(contours, key=cv2.contourArea)

#     # --- Bounding box for length and width ---
#     rect = cv2.minAreaRect(largest_contour)
#     (_, _), (width_px, height_px), _ = rect

#     # --- Convert pixel → inches → feet ---
#     length_in = max(width_px, height_px) / pixels_per_inch + 6
#     width_in = min(width_px, height_px) / pixels_per_inch + 6

#     length_ft = length_in / 12
#     width_ft = width_in / 12

#     # --- Calculate area (sq.ft) ---
#     area_sqft = length_ft * width_ft
#     random_number = random.randint(1000, 9999) 
#     # --- Visualization (Headless) ---
#     saved_plot_path = None
#     if save_plot:
#         overlay = image.copy()
#         cv2.drawContours(overlay, [largest_contour], -1, (255, 0, 0), 2)  # Red cracks

#         # Create smaller figure for frontend
#         fig, ax = plt.subplots(1, 2, figsize=(7, 4))
#         ax[0].imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
#         ax[0].set_title("Original")
#         ax[0].axis("off")

#         ax[1].imshow(cv2.cvtColor(overlay, cv2.COLOR_BGR2RGB))
#         ax[1].set_title(f"Crack\nL: {length_ft:.2f} ft | W: {width_ft:.2f} ft\nA: {area_sqft:.3f} sq.ft")
#         ax[1].axis("off")

#         plt.tight_layout()

#         # Save smaller web-friendly plot
#         if save_path is None:
#             save_path = os.path.join(os.path.dirname(image_path), "crack_detection_result_small_{random_number}.png")

#         plt.savefig(save_path, dpi=100, bbox_inches='tight')
#         plt.close(fig)
#         saved_plot_path = save_path
#         print(f"✅ Plot saved (frontend size): {save_path}")

#     return {
#         'status': 'success',
#         'length_ft': round(length_ft, 3),
#         'width_ft': round(width_ft, 3),
#         'crack_area': round(area_sqft, 3),
#         'plot_path': saved_plot_path,
#         'message': '✅ Crack measurements calculated successfully (sq.ft)'
#     }


import cv2
import numpy as np
import matplotlib
matplotlib.use('Agg')  # ✅ Prevent GUI crash in Flask threads
import matplotlib.pyplot as plt
import os
import random

def calculate_crack_area(image_path, pixels_per_inch=96, save_plot=True, save_path=None):
    """
    Detect crack length and width, convert both to feet, calculate area (sq.ft),
    and save a compact crack detection plot image for frontend use.
    """
    # --- Load Image ---
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"❌ Image not found or unreadable: {image_path}")

    # --- Convert to Grayscale & Enhance ---
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.equalizeHist(gray)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # --- Edge Detection ---
    edges = cv2.Canny(blurred, 40, 150)
    kernel = np.ones((3, 3), np.uint8)
    dilated = cv2.dilate(edges, kernel, iterations=2)

    # --- Find Contours ---
    contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return {'status': 'error', 'message': 'No cracks detected'}

    # --- Largest Contour (main crack) ---
    largest_contour = max(contours, key=cv2.contourArea)

    # --- Bounding box for length and width ---
    rect = cv2.minAreaRect(largest_contour)
    (_, _), (width_px, height_px), _ = rect

    # --- Convert pixel → inches → feet ---
    length_in = max(width_px, height_px) / pixels_per_inch + 6
    width_in = min(width_px, height_px) / pixels_per_inch + 6

    length_ft = length_in / 12
    width_ft = width_in / 12

    # --- Calculate area (sq.ft) ---
    area_sqft = length_ft * width_ft

    # --- Random unique filename suffix ---
    random_number = random.randint(1000, 9999)

    # --- Visualization (Headless) ---
    saved_plot_path = None
    if save_plot:
        overlay = image.copy()
        cv2.drawContours(overlay, [largest_contour], -1, (255, 0, 0), 2)  # Red cracks

        # Create smaller figure for frontend
        fig, ax = plt.subplots(1, 2, figsize=(7, 4))
        ax[0].imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        ax[0].set_title("Original")
        ax[0].axis("off")

        ax[1].imshow(cv2.cvtColor(overlay, cv2.COLOR_BGR2RGB))
        ax[1].set_title(f"Crack\nL: {length_ft:.2f} ft | W: {width_ft:.2f} ft\nA: {area_sqft:.3f} sq.ft")
        ax[1].axis("off")

        plt.tight_layout()

        # ✅ Proper unique filename
        if save_path is None:
            filename = f"crack_detection_result_small_{random_number}.png"
            save_path = os.path.join(os.path.dirname(image_path), filename)

        plt.savefig(save_path, dpi=100, bbox_inches='tight')
        plt.close(fig)
        saved_plot_path = save_path
        print(f"✅ Plot saved (frontend size): {save_path}")

    return {
        'status': 'success',
        'length_ft': round(length_ft, 3),
        'width_ft': round(width_ft, 3),
        'crack_area': round(area_sqft, 3),
        'plot_path': saved_plot_path,
        'filename': filename,
        'message': '✅ Crack measurements calculated successfully (sq.ft)'
    }
