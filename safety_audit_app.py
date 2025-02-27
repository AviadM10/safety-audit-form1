import streamlit as st
import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import datetime

# כותרת האפליקציה
st.title("טופס דיגיטלי למבדק בטיחות במוסדות חינוך")

# מילוי פרטי מוסד חינוכי
st.header("פרטי המוסד")
school_name = st.text_input("שם המוסד")
school_id = st.text_input("סמל המוסד")
ownership = st.text_input("בעלות (רשות מקומית / פרטית)")
location = st.text_input("יישוב")
address = st.text_input("כתובת")
num_students = st.number_input("מספר תלמידים", min_value=0, step=1)
year_established = st.number_input("שנת הקמה", min_value=1900, max_value=datetime.datetime.today().year, step=1)
phone = st.text_input("טלפון המוסד")
audit_date = st.date_input("תאריך המבדק", datetime.date.today())

# הגדרת טבלה למבדק
st.header("רשימת הבדיקות")
categories = ["כיתות לימוד", "חצרות", "בטיחות אש", "מערכות חשמל"]
elements = {
    "כיתות לימוד": ["רצפה", "תאורה"],
    "חצרות": ["מתקן משחקים"],
    "בטיחות אש": ["מטף כיבוי"],
    "מערכות חשמל": ["לוח חשמל ראשי"]
}

data = []
for category in categories:
    st.subheader(category)
    for item in elements[category]:
        col1, col2, col3, col4 = st.columns([2, 1, 2, 2])
        with col1:
            st.text(item)
        with col2:
            condition = st.radio(f"מצב - {item}", ["תקין", "לא תקין"], key=f"condition_{category}_{item}")
        with col3:
            description = st.text_input(f"תיאור הליקוי - {item}", key=f"desc_{category}_{item}")
        with col4:
            priority = st.selectbox(f"קדימות - {item}", ["0 - מפגע חמור", "1 - תיקון מיידי", "2 - טיפול בתוכנית עבודה"], key=f"priority_{category}_{item}")
        data.append([category, item, condition, description, priority])

# המרת הנתונים ל-DataFrame
results_df = pd.DataFrame(data, columns=["קטגוריה", "פריט נבדק", "מצב", "תיאור הליקוי", "קדימות"])

# יצירת דוח PDF
if st.button("הפק דוח PDF"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, "דוח מבדק בטיחות", ln=True, align="C")
    pdf.ln(10)
    pdf.set_font("Arial", "", 12)
    pdf.cell(200, 10, f"שם המוסד: {school_name}", ln=True, align="R")
    pdf.cell(200, 10, f"סמל מוסד: {school_id}", ln=True, align="R")
    pdf.cell(200, 10, f"כתובת: {address}, {location}", ln=True, align="R")
    pdf.cell(200, 10, f"מספר תלמידים: {num_students}", ln=True, align="R")
    pdf.cell(200, 10, f"תאריך מבדק: {audit_date}", ln=True, align="R")
    pdf.ln(10)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(200, 10, "ממצאים לפי תחומים:", ln=True, align="R")
    pdf.ln(5)
    
    pdf.set_font("Arial", "", 10)
    for index, row in results_df.iterrows():
        pdf.cell(200, 10, f"קטגוריה: {row['קטגוריה']} - {row['פריט נבדק']}", ln=True, align="R")
        pdf.cell(200, 10, f"מצב: {row['מצב']}", ln=True, align="R")
        pdf.cell(200, 10, f"תיאור: {row['תיאור הליקוי']}", ln=True, align="R")
        pdf.cell(200, 10, f"קדימות: {row['קדימות']}", ln=True, align="R")
        pdf.ln(5)

    pdf_filename = "safety_audit_report.pdf"
    def generate_pdf(school_name, results_df):
        pdf_filename = "safety_audit_report.pdf"
        c = canvas.Canvas(pdf_filename, pagesize=A4)
        width, height = A4

        c.setFont("Helvetica-Bold", 16)
        c.drawString(100, height - 50, "דוח מבדק בטיחות")

        c.setFont("Helvetica", 12)
        c.drawString(100, height - 80, f"שם המוסד: {school_name}")

        y_position = height - 120
        for index, row in results_df.iterrows():
            c.drawString(100, y_position, f"{row['קטגוריה']} - {row['פריט נבדק']}: {row['מצב']}")
            c.drawString(100, y_position - 20, f"תיאור: {row['תיאור הליקוי']}, קדימות: {row['קדימות']}")
            y_position -= 40

    c.save()
    return pdf_filename

    
    with open(pdf_filename, "rb") as f:
        st.download_button("הורד דוח PDF", f, file_name=pdf_filename, mime="application/pdf")
