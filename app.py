import streamlit as st
import pandas as pd
import datetime

# إعداد الصفحة
st.set_page_config(
    page_title="B2B Campaign Super Dashboard",
    page_icon="🚀",
    layout="wide"
)

# --- نظام الحماية بكلمة السر (موقع برايفت خاص بيك) ---
def check_password():
    def password_entered():
        if st.session_state["password"] == "123456": # 👈 تقدر تغير الباسورد ده لأي كلمة سر تعجبك
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.markdown("## 🔐 لوحة تحكم حملة الـ B2B الذكية (موقع خاص)")
        st.text_input("أدخل كلمة السر للمرور:", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        st.markdown("## 🔐 لوحة تحكم حملة الـ B2B الذكية (موقع خاص)")
        st.text_input("أدخل كلمة السر للمرور:", type="password", on_change=password_entered, key="password")
        st.error("❌ كلمة السر غير صحيحة يا فنان!")
        return False
    else:
        return True

if check_password():
    # عنوان لوحة التحكم
    st.title("🚀 لوحة تحكم حملة الـ B2B الذكية")
    st.markdown("متابعة حية لتسخين الحسابات الـ 100، إرسال الـ 20 إيميل يومياً (كل ربع ساعة)، ورصد الصفقات والردود لحظياً! 🔥")
    st.markdown("---")

    # تحميل البيانات
    @st.cache_data(ttl=5)
    def load_data():
        try:
            return pd.read_csv("b2b_campaign_results.csv")
        except Exception:
            return pd.DataFrame()

    df = load_data()

    if df.empty:
        st.warning("⚠️ لم يتم العثور على ملف النتائج (`b2b_campaign_results.csv`) حتى الآن. تأكد من تشغيل البوت لتوليد البيانات!")
    else:
        # 1. المؤشرات الحية
        col1, col2, col3, col4 = st.columns(4)
        total_sent = len(df)
        unique_accounts = df["Sender_Account"].nunique() if "Sender_Account" in df.columns else 0
        interested_df = df[df["Status"].str.contains("مهتم|عايز اتفاق", na=False)] if "Status" in df.columns else pd.DataFrame()
        hot_leads_count = len(interested_df)
        
        col1.metric("📦 إجمالي الإيميلات المرسلة", total_sent)
        col2.metric("🤖 الحسابات النشطة", f"{unique_accounts} / 100")
        col3.metric("🤝 صفقات وعملاء مهتمين", hot_leads_count)
        col4.metric("📈 نسبة التفاعل", f"{(hot_leads_count/total_sent*100):.1f}%" if total_sent > 0 else "0%")

        st.markdown("---")

        # 2. الفلاتر
        st.sidebar.header("🎛️ أدوات التحكم والفلترة")
        search_query = st.sidebar.text_input("🔍 بحث عن شركة أو إيميل", "")
        
        if "Status" in df.columns:
            status_options = ["الكل"] + list(df["Status"].unique())
            selected_status = st.sidebar.selectbox("📌 تصفية حسب الحالة", status_options)
        else:
            selected_status = "الكل"

        filtered_df = df.copy()
        if search_query:
            filtered_df = filtered_df[
                filtered_df["Target_Company"].str.contains(search_query, case=False, na=False) |
                filtered_df["Target_Email"].str.contains(search_query, case=False, na=False)
            ]
        if selected_status != "الكل":
            filtered_df = filtered_df[filtered_df["Status"] == selected_status]

        # 3. الرسومات البيانية
        col_chart1, col_chart2 = st.columns(2)
        with col_chart1:
            st.subheader("📈 معدل الإرسال اليومي")
            if "Day" in df.columns:
                st.bar_chart(df.groupby("Day").size())
        with col_chart2:
            st.subheader("🎯 توزيع حالات الاستجابة")
            if "Status" in df.columns:
                st.bar_chart(df["Status"].value_counts())

        st.markdown("---")

        # 4. الصفقات الساخنة
        st.subheader("🔥 الشركات الجاهزة لعقد اتفاق (Hot Leads)")
        if not interested_df.empty:
            st.dataframe(interested_df, use_container_width=True)
        else:
            st.info("جاري جمع الصفقات والردود...")

        st.markdown("---")

        # 5. جدول البيانات
        st.subheader("📋 سجل جميع العمليات")
        st.dataframe(filtered_df, use_container_width=True)
