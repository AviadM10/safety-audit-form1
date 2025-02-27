import streamlit as st
import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Image, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import arabic_reshaper
from bidi.algorithm import get_display
import os
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics

# רישום פונט תומך עברית
font_path = os.path.join(os.path.dirname(__file__), "Rubik-Regular.ttf")
pdfmetrics.registerFont(TTFont('HebrewFont', font_path))

# הגדרת סגנון עם גופן עברית
styles = getSampleStyleSheet()
hebrew_style = ParagraphStyle('Hebrew', parent=styles['Normal'], fontName='HebrewFont', fontSize=12, alignment=2)

def fix_rtl(text):
    """מתקן כיווניות טקסט בעברית ל-ReportLab"""
    reshaped_text = arabic_reshaper.reshape(text)
    return get_display(reshaped_text)

def generate_pdf(school_name, school_id, phone, city, ownership, results_df):
    pdf_filename = "safety_audit_report.pdf"
    doc = SimpleDocTemplate(pdf_filename, pagesize=A4)
    elements = []
    
    # כותרת הדוח
    elements.append(Paragraph(fix_rtl("דוח מבדק בטיחות"), hebrew_style))
    elements.append(Spacer(1, 12))  # רווח לפני טבלה
    
    # פרטי מוסד (ימין לשמאל)
    details = [[fix_rtl(school_name), fix_rtl("שם המוסד")],
               [fix_rtl(school_id), fix_rtl("סמל מוסד")],
               [fix_rtl(phone), fix_rtl("טלפון")],
               [fix_rtl(city), fix_rtl("עיר")],
               [fix_rtl(ownership), fix_rtl("רשות/בעלות")]]
    details_table = Table(details, colWidths=[300, 150])
    details_table.setStyle(TableStyle([
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, -1), 'HebrewFont'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(details_table)
    elements.append(Spacer(1, 12))  # רווח לפני הטבלה הבאה
    
    # טבלת הבדיקות מסודרת מימין לשמאל
    data = [[fix_rtl("תמונה"), fix_rtl("קדימות"), fix_rtl("תיאור הליקוי"), fix_rtl("מצב"), fix_rtl("פריט נבדק"), fix_rtl("קטגוריה")]]
    for _, row in results_df.iterrows():
        img = ""
        if row['תמונה']:
            try:
                img = Image(row['תמונה'], width=50, height=50)
            except:
                img = ""
        data.append([img, fix_rtl(row['קדימות']), fix_rtl(row['תיאור הליקוי']), fix_rtl(row['מצב']), fix_rtl(row['פריט נבדק']), fix_rtl(row['קטגוריה'])])

    table = Table(data, colWidths=[60, 70, 150, 70, 100, 100])
    table.setStyle(TableStyle([
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, -1), 'HebrewFont'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(table)
    
    doc.build(elements)
    return pdf_filename

# ממשק משתמש ב-Streamlit
st.title("טופס דיגיטלי למבדק בטיחות במוסדות חינוך")

# מילוי פרטי מוסד חינוכי
st.header("פרטי המוסד")
school_name = st.text_input("שם המוסד")
school_id = st.text_input("סמל מוסד")
phone = st.text_input("טלפון")
city = st.text_input("עיר")
ownership = st.text_input("רשות/בעלות")

# יצירת טבלה דינמית לבדיקות
st.header("רשימת הבדיקות")
data = []
categories = ["כיתות לימוד", "חצרות", "בטיחות אש", "מערכות חשמל"]
elements = {
    "כיתות לימוד": ["רצפה", "תאורה"],
    "חצרות": ["מתקן משחקים"],
    "בטיחות אש": ["מטף כיבוי"],
    "מערכות חשמל": ["לוח חשמל ראשי"]
}

for category in categories:
    st.subheader(category)
    for item in elements[category]:
        col1, col2, col3, col4, col5 = st.columns([2, 1, 2, 2, 2])
        with col1:
            st.text(item)
        with col2:
            condition = st.radio(f"מצב - {item}", ["תקין", "לא תקין"], key=f"condition_{category}_{item}")
        with col3:
            description = st.text_input(f"תיאור הליקוי - {item}", key=f"desc_{category}_{item}")
        with col4:
            priority = st.selectbox(f"קדימות - {item}", ["0 - מפגע חמור", "1 - תיקון מיידי", "2 - טיפול בתוכנית עבודה"], key=f"priority_{category}_{item}")
        with col5:
            image = st.file_uploader(f"העלה תמונה - {item}", type=["jpg", "png"], key=f"image_{category}_{item}")
        data.append([category, item, condition, description, priority, image])

# המרת הנתונים ל-DataFrame
results_df = pd.DataFrame(data, columns=["קטגוריה", "פריט נבדק", "מצב", "תיאור הליקוי", "קדימות", "תמונה"])

# יצירת דוח PDF
if st.button("הפק דוח PDF"):
    pdf_file = generate_pdf(school_name, school_id, phone, city, ownership, results_df)
    with open(pdf_file, "rb") as f:
        st.download_button("הורד דוח PDF", f, file_name=pdf_file, mime="application/pdf")
