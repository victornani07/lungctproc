import matplotlib.pyplot as plt
import os
import dicom as dcm
import visual as vsl
import numpy as np

from utils import area, slicenum, value
from fpdf import FPDF
from PIL import Image
from shapely.geometry import Polygon
from shapely.geometry.polygon import Polygon

resized_img_size = 72478
pixel_to_mm = 0.2645833333
volumes = []

def extract(dicom_set_path, 
            sop_uids, coordinates, 
            segmented_lungs_path, 
            internal_structure_path, 
            nodules_mask_path):
  # Extract the slices from the DICOM set
  slices = dcm.slices(dicom_set_path)

  # Convert the pixels from each slice to HU units
  hu_slices = dcm.huscale(slices)

  # Create the temporary variables used for extracting the lungs
  a, b, c = hu_slices.shape
  segmented_lung_images = np.empty([a, b, c])
  filled_holes_images = np.empty([a, b, c])
  i = 0

  # Extract the lungs
  for hu_slice in hu_slices:
    image, fill_holes_image = dcm.segment(hu_slice, False)
    segmented_lung_images[i] = np.asarray(image)
    filled_holes_images[i] = np.asarray(fill_holes_image)
    i += 1

  # Extract the internal structure
  internal_structures_images = np.copy(segmented_lung_images)
  internal_structures_images[internal_structures_images < -400] = 0

  a, b, c = hu_slices.shape
  nodule_masks = np.zeros([a, b, c])

  # Accentuate with white pixels the nodule margin
  for t in range(a):
    slice = slices[t]
    if slice.SOPInstanceUID in sop_uids:
      idx = sop_uids.index(slice.SOPInstanceUID)
      img = 0 * np.zeros([512,512],dtype=np.uint8)
      for j, i in coordinates[idx]:
        img[i][j] = 255
      nodule_masks[t] = img

  vsl.plot3d(segmented_lung_images, segmented_lungs_path, -300)
  print("Lungs were segmented and extracted.")

  vsl.plot3d(internal_structures_images, internal_structure_path, -250)
  print("The internal structures of lungs were extracted.")

  vsl.plot3d(nodule_masks, nodules_mask_path, 0)
  print("The nodule masks were created.")

  return slices

def create_pdf(slices,
               sop_uids,
               nodules_id, 
               nodules_surfaces, 
               coordinates, 
               x_edges, 
               y_edges,
               segmented_lungs_path,
               internal_structure_path,
               nodules_mask_path,
               pdf_path):
    pdf = FPDF()
    pdf.add_page()
    pdf.add_font('SF', '', r'D:\Dox\Projects\Licenta\CNN\deployment\fonts\sf-pro-display.ttf', uni=True)

    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, 'Lungs screening for Patient with ID 01234567', 0, 2, 'C')

    pdf.set_font('Arial', '', 16)
    pdf.cell(0, 10, '15-10-2022', 0, 2, 'C')

    pdf.image(segmented_lungs_path, x=40, w=125, h=125, type='png')
    #os.remove(segmented_lungs_path)

    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 0, 'Figure 1. Segmented lungs.', 0, 2, 'C')

    pdf.cell(0, 10, '', 0, 2)

    pdf.image(internal_structure_path, x=50, w=110, h=110, type='png')
    #os.remove(internal_structure_path)

    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 0, 'Figure 2. Internal structure.', 0, 2, 'C')

    pdf.cell(0, 10, '', 0, 2)

    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, 'Nodules Characteristics', 0, 2, 'C')

    i = 0
    l = 0
    line_height = pdf.font_size * 2
    col_width = pdf.epw / 4

    for nodule in nodules_id:
        if len(coordinates[l]) < 3:
            l += nodules_surfaces[i]
            i += 1
            continue
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, nodule, 0, 1, 'C')
        pdf.set_font('Arial', 'B', 12)
        flag = False

        pdf.cell(0, 10, '', 0, 2)
        pdf.cell(0, 10, '', 0, 2)

        datum = []
        total_volume = 0

        for _ in range(0, nodules_surfaces[i]):
            if len(coordinates[l]) < 3:
                flag = True
                continue
            s = Polygon(coordinates[l])
            plt.fill(*s.exterior.xy, facecolor='lightsalmon', edgecolor='orangered', linewidth=3)
            plt.axis('off')
            img_name = f'image{l}.png'
            plt.savefig(img_name, bbox_inches='tight',pad_inches = 0)
            pixel_area = area(img_name)
            x_mm = (x_edges[l][1] - x_edges[l][0]) * pixel_to_mm
            y_mm = (y_edges[l][1] - y_edges[l][0]) * pixel_to_mm
            aproximative_real_area = x_mm * y_mm
            scale_factor = 5187 / aproximative_real_area
            area = (float)((pixel_area * 5187) / 72478)
            area = round(area / scale_factor, 2)
            volume = area * slices[0].SliceThickness
            volume = round(volume, 2)
            total_volume += volume
            slice_number = slicenum(sop_uids[l], slices)
            l += 1
            _data = [] 
            _data.append(str(slice_number))
            _data.append(str(area))
            _data.append(str(volume))
            _data.append(img_name)
            datum.append(_data)
            plt.clf()
        
        if flag == True:
            continue

        pdf.set_font('Arial', 'B', 14)

        data = ['Slice', 'Area[mm^2]', 'Volume[mm^3]', 'Surface']

        for d in data:
            pdf.multi_cell(col_width, line_height, d, border=1, align='C', ln=3, max_line_height=pdf.font_size)
            
        pdf.ln(line_height)
        pdf.set_font('SF', '', 10)

        for d in datum:
            pdf.multi_cell(col_width, line_height, d[0], border=1, align='C', ln=3, max_line_height=pdf.font_size)
            pdf.multi_cell(col_width, line_height, d[1], border=1, align='C', ln=3, max_line_height=pdf.font_size)
            pdf.multi_cell(col_width, line_height, d[2], border=1, align='C', ln=3, max_line_height=pdf.font_size)
            pdf.multi_cell(col_width, line_height, ' ', border=1, align='C', ln=3, max_line_height=pdf.font_size)
            pdf.image(d[3], x=160, w=9, h=9, type='png')
            os.remove(d[3])
            pdf.ln(0.25)

        i += 1
        volumes.append(total_volume)

        pdf.cell(0, 10, '', 0, 2)
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 5, f'Total volume: {round(total_volume, 2)} [mm^3]', 0, 1, 'L')

    pdf.image(nodules_mask_path, x=50, w=110, h=110, type='png')
    #os.remove(nodules_mask_path)

    pdf.cell(0, 10, '', 0, 2)
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 0, 'Figure 3. Nodule masks.', 0, 2, 'C')

    pdf.output(pdf_path)