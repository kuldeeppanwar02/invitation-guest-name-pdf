import os
import io
import urllib.request
from typing import Optional
from fastapi import FastAPI, Form
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader
from PyPDF2 import PdfReader, PdfWriter
from PIL import Image, ImageDraw, ImageFont

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
TEMPLATE_PATH = os.path.join(BASE_DIR, "shadi card.pdf")
FONT_PATH = os.path.join(os.path.dirname(__file__), "NotoSansDevanagari-Regular.ttf")

if not os.path.exists(FONT_PATH):
    print("Downloading Noto Sans Devanagari font...")
    font_url = "https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoSansDevanagari/NotoSansDevanagari-Regular.ttf"
    urllib.request.urlretrieve(font_url, FONT_PATH)

pdfmetrics.registerFont(TTFont("NotoSansDevanagari", FONT_PATH))

# ==========================================
# CONFIGURATION FOR TEXT PLACEMENT
# Adjust these values to fit your PDF perfectly!
# ==========================================
START_X = 200      # The Left-to-Right position where the name starts right after 'श्रीमान्'
START_Y = 400      # The Bottom-to-Top position of the first line
LINE_SPACING = 30  # Space between multiple family member lines
TEXT_COLOR = "#5c2a1a" # Dark maroon/brown color matching traditional wedding text
FONT_SIZE_MAIN = 22
FONT_SIZE_FAMILY = 16

def draw_text_as_image(canvas, text, x_pos, y_pos, font_path, font_size, color_hex):
    # Dynamically size the image based on the text
    try:
        font = ImageFont.truetype(font_path, font_size)
    except:
        font = ImageFont.load_default()
        
    temp_img = Image.new('RGBA', (1, 1), (255, 255, 255, 0))
    temp_d = ImageDraw.Draw(temp_img)
    left, top, right, bottom = temp_d.textbbox((0, 0), text, font=font)
    text_w = right - left
    text_h = bottom - top + 10 # add padding
    
    # Create the actual image container
    img = Image.new('RGBA', (text_w, text_h), (255, 255, 255, 0))
    d = ImageDraw.Draw(img)
    
    # Parse color
    color_hex = color_hex.lstrip('#')
    if len(color_hex) == 6:
        r, g, b = tuple(int(color_hex[i:i+2], 16) for i in (0, 2, 4))
    else:
        r, g, b = (92, 42, 26) # fallback maroon
        
    d.text((0, 0), text, font=font, fill=(r, g, b, 255))
    
    img_buffer = io.BytesIO()
    img.save(img_buffer, format="PNG")
    img_buffer.seek(0)
    img_reader = ImageReader(img_buffer)
    
    # drawImage at the exact X, Y
    canvas.drawImage(img_reader, x_pos, y_pos, text_w, text_h, mask='auto')

@app.post("/api/generate")
async def generate_pdf(
    guest_name: str = Form(...),
    family_members: Optional[str] = Form("")):
    
    try:
        overlay_buffer = io.BytesIO()
        c = canvas.Canvas(overlay_buffer, pagesize=letter)
        
        # Write guest name right after श्रीमान्
        draw_text_as_image(c, guest_name, START_X, START_Y, FONT_PATH, FONT_SIZE_MAIN, TEXT_COLOR)
        
        if family_members:
            lines = family_members.split('\n')
            current_y = START_Y - LINE_SPACING
            for line in lines:
                if line.strip():
                    # For family members, we can still use START_X to align them on the left, 
                    # or slightly indent them. Lets use START_X
                    draw_text_as_image(c, line.strip(), START_X, current_y, FONT_PATH, FONT_SIZE_FAMILY, TEXT_COLOR)
                    current_y -= LINE_SPACING
                
        c.save()
        overlay_buffer.seek(0)
        
        # 2. Merge overlay with template in memory
        template_reader = PdfReader(TEMPLATE_PATH)
        overlay_reader = PdfReader(overlay_buffer)
        
        writer = PdfWriter()
        
        page0 = template_reader.pages[0]
        page0.merge_page(overlay_reader.pages[0])
        writer.add_page(page0)
        
        for i in range(1, len(template_reader.pages)):
            writer.add_page(template_reader.pages[i])
            
        output_buffer = io.BytesIO()
        writer.write(output_buffer)
        pdf_bytes = output_buffer.getvalue()
            
        safe_filename = urllib.parse.quote(f"{guest_name}_Invitation.pdf")
        return Response(
            content=pdf_bytes, 
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename*=utf-8''{safe_filename}"
            }
        )
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail=str(e))

# Serve frontend at root AFTER all api routes
app.mount("/", StaticFiles(directory=os.path.join(BASE_DIR, "frontend"), html=True), name="frontend")

