import streamlit as st
import plotly.graph_objects as go

# 设置页面配置
st.set_page_config(page_title="购房总成本计算器", layout="wide")

st.title("🏠 购房总成本计算器")

# 侧边栏：输入参数
st.sidebar.header("参数设置")

# 房价
house_price = st.sidebar.number_input("房屋总价 (万元)", min_value=10.0, value=315.0, step=5.0) * 10000

# 首付比例
down_payment_ratio = st.sidebar.slider("首付比例 (%)", min_value=10, max_value=100, value=30, step=5) / 100.0

# 贷款参数
loan_years = st.sidebar.selectbox("贷款年限 (年)", options=[10, 15, 20, 25, 30], index=0)
interest_rate = st.sidebar.number_input("商贷利率 (%)", min_value=1.0, value=3.05, step=0.05) / 100.0

# 其他费用
agency_fee_ratio = st.sidebar.number_input("中介费率 (%)", min_value=0.0, value=2.0, step=0.1) / 100.0
deed_tax_ratio = st.sidebar.number_input("契税税率 (%)", min_value=0.0, value=1.0, step=0.5) / 100.0

# --- 计算逻辑 ---
# 1. 首付款和贷款额
down_payment = house_price * down_payment_ratio
loan_amount = house_price - down_payment

# 2. 贷款利息 (等额本息计算)
if loan_amount > 0 and interest_rate > 0:
    monthly_rate = interest_rate / 12
    months = loan_years * 12
    # 等额本息月供计算公式: [贷款本金 × 月利率 × (1+月利率)^还款月数] ÷ [(1+月利率)^还款月数 - 1]
    monthly_payment = loan_amount * monthly_rate * ((1 + monthly_rate) ** months) / (((1 + monthly_rate) ** months) - 1)
    total_repayment = monthly_payment * months
    total_interest = total_repayment - loan_amount
else:
    total_interest = 0
    monthly_payment = 0

# 3. 中介费与契税
agency_fee = house_price * agency_fee_ratio
deed_tax = house_price * deed_tax_ratio

# 4. 总成本
total_cost = house_price + total_interest + agency_fee + deed_tax

# --- 布局与展示 ---
st.subheader("💰 核心数据概览")
col1, col2, col3, col4 = st.columns(4)
col1.metric("房屋总价", f"{house_price / 10000:,.2f} 万")
col2.metric("首付款", f"{down_payment / 10000:,.2f} 万")
col3.metric("贷款总额", f"{loan_amount / 10000:,.2f} 万")
col4.metric("总利息", f"{total_interest / 10000:,.2f} 万")

col5, col6, col7, col8 = st.columns(4)
col5.metric("中介费", f"{agency_fee / 10000:,.2f} 万")
col6.metric("契税", f"{deed_tax / 10000:,.2f} 万")
col7.metric("总支出成本", f"{total_cost / 10000:,.2f} 万")
col8.metric("参考月供", f"{monthly_payment:,.2f} 元")

st.markdown("---")
st.subheader("📊 购房成本瀑布图")

# 构建瀑布图数据
measures = ["absolute", "relative", "relative", "relative", "total"]
labels = ["房屋总价", "贷款利息", "中介费", "契税", "总成本"]
values = [house_price, total_interest, agency_fee, deed_tax, total_cost]

fig = go.Figure(go.Waterfall(
    name="购房成本",
    orientation="v",
    measure=measures,
    x=labels,
    textposition="outside",
    text=[f"{v / 10000:,.1f}万" if v != 0 else "" for v in values],
    y=values,
    connector={"line": {"color": "rgb(63, 63, 63)"}}
))

fig.update_layout(
    title=f"购房总成本瀑布图（{house_price/10000:g}万房价, {loan_years}年贷款, {interest_rate*100:.2f}%利率）",
    title_x=0.5,
    waterfallgap=0.3,
    yaxis_title="金额 (元)",
    height=600
)

st.plotly_chart(fig, use_container_width=True)

# 提供详细明细表格
st.subheader("📋 费用明细表")
details = [
    {"项目": "房屋总价", "金额 (元)": f"{house_price:,.2f}", "金额 (万元)": f"{house_price/10000:,.2f}"},
    {"项目": "首付款", "金额 (元)": f"{down_payment:,.2f}", "金额 (万元)": f"{down_payment/10000:,.2f}"},
    {"项目": "贷款总额", "金额 (元)": f"{loan_amount:,.2f}", "金额 (万元)": f"{loan_amount/10000:,.2f}"},
    {"项目": "贷款总利息", "金额 (元)": f"{total_interest:,.2f}", "金额 (万元)": f"{total_interest/10000:,.2f}"},
    {"项目": "中介费", "金额 (元)": f"{agency_fee:,.2f}", "金额 (万元)": f"{agency_fee/10000:,.2f}"},
    {"项目": "契税", "金额 (元)": f"{deed_tax:,.2f}", "金额 (万元)": f"{deed_tax/10000:,.2f}"},
    {"项目": "总支出成本", "金额 (元)": f"{total_cost:,.2f}", "金额 (万元)": f"{total_cost/10000:,.2f}"}
]
st.dataframe(details, use_container_width=True)


