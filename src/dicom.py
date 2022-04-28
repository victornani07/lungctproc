import pydicom as dicom
import matplotlib.pyplot as plt
import numpy as np
import os

from scipy import ndimage as ndi

from skimage.segmentation import clear_border
from skimage.measure import label, regionprops
from skimage.morphology import ball, disk, binary_erosion, binary_closing
from skimage.filters import roberts


def slices(path):
  # Storing all the DICOM files in a list
  slices = [dicom.dcmread(path + '/' + s) for s in os.listdir(path)]
  slices.sort(key = lambda x: float(x.ImagePositionPatient[2]))
  
  # Taking the z-coordinates of 2 consecutive files to determine
  # the slice thickness
  z_pos_0 = slices[0].ImagePositionPatient[2]
  z_pos_1 = slices[1].ImagePositionPatient[2]
  slice_thickness = np.abs(z_pos_0 - z_pos_1)
  
  # Setting the SliceThickness attribute to a default value
  for s in slices:
    s.SliceThickness = slice_thickness

  return slices


def huscale(slices):
  # Getting the image itself from the DICOM files
  image = np.stack([s.pixel_array for s in slices])
  image = image.astype(np.int16)

  # Setting the outside-of-scan pixels to 0
  # The air has a HU = 0
  image[image == -2000] = 0

  intercept = slices[0].RescaleIntercept
  slope = slices[0].RescaleSlope
  
  # To convert into HU units, we use the following formula:
  # U = m * SV + b, where
  # U is the desired unit(HU in this case)
  # m is the RescaleSlope
  # SV is the actual value of pixels stored int pixel_array
  # b is the RescaleIntercept
  if slope != 1:
    image = slope * image.astype(np.float64)
    image = image.astype(np.int16)

  image += np.int16(intercept)

  image_hu_pixels = np.array(image, dtype=np.int16)

  return image_hu_pixels


def segment(image, do_plot=False):
  # 1. Create the binary mask
  binary_image = image < -400

  # 2. Maintain only the lungs
  cleared_binary_image = clear_border(binary_image)

  # 3. Label the image
  label_image = label(cleared_binary_image)

  # 4. Maintain only 2 labels with the largest areas
  areas = [r.area for r in regionprops(label_image)]
  areas.sort()
  if len(areas) > 2:
    for region in regionprops(label_image):
      if region.area < areas[-2]:
        for coordinates in region.coords:                
          label_image[coordinates[0], coordinates[1]] = 0

  plt_binary = label_image > 0
  binary = label_image > 0

  # 5. Apply erosion to separate the nodules from the blood vessels
  selem = disk(2)
  erosion = binary_erosion(binary, selem)
  binary = erosion

  # 6. Apply closure to keep nodules attacked to lung walls
  selem = disk(10)
  closure = binary_closing(binary, selem)
  binary = closure

  # 7. Fill in the small holes inside the binary mask of lungs
  edges = roberts(binary)
  fill_holes = ndi.binary_fill_holes(edges)
  binary = fill_holes

  # 8. Apply the binary mask to the original mask
  get_high_vals = binary == 0
  image[get_high_vals] = 0

  if do_plot == True:
    # Define the the plots
    f, plots = plt.subplots(2, 4, figsize=(25, 10))

    plots[0, 0].axis('off')
    plots[0, 0].imshow(binary_image, cmap=plt.cm.bone)

    plots[0, 1].axis('off')
    plots[0, 1].imshow(cleared_binary_image, cmap=plt.cm.bone)

    plots[0, 2].axis('off')
    plots[0, 2].imshow(label_image, cmap=plt.cm.bone)

    plots[0, 3].axis('off')
    plots[0, 3].imshow(plt_binary, cmap=plt.cm.bone)

    plots[1, 0].axis('off')
    plots[1, 0].imshow(erosion, cmap=plt.cm.bone) 

    plots[1, 1].axis('off')
    plots[1, 1].imshow(closure, cmap=plt.cm.bone) 

    plots[1, 2].axis('off')
    plots[1, 2].imshow(fill_holes, cmap=plt.cm.bone) 

    plots[1, 3].axis('off')
    plots[1, 3].imshow(image, cmap=plt.cm.bone)

  return image, fill_holes


def filtervess(images):
  selem = ball(2)
  binary = binary_closing(images, selem)

  label_scan = label(binary)

  areas = [r.area for r in regionprops(label_scan)]
  areas.sort()

  for r in regionprops(label_scan):
    max_x, max_y, max_z = 0, 0, 0
    min_x, min_y, min_z = 1000, 1000, 1000
      
    for c in r.coords:
      max_z = max(c[0], max_z)
      max_y = max(c[1], max_y)
      max_x = max(c[2], max_x)
          
      min_z = min(c[0], min_z)
      min_y = min(c[1], min_y)
      min_x = min(c[2], min_x)

    if (min_z == max_z or min_y == max_y or min_x == max_x or r.area > areas[-3]):
      for c in r.coords:
        images[c[0], c[1], c[2]] = 0
    else:
      index = (max((max_x - min_x), (max_y - min_y), (max_z - min_z))) / (min((max_x - min_x), (max_y - min_y) , (max_z - min_z)))

  return images



