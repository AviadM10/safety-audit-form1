import streamlit as st
import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
import arabic_reshaper
from bidi.algorithm import get_display
import os

# רישום פונט תומך עברית מהפרויקט
font_path = os.path.join(os.path.dirname(__file__), "Rubik-Regular.ttf")
pdfmetrics.registerFont(TTFont('Rubik', font_path))

def fix_rtl(text):
    """מתקן כיווניות טקסט בעברית ל-ReportLab"""
    reshaped_text = arabic_reshaper.reshape(text)
    return get_display(reshaped_text)

def generate_pdf(school_name, school_id, phone, city, ownership, results_df):
    pdf_filename = "safety_audit_report.pdf"
    c = canvas.Canvas(pdf_filename, pagesize=A4)
    width, height = A4

    c.setFont("Rubik", 16)
    c.drawRightString(width - 100, height - 50, fix_rtl("דוח מבדק בטיחות"))

    c.setFont("Rubik", 12)
    c.drawRightString(width - 100, height - 80, fix_rtl(f"שם המוסד: {school_name}"))
    c.drawRightString(width - 100, height - 100, fix_rtl(f"סמל מוסד: {school_id}"))
    c.drawRightString(width - 100, height - 120, fix_rtl(f"טלפון: {phone}"))
    c.drawRightString(width - 100, height - 140, fix_rtl(f"עיר: {city}"))
    c.drawRightString(width - 100, height - 160, fix_rtl(f"רשות/בעלות: {ownership}"))

    y_position = height - 200
    c.setFont("Rubik", 10)
    for index, row in results_df.iterrows():
        c.drawRightString(width - 100, y_position, fix_rtl(f"{row['קטגוריה']} - {row['פריט נבדק']}: {row['מצב']}"))
        c.drawRightString(width - 100, y_position - 20, fix_rtl(f"תיאור: {row['תיאור הליקוי']}, קדימות: {row['קדימות']}"))
        y_position -= 40

    c.save()
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
