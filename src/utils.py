import cv2 as cv

subtlety_config = [ 
    "Extreme subtlety",
    "Between Extreme subtlety and Obvious",
    "Between Extreme subtlety and Obvious",
    "Between Extreme subtlety and Obvious",
    "Obvious",
    "\\"
]

internal_structure_config = [ 
    "Soft",
    "Fluid",
    "Flat",
    "Air",
    "\\"
]

calcification_config = [ 
    "Popcorn",
    "Luminated",
    "Solid",
    "Central",
    "Non-central",
    "Absent"
]

sphericity_config = [ 
    "Linear",
    "Between Linear and Ovoid",
    "Ovoid",
    "Between Ovoid and Round",
    "Round",
    "\\"
]

margin_config = [ 
    "Poorly defined",
    "Between Poorly defined and Sharp",
    "Between Poorly defined and Sharp",
    "Between Poorly defined and Sharp",
    "Sharp",
    "\\"
]

lobulation_config = [ 
    "None",
    "Between None and Marked",
    "Between None and Marked",
    "Between None and Marked",
    "Marked",
    "\\"
]

spiculation_config = [ 
    "None",
    "Between None and Marked",
    "Between None and Marked",
    "Between None and Marked",
    "Marked",
    "\\"
]

texture_config = [ 
    "GGO",
    "Between GGO and Part-solid",
    "Part-solid",
    "Between Part-solid and Solid",
    "Solid",
    "\\"
]

malignancy_config = [ 
    "Highly unlikely",
    "Moderately unlikely",
    "Indeterminate",
    "Moderately suspicious",
    "Highly suspicious",
    "\\"
]

def area(img_name):
    img = cv.imread(img_name,0)
    _, thresh = cv.threshold(img,127,255,0)
    contours, _ = cv.findContours(thresh, 1, 2)
    cnt = contours[0]
    area = cv.contourArea(cnt)

    return area


def slicenum(slices, sop_uid):
    for i in range(0, len(slices)):
        if slices[i].SOPInstanceUID == sop_uid:
            return i

    return -1  


def value(title, value):
    if value > 6:
        return "\\"

    idx = value - 1

    if title == "Subtlety":
        return subtlety_config[idx]
    
    if title == "Internal structure":
        return internal_structure_config[idx]
    
    if title == "Calcification":
        return calcification_config[idx]
    
    if title == "Sphericity":
        return sphericity_config[idx]

    if title == "Margin":
        return margin_config[idx]
    
    if title == "Lobulation":
        return lobulation_config[idx]
    
    if title == "Spiculation":
        return spiculation_config[idx]
    
    if title == "Texture":
        return texture_config[idx]
    
    if title == "Malignancy":
        return malignancy_config[idx]
    
    return "\\\\"