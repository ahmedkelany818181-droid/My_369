
import streamlit as st
import pandas as pd
import os

# إعدادات الصفحة
st.set_page_config(page_title="نظام إدارة الأرباح والتكاليف", layout="wide")
st.title("📊 نظام إدارة الأرباح والتكاليف للمشروعات")

# وظائف إدارة البيانات (تخزين في ملفات CSV محلية)
def load_data(filename, columns):
    if os.path.exists(filename):
        return pd.read_csv(filename)
    return pd.DataFrame(columns=columns)

def save_data(df, filename):
    df.to_csv(filename, index=False)

# تحميل البيانات
fixed_df = load_data("fixed_costs.csv", ["البند", "القيمة (جنيه)"])
products_df = load_data("products_costs.csv", ["اسم المنتج", "خامات", "تصنيع", "شحن وتغليف"])
sales_df = load_data("sales.csv", ["اسم المنتج", "الكمية", "سعر البيع الفعلي"])

# تقسيم الواجهة إلى تبويبات (Tabs) لسهولة العمل
tab1, tab2, tab3, tab4 = st.tabs(["💰 التكاليف الثابتة", "📦 تكاليف المنتجات", "🛍️ حركة المبيعات", "📈 التقارير والأرباح"])

# ---------------------------------------------------------
# 1. التكاليف الثابتة
# ---------------------------------------------------------
with tab1:
    st.header("إدخال التكاليف الثابتة (أجور، إيجار، فواتير...) ")
    with st.form("fixed_form", clear_on_submit=True):
        item = st.text_input("بند التكلفة (مثال: إيجار الورشة)")
        cost = st.number_input("القيمة المالية", min_value=0.0, step=50.0)
        submitted = st.form_submit_button("حفظ البند")
        if submitted and item:
            new_row = pd.DataFrame([{"البند": item, "القيمة (جنيه)": cost}])
            fixed_df = pd.concat([fixed_df, new_row], ignore_index=True)
            save_data(fixed_df, "fixed_costs.csv")
            st.success(f"تم حفظ {item} بنجاح")
    
    st.subheader("قائمة التكاليف الثابتة الحالية")
    st.dataframe(fixed_df, use_container_width=True)
    if st.button("مسح كل التكاليف الثابتة"):
        fixed_df = pd.DataFrame(columns=["البند", "القيمة (جنيه)"])
        save_data(fixed_df, "fixed_costs.csv")
        st.rerun()

# ---------------------------------------------------------
# 2. تكاليف المنتجات المتغيرة
# ---------------------------------------------------------
with tab2:
    st.header("تعريف تكاليف المنتجات (المتغيرة)")
    with st.form("product_form", clear_on_submit=True):
        p_name = st.text_input("اسم المنتج (مثال: تسريحة مضيئة 105سم)")
        raw_mat = st.number_input("تكلفة المواد الخام (MDF، إكسسوار، ليد)", min_value=0.0, step=10.0)
        mfg_cost = st.number_input("تكلفة التصنيع والعمالة المباشرة للقطعة", min_value=0.0, step=10.0)
        pack_cost = st.number_input("تكلفة الشحن والتغليف للقطعة", min_value=0.0, step=10.0)
        p_submitted = st.form_submit_button("حفظ المنتج")
        if p_submitted and p_name:
            new_p = pd.DataFrame([{"اسم المنتج": p_name, "خامات": raw_mat, "تصنيع": mfg_cost, "شحن وتغليف": pack_cost}])
            products_df = pd.concat([products_df, new_p], ignore_index=True)
            save_data(products_df, "products_costs.csv")
            st.success(f"تم تسجيل المنتج {p_name}")

    st.subheader("قائمة تكاليف المنتجات المسجلة")
    st.dataframe(products_df, use_container_width=True)
    if st.button("مسح كل المنتجات"):
        products_df = pd.DataFrame(columns=["اسم المنتج", "خامات", "تصنيع", "شحن وتغليف"])
        save_data(products_df, "products_costs.csv")
        st.rerun()

