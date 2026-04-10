import os
import urllib.request
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.colors import HexColor

# 1. Download Devanagari Font
font_url = "https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoSansDevanagari/NotoSansDevanagari-Regular.ttf"
font_path = os.path.join(os.path.dirname(__file__), "backend", "NotoSansDevanagari-Regular.ttf")

os.makedirs(os.path.dirname(font_path), exist_ok=True)
if not os.path.exists(font_path):
    print("Downloading Noto Sans Devanagari font...")
    urllib.request.urlretrieve(font_url, font_path)
    print("Downloaded font.")

# 2. Generate dummy template.pdf
template_path = os.path.join(os.path.dirname(__file__), "template.pdf")

if not os.path.exists(template_path):
    print("Generating dummy template.pdf...")
    c = canvas.Canvas(template_path, pagesize=letter)
    
    # Page 1 (The one we will modify)
    c.setFillColor(HexColor("#FFFDD0")) # Cream background
    c.rect(0, 0, letter[0], letter[1], stroke=0, fill=1)
    
    c.setFillColor(HexColor("#D4AF37")) # Gold text
    c.setFont("Helvetica-Bold", 40)
    c.drawCentredString(letter[0]/2, 600, "Wedding Invitation")
    
    c.setFont("Helvetica", 20)
    c.drawCentredString(letter[0]/2, 500, "You are cordially invited to our wedding.")
    
    # Existing blank space
    c.setFont("Helvetica", 18)
    c.drawCentredString(letter[0]/2, 350, "श्रीमान _____________________")
    
    c.showPage()
    
    # Page 2
    c.setFillColor(HexColor("#FFFDD0"))
    c.rect(0, 0, letter[0], letter[1], stroke=0, fill=1)
    c.setFillColor(HexColor("#D4AF37"))
    c.setFont("Helvetica", 30)
    c.drawCentredString(letter[0]/2, 400, "Page 2: Events & Timeline")
    c.showPage()

    # Page 3
    c.setFillColor(HexColor("#FFFDD0"))
    c.rect(0, 0, letter[0], letter[1], stroke=0, fill=1)
    c.setFillColor(HexColor("#D4AF37"))
    c.setFont("Helvetica", 30)
    c.drawCentredString(letter[0]/2, 400, "Page 3: Venue Details")
    c.save()
    
    print("Generated template.pdf")
else:
    print("template.pdf already exists.")
