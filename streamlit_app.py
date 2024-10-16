import altair as alt
import pandas as pd
import streamlit as st

### P1.2 ###

@st.cache
def load_data():
    ## {{ CODE HERE }} ##
    cancer_df = pd.read_csv("https://raw.githubusercontent.com/hms-dbmi/bmi706-2022/main/cancer_data/cancer_ICD10.csv").melt( 
        id_vars=["Country", "Year", "Cancer", "Sex"],
        var_name="Age",
        value_name="Deaths",
    )

    pop_df = pd.read_csv("https://raw.githubusercontent.com/hms-dbmi/bmi706-2022/main/cancer_data/population.csv").melt(
        id_vars=["Country", "Year", "Sex"],
        var_name="Age",
        value_name="Pop",
    )

    df = pd.merge(left=cancer_df, right=pop_df, how="left")
    df["Pop"] = df.groupby(["Country", "Sex", "Age"])["Pop"].fillna(method="bfill")
    df.dropna(inplace=True)

    df = df.groupby(["Country", "Year", "Cancer", "Age", "Sex"]).sum().reset_index()
    df["Rate"] = df["Deaths"] / df["Pop"] * 100_000

    return df


# Uncomment the next line when finished
df = load_data()

### P1.2 ###
st.write("## Age-specific cancer mortality rates")

### P2.1 ###
# replace with st.slider
min_year = df['Year'].min()
max_year = df['Year'].max()
year = st.slider("Select a Year", min_value=min_year, max_value=max_year, step=1)
subset = df[df["Year"] == year]
### P2.1 ###


### P2.2 ###
# replace with st.radio
sex = st.radio("Select Sex", options=df['Sex'].unique())
subset = subset[subset["Sex"] == sex]
### P2.2 ###


### P2.3 ###
# replace with st.multiselect
# (hint: can use current hard-coded values below as as `default` for selector)
countries = [
    "Austria",
    "Germany",
    "Iceland",
    "Spain",
    "Sweden",
    "Thailand",
    "Turkey",
]
selected_countries = st.multiselect(
    "Select Countries",
    options=df['Country'].unique(),
    default=countries
)
subset = subset[subset["Country"].isin(selected_countries)]
### P2.3 ###


### P2.4 ###
# replace with st.selectbox
cancer = st.selectbox(
    "Select Cancer Type",
    options=df['Cancer'].unique(),
    index=0
)
subset = subset[subset["Cancer"] == cancer]
### P2.4 ###


### P2.5 ###
ages = [
    "Age <5",
    "Age 5-14",
    "Age 15-24",
    "Age 25-34",
    "Age 35-44",
    "Age 45-54",
    "Age 55-64",
    "Age >64",
]

chart = alt.Chart(subset).mark_rect().encode(
    x=alt.X("Age", sort=ages),
    y=alt.Y('Country:N', title='Country'),
    color=alt.Color('Rate:Q', title='Mortality rate per 100k',
        scale=alt.Scale(type='log', domain=[0.01, 1000], clamp=True),  
        legend=alt.Legend(title="Mortality rate per 100k")
    ),
    tooltip=["Rate"],
).properties(
    title=f"{cancer} mortality rates for {'males' if sex == 'M' else 'females'} in {year}",
)

pop_chart = alt.Chart(subset).mark_bar().encode(
    y=alt.Y('Country:N', sort='-x'), 
    x=alt.X('Pop:Q', title='Sum of population size'),
    tooltip=[alt.Tooltip('Country'), alt.Tooltip('Pop:Q')]
).properties(
    title='Population Size by Country'
)
### P2.5 ###

st.altair_chart(chart, use_container_width=True)
st.altair_chart(pop_chart, use_container_width=True)

countries_in_subset = subset["Country"].unique()
if len(countries_in_subset) != len(countries):
    if len(countries_in_subset) == 0:
        st.write("No data avaiable for given subset.")
    else:
        missing = set(countries) - set(countries_in_subset)
        st.write("No data available for " + ", ".join(missing) + ".")
