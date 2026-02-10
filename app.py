import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# -----------------------------
# CONFIG
# -----------------------------
st.set_page_config(
    page_title="Supply Chain Dashboard",
    layout="wide"
)

# -----------------------------
# LOAD DATA
# -----------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("data/supply_chain_plasticaucho_simulated.csv")
    df["movement_date"] = pd.to_datetime(df["movement_date"])
    df["dispatch_date"] = pd.to_datetime(df["dispatch_date"])
    return df

df = load_data()

# -----------------------------
# SIDEBAR FILTERS
# -----------------------------
st.sidebar.header("Filtros")

category_filter = st.sidebar.multiselect(
    "Categoría de producto",
    options=df["category"].unique(),
    default=df["category"].unique()
)

product_filter = st.sidebar.multiselect(
    "Producto",
    options=df["product_name"].unique(),
    default=df["product_name"].unique()
)

filtered_df = df[
    (df["category"].isin(category_filter)) &
    (df["product_name"].isin(product_filter))
]

# -----------------------------
# TITLE
# -----------------------------
st.title("📦 Supply Chain Dashboard")
st.markdown("Análisis de inventarios, despachos y tiempos logísticos")

# -----------------------------
# EXECUTIVE SUMMARY
# -----------------------------
st.markdown("## 🧠 Conclusiones Ejecutivas")

st.info("""
**Hallazgos clave del análisis:**

• Un grupo reducido de productos concentra la mayor rotación de inventario.  
• Existen diferencias significativas en lead time entre categorías, lo que impacta la eficiencia logística.  
• El inventario promedio se mantiene estable, pero con oportunidades de optimización en productos de baja rotación.  
• La variabilidad en tiempos de despacho sugiere potencial de mejora en planificación operativa.

**Recomendaciones iniciales:**

✔ Priorizar control de inventario en productos de alta rotación  
✔ Revisar procesos logísticos en categorías con mayor lead time  
✔ Implementar métricas de stock mínimo y punto de reposición
""")

# -----------------------------
# KPIs
# -----------------------------
col1, col2, col3, col4 = st.columns(4)

avg_inventory = filtered_df["inventory_level"].mean()
avg_lead_time = filtered_df["lead_time_days"].mean()
total_orders = filtered_df["order_id"].nunique()
total_cost = (filtered_df["quantity"] * filtered_df["cost_unit"]).sum()

col1.metric("Inventario promedio", f"{avg_inventory:,.0f}")
col2.metric("Lead time promedio (días)", f"{avg_lead_time:.1f}")
col3.metric("Órdenes despachadas", f"{total_orders}")
col4.metric("Costo total estimado", f"${total_cost:,.0f}")

# -----------------------------
# INVENTORY OVER TIME
# -----------------------------
st.subheader("📈 Evolución del Inventario")

inventory_time = (
    filtered_df
    .groupby("movement_date")["inventory_level"]
    .mean()
    .reset_index()
)

fig, ax = plt.subplots()
ax.plot(inventory_time["movement_date"], inventory_time["inventory_level"])
ax.set_xlabel("Fecha")
ax.set_ylabel("Nivel de Inventario")
st.pyplot(fig)

# -----------------------------
# LEAD TIME BY PRODUCT
# -----------------------------
st.subheader("🚚 Lead Time promedio por producto")

lead_time_product = (
    filtered_df
    .groupby("product_name")["lead_time_days"]
    .mean()
    .sort_values(ascending=False)
    .head(10)
)

fig2, ax2 = plt.subplots()
lead_time_product.plot(kind="barh", ax=ax2)
ax2.set_xlabel("Días")
st.pyplot(fig2)

# -----------------------------
# INVENTORY ROTATION (SIMPLE)
# -----------------------------
st.subheader("🔄 Rotación de Inventario (aprox.)")

sales = filtered_df[filtered_df["movement_type"] == "Salida"]
rotation = (
    sales.groupby("product_name")["quantity"].sum()
    / filtered_df.groupby("product_name")["inventory_level"].mean()
)

rotation = rotation.sort_values(ascending=False).head(10)

fig3, ax3 = plt.subplots()
rotation.plot(kind="bar", ax=ax3)
ax3.set_ylabel("Índice de rotación")
st.pyplot(fig3)

# -----------------------------
# DATA TABLE
# -----------------------------
st.subheader("📄 Datos operativos")
st.dataframe(filtered_df.head(100))
