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
from PyPDF2 import PdfReader, PdfWriter

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
TEMPLATE_PATH = os.path.join(BASE_DIR, "template.pdf")
FONT_PATH = os.path.join(os.path.dirname(__file__), "NotoSansDevanagari-Regular.ttf")

# ==========================================
# AUTO-DOWNLOAD MISSING ASSETS FOR CLOUD
# ==========================================
if not os.path.exists(FONT_PATH):
    print("Downloading Noto Sans Devanagari font...")
    font_url = "https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoSansDevanagari/NotoSansDevanagari-Regular.ttf"
    urllib.request.urlretrieve(font_url, FONT_PATH)

if not os.path.exists(TEMPLATE_PATH):
    print("Generating dummy template.pdf...")
    c = canvas.Canvas(TEMPLATE_PATH, pagesize=letter)
    c.setFillColor(HexColor("#FFFDD0"))
    c.rect(0, 0, letter[0], letter[1], stroke=0, fill=1)
    c.setFillColor(HexColor("#D4AF37"))
    c.setFont("Helvetica-Bold", 40)
    c.drawCentredString(letter[0]/2, 600, "Wedding Invitation")
    c.setFont("Helvetica", 20)
    c.drawCentredString(letter[0]/2, 500, "You are cordially invited to our wedding.")
    c.setFont("Helvetica", 18)
    c.drawCentredString(letter[0]/2, 350, "श्रीमान _____________________")
    c.showPage()
    # Create 2 more dummy pages
    for page_num in range(2, 4):
        c.setFillColor(HexColor("#FFFDD0"))
        c.rect(0, 0, letter[0], letter[1], stroke=0, fill=1)
        c.setFillColor(HexColor("#D4AF37"))
        c.setFont("Helvetica", 30)
        c.drawCentredString(letter[0]/2, 400, f"Page {page_num}: Content Details")
        c.showPage()
    c.save()

pdfmetrics.registerFont(TTFont("NotoSansDevanagari", FONT_PATH))

@app.post("/api/generate")
async def generate_pdf(
    guest_name: str = Form(...),
    family_members: Optional[str] = Form("")):
    
    try:
        # 1. Create overlay PDF in memory
        overlay_buffer = io.BytesIO()
        c = canvas.Canvas(overlay_buffer, pagesize=letter)
        
        c.setFillColor(HexColor("#FFFDD0"))
        rect_width = 400
        rect_height = 40
        c.rect((letter[0] - rect_width)/2, 335, rect_width, rect_height, stroke=0, fill=1)
        
        c.setFillColor(HexColor("#D4AF37"))
        c.setFont("NotoSansDevanagari", 22)
        
        main_text = f"श्रीमान {guest_name}"
        c.drawCentredString(letter[0]/2, 350, main_text)
        
        if family_members:
            c.setFont("NotoSansDevanagari", 14)
            lines = family_members.split('\n')
            y_offset = 320
            for line in lines:
                if line.strip():
                    c.drawCentredString(letter[0]/2, y_offset, line.strip())
                    y_offset -= 20
                
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

