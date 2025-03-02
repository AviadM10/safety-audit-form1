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
from datetime import datetime

# רישום פונט תומך עברית
font_path = os.path.join(os.path.dirname(__file__), "Rubik-Regular.ttf")
pdfmetrics.registerFont(TTFont('HebrewFont', font_path))

# הגדרת סגנון עם גופן עברית
styles = getSampleStyleSheet()
hebrew_style = ParagraphStyle('Hebrew', parent=styles['Normal'], fontName='HebrewFont', fontSize=12, alignment=2, rightIndent=10)

def fix_rtl(text):
    """מתקן כיווניות טקסט בעברית ל-ReportLab"""
    reshaped_text = arabic_reshaper.reshape(text)
    return get_display(reshaped_text)

def generate_pdf(school_name, school_id, phone, city, ownership, audit_date, auditor_name, results_df):
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
               [fix_rtl(ownership), fix_rtl("רשות/בעלות")],
               [fix_rtl(audit_date), fix_rtl("תאריך")],
               [fix_rtl(auditor_name), fix_rtl("שם עורך המבדק")]]
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
    priority_color = colors.black  # ברירת מחדל
    data = [[fix_rtl("קטגוריה"), fix_rtl("סטנדרט"), fix_rtl("סעיף"), fix_rtl("פריט נבדק"), fix_rtl("מצב"), fix_rtl("תיאור הליקוי"), fix_rtl("קדימות"), fix_rtl("תמונה")]]
    for _, row in results_df.iterrows():
        priority_color = colors.red if row['קדימות'] == "2 - טיפול בתוכנית עבודה" else colors.black
        img = ""
        if row['תמונה']:
            try:
                img = Image(row['תמונה'], width=50, height=50)
            except:
                img = ""
        data.append([fix_rtl(row['קטגוריה']), fix_rtl(row['סטנדרט']), fix_rtl(row['סעיף']), fix_rtl(row['פריט נבדק']), fix_rtl(row['מצב']), Paragraph(fix_rtl(row['תיאור הליקוי']), hebrew_style), (fix_rtl(row['קדימות']), priority_color), img])

    table = Table(data, colWidths=[80, 60, 60, 100, 70, 150, 70, 60])
    table.setStyle(TableStyle([
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, -1), 'HebrewFont'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('TEXTCOLOR', (6, 1), (6, -1), priority_color)
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
audit_date = st.text_input("תאריך", value=datetime.today().strftime('%d-%m-%Y'))
auditor_name = st.text_input("שם עורך המבדק")

# המרת הנתונים ל-DataFrame
columns = ["קטגוריה", "סטנדרט", "סעיף", "פריט נבדק", "מצב", "תיאור הליקוי", "קדימות", "תמונה"]
results_df = pd.DataFrame(columns=columns)

# יצירת דוח PDF
if st.button("הפק דוח PDF"):
    pdf_file = generate_pdf(school_name, school_id, phone, city, ownership, audit_date, auditor_name, results_df)
    with open(pdf_file, "rb") as f:
        st.download_button("הורד דוח PDF", f, file_name=pdf_file, mime="application/pdf")
