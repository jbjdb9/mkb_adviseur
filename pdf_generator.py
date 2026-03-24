from fpdf import FPDF
import io
import re
import textwrap
from datetime import date
import os

class AdviesPDF(FPDF):
    pass

def _clean_long_words(text: str, max_word_length: int = 60) -> str:
    woorden = text.split(" ")
    veilige_woorden = []
    for woord in woorden:
        if len(woord) > max_word_length:
            wrapped = textwrap.fill(woord, max_word_length)
            veilige_woorden.append(wrapped)
        else:
            veilige_woorden.append(woord)
    return " ".join(veilige_woorden)

def genereer_pdf(titel: str, inhoud: str) -> bytes:
    pdf = AdviesPDF()
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()
    pdf.set_margins(20, 20, 20)
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    pdf.add_font("DejaVu", style="", fname=os.path.join(base_dir, "fonts", "DejaVuSans.ttf"))
    pdf.add_font("DejaVu", style="B", fname=os.path.join(base_dir, "fonts", "DejaVuSans-Bold.ttf"))
    
    usable_width = pdf.w - pdf.l_margin - pdf.r_margin
    
    # Titel
    pdf.set_font("DejaVu", "B", 18)
    pdf.set_x(pdf.l_margin)
    pdf.multi_cell(usable_width, 10, titel)
    pdf.ln(2)
    
    # Datum
    pdf.set_font("DejaVu", "", 10)
    pdf.set_x(pdf.l_margin)
    pdf.multi_cell(
        usable_width,
        6,
        f"Gegenereerd op: {date.today().strftime('%d-%m-%Y')}",
    )
    pdf.ln(5)
    
    # Scheidingslijn
    y = pdf.get_y()
    pdf.set_draw_color(200, 200, 200)
    pdf.line(pdf.l_margin, y, pdf.w - pdf.r_margin, y)
    pdf.ln(8)
    
    # Inhoud processing
    for raw_line in inhoud.split("\n"):
        line = raw_line.strip()
        if not line:
            pdf.ln(4)
            continue
        
        line = _clean_long_words(line)
        
        # Titel
        if line.startswith("# "):
            pdf.set_font("DejaVu", "B", 16)
            pdf.set_x(pdf.l_margin)
            pdf.multi_cell(usable_width, 8, line.replace("# ", ""))
            pdf.ln(2)
            continue
        
        # Subtitel
        if line.startswith("## "):
            pdf.set_font("DejaVu", "B", 14)
            pdf.set_x(pdf.l_margin)
            pdf.multi_cell(usable_width, 8, line.replace("## ", ""))
            pdf.ln(1)
            continue
        
        # Bullet points
        if line.startswith("- "):
            pdf.set_font("DejaVu", "", 11)
            bullet_text = "• " + line.replace("- ", "")
            pdf.set_x(pdf.l_margin + 5)
            pdf.multi_cell(usable_width - 5, 7, bullet_text)
            continue
        
        # Bold inline
        bold_match = re.findall(r"\*\*(.*?)\*\*", line)
        if bold_match:
            parts = re.split(r"(\*\*.*?\*\*)", line)
            pdf.set_x(pdf.l_margin)
            for part in parts:
                if part.startswith("**") and part.endswith("**"):
                    pdf.set_font("DejaVu", "B", 11)
                    pdf.write(7, part.replace("**", ""))
                else:
                    pdf.set_font("DejaVu", "", 11)
                    pdf.write(7, part)
            pdf.ln(7)
            continue
        
        # Normale tekst
        pdf.set_font("DejaVu", "", 11)
        pdf.set_x(pdf.l_margin)
        pdf.multi_cell(usable_width, 7, line)
    
    return bytes(pdf.output())  