import pandas as pd
import plotly.express as px
import streamlit as st
from PIL import Image
import plotly.graph_objects as go
from sklearn.ensemble import RandomForestRegressor
import matplotlib.pyplot as plt
import shap

# --- config ---
st.set_page_config(page_title="AgriNurture",
                   page_icon=":seedling:",
                   layout="wide"
                   )
df = pd.read_csv('Final_project_df.csv', encoding="utf-8")
df.columns = df.columns.str.replace(' ', '_')

# --- sidebar ---
st.sidebar.header("Select Input Parameters:")
crop = st.sidebar.selectbox(
    "Select the your Crop:",
    options=df["Crop"].unique()
)
location = st.sidebar.selectbox(
    "Select Location:",
    options=df["Location"].unique(),
)


def user_input_features():
    K = st.sidebar.slider('K [Potassium]', float(df.K.min()), float(df.K.max()), float(df.K.mean()))
    P = st.sidebar.slider('P [phosphorus]', float(df.P.min()), float(df.P.max()), float(df.P.mean()))
    N = st.sidebar.slider('N [nitrogen]', float(df.P.min()), float(df.P.max()), float(df.P.mean()))
    avg_Humidity = st.sidebar.slider('Average Humidity', float(df.avg_Humidity.min()), float(df.avg_Humidity.max()),
                                     float(df.avg_Humidity.mean()))
    avg_Rainfall = st.sidebar.slider('Average Rainfall', float(df.avg_Rainfall.min()), float(df.avg_Rainfall.max()),
                                     float(df.avg_Rainfall.mean()))
    avg_Temperature = st.sidebar.slider('Average Temperature', float(df.avg_Temperature.min()),
                                        float(df.avg_Temperature.max()),
                                        float(df.avg_Temperature.mean()))
    data = {'K': K,
            'P': P,
            'N': N,
            'avg_Humidity': avg_Humidity,
            'avg_Rainfall': avg_Rainfall,
            'avg_Temperature': avg_Temperature}
    features = pd.DataFrame(data, index=[0])
    return features


df_for_prediction = user_input_features()

# --- dataframe ---
df_selection_crop = df.query(
    "`Crop` == @crop and `Location` == @location"
)

df_selection_location = df.query(
    "`Location` == @location "
)

df_cp = df_selection_crop.copy()
df_cp.drop(['Year', 'Crop', 'Location', 'Unit'], axis=1, inplace=True)  # dataframe for prediction

# Set X and y
y = df_cp['Amount']
X = df_cp.drop('Amount', axis=1)

# Correlation Heat map
fig_Correlation = go.Figure()
fig_Correlation.add_traces(go.Heatmap(
    z=df_cp.corr(),
    x=df_cp.columns,
    y=df_cp.columns,
))
title_Correlation = "Crop Correlation Heatmap " + crop + " in " + location
fig_Correlation.update_layout({
    'title': title_Correlation
})
# bar chart  x=countries,y= Amount mean
countries = df.groupby(by='Location')
countries_mean = countries.mean()
fig_bar = go.Figure()
fig_bar.add_trace(go.Bar(x=countries_mean.index, y=countries_mean.Amount, marker_color='lightsalmon'))
fig_bar.update_layout(
    title='Amount By Country',
    yaxis_title='Amount of crops [hg/ha]')

# crop by item [Bar Chart]
crop_by_item = df_selection_location.groupby(by=["Crop"]).sum()[["Amount"]].sort_values(by="Amount")
title_bar_Country = 'Amount By Country'
fig_crop_country = px.bar(
    crop_by_item,
    x="Amount",
    y=crop_by_item.index,
    orientation="h",
    title="<b>Amount by Crops of " + location + "<b>",
    template="plotly_dark",
)
# Amount by year [Bar Chart]
Amount_by_year = df_selection_crop.groupby(by=["Year"]).sum()[["Amount"]].sort_values(by="Amount")
fig_yearly_Amounts = px.bar(
    Amount_by_year,
    x=Amount_by_year.index,
    y="Amount",
    title="<b>Amount by Year of " + crop + " in " + location + "<b>",
    template="plotly_dark",
)

# Box Plot of Amount
fig_boxplot = go.Figure()
fig_boxplot.add_trace(go.Box(name='Amount', y=df_selection_crop.Amount, boxmean=True))
title_boxplot = "Outliers of " + crop + " in " + location
fig_boxplot.update_layout({
    'title': title_boxplot
})

# ---------------------------------------------------------------------------------------------------------------------------------------------------------

# --- main ---
st.set_option('deprecation.showPyplotGlobalUse', False)
st.title(":seedling: AgriNurture")
st.markdown("##")
st.write("""This app predicts crop yields by countries and crop""")
st.write('---')
st.header('Total crops each country has yields')
st.plotly_chart(fig_bar, use_container_width=True)
image_crop = Image.open('pic/' + crop + '.png')
col1, col2, col3 = st.columns([0.2, 5, 0.2])
col2.image(image_crop, use_column_width=True)
# st.image(image_crop)
st.write('---')
left_col, right_col = st.columns(2)
with left_col:
    st.plotly_chart(fig_crop_country, use_container_width=True)
    st.plotly_chart(fig_Correlation, use_container_width=True)

with right_col:
    st.plotly_chart(fig_yearly_Amounts, use_container_width=True)
    st.plotly_chart(fig_boxplot, use_container_width=True)

st.write('---')
title_dataframe = "Dataframe based on " + crop + " in " + location + " for prediction"
st.header(title_dataframe)
st.dataframe(df_selection_crop)
st.write('---')
# Build Regression Model
model = RandomForestRegressor()
model.fit(X, y)
# Apply Model to Make Prediction
prediction = model.predict(df_for_prediction)
st.header('Prediction of Amount')
st.write("""Prediction: """, prediction)

# Explaining the model's predictions using SHAP values
# https://github.com/slundberg/shap
explainer = shap.TreeExplainer(model)
shap_values = explainer.shap_values(X)

st.header('Feature Importance')
plt.title('Feature importance based on SHAP values')
shap.summary_plot(shap_values, X)
st.pyplot(bbox_inches='tight')
st.write('---')

plt.title('Feature importance based on SHAP values (Bar)')
shap.summary_plot(shap_values, X, plot_type="bar")
st.pyplot(bbox_inches='tight')

# HIDE STREAMLIT STYLE
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)
