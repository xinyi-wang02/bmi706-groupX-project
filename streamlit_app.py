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

    ## interpret cardiovascular related responses ##
    alc_car_bp_asp ['CDQ009A'] = alc_car_bp_asp ['CDQ009A'].replace({1: 'Pain in right arm', 77: 'Refused', 99: "Don't know"})
    alc_car_bp_asp ['CDQ009B'] = alc_car_bp_asp ['CDQ009B'].replace({2: 'Pain in right chest'})
    alc_car_bp_asp ['CDQ009C'] = alc_car_bp_asp ['CDQ009C'].replace({3: 'Pain in neck'})
    alc_car_bp_asp ['CDQ009D'] = alc_car_bp_asp ['CDQ009D'].replace({4: 'Pain in upper sternum'})
    alc_car_bp_asp ['CDQ009E'] = alc_car_bp_asp ['CDQ009E'].replace({5: 'Pain in lower sternum'})
    alc_car_bp_asp ['CDQ009F'] = alc_car_bp_asp ['CDQ009F'].replace({6: 'Pain in left chest'})
    alc_car_bp_asp ['CDQ009G'] = alc_car_bp_asp ['CDQ009G'].replace({7: 'Pain in left arm'})
    alc_car_bp_asp ['CDQ009H'] = alc_car_bp_asp ['CDQ009H'].replace({8: 'Pain in epigastric area'})

    alc_car_bp_asp['secondary_symptom'] = alc_car_bp_asp['CDQ009A'].fillna(alc_car_bp_asp['CDQ009B']).fillna(alc_car_bp_asp['CDQ009C']).fillna(alc_car_bp_asp['CDQ009D']).fillna(alc_car_bp_asp['CDQ009E']).fillna(alc_car_bp_asp['CDQ009F']).fillna(alc_car_bp_asp['CDQ009G']).fillna(alc_car_bp_asp['CDQ009H'])
    alc_car_bp_asp = alc_car_bp_asp.drop(columns=['CDQ009A', 'CDQ009B', 'CDQ009C', 'CDQ009D', 'CDQ009E', 'CDQ009F', 'CDQ009G', 'CDQ009H'])

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
st.write("## Exploring the associations between alcohol use, asprin use and cardiovascular symptoms with NHANES dataset (2017-2020)")

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

## Linked view of alcohol consumption population bar chart and heatmap ##
# Prepare data for the bar chart
agg_data1 = df['alc_Frequency'].value_counts().reset_index()
agg_data1.columns = ['Frequency', 'Count']
alc_cons = st.multiselect("Select Alcohol Consumptions", 
                          options=agg_data1['Frequency'].unique(), 
                          default=agg_data1['Frequency'].unique())
subset = agg_data1[agg_data1['Frequency'].isin(alc_cons)]

# Prepare data for the heatmap
agg_data2 = df[['alc_Frequency', 'CDQ001']].groupby(['alc_Frequency', 'CDQ001']).size().reset_index(name='Count')
subset2 = agg_data2[agg_data2['alc_Frequency'].isin(alc_cons)]

## Boxplot (Alcohol Frequency) ##
alc_chart = alt.Chart(subset).mark_bar().encode(
    x=alt.X(
        'Frequency:O', 
        title='Selected Alcohol Consumption Frequency',
        sort=list(category_mapping.values()),
        axis=alt.Axis(labels=False)
    ),
    y=alt.Y(
        'Count:Q', 
        title='Number of Participants'
    ),
    color=alt.Color(
        'Frequency:O',
        sort=list(category_mapping.values()),
        scale=alt.Scale(scheme='tableau20'),
        legend=alt.Legend(title="Alcohol Consumption")
    ),
    tooltip=['Frequency', 'Count']
).properties(
    title='Distribution of Alcohol Consumption Frequency Among Participants',
    width=300,
    height=600
)

## Heatmap (Alcohol Frequency vs Chest Pain) ##
heatmap = alt.Chart(subset2).mark_rect().encode(
    x=alt.X('alc_Frequency:O', title='Selected Alcohol Consumption Frequency', sort=list(category_mapping.values())),
    y=alt.Y('CDQ001:O', title='Chest Pain'),
    color=alt.Color('Count:Q', title='Count', scale=alt.Scale(scheme='blues')),
    tooltip=['alc_Frequency', 'CDQ001', 'Count']
).properties(
    title=f'Heatmap of relationships between Selected Alcohol Frequency and Chest Pain',
    width=600,
    height=300
)

## Pie Chart (Cardiovascular symptoms) ##
columns_to_analyze3 = ['CDQ001','CDQ006','secondary_symptom']
df3 = df[columns_to_analyze3]
pain_df = df3[df3['secondary_symptom'].notna()]

agg_data3 = pain_df['secondary_symptom'].value_counts().reset_index()
agg_data3.columns = ['secondary_symptom', 'Count']

pain_chart = alt.Chart(agg_data3).mark_arc().encode(
    theta=alt.Theta(field='Count', type='quantitative', title='Count'),
    color=alt.Color(field='secondary_symptom', type='nominal', legend=alt.Legend(title="Cardiovascular Symptom")),
    tooltip=['secondary_symptom', 'Count']
).properties(
    title='Distribution of Different Cardiovascular Related Symptoms Among Participants',
    width=600,
    height=400
).interactive()

## Bubble plot for asprin use vs chest pain chances ##
columns_to_analyze4 = ['RXQ515','CDQ001']
df4 = df[columns_to_analyze4].groupby(['CDQ001', 'RXQ515']).size().reset_index(name='count')

bubble = alt.Chart(df4).mark_circle().encode(
    x=alt.X('CDQ001:O', title='Whether have chest pain'),
    y=alt.Y('RXQ515:O', title='Whether Use Asprin'),
    size=alt.Size('count:Q', scale=alt.Scale(range=[10, 100])),
    color=alt.Color('count:Q', title='Number of Participants', scale=alt.Scale(scheme='plasma')),
    tooltip=['CDQ001', 'RXQ515', 'count']
).properties(
    title='Relationship Between Aspirin Use and Chest Pain Prevalence Among Participants',
    width=300,
    height=300
).configure_view(
    #strokeWidth=0,  
    fill='white'
).interactive()


st.altair_chart(alc_chart, use_container_width=True)
st.altair_chart(heatmap, use_container_width=True)
st.altair_chart(pain_chart, use_container_width=True)
st.altair_chart(bubble, use_container_width=True)
