from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.enums import TA_LEFT, TA_JUSTIFY, TA_RIGHT
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os
import re

# Try to register a font that supports Polish characters
try:
    # Use DejaVu fonts if available
    pdfmetrics.registerFont(TTFont('DejaVuSans', 'DejaVuSans.ttf'))
    pdfmetrics.registerFont(TTFont('DejaVuSans-Bold', 'DejaVuSans-Bold.ttf'))
    pdfmetrics.registerFont(TTFont('DejaVuSans-Oblique', 'DejaVuSans-Oblique.ttf'))
    FONT_NAME = 'DejaVuSans'
    FONT_BOLD = 'DejaVuSans-Bold'
    FONT_ITALIC = 'DejaVuSans-Oblique'
    print("Using DejaVu fonts")
except:
    # Fallback to Helvetica
    FONT_NAME = 'Helvetica'
    FONT_BOLD = 'Helvetica-Bold'
    FONT_ITALIC = 'Helvetica-Oblique'
    print("Using Helvetica fonts (Polish characters may not display correctly)")

def latex_to_reportlab(text):
    """
    Convert a string with simple LaTeX-like math markup to ReportLab's
    rich text format.
    """
    replacements = {
        r'\to': '→', r'\psi': 'ψ', r'\phi': 'φ', r'\pi': 'π',
    }
    for command, unicode_char in replacements.items():
        text = text.replace(command, unicode_char)
    
    text = re.sub(r'\\bar\{(.)\}', r'\1&#773;', text)
    text = re.sub(r'\^\{(.*?)\}', r'<super>\1</super>', text)
    text = re.sub(r'\^([+\-0-9a-zA-Z])', r'<super>\1</super>', text)
    text = re.sub(r'\_\{(.*?)\}', r'<sub>\1</sub>', text)
    text = re.sub(r'\_(\w)', r'<sub>\1</sub>', text)
    text = text.replace('$', '')
    return text

