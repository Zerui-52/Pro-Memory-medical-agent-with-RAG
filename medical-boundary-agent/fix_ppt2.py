from pptx import Presentation
from lxml import etree
from copy import deepcopy

src = r'C:\Users\24991\Desktop\Modern Redesign (Same Content).pptx'
dst = r'C:\Users\24991\Desktop\Modern Redesign Fixed2.pptx'

prs = Presentation(src)

def get_non_text_group_xmls(slide):
    """Get XML of GROUP shapes that are likely background (not text-heavy areas)"""
    sw = int(prs.slide_width)
    sh = int(prs.slide_height)
    results = []
    for shape in slide.shapes:
        if shape.shape_type != 6:  # GROUP only
            continue
        left = int(shape.left)
        top = int(shape.top)
        w = int(shape.width)
        h = int(shape.height)
        
        # Skip large center-aligned groups (likely content illustrations)
        # Content groups are typically in the middle-right area
        is_content = (
            left > sw * 0.4 and top > sh * 0.1 and w < sw * 0.5 and h < sh * 0.8
            and left + w < sw * 0.95
        )
        # But include small edge elements (decorations)
        is_edge = (
            top <= 0 or  # top edge
            left <= 0 or  # left edge
            left + w >= sw or  # right edge
            top + h >= sh or  # bottom edge
            (w < sw * 0.05 and h < sh * 0.05) or  # small elements
            (h < sw * 0.01 and w == sw)  # thin full-width bar
        )
        
        if is_edge or (not is_content and (w < sw * 0.35 or h < sh * 0.1)):
            xml = etree.tostring(shape._element)
            results.append((left, top, xml))
    return results

# Get background elements from slide 2 and 3
ref_bg = []
for idx in [1, 2, 3]:  # slides 2, 3, 4
    slide = prs.slides[idx]
    elements = get_non_text_group_xmls(slide)
    ref_bg.extend(elements)
    print(f'Slide {idx+1}: found {len(elements)} background groups')

# Dedup by position
seen_positions = set()
unique_bg = []
for left, top, xml in ref_bg:
    pos_key = (left // 10000, top // 10000)
    if pos_key not in seen_positions:
        seen_positions.add(pos_key)
        unique_bg.append(xml)

print(f'Total unique background elements: {len(unique_bg)}')

# Apply to slides 5-12
for i in range(4, len(prs.slides)):
    slide = prs.slides[i]
    # Check which bg elements this slide already has
    existing = get_non_text_group_xmls(slide)
    existing_positions = set()
    for left, top, xml in existing:
        existing_positions.add((left // 10000, top // 10000))

    count = 0
    for xml in unique_bg:
        new_elem = etree.fromstring(xml)
        # Quick position check from the XML
        slide.shapes._spTree.append(new_elem)
        count += 1
    print(f'Slide {i+1}: added {count} background elements')

prs.save(dst)
print(f'\nSaved to: {dst}')
