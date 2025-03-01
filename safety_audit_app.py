import streamlit as st
import pandas as pd
from PIL import Image
import io
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# פונקציה לטעינת רשימת הדרישות
@st.cache_data
def load_requirements():
    return pd.DataFrame({
        "קטגוריה": ["שערים", "שערים", "שערים", "חשמל", "חשמל", "חשמל", "חצר", "חצר", "חצר", "מבנים", "מבנים", "מבנים"],
        "מספר סעיף": ["3.32", "3.33", "3.34", "9.1", "9.2", "9.3", "3.1", "3.2", "3.3", "8.1", "8.2", "8.3"],
        "תיאור": [
            "שערים ייפתחו כלפי חוץ, ללא בליטות מסוכנות.",
            "שערים יכילו מנגנון נעילה בטיחותי.",
            "השערים יהיו בגובה מתאים למניעת טיפוס.",
            "לוחות חשמל חייבים להיות סגורים עם סידורי נעילה.",
            "כל מערכת חשמל חייבת להיות עם מפסק פחת.",
            "מערכות חשמל חייבות להיות מסומנות בבירור.",
            "החצר תהיה נקייה ממפגעים.",
            "שבילי גישה יהיו סלולים וללא מכשולים.",
            "לא יהיו חפצים חדים או בולטים בשטח החצר.",
            "מבנים יבילים יוצבו על בסיס מוגבה.",
            "כל מבנה יביל יכיל יציאת חירום נוספת.",
            "מבנים יבילים יכללו שילוט בטיחות מתאים."
        ]
    })

# הגדרת מבנה הדוח
st.title("אפליקציית דוח מבדק בטיחות דיגיטלי")

# פרטי המבצע
st.subheader("פרטי המבדק")
school_name = st.text_input("שם בית הספר:")
inspector_name = st.text_input("שם עורך המבדק:")
date = st.date_input("תאריך המבדק:")

# בחירת קדימות
priority_options = ["קדימות 0 - סכנת חיים", "קדימות 1 - תיקון מיידי", "קדימות 2 - תיקון בתוכנית עבודה"]

data = []

st.subheader("הוספת ליקוי")
lakuy = st.text_input("תיאור הליקוי:")
category_options = load_requirements()["קטגוריה"].unique()
category = st.selectbox("בחר קטגוריה:", category_options)
relevant_requirements = load_requirements()[load_requirements()["קטגוריה"] == category]
selected_requirement = st.selectbox("בחר דרישה רלוונטית:", relevant_requirements["תיאור"])
specific_section = relevant_requirements[relevant_requirements["תיאור"] == selected_requirement]["מספר סעיף"].values[0]
priority = st.selectbox("קדימות:", priority_options)
description = st.text_area("תיאור נוסף:")
image = st.file_uploader("העלה תמונה (אופציונלי):", type=["jpg", "png", "jpeg"])

if st.button("הוסף לדוח"):
    if 'data' not in st.session_state:
        st.session_state.data = []
    row = {"ליקוי": lakuy, "קטגוריה": category, "מספר סעיף": specific_section, "דרישה": selected_requirement, "קדימות": priority, "תיאור נוסף": description, "תמונה": image}
    st.session_state.data.append(row)
    st.success("הליקוי נוסף לדוח!")

if 'data' in st.session_state and len(st.session_state.data) > 0:
    st.subheader("דוח מבדק")
    df = pd.DataFrame(st.session_state.data)
    st.dataframe(df.drop(columns=["תמונה"]))

    if st.button("ייצוא ל-Excel"):
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            df.to_excel(writer, index=False)
        output.seek(0)
        st.download_button(label="הורד קובץ Excel", data=output, file_name="safety_audit.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    if st.button("ייצוא ל-PDF"):
        output_pdf = io.BytesIO()
        pdf = canvas.Canvas(output_pdf, pagesize=letter)
        pdf.drawString(100, 750, f"דוח מבדק בטיחות")
        pdf.drawString(100, 730, f"שם בית הספר: {school_name}")
        pdf.drawString(100, 710, f"שם עורך המבדק: {inspector_name}")
        pdf.drawString(100, 690, f"תאריך המבדק: {date}")
        
        y_position = 660
        for index, row in df.iterrows():
            pdf.drawString(100, y_position, f"ליקוי: {row['ליקוי']}, קטגוריה: {row['קטגוריה']}, סעיף: {row['מספר סעיף']}, דרישה: {row['דרישה']}, קדימות: {row['קדימות']}")
            y_position -= 20
            if y_position < 50:
                pdf.showPage()
                y_position = 750
        
        pdf.save()
        output_pdf.seek(0)
        st.download_button(label="הורד PDF", data=output_pdf, file_name="safety_audit.pdf", mime="application/pdf")
