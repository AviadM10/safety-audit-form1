import streamlit as st
import pandas as pd
from PIL import Image
import io

# פונקציה לטעינת רשימת הדרישות
@st.cache_data
def load_requirements():
    return pd.DataFrame({
        "קטגוריה": ["שערים", "חשמל", "חצר", "מבנים"],
        "תיאור": [
            "שערים ייפתחו כלפי חוץ, ללא בליטות מסוכנות.",
            "לוחות חשמל חייבים להיות סגורים עם סידורי נעילה.",
            "החצר תהיה נקייה ממפגעים.",
            "מבנים יבילים יוצבו על בסיס מוגבה."
        ]
    })

# הגדרת מבנה הדוח
st.title("אפליקציית דוח מבדק בטיחות דיגיטלי")

# בחירת קדימות
priority_options = ["קדימות 0 - סכנת חיים", "קדימות 1 - תיקון מיידי", "קדימות 2 - תיקון בתוכנית עבודה"]

data = []

st.subheader("הוספת ליקוי")
lakuy = st.text_input("תיאור הליקוי:")
category_options = load_requirements()["קטגוריה"].unique()
category = st.selectbox("בחר קטגוריה:", category_options)
selected_requirement = st.selectbox(
    "בחר דרישה רלוונטית:", 
    load_requirements()[load_requirements()["קטגוריה"] == category]["תיאור"]
)
priority = st.selectbox("קדימות:", priority_options)
description = st.text_area("תיאור נוסף:")
image = st.file_uploader("העלה תמונה (אופציונלי):", type=["jpg", "png", "jpeg"])

if st.button("הוסף לדוח"):
    row = {"ליקוי": lakuy, "קטגוריה": category, "דרישה": selected_requirement, "קדימות": priority, "תיאור נוסף": description, "תמונה": image}
    data.append(row)
    st.success("הליקוי נוסף לדוח!")

if len(data) > 0:
    st.subheader("דוח מבדק")
    df = pd.DataFrame(data)
    st.dataframe(df.drop(columns=["תמונה"]))

    if st.button("ייצוא ל-Excel"):
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            df.to_excel(writer, index=False)
        output.seek(0)
        st.download_button(label="הורד קובץ Excel", data=output, file_name="safety_audit.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    if st.button("ייצוא ל-PDF"):
        import pdfkit
        html = df.to_html()
        pdf = pdfkit.from_string(html, False)
        st.download_button(label="הורד PDF", data=pdf, file_name="safety_audit.pdf", mime="application/pdf")
