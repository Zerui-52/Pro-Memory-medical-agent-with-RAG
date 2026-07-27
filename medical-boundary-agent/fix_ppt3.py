from pptx import Presentation
from lxml import etree
from copy import deepcopy

src = r'C:\Users\24991\Desktop\Modern Redesign (Same Content).pptx'
dst = r'C:\Users\24991\Desktop\Modern Redesign Fixed3.pptx'

prs = Presentation(src)
ns = {
    'p': 'http://schemas.openxmlformats.org/presentationml/2006/main',
    'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
}

def get_group_info(slide):
    """Return {(x, y, cx, cy): xml} for all group shapes"""
    spTree = slide.shapes._spTree
    groups = spTree.findall('.//p:grpSp', ns)
    result = {}
    for grp in groups:
        xfrm = grp.find('./p:grpSpPr/a:xfrm', ns)
        if xfrm is None:
            continue
        off = xfrm.find('a:off', ns)
        ext = xfrm.find('a:ext', ns)
        if off is None or ext is None:
            continue
        x = int(off.get('x'))
        y = int(off.get('y'))
        cx = int(ext.get('cx'))
        cy = int(ext.get('cy'))
        key = (x // 1000, y // 1000, cx // 1000, cy // 1000)
        result[key] = etree.tostring(grp)
    return result

# Get all groups from slides 2-4 (source templates)
source_groups = {}
for idx in [1, 2, 3]:
    info = get_group_info(prs.slides[idx])
    source_groups.update(info)
    print(f'Slide {idx+1}: {len(info)} groups')

# For each target slide 5-12, find missing groups and add them
for i in range(4, len(prs.slides)):
    slide = prs.slides[i]
    existing = get_group_info(slide)
    missing = 0
    for key, xml in source_groups.items():
        if key not in existing:
            new_elem = etree.fromstring(xml)
            # Regenerate id to avoid conflicts
            cNvPr = new_elem.find('.//p:cNvPr', ns)
            if cNvPr is not None:
                old_id = cNvPr.get('id')
                cNvPr.set('id', f'{old_id}_{i+1}')
            slide.shapes._spTree.append(new_elem)
            missing += 1
    print(f'Slide {i+1}: added {missing} missing groups')

prs.save(dst)
print(f'\nSaved to: {dst}')