def create_declaration_pdf(publication_id, title, journal, year):
    """
    Create a scientific declaration PDF matching the AGH template.
    """
    filename = f"{publication_id}.pdf"
    doc = SimpleDocTemplate(filename, pagesize=A4,
                           topMargin=2*cm, bottomMargin=2*cm,
                           leftMargin=2.5*cm, rightMargin=2.5*cm)
    
    story = []
    styles = getSampleStyleSheet()
    
    # --- Custom Styles ---
    title_style = ParagraphStyle(
        'CustomTitle', parent=styles['Heading1'], fontSize=14,
        textColor=colors.black, spaceAfter=12, alignment=TA_LEFT,
        fontName=FONT_BOLD
    )
    normal_style_justified = ParagraphStyle(
        'CustomNormalJustified', parent=styles['Normal'], fontSize=11,
        leading=14, alignment=TA_JUSTIFY, fontName=FONT_NAME
    )
    normal_style_left = ParagraphStyle(
        'CustomNormalLeft', parent=normal_style_justified, alignment=TA_LEFT
    )
    bold_style = ParagraphStyle(
        'CustomBold', parent=normal_style_left, fontName=FONT_BOLD
    )
    small_style = ParagraphStyle(
        'Small', parent=styles['Normal'], fontSize=9, leading=11,
        alignment=TA_JUSTIFY, fontName=FONT_NAME
    )
    right_aligned_bold_style = ParagraphStyle(
        'RightBold', parent=bold_style, alignment=TA_RIGHT
    )
    right_aligned_normal_style = ParagraphStyle(
        'RightNormal', parent=normal_style_left, alignment=TA_RIGHT
    )
    
    # --- PDF Content ---
    authors = "R. Aaij, [et al.], S. BASHIR, [et al.], M. FIRLEJ, [et al.], T. FIUTOWSKI, [et al.], W. GOMUŁKA, [et al.], S. HASHMI, [et al.], M. IDZIK, [et al.], J. MOROŃ, [et al.], A. OBŁĄKOWSKA-MUCHA, [et al.], K. ŚWIENTEK, [et al.], T. SZUMLAK, [et al.], A. UKLEJA, [et al.]"
    
    story.append(Paragraph("<b>Oświadczenie o osiągnięciu naukowym</b>", title_style))
    story.append(Spacer(1, 0.3*cm))
    
    # --- Corrected Personal Information ---
    story.append(Paragraph("Imię i nazwisko: <b>Sabin Hashmi</b>", bold_style))
    story.append(Spacer(1, 0.2*cm))
    # ORCID line is now normal text
    story.append(Paragraph("ORCID: 0000-0003-2714-2706", normal_style_left))
    story.append(Spacer(1, 0.2*cm))
    story.append(Paragraph("<b>Jednostka organizacyjna:</b> Wydział Fizyki i Informatyki Stosowanej", normal_style_left))
    story.append(Spacer(1, 0.4*cm))
    
    declaration_text = "1. Niniejszym oświadczam, że niżej wymienione osiągnięcie/a naukowe powstały w związku z zatrudnieniem w Akademii Górniczo-Hutniczej im. Stanisława Staszica w Krakowie lub odbywaniem kształcenia w podmiocie i przypisuję do następujących dyscyplin:"
    story.append(Paragraph(declaration_text, normal_style_justified))
    story.append(Spacer(1, 0.4*cm))
    
    processed_title = latex_to_reportlab(title)
    story.append(Paragraph(f"<b>{processed_title}</b>", normal_style_left))
    story.append(Paragraph(authors, normal_style_left))
    if journal:
        story.append(Paragraph(journal, normal_style_left))
    if year:
        story.append(Paragraph(year, normal_style_left))
    story.append(Spacer(1, 0.2*cm))
    
    story.append(Paragraph("<b>nauki fizyczne</b>", right_aligned_bold_style))
    story.append(Spacer(1, 0.5*cm))

    declaration2_text = "2. Jeżeli moje osiągnięcie naukowe będzie wykazywane przez Akademię Górniczo-Hutniczą im. Stanisława Staszica w Krakowie na potrzeby ewaluacji Uczelni, niniejszym upoważniam Akademię Górniczo-Hutniczą im. Stanisława Staszica w Krakowie do wykazania osiągnięcia wymienionego w powyższej tabeli jako powstałego w związku z prowadzeniem przeze mnie działalności naukowej albo kształceniem w Akademii Górniczo-Hutniczej im. Stanisława Staszica w Krakowie."
    story.append(Paragraph(declaration2_text, normal_style_justified))
    story.append(Spacer(1, 1*cm))
    
    story.append(Paragraph("(data i czytelny podpis)", right_aligned_normal_style))
    story.append(Spacer(1, 0.8*cm))
    
    story.append(Paragraph("<b>Pouczenia:</b>", bold_style))
    story.append(Spacer(1, 0.2*cm))
    
    instructions = [
        "Zgodnie z art. 265 ust. 12 ustawy, na potrzeby ewaluacji osiągnięcia jednej osoby mogą być wykazywane w ramach nie więcej niż 2 dyscyplin, przy czym dane osiągnięcie może być wykazane przez osobę będącą jego autorem tylko raz i tylko w ramach jednej dyscypliny.",
        "Zgodnie z art. 265 ust. 6 ustawy, należy wskazać te osiągnięcia, które powstały w związku z zatrudnieniem lub odbywaniem kształcenia w podmiocie, w którym składa się niniejsze oświadczenie.",
        "Osiągnięcia można wykazać tylko w dyscyplinie, która jest uwzględniona w oświadczeniu o dziedzinie i dyscyplinie naukowej, o którym mowa w art. 343 ust. 7.",
        "Szczegółowa informacja znajduje się na stronie Bibliografii Publikacji Pracowników AGH, a w razie wątpliwości proszę kontaktować się z pracownikami Oddziału Informacji Naukowej Biblioteki Głównej - tel. 617-32-15, e-mail: oin@bg.agh.edu.pl",
        "Oświadczenie to powinno zostać złożone nie później niż do 31 grudnia roku poprzedzającego rok przeprowadzenia ewaluacji jakości działalności naukowej lub przed zakończeniem stosunku pracy w danym podmiocie."
    ]
    
    for instruction in instructions:
        story.append(Paragraph(instruction, small_style))
        story.append(Spacer(1, 0.2*cm))
    
    doc.build(story)
    print(f"\n✓ PDF created successfully: {filename}")
    return filename

def main():
    """Main function to run the interactive PDF generator."""
    print("=" * 70)
    print("Scientific Declaration PDF Generator")
    print("AGH University of Science and Technology")
    print("=" * 70)
    print()
    
    publication_id = input("Enter Publication ID (for filename, e.g., '001'): ").strip()
    if not publication_id:
        print("Error: Publication ID is required!")
        return
    
    print()
    title = input("Enter the title (use LaTeX-like syntax for symbols):\n> ").strip()
    if not title:
        print("Error: Title is required!")
        return
        
    print()
    journal = input("Enter the journal name (optional, press Enter to skip): ").strip()
    year = input("Enter the publication year (optional, press Enter to skip): ").strip()

    print()
    print("-" * 70)
    print("Generating PDF...")
    
    try:
        filename = create_declaration_pdf(
            publication_id=publication_id, title=title,
            journal=journal, year=year
        )
        print()
        print("=" * 70)
        print(f"SUCCESS! File saved as: {filename}")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n✗ Error creating PDF: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
