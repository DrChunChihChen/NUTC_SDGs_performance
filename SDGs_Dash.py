import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import numpy as np
import os
from collections import defaultdict

# Configure page
st.set_page_config(
    page_title="SDG 分佈儀表板",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main > div {
        padding-top: 2rem;
    }
    .stMetric {
        background-color: #f0f2f6;
        border: 1px solid #e6e9ef;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }
    .stTabs [data-baseweb="tab"] {
        padding-left: 1rem;
        padding-right: 1rem;
    }
    div[data-testid="stSidebar"] > div:first-child {
        background-color: #f8f9fa;
    }
    .plot-container {
        border: 1px solid #e6e9ef;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)


# Load data function
@st.cache_data
def load_data(data_type, year):
    """根據指定的資料類型與學年度載入所有 JSON 資料檔案，並回傳為 pandas DataFrames。"""
    # Define root paths
    relative_root = "data"
    hardcoded_root = r"file"
    root_path = hardcoded_root if os.path.isdir(hardcoded_root) else relative_root

    # Initialize data variables
    dept_counts, dept_percentages, overall_dist, sdg13_dist = [], [], [], []

    try:
        # Handle '產學' and '論文' which have a similar summary file structure
        if data_type in ['產學', '論文']:
            if data_type == '產學':
                file_name = f'department_sdg_summary_產學{year}.json'
            else:  # '論文'
                # Assuming the pattern is year + "-1" for thesis data
                file_name = f'department_sdg_summary_論文{year}-1.json'

            file_path = os.path.join(root_path, file_name)
            st.sidebar.info(f"📁 正在嘗試載入檔案: `{file_path}`")
            with open(file_path, 'r', encoding='utf-8') as f:
                raw_summary_data = json.load(f)

            # Transform the summary data into the format used by the dashboard
            dept_counts = []
            for dept_name, sdgs in raw_summary_data.items():
                dept_dict = {'科系名稱': dept_name}
                dept_dict.update(sdgs)
                dept_counts.append(dept_dict)

            sdg_totals = defaultdict(int)
            for dept in dept_counts:
                for key, value in dept.items():
                    if key.startswith('SDG'):
                        sdg_totals[key] += value
            overall_dist = [{"SDG": sdg, "次數": count} for sdg, count in sdg_totals.items()]

            sdg13_dist = []
            for dept in dept_counts:
                if 'SDG13' in dept and dept['SDG13'] > 0:
                    sdg13_dist.append({
                        '提及課程數量': dept['科系名稱'],
                        'count': dept['SDG13']
                    })

            # These summary files do not contain percentage data
            dept_percentages = []

        # Handle '課程' which has a folder structure with multiple files
        elif data_type == '課程':
            data_folder = os.path.join(root_path, year)
            st.sidebar.info(f"📁 正在嘗試載入資料夾: `{data_folder}`")
            counts_path = os.path.join(data_folder, 'department_sdg_counts.json')
            percentages_path = os.path.join(data_folder, 'department_sdg_percentages.json')
            overall_path = os.path.join(data_folder, 'overall_sdg_distribution.json')
            sdg13_path = os.path.join(data_folder, 'specific_SDG13_distribution.json')

            with open(counts_path, 'r', encoding='utf-8') as f:
                dept_counts = json.load(f)
            with open(percentages_path, 'r', encoding='utf-8') as f:
                dept_percentages = json.load(f)
            with open(overall_path, 'r', encoding='utf-8') as f:
                overall_dist = json.load(f)
            with open(sdg13_path, 'r', encoding='utf-8') as f:
                sdg13_dist = json.load(f)

        st.sidebar.success(f"✅ {data_type} / {year} 學年度資料檔案載入成功！")

    except FileNotFoundError as e:
        st.sidebar.warning(f"⚠️ 找不到檔案或路徑: {e}。正在改用範例資料。")
        dept_counts, dept_percentages, overall_dist, sdg13_dist = get_sample_data()
    except Exception as e:
        st.sidebar.error(f"❌ 載入檔案時發生錯誤: {e}。正在使用範例資料。")
        dept_counts, dept_percentages, overall_dist, sdg13_dist = get_sample_data()

    # Convert to DataFrames
    df_dept_counts = pd.DataFrame(dept_counts)
    df_dept_percentages = pd.DataFrame(dept_percentages)
    df_overall_dist = pd.DataFrame(overall_dist)
    df_sdg13_dist = pd.DataFrame(sdg13_dist)

    return df_dept_counts, df_dept_percentages, df_overall_dist, df_sdg13_dist


def get_sample_data():
    """Provides sample data if real files can't be loaded."""
    dept_counts = [
        {"科系名稱": "中文系", "NONE": 30, "SDG1": 0, "SDG10": 1, "SDG11": 1, "SDG12": 1, "SDG13": 0, "SDG15": 0,
         "SDG16": 3, "SDG17": 0, "SDG2": 0, "SDG3": 4, "SDG4": 35, "SDG5": 0, "SDG6": 0, "SDG7": 0, "SDG8": 9,
         "SDG9": 0},
        {"科系名稱": "企業管理", "NONE": 195, "SDG1": 0, "SDG10": 0, "SDG11": 0, "SDG12": 15, "SDG13": 2, "SDG15": 2,
         "SDG16": 5, "SDG17": 0, "SDG2": 0, "SDG3": 15, "SDG4": 49, "SDG5": 0, "SDG6": 0, "SDG7": 2, "SDG8": 183,
         "SDG9": 31},
    ]
    dept_percentages = [
        {"科系名稱": "中文系", "NONE": 35.71, "SDG4": 41.67, "SDG8": 10.71, "SDG3": 4.76, "SDG16": 3.57},
        {"科系名稱": "企業管理", "NONE": 39.08, "SDG8": 36.67, "SDG4": 9.82, "SDG9": 6.21, "SDG3": 3.01},
    ]
    overall_dist = [
        {"SDG": "NONE", "次數": 2766}, {"SDG": "SDG8", "次數": 1383}, {"SDG": "SDG4", "次數": 801},
    ]
    sdg13_dist = [
        {"提及課程數量": "通識教育與其他", "count": 5}, {"提及課程數量": "企業管理", "count": 2},
    ]
    return dept_counts, dept_percentages, overall_dist, sdg13_dist


# SDG descriptions in Traditional Chinese
SDG_DESCRIPTIONS = {
    "SDG1": "消除貧窮", "SDG2": "消除飢餓", "SDG3": "良好健康與福祉",
    "SDG4": "優質教育", "SDG5": "性別平等", "SDG6": "清潔飲水與衛生設施",
    "SDG7": "可負擔的潔淨能源", "SDG8": "尊嚴就業與經濟成長",
    "SDG9": "工業、創新與基礎設施", "SDG10": "減少不平等",
    "SDG11": "永續城市與社區", "SDG12": "負責任的消費與生產",
    "SDG13": "氣候行動", "SDG15": "陸地生態",
    "SDG16": "和平、正義與強健制度", "SDG17": "促進目標的夥伴關係"
}


def main():
    st.sidebar.title("📊 儀表板導覽")

    # Add selectors for data type and year
    st.session_state.data_type = st.sidebar.selectbox(
        "選擇資料類型:",
        ['課程', '產學', '論文'],
        key='data_type_selector'
    )

    st.session_state.year = st.sidebar.selectbox(
        "選擇學年度:",
        ['112', '113'],
        key='year_selector'
    )

    # Load data based on the selections
    df_dept_counts, df_dept_percentages, df_overall_dist, df_sdg13_dist = load_data(st.session_state.data_type,
                                                                                    st.session_state.year)

    if df_dept_counts.empty and df_overall_dist.empty:
        st.error("資料載入失敗或資料為空，無法顯示儀表板。請檢查您的 JSON 檔案與路徑。")
        return

    st.title(f"🎯 {st.session_state.year} 學年度 {st.session_state.data_type} SDG 分佈儀表板")
    st.markdown("### 分析各學術部門的永續發展目標 (SDGs) 對應情況")
    st.markdown("---")

    col1, col2, col3, col4 = st.columns(4)

    count_column = '次數' if '次數' in df_overall_dist.columns else 'count'

    total_mentions = df_overall_dist[count_column].sum() if not df_overall_dist.empty else 0
    sdg_mentions = df_overall_dist[df_overall_dist['SDG'] != 'NONE'][
        count_column].sum() if not df_overall_dist.empty else 0
    total_departments = len(df_dept_counts)
    alignment_rate = (sdg_mentions / total_mentions * 100) if total_mentions > 0 else 0

    with col1:
        st.metric("總單位/科系數", total_departments)
    with col2:
        st.metric(f"總提及數 ({st.session_state.data_type})", f"{total_mentions:,}")
    with col3:
        st.metric("SDG 相關提及數", f"{sdg_mentions:,}")
    with col4:
        st.metric("總體對應率", f"{alignment_rate:.1f}%")

    st.markdown("---")

    # Navigation for different views
    page = st.sidebar.selectbox(
        "選擇一個視圖:",
        ["📈 總覽", "🏫 科系/單位分析", "🔍 SDG 比較", "🌍 氣候行動 (SDG13)", "📋 詳細數據"]
    )

    if page == "📈 總覽":
        show_overview(df_overall_dist, df_dept_counts)
    elif page == "🏫 科系/單位分析":
        show_department_analysis(df_dept_counts, df_dept_percentages)
    elif page == "🔍 SDG 比較":
        show_sdg_comparison(df_dept_counts)
    elif page == "🌍 氣候行動 (SDG13)":
        show_sdg13_analysis(df_sdg13_dist, df_dept_counts)
    elif page == "📋 詳細數據":
        show_detailed_exploration(df_dept_counts, df_dept_percentages)


def show_overview(df_overall, df_dept):
    st.header("📊 整體 SDG 分佈")

    if df_overall.empty:
        st.warning("無整體分佈資料可顯示。")
        return

    count_column = '次數' if '次數' in df_overall.columns else 'count'

    col1, col2 = st.columns([3, 2])

    with col1:
        fig_pie = px.pie(
            df_overall,
            values=count_column,
            names='SDG',
            title="所有單位 SDG 分佈",
            color_discrete_sequence=px.colors.qualitative.Set3,
        )
        fig_pie.update_traces(
            textposition='inside',
            textinfo='percent+label',
            hovertemplate='<b>%{label}</b><br>次數: %{value:,}<br>百分比: %{percent}<extra></extra>'
        )
        fig_pie.update_layout(height=500, legend_title_text='SDGs')
        st.plotly_chart(fig_pie, use_container_width=True)

    with col2:
        st.subheader("📈 關鍵洞察")

        total_mentions = df_overall[count_column].sum()
        sdg_mentions = df_overall[df_overall['SDG'] != 'NONE'][count_column].sum()
        none_mentions_series = df_overall[df_overall['SDG'] == 'NONE'][count_column]
        none_mentions = none_mentions_series.iloc[0] if not none_mentions_series.empty else 0

        st.metric("📊 總提及數", f"{total_mentions:,}")
        st.metric("🎯 SDG 相關", f"{sdg_mentions:,}", f"{(sdg_mentions / total_mentions * 100):.1f}%")
        st.metric("❌ 非相關", f"{none_mentions:,}", f"{(none_mentions / total_mentions * 100):.1f}%")

        st.subheader("🏆 表現最佳的 SDG")
        top_sdgs = df_overall[df_overall['SDG'] != 'NONE'].nlargest(5, count_column)
        for idx, row in top_sdgs.iterrows():
            sdg_name = SDG_DESCRIPTIONS.get(row['SDG'], row['SDG'])
            percentage = (row[count_column] / sdg_mentions) * 100 if sdg_mentions > 0 else 0
            st.write(f"**{row['SDG']}** - {sdg_name}")
            st.progress(percentage / 100)
            st.write(f"📊 {row[count_column]:,} 次提及 ({percentage:.1f}% of aligned)")
            st.markdown("---", unsafe_allow_html=True)

    st.subheader("📊 SDG 頻率分析")

    df_sdg_only = df_overall[df_overall['SDG'] != 'NONE'].sort_values(count_column, ascending=True)

    fig_bar = px.bar(
        df_sdg_only,
        x=count_column,
        y='SDG',
        orientation='h',
        title="SDG 提及次數 (不含無對應項目)",
        color=count_column,
        color_continuous_scale='viridis',
        text=count_column
    )

    hover_text = [f"{sdg}: {SDG_DESCRIPTIONS.get(sdg, sdg)}" for sdg in df_sdg_only['SDG']]

    fig_bar.update_traces(
        texttemplate='%{text:,}',
        textposition='outside',
        hovertemplate='<b>%{y}</b><br>%{customdata}<br>次數: %{x:,}<extra></extra>',
        customdata=hover_text
    )
    fig_bar.update_layout(height=600, showlegend=False, coloraxis_showscale=False)
    fig_bar.update_xaxes(title="提及次數")
    fig_bar.update_yaxes(title="永續發展目標")

    st.plotly_chart(fig_bar, use_container_width=True)


def show_sdg13_analysis(df_sdg13, df_dept):
    st.header("🌍 氣候行動 (SDG13) 分析")
    st.markdown("### 深入探討氣候相關項目的分佈情況")

    if df_sdg13.empty:
        st.warning("目前沒有 SDG13 的相關資料。")
        return

    df_sdg13 = df_sdg13.rename(columns={'提及課程數量': '單位名稱', 'count': '計數'})

    col1, col2 = st.columns([2, 1])

    with col1:
        fig_sdg13 = px.bar(
            df_sdg13.sort_values('計數', ascending=False),
            x='單位名稱',
            y='計數',
            title="各單位 SDG13 (氣候行動) 項目數量",
            text='計數',
            color='計數',
            color_continuous_scale='greens'
        )
        fig_sdg13.update_traces(textposition='outside')
        fig_sdg13.update_xaxes(tickangle=45, title="單位/科系")
        fig_sdg13.update_yaxes(title="氣候行動項目數量")
        fig_sdg13.update_layout(showlegend=False, height=500, coloraxis_showscale=False)
        st.plotly_chart(fig_sdg13, use_container_width=True)

        st.subheader("📊 氣候行動參與度分析")

        total_sdg13 = df_sdg13['計數'].sum()
        engaging_depts = len(df_sdg13)
        total_depts = len(df_dept)
        engagement_rate = (engaging_depts / total_depts) * 100 if total_depts > 0 else 0

        col3, col4, col5 = st.columns(3)
        with col3:
            st.metric("氣候項目總數", total_sdg13)
        with col4:
            st.metric("參與單位數", f"{engaging_depts}/{total_depts}")
        with col5:
            st.metric("參與率", f"{engagement_rate:.1f}%")

    with col2:
        st.subheader("🎯 關鍵洞察")

        st.write("**🏆 領先單位:**")
        for idx, row in df_sdg13.nlargest(5, '計數').iterrows():
            st.write(f"• **{row['單位名稱']}**: {row['計數']} 個項目")

        st.write("---")

        st.subheader("💡 改善建議")
        st.write(f"""
        **提升氣候行動參與度的建議：**

        🌱 **擴展至更多單位**
        - 目前僅有 {engagement_rate:.0f}% 的單位參與。
        - 可鎖定商業、工程、健康等高潛力領域。

        📚 **跨領域整合**
        - 開發跨學科的氣候模組和永續發展專案。

        🎓 **促進教師/職員發展**
        - 提供氣候教育和綠色實踐的培訓。
        """)


def show_department_analysis(df_dept, df_perc):
    st.header("🏫 科系/單位分析")

    if df_dept.empty:
        st.warning("無科系/單位資料可顯示。")
        return

    unit_column = '科系名稱'
    departments = sorted(df_dept[unit_column].tolist())
    selected_dept = st.selectbox(f"🔍 請選擇一個{unit_column.replace('名稱', '')}:", departments)

    dept_data = df_dept[df_dept[unit_column] == selected_dept].iloc[0]

    col1, col2 = st.columns([2, 1])

    with col1:
        sdg_cols = [col for col in df_dept.columns if col.startswith('SDG')]
        dept_sdg_data = {sdg: dept_data[sdg] for sdg in sdg_cols if dept_data.get(sdg, 0) > 0}

        if dept_sdg_data:
            df_plot = pd.DataFrame(list(dept_sdg_data.items()), columns=['SDG', 'Count']).sort_values('Count',
                                                                                                      ascending=False)

            fig = px.bar(
                df_plot,
                x='SDG',
                y='Count',
                title=f"{selected_dept} SDG 項目數量分佈",
                text='Count',
                color='Count',
                color_continuous_scale='cividis'
            )
            fig.update_traces(textposition='outside')
            fig.update_layout(showlegend=False, coloraxis_showscale=False)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("此單位無 SDG 相關資料。")

    with col2:
        st.subheader(f"📊 {unit_column}統計數據")

        all_cols = [col for col in df_dept.columns if col != unit_column]
        total_items = dept_data.fillna(0)[all_cols].sum()
        aligned_items = sum(dept_sdg_data.values())
        none_items = dept_data.get('NONE', 0)

        st.metric("📚 項目總數", int(total_items))
        st.metric("🎯 SDG 相關項目", aligned_items)
        st.metric("❌ 非相關項目", int(none_items))

        alignment_rate = (aligned_items / total_items) * 100 if total_items > 0 else 0
        st.metric("📈 對應率", f"{alignment_rate:.1f}%")
        st.progress(alignment_rate / 100)

        st.subheader("🏆 主要 SDGs")
        if dept_sdg_data:
            sorted_sdgs = sorted(dept_sdg_data.items(), key=lambda item: item[1], reverse=True)
            for sdg, count in sorted_sdgs[:3]:
                sdg_name = SDG_DESCRIPTIONS.get(sdg, sdg)
                percentage = (count / total_items) * 100 if total_items > 0 else 0
                st.write(f"**{sdg}**: {sdg_name}")
                st.write(f"📊 {count} 個項目 ({percentage:.1f}%)")
                st.markdown("---")


def show_sdg_comparison(df_dept):
    st.header("🔍 SDG 比較")
    st.markdown("### 比較各單位的 SDG 參與度")

    if df_dept.empty:
        st.warning("無單位資料可供比較。")
        return

    unit_column = '科系名稱'
    sdg_cols = sorted([col for col in df_dept.columns if col.startswith('SDG')])

    if not sdg_cols:
        st.warning("找不到可比較的 SDG 資料。")
        return

    st.info("請選擇多個 SDG，以比較它們在不同單位中的分佈情況。")
    selected_sdgs = st.multiselect(
        "選擇要比較的 SDGs:",
        options=sdg_cols,
        default=sdg_cols[:3] if len(sdg_cols) >= 3 else sdg_cols
    )

    if not selected_sdgs:
        st.warning("請至少選擇一個 SDG。")
        return

    comparison_data = df_dept[[unit_column] + selected_sdgs].fillna(0)
    comparison_data = comparison_data.loc[(comparison_data[selected_sdgs] > 0).any(axis=1)]

    if comparison_data.empty:
        st.info("沒有單位提及所選的 SDGs。")
        return

    df_melted = comparison_data.melt(
        id_vars=unit_column,
        value_vars=selected_sdgs,
        var_name='SDG',
        value_name='Count'
    ).query("Count > 0")

    st.subheader("所選 SDGs 的單位參與度")
    fig = px.bar(
        df_melted,
        x=unit_column,
        y='Count',
        color='SDG',
        barmode='group',
        title="各單位 SDG 項目數量比較",
        labels={unit_column: '單位/科系', 'Count': '項目提及次數'},
        height=600,
        category_orders={"SDG": selected_sdgs}
    )
    fig.update_xaxes(tickangle=45)
    st.plotly_chart(fig, use_container_width=True)


def show_detailed_exploration(df_dept, df_perc):
    st.header("🔎 詳細數據探索")

    tab1, tab2, tab3, tab4 = st.tabs(["📊 原始數據", "🔗 相關性分析", "📈 排名", "📋 匯出"])

    with tab1:
        st.subheader("項目計數資料")
        st.dataframe(df_dept, use_container_width=True)

        st.subheader("百分比分佈資料")
        if not df_perc.empty:
            st.dataframe(df_perc, use_container_width=True)
        else:
            st.info("此資料類型沒有百分比分佈資料。")

    with tab2:
        if df_dept.empty or len(df_dept) < 2:
            st.warning("相關性分析需要至少兩個單位的資料。")
        else:
            st.subheader("SDG 相關性分析")
            sdg_cols = [col for col in df_dept.columns if col.startswith('SDG')]
            corr_matrix = df_dept.fillna(0)[sdg_cols].corr()  # Fill NA for correlation

            fig_corr = px.imshow(
                corr_matrix,
                title="SDG 相關性矩陣 - 哪些 SDGs 會一起出現？",
                color_continuous_scale='RdBu_r',
                aspect="auto",
                text_auto=".2f"
            )
            fig_corr.update_layout(height=600)
            st.plotly_chart(fig_corr, use_container_width=True)
            st.write(
                "💡 **解讀**: 正相關（接近+1，藍色）表示這些 SDGs 傾向於在同一個項目中一起出現。負相關（接近-1，紅色）表示它們較少一起出現。")

    with tab3:
        if df_dept.empty:
            st.warning("無資料可進行排名。")
        else:
            st.subheader("單位/科系排名")

            unit_column = '科系名稱'
            sdg_cols = [col for col in df_dept.columns if col.startswith('SDG')]
            df_analysis = df_dept.copy().fillna(0)
            df_analysis['項目總數'] = df_analysis.drop(unit_column, axis=1, errors='ignore').sum(axis=1)
            df_analysis['SDG項目數'] = df_analysis[sdg_cols].sum(axis=1)
            df_analysis['對應率'] = np.where(df_analysis['項目總數'] > 0,
                                             (df_analysis['SDG項目數'] / df_analysis['項目總數']) * 100, 0)
            df_analysis['SDG多樣性'] = (df_analysis[sdg_cols] > 0).sum(axis=1)

            rank_by_translation = {
                '對應率': '對應率',
                'SDG項目數': 'SDG項目數',
                'SDG多樣性': 'SDG多樣性',
                '項目總數': '項目總數'
            }

            rank_by_display = st.selectbox(
                "請選擇排名依據:",
                list(rank_by_translation.keys())
            )

            rank_by = rank_by_translation[rank_by_display]

            display_columns = [unit_column, '項目總數', 'SDG項目數', '對應率', 'SDG多樣性']

            df_ranked = df_analysis.nlargest(10, rank_by)[display_columns]

            st.dataframe(
                df_ranked.style.format({
                    '對應率': '{:.1f}%',
                    '項目總數': '{:,.0f}',
                    'SDG項目數': '{:,.0f}',
                    'SDG多樣性': '{:,.0f}'
                }).background_gradient(cmap='viridis', subset=[rank_by]),
                use_container_width=True
            )

    with tab4:
        st.subheader("📁 資料匯出")
        st.info("下載原始資料以進行您自己的分析。")

        col1, col2 = st.columns(2)
        with col1:
            csv_counts = df_dept.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                label="📊 下載計數資料 (CSV)",
                data=csv_counts,
                file_name=f"{st.session_state.data_type}_{st.session_state.year}_counts.csv",
                mime="text/csv"
            )

        with col2:
            if not df_perc.empty:
                csv_percentages = df_perc.to_csv(index=False, encoding='utf-8-sig')
                st.download_button(
                    label="📈 下載百分比資料 (CSV)",
                    data=csv_percentages,
                    file_name=f"{st.session_state.data_type}_{st.session_state.year}_percentages.csv",
                    mime="text/csv"
                )
            else:
                st.button("📈 下載百分比資料 (CSV)", disabled=True)


def show_footer():
    st.markdown("---")
    st.subheader("📖 如何使用此儀表板")

    with st.expander("🚀 開始使用"):
        st.markdown("""
        **1. 資料設定:**
        - **對於「課程」資料**: 
          - 在此腳本的同層目錄建立路徑 `data/112/` 和 `data/113/`。
          - 將四個獨立的 JSON 檔案 (`department_sdg_counts.json`, etc.) 放入對應的學年度資料夾。
        - **對於「產學」和「論文」資料**:
          - 在此腳本的同層目錄建立 `data/` 資料夾。
          - 將摘要檔 (例如: `department_sdg_summary_產學112.json`, `department_sdg_summary_論文112-1.json`) 直接放入 `data/` 資料夾。
        - 如果找不到上述路徑，程式會嘗試讀取您的絕對路徑 `C:\\Users\\Elvischen\\...`
        - 若所有路徑皆失敗，將使用內建的範例資料。

        **2. 導覽:**
        - 使用左側的側邊欄選擇**資料類型** (課程/產學/論文)，再選擇**學年度**，最後選擇要查看的**分析視圖**。

        **3. 互動功能:**
        - 將滑鼠懸停在圖表上可查看更多詳細資訊。
        - 使用下拉選單和選擇器來篩選和探索資料。
        """)

    with st.expander("🎯 了解指標"):
        st.markdown("""
        - **對應率**: 一個單位(科系)的總項目中，與任一 SDG 相關的項目所佔的百分比。
        - **SDG 多樣性**: 一個單位(科系)所涵蓋的不同 SDG 的數量。數字越高，表示 SDG 參與度越廣。
        - **相關性**: 衡量兩個 SDG 一起出現的頻率。高的正值表示它們經常在同一個項目中被提及。
        """)

    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; padding: 2rem;'>
        <p>🎯 SDG 分佈儀表板 | 使用 Streamlit & Plotly 構建</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    # Initialize session state for selectors to ensure they exist
    if 'data_type' not in st.session_state:
        st.session_state.data_type = '課程'
    if 'year' not in st.session_state:
        st.session_state.year = '112'

    main()
    show_footer()
