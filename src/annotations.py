import xml.etree.ElementTree as et

def characteristics(xml_path):
  tree = et.parse(xml_path)
  root = tree.getroot()
  sop_uids = []
  coordinates = []
  nodules_id = []
  nodules_surfaces = []
  characteristics = []
  x_edges = []
  y_edges = []
  i = 0
  counter = 0

  # Getting access to all tags
  for reading_session in root.getchildren():
    if reading_session.tag == "{http://www.nih.gov}readingSession":
      for unblinded_read_nodule in reading_session.getchildren():
        if unblinded_read_nodule.tag == "{http://www.nih.gov}unblindedReadNodule": 

          for roi in unblinded_read_nodule.getchildren():
            if roi.tag == "{http://www.nih.gov}noduleID":
              nodules_id.append(roi.text)
              nodules_surfaces.append(0)
              counter += 1
            if roi.tag == "{http://www.nih.gov}characteristics":
              ch = []
              for characteristic in roi.getchildren():
                ch.append([characteristic.tag.split('}')[1], characteristic.text])
              characteristics.append(ch)
            if roi.tag == "{http://www.nih.gov}roi":
              sop_uids.append(roi[1].text)
              coord = []
              min_x = 512
              min_y = 512
              max_x = -1
              max_y = -1
              for i in range(3, len(roi.getchildren())):
                x = int(roi[i][0].text)
                y = int(roi[i][1].text)
                if x < min_x:
                  min_x = x
                if x > max_x:
                  max_x = x
                if y < min_y:
                  min_y = y
                if y > max_y:
                  max_y = y
                coord.append(tuple((x, y)))
              coordinates.append(coord)  
              x_edges.append(tuple((min_x, max_x)))
              y_edges.append(tuple((min_y, max_y)))
              nodules_surfaces[counter - 1] += 1

  return sop_uids, coordinates, x_edges, y_edges, nodules_id, characteristics, nodules_surfaces