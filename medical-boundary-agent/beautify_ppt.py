from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
import os

src = r'C:\Users\24991\Desktop\RLtest.pptx'
dst = r'C:\Users\24991\Desktop\RLtest_beautified.pptx'

prs = Presentation(src)

# Color palette
DARK_BLUE = RGBColor(0x1B, 0x2A, 0x4A)
ACCENT_BLUE = RGBColor(0x2E, 0x86, 0xC1)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
LIGHT_GRAY = RGBColor(0xF0, 0xF0, 0xF0)
DARK_GRAY = RGBColor(0x33, 0x33, 0x33)
MEDIUM_GRAY = RGBColor(0x66, 0x66, 0x66)

def style_textbox(shape, title=False, body=False, code=False):
    """Apply consistent styling to a text box"""
    if not shape.has_text_frame:
        return
    tf = shape.text_frame
    tf.word_wrap = True
    
    for para in tf.paragraphs:
        para.alignment = PP_ALIGN.LEFT
        if para.text.strip() == '':
            continue
            
        for run in para.runs:
            if title:
                run.font.name = 'Calibri'
                run.font.size = Pt(28)
                run.font.bold = True
                run.font.color.rgb = DARK_BLUE
            elif body:
                run.font.name = 'Calibri'
                run.font.size = Pt(16)
                run.font.bold = False
                run.font.color.rgb = DARK_GRAY
            else:
                # Keep existing but clean up
                if run.font.size is None or run.font.size < Pt(10):
                    run.font.size = Pt(14)
                if run.font.name is None:
                    run.font.name = 'Calibri'
                if run.font.color.rgb is None or str(run.font.color.rgb) == '000000':
                    run.font.color.rgb = DARK_GRAY

for idx, slide in enumerate(prs.slides):
    # Determine slide type by content
    for shape in slide.shapes:
        if not shape.has_text_frame:
            continue
        text = shape.text_frame.text.strip()
        
        # Slide 1: Title slide
        if idx == 0:
            style_textbox(shape, title=True, body=False)
            if 'Agent Internal' in text or 'GiGPO' in text:
                for para in shape.text_frame.paragraphs:
                    for run in para.runs:
                        run.font.size = Pt(20)
                        run.font.color.rgb = ACCENT_BLUE
                        run.font.bold = False
            continue
        
        # Section title shapes (typically short text at top)
        if shape.shape_type == 1:  # AUTO_SHAPE
            is_title = len(text) < 60 and not text.startswith('  ')
            style_textbox(shape, title=is_title, body=not is_title)
            if is_title:
                for para in shape.text_frame.paragraphs:
                    for run in para.runs:
                        run.font.size = Pt(32)
                        run.font.color.rgb = DARK_BLUE
            continue
        
        # Regular text boxes
        if shape.shape_type == 17:  # TEXT_BOX
            if len(text) < 80:
                style_textbox(shape, title=True)
                for para in shape.text_frame.paragraphs:
                    for run in para.runs:
                        run.font.size = Pt(24)
                        run.font.color.rgb = DARK_BLUE
            else:
                style_textbox(shape, body=True)

# Set uniform slide background colors
for slide in prs.slides:
    background = slide.background
    fill = background.fill
    # Keep existing background (often an image) - don't override

prs.save(dst)
print(f'Saved to: {dst}')
