import streamlit as st
import numpy as np
import pandas as pd
from datetime import datetime
from catboost import CatBoostRegressor
from io import BytesIO

# 设置页面配置
st.set_page_config(
    page_title="二氧化碳转化率预测",
    page_icon="🌿",
    layout="wide")

@st.cache_resource
def load_model(model_name):
    if model_name == "none":
        return CatBoostRegressor().load_model('model-424-2000.cbm')

#碳转化率预测界面
st.subheader("二氧化碳甲烷化反应的二氧化碳转化率预测",divider="green")
model = load_model("none")
#参数输入
with st.form("user_input"):
    st.subheader("输入参数",divider="gray")
    col1,col2,col3 = st.columns(3)
    with col1:
        AM = st.selectbox("活性金属类型(AM)"
                          , ("Co", "Fe", "Metal-free", "Ni", "Pd", "Rh", "Ru")
                          , accept_new_options=True)
        Pr = st.selectbox("助催化剂类型(Pr)"
                          , ("Ba", "Ca", "Ce", "Co", "Cs", "Cu", "Eu", "Fe", "Gd", "K", "La", "Li", "Mg", "Mn", "Na", "Nd", "Pr", "Promoter-free", 
                             "Ru", "Sm", "Sr", "V", "W", "Y", "Yb", "Zr")
                          , accept_new_options=True)
        Sp = st.selectbox("载体1类型(Sp)"
                          , ("Al2O3", "CB", "CeO2", "CM", "Cr2O3", "Fe2O3", "Gd2O3", "MgO", "Mn3O4", "SBP", "SiO2", "TiO2", "Y2O3", "Zeolite", "ZnO", "ZrO2")
                          , accept_new_options=True)
        Sp2 = st.selectbox("载体2类型(Sp2)"
                          , ("Al2O3", "BaO", "CaO", "CeO2", "Cr2O3", "Gd2O3", "K2O", "MgO", "Mn3O4", "SiO2", "SrO2", "Y2O3", "ZrO2", "Sp2-free")
                          , accept_new_options=True)
        PM = st.selectbox("制备方法(PM)"
                          , ("CP", "CSG", "IMP", "IWI", "MP", "PGP", "TH", "WI")
                          , accept_new_options=True)
        MCP = st.number_input("主载体比例(MSP, %)", min_value=50.00, max_value=100.00
                            , value=70.00, step=0.10)
    with col2:
        AMc = st.number_input("活性金属含量(AMc, %)", min_value=0.00, max_value=65.00
                            , value=30.00, step=0.10)
        Prc = st.number_input("助催化剂含量(Prc, %)", min_value=0.00, max_value=34.00
                            , value=15.00, step=0.10)
        CT = st.number_input("煅烧温度(CT, °C)", min_value=25.00, max_value=900.00
                            , value=450.00, step=0.10)
        Ct = st.number_input("煅烧时间(Ct, h)", min_value=0.00, max_value=24.00
                            , value=12.00, step=0.10)
        RT = st.number_input("还原温度(RT, °C)", min_value=25.00, max_value=800.00
                            , value=400.00, step=0.10)
        Rt = st.number_input("还原时间(Rt, h)", min_value=0.00, max_value=24.00
                            , value=12.00, step=0.10)
    with col3:
        RH = st.number_input("还原氢气百分比(RH, %)", min_value=0.00, max_value=100.00
                            , value=50.00, step=0.10)
        T = st.number_input("温度(T, °C)", min_value=20.00, max_value=800.00
                            , value=400.00, step=0.10)
        P = st.number_input("压力(P, bar)", min_value=1.00, max_value=40.00
                            , value=20.00, step=0.10)
        GHSV = st.number_input("气体时空速度(GHSV, L/gcath)", min_value=1.20, max_value=400.00
                            , value=200.00, step=0.10)
        Inert = st.number_input("进料中惰性气体百分比(Inert, %)", min_value=0.00, max_value=96.00
                            , value=50.00, step=0.10)
        HC = st.number_input("进料中H₂/CO₂百分比(H₂/CO₂, %)", min_value=1.00, max_value=50.00
                            , value=20.00, step=0.10)
#参数提交
    submitted = st.form_submit_button("提交预测", use_container_width=True)
if submitted and model:
    with st.spinner("预测中，请稍候......"):
        temp_feature = [(AM, AMc, Pr, Prc, Sp, Sp2, MCP, PM, CT, Ct, RT, Rt, RH, T, P, GHSV, Inert, HC)]
        data_frame = pd.DataFrame(temp_feature, columns=['AM', 'AMc', 'Pr', 'Prc', 'Sp', 'Sp2', 'MCP', 'PM', 'CT', 'Ct', 'RT', 'Rt', 'RH', 'T', 'P', 'GHSV', 'Inert', 'H2/CO2'])

#模型预测
    try:
        new_prediction = model.predict(data_frame)[0]
        st.success("预测完成！")
        st.subheader("预测结果", divider="green")
        st.metric(label="二氧化碳转化率", value=f"{new_prediction:.2f}%")
        #结果解读
    except Exception as e:
        st.error(f"预测失败：{str(e)}")

#数据批量上传
uploaded_file = st.file_uploader("上传包含批量数据的文件", type=["csv", "xlsx"])
if uploaded_file is not None:
    try:
        if uploaded_file.type == "text/csv":
            dataframe = pd.read_csv(uploaded_file)
        elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
            dataframe = pd.read_excel(uploaded_file)
        else:
            st.error("不支持该文件类型")
            st.stop
    except Exception as e:
        st.error(f"读取文件失败：{str(e)}")
        st.stop
    #模型预测
    try:
        predictions = model.predict(dataframe)
        dataframe['Rate'] = predictions
    except Exception as e:
        st.error(f"模型计算失败：{str(e)}")
        st.stop()
    #转换导出格式
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        dataframe.to_excel(writer, index=False, sheet_name='Sheet1')
    output.seek(0)
    st.download_button(label="下载预测结果"
                       , data=output
                       , file_name="预测结果.xlsx"
                       , mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

