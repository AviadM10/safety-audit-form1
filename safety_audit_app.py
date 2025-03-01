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