# ---------------------------------------------------------
# 3. حركة المبيعات
# ---------------------------------------------------------
with tab3:
    st.header("تسجيل المبيعات الفعلية")
    if products_df.empty:
        st.warning("برجاء تسجيل منتج واحد على الأقل في التبويب السابق أولاً لتتمكن من البيع.")
    else:
        with st.form("sales_form", clear_on_submit=True):
            selected_p = st.selectbox("اختر المنتج المباع", products_df["اسم المنتج"].unique())
            qty = st.number_input("الكمية المباعة", min_value=1, step=1)
            actual_price = st.number_input("سعر البيع الفعلي للقطعة الواحدة", min_value=0.0, step=50.0)
            s_submitted = st.form_submit_button("تسجيل عملية البيع")
            if s_submitted:
                new_sale = pd.DataFrame([{"اسم المنتج": selected_p, "الكمية": qty, "سعر البيع الفعلي": actual_price}])
                sales_df = pd.concat([sales_df, new_sale], ignore_index=True)
                save_data(sales_df, "sales.csv")
                st.success(f"تم تسجيل بيع {qty} من {selected_p}")

    st.subheader("سجل المبيعات الحالية")
    st.dataframe(sales_df, use_container_width=True)
    if st.button("مسح سجل المبيعات"):
        sales_df = pd.DataFrame(columns=["اسم المنتج", "الكمية", "سعر البيع الفعلي"])
        save_data(sales_df, "sales.csv")
        st.rerun()

# ---------------------------------------------------------
# 4. لوحة التقارير والتحليل المالي
# ---------------------------------------------------------
with tab4:
    st.header("📈 الحسابات الختامية والتقارير")
    
    # حساب الإيرادات
    sales_df["إجمالي البيع"] = sales_df["الكمية"] * sales_df["سعر البيع الفعلي"]
    total_revenues = sales_df["إجمالي البيع"].sum()
    
    # حساب التكاليف الثابتة
    total_fixed = fixed_df["القيمة (جنيه)"].sum()
    
    # حساب التكاليف المتغيرة بناءً على المبيعات الفعلية
    total_variable = 0.0
    for index, row in sales_df.iterrows():
        p_info = products_df[products_df["اسم المنتج"] == row["اسم المنتج"]]
        if not p_info.empty:
            unit_variable_cost = p_info["خامات"].values[0] + p_info["تصنيع"].values[0] + p_info["شحن وتغليف"].values[0]
            total_variable += unit_variable_cost * row["الكمية"]
            
    total_costs = total_fixed + total_variable
    net_profit = total_revenues - total_costs
    
    # عرض المؤشرات الرئيسية (KPIs)
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("إجمالي الإيرادات", f"{total_revenues:,.2f} جنيه")
    col2.metric("التكاليف الثابتة", f"{total_fixed:,.2f} جنيه")
    col3.metric("التكاليف المتغيرة للمبيعات", f"{total_variable:,.2f} جنيه")
    
    if net_profit >= 0:
        col4.metric("صافي الربح 😊", f"{net_profit:,.2f} جنيه", delta=f"{net_profit:,.2f}")
    else:
        col4.metric("صافي الخسارة 😞", f"{net_profit:,.2f} جنيه", delta=f"{net_profit:,.2f}", delta_color="inverse")
        
    st.markdown("---")
    st.subheader("🎯 تحليل هامش ربحية المنتجات")
    
    if not products_df.empty:
        analysis_prod = products_df.copy()
        analysis_prod["إجمالي تكلفة القطعة"] = analysis_prod["خامات"] + analysis_prod["تصنيع"] + analysis_prod["شحن وتغليف"]
        
        # حساب متوسط سعر البيع لكل منتج من جدول المبيعات
        avg_prices = sales_df.groupby("اسم المنتج")["سعر البيع الفعلي"].mean().reset_index()
        avg_prices.columns = ["اسم المنتج", "متوسط سعر البيع"]
        
        analysis_df = pd.merge(analysis_prod, avg_prices, on="اسم المنتج", how="left")
        analysis_df["متوسط سعر البيع"] = analysis_df["متوسط سعر البيع"].fillna(0.0)
        
        # حساب هامش ربح القطعة = سعر البيع - التكلفة المتغيرة للقطعة
        analysis_df["ربح القطعة المتوقع"] = analysis_df["متوسط سعر البيع"] - analysis_df["إجمالي تكلفة القطعة"]
        
        # نسبة هامش الربح = (ربح القطعة / سعر البيع) * 100
        analysis_df["نسبة هامش الربح (%)"] = analysis_df.apply(
            lambda r: (r["ربح القطعة المتوقع"] / r["متوسط سعر البيع"] * 100) if r["متوسط سعر البيع"] > 0 else 0, axis=1
        )
        
        st.dataframe(analysis_df[["اسم المنتج", "إجمالي تكلفة القطعة", "متوسط سعر البيع", "ربح القطعة المتوقع", "نسبة هامش الربح (%)"]], use_container_width=True)
    else:
        st.info("لا توجد بيانات كافية لتحليل المنتجات.")
