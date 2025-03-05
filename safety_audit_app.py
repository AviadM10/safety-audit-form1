import streamlit as st
import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
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
hebrew_style = ParagraphStyle('Hebrew', parent=styles['Normal'], fontName='HebrewFont', fontSize=12, alignment=2, rightIndent=10, wordWrap='CJK')

# פונקציה לתיקון כיווניות בעברית
def fix_rtl(text):
    reshaped_text = arabic_reshaper.reshape(str(text))
    return get_display(reshaped_text)

# יצירת דוח PDF
def generate_pdf(school_name, school_id, phone, city, ownership, audit_date, auditor_name, results_df):
    pdf_filename = "safety_audit_report.pdf"
    doc = SimpleDocTemplate(pdf_filename, pagesize=A4)
    elements = []
    
    elements.append(Paragraph(fix_rtl("דוח מבדק בטיחות"), hebrew_style))
    elements.append(Spacer(1, 12))
    
    details = [[fix_rtl("שם המוסד"), fix_rtl(school_name)],
               [fix_rtl("סמל מוסד"), fix_rtl(school_id)],
               [fix_rtl("טלפון"), fix_rtl(phone)],
               [fix_rtl("עיר"), fix_rtl(city)],
               [fix_rtl("רשות/בעלות"), fix_rtl(ownership)],
               [fix_rtl("תאריך"), fix_rtl(audit_date)],
               [fix_rtl("שם עורך המבדק"), fix_rtl(auditor_name)]]
    details_table = Table(details, colWidths=[150, 300])
    details_table.setStyle(TableStyle([
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, -1), 'HebrewFont'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(details_table)
    elements.append(Spacer(1, 12))
    
    table_data = [[fix_rtl(col) for col in results_df.columns]]
    for _, row in results_df.iterrows():
        row_data = [fix_rtl(str(row[col])) for col in results_df.columns]
        table_data.append(row_data)
    
    table = Table(table_data)
    table.setStyle(TableStyle([
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, -1), 'HebrewFont'),
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
audit_date = st.text_input("תאריך", value=datetime.today().strftime('%d-%m-%Y'))
auditor_name = st.text_input("שם עורך המבדק")

# טופס להוספת ליקוי
st.header("רשימת ליקויים")
if "results_df" not in st.session_state:
    st.session_state.results_df = pd.DataFrame(columns=["קטגוריה", "סטנדרט", "סעיף", "פריט נבדק", "מצב", "תיאור הליקוי", "קדימות", "תמונה"])

category = st.selectbox("בחר קטגוריה", ["כיתות", "חצר", "בטיחות אש", "מערכות חשמל"])  
standard = st.text_input("סטנדרט")  
section = st.text_input("סעיף")  
item = st.text_input("פריט נבדק")  
condition = st.text_input("מצב")  
defect_description = st.text_area("תיאור הליקוי")  
priority = st.selectbox("קדימות", ["נמוכה", "בינונית", "גבוהה", "דחופה"])  
image = st.file_uploader("העלה תמונה", type=["jpg", "png", "jpeg"])  

def add_defect():
    new_entry = {"קטגוריה": category, "סטנדרט": standard, "סעיף": section, "פריט נבדק": item, "מצב": condition, "תיאור הליקוי": defect_description, "קדימות": priority, "תמונה": image.name if image else ""}
    st.session_state.results_df = pd.concat([st.session_state.results_df, pd.DataFrame([new_entry])], ignore_index=True)

if st.button("הוסף ליקוי"):
    add_defect()
    st.success("הליקוי נוסף בהצלחה!")

st.dataframe(st.session_state.results_df)

# יצירת דוח PDF
if st.button("הפק דוח PDF"):
    pdf_file = generate_pdf(school_name, school_id, phone, city, ownership, audit_date, auditor_name, st.session_state.results_df)
    with open(pdf_file, "rb") as f:
        st.download_button("הורד דוח PDF", f, file_name=pdf_file, mime="application/pdf")
