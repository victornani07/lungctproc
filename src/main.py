import annotations as ant

from pdf import extract, create_pdf

dicom_set_path_1 = "D:/Dox/Projects/Licenta/Data/LIDC/set_2"
xml_path_1 = "D:/Dox/Projects/Licenta/Data/LIDC/set_2_annotations.xml"
segmented_lungs_path_1 = 'segmented-lungs-2.png'
internal_structure_path_1 = 'internal-structure-2.png'
nodules_mask_path_1= 'nodules-mask-2.png'
pdf_path_1 = 'results-pdf-2.pdf'

sop_uids, coordinates, x_edges, y_edges, nodules_id, characteristics, nodules_surfaces = ant.characteristics(xml_path_1)

slices = extract(dicom_set_path_1, 
                 sop_uids, coordinates, 
                 segmented_lungs_path_1, 
                 internal_structure_path_1, 
                 nodules_mask_path_1)

create_pdf(slices, 
           sop_uids, 
           nodules_id, 
           nodules_surfaces, 
           coordinates, 
           x_edges, 
           y_edges, 
           segmented_lungs_path_1, 
           internal_structure_path_1, 
           nodules_mask_path_1, 
           pdf_path_1)