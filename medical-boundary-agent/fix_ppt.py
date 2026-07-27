from pptx import Presentation
from lxml import etree
from copy import deepcopy

src = r'C:\Users\24991\Desktop\Modern Redesign (Same Content).pptx'
dst = r'C:\Users\24991\Desktop\Modern Redesign Fixed.pptx'

prs = Presentation(src)

def get_bg_group_xml(slide):
    """Get XML of GROUP shapes that are background elements (positioned at slide edges)"""
    bg_elements = []
    for shape in slide.shapes:
        if shape.shape_type == 6:  # GROUP
            left = int(shape.left)
            top = int(shape.top)
            width = int(shape.width)
            height = int(shape.height)
            sw = int(prs.slide_width)
            sh = int(prs.slide_height)
            # Background elements are at edges: top bar, bottom corners, etc.
            is_edge = (
                (top == 0 and width == sw) or   # Full-width top bar
                (top == 0 and left == sw - width and height == height)  # Top-right corner
            )
            if is_edge:
                bg_elements.append(etree.tostring(shape._element))
    return bg_elements

# Get background elements from slide 2 (reference)
ref_slide = prs.slides[1]  # slide 2
bg_xmls = get_bg_group_xml(ref_slide)
print(f'Found {len(bg_xmls)} background elements in slide 2')

# Also get from slide 3
ref_slide3 = prs.slides[2]
bg_xmls3 = get_bg_group_xml(ref_slide3)
for xml in bg_xmls3:
    # Check if already captured
    already = False
    for existing in bg_xmls:
        if len(xml) == len(existing):
            already = True
            break
    if not already:
        bg_xmls.append(xml)

print(f'Total unique background elements: {len(bg_xmls)}')

# Apply to slides 5-12 (index 4-11)
for i in range(4, len(prs.slides)):
    slide = prs.slides[i]
    # Check if slide already has background elements
    existing_bg = get_bg_group_xml(slide)
    if existing_bg:
        print(f'Slide {i+1}: already has {len(existing_bg)} bg elements, skipping')
        continue
    
    # Find the slide's group elements container
    for xml in bg_xmls:
        new_element = etree.fromstring(xml)
        slide.shapes._spTree.append(new_element)
    print(f'Slide {i+1}: applied {len(bg_xmls)} background elements')

prs.save(dst)
print(f'\nSaved to: {dst}')
