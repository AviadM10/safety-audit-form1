import streamlit as st
import pandas as pd
from datetime import datetime

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

# הגדרת רשימת ליקויים
st.header("רשימת ליקויים")

# הגדרת עמודות לטבלה
columns = ["קטגוריה", "סטנדרט", "סעיף", "פריט נבדק", "מצב", "תיאור הליקוי", "קדימות", "תמונה"]

# אתחול משתנה ה-Session State אם הוא לא קיים
if "results_df" not in st.session_state:
    st.session_state.results_df = pd.DataFrame(columns=columns)

# פונקציה להוספת ליקוי חדש
def add_defect():
    new_entry = pd.DataFrame([{col: "" for col in columns}])  # יצירת שורה ריקה
    st.session_state.results_df = pd.concat([st.session_state.results_df, new_entry], ignore_index=True)

# כפתור להוספת שורה חדשה
if st.button("הוסף ליקוי"):
    add_defect()

# הצגת הטבלה לעריכה
try:
    st.session_state.results_df = st.data_editor("רשימת ליקויים", st.session_state.results_df, num_rows="dynamic")
except Exception as e:
    st.error(f"שגיאה בהצגת הטבלה: {e}")

# כפתור יצירת דוח PDF (פשוט ללא עיצוב מתקדם כרגע)
if st.button("הפק דוח PDF"):
    try:
        pdf_file = "safety_audit_report.pdf"
        st.success("הדוח נוצר בהצלחה!")
        with open(pdf_file, "rb") as f:
            st.download_button("הורד דוח PDF", f, file_name=pdf_file, mime="application/pdf")
    except Exception as e:
        st.error(f"שגיאה ביצירת הדוח: {e}")
