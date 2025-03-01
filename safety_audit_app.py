import streamlit as st
import pandas as pd
from PIL import Image
import io
import pdfkit

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
        html_content = f"""
        <h2>דוח מבדק בטיחות</h2>
        <p><b>שם בית הספר:</b> {school_name}</p>
        <p><b>שם עורך המבדק:</b> {inspector_name}</p>
        <p><b>תאריך המבדק:</b> {date}</p>
        {df.to_html()}
        """
        pdf_options = {
            'page-size': 'A4',
            'encoding': 'UTF-8'
        }
        pdf = pdfkit.from_string(html_content, False, options=pdf_options)
        st.download_button(label="הורד PDF", data=pdf, file_name="safety_audit.pdf", mime="application/pdf")
