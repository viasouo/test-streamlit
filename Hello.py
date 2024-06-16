import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# 設定頁面配置
st.set_page_config(page_title="全台灣縣市投票分析", layout="wide")

# 讀取 CSV 檔案
@st.cache_data  # 使用 st.cache_data 來快取資料
def load_data():
    # 嘗試使用不同的編碼方式讀取檔案
    encodings = ['utf-8', 'cp950', 'cp1252']
    for encoding in encodings:
        try:
            df = pd.read_csv("全國性公民投票概況(全國).csv", encoding=encoding)
            df.columns = [col.strip() for col in df.columns]  # 去除欄位名稱的前後空白
            return df
        except UnicodeDecodeError:
            continue
    raise UnicodeDecodeError("None of the tried encodings worked!")

df = load_data()

# 在 Streamlit 上顯示應用
st.title('全台灣縣市投票分析')

# 總覽視圖
st.header('全台灣投票情況總覽')

total_agree = df['同意票 C1 票數'].apply(lambda x: float(x.replace(',', ''))).sum()
total_disagree = df['不同意票 C2票數'].apply(lambda x: float(x.replace(',', ''))).sum()

fig_overview = go.Figure(
    data=[go.Pie(
        labels=['同意票', '不同意票'],
        values=[total_agree, total_disagree],
        hole=0.3,
        marker=dict(colors=['#34eb68', '#eb4034']),
        hoverinfo='label+percent',
        textinfo='value'
    )]
)
fig_overview.update_layout(title='全台灣投票情況')
st.plotly_chart(fig_overview)

# 使用者選擇縣市
st.header('選擇縣市進行分析')
selected_county = st.selectbox('選擇縣市', df['行政區別'].unique())

# 根據使用者選擇的縣市，顯示投票資訊
county_data = df[df['行政區別'] == selected_county]

if not county_data.empty:
    st.subheader(f'縣市: {selected_county}')
    st.write(f"同意票數: {county_data.iloc[0]['同意票 C1 票數']} ({county_data.iloc[0]['同意票 百分比 C1/C']:.2f}%)")
    st.write(f"不同意票數: {county_data.iloc[0]['不同意票 C2票數']} ({county_data.iloc[0]['不同意票 百分比 C2/C']:.2f}%)")
    st.write('無效票數：', county_data.iloc[0]['無效票數'])
    st.write('投票人數：', county_data.iloc[0]['投票人數'])
    
    # 選擇圖表類型：長條圖或圓餅圖
    chart_type = st.radio("選擇圖表類型", ['長條圖', '圓餅圖'])
    
    agree_count = float(county_data.iloc[0]['同意票 C1 票數'].replace(',', ''))
    disagree_count = float(county_data.iloc[0]['不同意票 C2票數'].replace(',', ''))
    
    if chart_type == '長條圖':
        # 繪製長條圖
        fig = px.bar(
            x=['同意票', '不同意票'], 
            y=[agree_count, disagree_count], 
            labels={'x': '投票選項', 'y': '票數'},
            color=['同意票', '不同意票'],
            color_discrete_map={'同意票': '#34eb68', '不同意票': '#eb4034'},
            title='同意票 vs 不同意票'
        )
        fig.update_layout(yaxis_title='票數', xaxis_title='投票選項')
        st.plotly_chart(fig)
    
    elif chart_type == '圓餅圖':
        # 繪製圓餅圖
        fig = go.Figure(
            data=[go.Pie(
                labels=['同意票', '不同意票'],
                values=[agree_count, disagree_count],
                hole=0.3,
                marker=dict(colors=['#34eb68', '#eb4034']),
                hoverinfo='label+percent',
                textinfo='value'
            )]
        )
        fig.update_layout(title='同意票 vs 不同意票')
        st.plotly_chart(fig)

else:
    st.warning('找不到該縣市的投票資料。')

# 數據搜尋功能
st.header('搜尋特定投票數據')
search_term = st.text_input('輸入搜尋關鍵字 (縣市名)')
search_results = df[df['行政區別'].str.contains(search_term, case=False, na=False)]

if not search_results.empty:
    st.write('搜尋結果：')
    st.dataframe(search_results)
else:
    st.write('找不到符合條件的資料。')
