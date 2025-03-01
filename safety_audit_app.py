import streamlit as st
import pandas as pd
from PIL import Image
import io
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from bidi.algorithm import get_display
import arabic_reshaper
import os

# פונקציה לטעינת רשימת הדרישות
@st.cache_data
def load_requirements():
    return pd.DataFrame({
        "קטגוריה": [
            "שערים", "שערים", "שערים", "שערים", "שערים", "שערים",
            "חשמל", "חשמל", "חשמל", "חשמל", "חשמל", "חשמל",
            "חצר", "חצר", "חצר", "חצר", "חצר", "חצר",
            "מבנים", "מבנים", "מבנים", "מבנים", "מבנים", "מבנים"
        ],
        "מספר סעיף": [
            "3.32", "3.33", "3.34", "3.35", "3.36", "3.37",
            "9.1", "9.2", "9.3", "9.4", "9.5", "9.6",
            "3.1", "3.2", "3.3", "3.4", "3.5", "3.6",
            "8.1", "8.2", "8.3", "8.4", "8.5", "8.6"
        ],
        "תיאור": [
            "שערים ייפתחו כלפי חוץ, ללא בליטות מסוכנות.",
            "שערים יכילו מנגנון נעילה בטיחותי.",
            "השערים יהיו בגובה מתאים למניעת טיפוס.",
            "שערים יהיו עמידים בתנאי מזג האוויר.",
            "שערים לא יכילו חורים או פתחים מסוכנים.",
            "שערים יהיו תקינים וללא נזקים מבניים.",
            "לוחות חשמל חייבים להיות סגורים עם סידורי נעילה.",
            "כל מערכת חשמל חייבת להיות עם מפסק פחת.",
            "מערכות חשמל חייבות להיות מסומנות בבירור.",
            "חיווט חשוף יוסתר כראוי ולא יהיה נגיש לילדים.",
            "שקעים ותקעים יהיו תקינים וללא חוטים קרועים.",
            "חדרי חשמל יהיו נעולים ונגישים רק לאנשי מקצוע.",
            "החצר תהיה נקייה ממפגעים.",
            "שבילי גישה יהיו סלולים וללא מכשולים.",
            "לא יהיו חפצים חדים או בולטים בשטח החצר.",
            "תשתיות ניקוז יהיו מתוחזקות וללא חסימות.",
            "תאורת החצר תפעל כראוי ובטיחותית.",
            "ריהוט חצר יהיה תקין וללא פגמים מסוכנים.",
            "מבנים יבילים יוצבו על בסיס מוגבה.",
            "כל מבנה יביל יכיל יציאת חירום נוספת.",
            "מבנים יבילים יכללו שילוט בטיחות מתאים.",
            "קירות המבנה יהיו במצב תקין ללא סדקים מסוכנים.",
            "תקרות המבנה לא יכילו נזילות או עובש.",
            "מבנה יהיה יציב וללא חשש לקריסה."
        ]
    })

# פונקציה להתאמת טקסט עברי

def rtl_text(text):
    return get_display(arabic_reshaper.reshape(text))

# הגדרת מבנה הדוח
st.title("אפליקציית דוח מבדק בטיחות דיגיטלי")

# פרטי המבצע
st.subheader("פרטי המבדק")
school_name = st.text_input("שם בית הספר:")
inspector_name = st.text_input("שם עורך המבדק:")
date = st.date_input("תאריך המבדק:")

# בחירת קדימות
priority_options = ["קדימות 0 - סכנת חיים", "קדימות 1 - תיקון מיידי", "קדימות 2 - תיקון בתוכנית עבודה"]

if "data" not in st.session_state:
    st.session_state.data = []

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

if st.button("הוסף ליקוי"):
    st.session_state.data.append({
        "ליקוי": lakuy, "קטגוריה": category, "מספר סעיף": specific_section, "דרישה": selected_requirement, "קדימות": priority, "תיאור נוסף": description
    })

st.subheader("דוח ליקויים")
df = pd.DataFrame(st.session_state.data)
st.dataframe(df)

if st.button("ייצוא ל-PDF"):
    output_pdf = io.BytesIO()
    pdf = canvas.Canvas(output_pdf, pagesize=A4)
    font_path = "fonts/Rubik-Regular.ttf"
    
    if os.path.exists(font_path):
        pdfmetrics.registerFont(TTFont("Rubik", font_path))
        font_name = "Rubik"
    else:
        font_name = "Helvetica"
    
    pdf.setFont(font_name, 12)
    pdf.drawRightString(550, 800, rtl_text("דוח מבדק בטיחות"))
    pdf.drawRightString(550, 780, rtl_text(f"שם בית הספר: {school_name}"))
    pdf.drawRightString(550, 760, rtl_text(f"שם עורך המבדק: {inspector_name}"))
    pdf.drawRightString(550, 740, rtl_text(f"תאריך המבדק: {date}"))
    
    y_position = 700
    for index, row in df.iterrows():
        text = rtl_text(f"ליקוי: {row['ליקוי']} | קטגוריה: {row['קטגוריה']} | סעיף: {row['מספר סעיף']} | דרישה: {row['דרישה']} | קדימות: {row['קדימות']}")
        pdf.drawRightString(550, y_position, text)
        y_position -= 20
        if y_position < 50:
            pdf.showPage()
            pdf.setFont(font_name, 12)
            y_position = 800
    
    pdf.save()
    output_pdf.seek(0)
    st.download_button(label="הורד PDF", data=output_pdf, file_name="safety_audit.pdf", mime="application/pdf")
