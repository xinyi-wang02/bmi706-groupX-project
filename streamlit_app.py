import pyreadstat
import altair as alt
import pandas as pd
import streamlit as st

@st.cache
def load_data_preprocess():
    ## load data ##
    alcohol, alc_meta = pyreadstat.read_xport('P_ALQ.XPT')
    cardio, car_meta = pyreadstat.read_xport('P_CDQ.XPT')
    bp_chol, bp_meta = pyreadstat.read_xport('P_BPQ.XPT')
    asp, asp_meta = pyreadstat.read_xport('P_RXQASA.XPT')

    ## merge the data frames ##
    alc_car = pd.merge(alcohol, cardio, on='SEQN', how='inner')
    alc_car_bp = pd.merge(alc_car, bp_chol, on='SEQN', how='inner')
    alc_car_bp_asp = pd.merge(alc_car_bp, asp, on='SEQN', how='inner')

    ## interpret blood pressure related responses ##
    alc_car_bp_asp ['BPQ020'] = alc_car_bp_asp ['BPQ020'].replace({1:'With hypertension',2: 'Without hypertension', 7: 'Refused', 9: "Don't know"})
    alc_car_bp_asp ['BPQ040A'] = alc_car_bp_asp ['BPQ040A'].replace({1:'Take hypertension prescription',2: 'Do not take hypertension prescription', 7: 'Refused', 9: "Don't know"})
    alc_car_bp_asp ['BPQ080'] = alc_car_bp_asp ['BPQ080'].replace({1:'With high cholesterol',2: 'Without high cholesterol', 7: 'Refused', 9: "Don't know"})
    alc_car_bp_asp ['BPQ100D'] = alc_car_bp_asp ['BPQ100D'].replace({1:'Take prescriptn for cholesterol',2: 'Do not take prescriptn for cholesterol', 7: 'Refused', 9: "Don't know"})

    ## interpret asprin related responses ##
    alc_car_bp_asp ['RXQ510'] = alc_car_bp_asp ['RXQ510'].replace({1:'Yes', 2: 'No', 7: 'Refused', 9: "Don't know"})
    alc_car_bp_asp ['RXQ515'] = alc_car_bp_asp ['RXQ515'].replace({1:'Take Aspirin',2: 'Do not take aspirin', 3: 'Sometimes Take Aspirin',4: 'Stopped aspirin use due to side effects', 9: "Don't know"})
    alc_car_bp_asp ['RXQ520'] = alc_car_bp_asp ['RXQ520'].replace({1:'Yes',2: 'No', 7: 'Refused', 9: "Don't know"})

    ## interpret alcohol related responses ##
    category_mapping = {
    0: 'Never in the last year',
    1: 'Every day',
    2: 'Nearly every day',
    3: '3 to 4 times a week',
    4: '2 times a week',
    5: 'Once a week',
    6: '2 to 3 times a month',
    7: 'Once a month',
    8: '7 to 11 times in the last year',
    9: '3 to 6 times in the last year',
    10: '1 to 2 times in the last year',
    77: 'Refused',
    99: 'Don\'t know',
    None: 'Missing'}
    alc_car_bp_asp['alc_Frequency'] = alc_car_bp_asp['ALQ121'].map(category_mapping)
    alc_car_bp_asp ['CDQ001'] = alc_car_bp_asp ['CDQ001'].replace({1:'Yes', 2: 'No', 7: 'Refused', 9: "Don't know"})

    return alc_car_bp_asp

df = load_data_preprocess()
st.write("## Exploring relationships between alcohol use, cardiovascular disease, blood pressure, and asprin use with NHANES dataset")

alt.data_transformers.disable_max_rows()

## Frequency of Alcohol intake within a year ##
category_mapping = {
    0: 'Never in the last year',
    1: 'Every day',
    2: 'Nearly every day',
    3: '3 to 4 times a week',
    4: '2 times a week',
    5: 'Once a week',
    6: '2 to 3 times a month',
    7: 'Once a month',
    8: '7 to 11 times in the last year',
    9: '3 to 6 times in the last year',
    10: '1 to 2 times in the last year',
    77: 'Refused',
    99: 'Don\'t know',
    None: 'Missing'}

agg_data1 = df['alc_Frequency'].value_counts().reset_index()
agg_data1.columns = ['alc_Frequency', 'Count']

alc_chart = alt.Chart(agg_data1).mark_bar().encode(
    x=alt.X('alc_Frequency:N', title='Frequency of Alcohol intake', sort=list(category_mapping.values())),
    y=alt.Y('count():Q', title='Count'),
    tooltip=['alc_Frequency', 'count()']
).properties(
    title='Frequency of Alcohol intake within a year',
    width=600,
    height=400
).interactive()

## Count of Different Symptoms in Chest Pain ##
columns_to_analyze2 = ['CDQ001','CDQ006','secondary_symptom']
df1 = df[columns_to_analyze2]
pain_df = df1[df1['secondary_symptom'].notna()]

agg_data2 = pain_df['secondary_symptom'].value_counts().reset_index()
agg_data2.columns = ['secondary_symptom', 'Count']

pain_chart = alt.Chart(agg_data2).mark_arc().encode(
    theta=alt.Theta(field='Count', type='quantitative', title='Count'),
    color=alt.Color(field='secondary_symptom', type='nominal'),
    tooltip=['secondary_symptom', 'Count']
).properties(
    title='Count of Different Symptoms',
    width=400,
    height=200
).interactive()

st.altair_chart(alc_chart, use_container_width=True)
st.altair_chart(pain_chart, use_container_width=True)
