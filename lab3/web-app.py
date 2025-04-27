import pandas as pd
import streamlit as st
import datetime
import glob
import altair as alt

@st.cache_data
def load_data():
    current_time = datetime.datetime.now().strftime('%Y-%m-%d')
    file = glob.glob(f'cleaned_data_for_{current_time}_*.csv')
    return pd.read_csv(file[0])


df = load_data()

if 'selected_index' not in st.session_state:
    st.session_state.selected_index = 'VCI'
if 'selected_area' not in st.session_state:
    st.session_state.selected_area = df['region_name'].unique()[0]
if 'selected_week' not in st.session_state:
    st.session_state.selected_week = None  # None на старті
if 'selected_year' not in st.session_state:
    st.session_state.selected_year = None  # None на старті
if 'sort_option' not in st.session_state:
    st.session_state.sort_option = 'Don\'t sort'

with st.sidebar:
    st.title("Filters")

    if st.button("Drop Filters"):
        st.session_state.selected_area = df['region_name'].unique()[0]
        st.session_state.selected_index = 'VCI'
        st.session_state.selected_week = (int(df['Week'].min()), int(df['Week'].max()))
        st.session_state.selected_year = (int(df['Year'].min()), int(df['Year'].max()))
        sort_option = 'Don\'t sort'
        st.rerun()

    st.selectbox("Select the index", options=['VCI', 'TCI', 'VHI'],
                 key='selected_index')

    st.selectbox(
        "Select the region", options=list(df['region_name'].unique()),
        index=list(df['region_name'].unique()).index(st.session_state.selected_area),
        key="selected_area"
    )

    # Установка дефолтних значень тільки якщо немає в session_state
    if st.session_state.selected_week is None:
        st.session_state.selected_week = (int(df['Week'].min()), int(df['Week'].max()))

    if st.session_state.selected_year is None:
        st.session_state.selected_year = (int(df['Year'].min()), int(df['Year'].max()))

    st.slider(
        "Select the week range", int(df['Week'].min()), int(df['Week'].max()),
        value=st.session_state.selected_week,
        key='selected_week'
    )

    st.slider(
        "Select the year range", int(df['Year'].min()), int(df['Year'].max()),
        value=st.session_state.selected_year,
        key='selected_year'
    )

    st.sidebar.radio(
        "Sorting for index",
        options=['Don\'t sort', 'Ascending sort', 'Descending sort'],
        index=0, key='sort_option'
    )


index_option = st.session_state.selected_index
region_option = st.session_state.selected_area
week_range = st.session_state.selected_week
year_range = st.session_state.selected_year
sort_option = st.session_state.sort_option

filtered_df = df[
    (df['region_name'] == region_option) &
    (df['Week'].between(*week_range)) &
    (df['Year'].between(*year_range))
]


if sort_option == 'Ascending sort':
    filtered_df = filtered_df.sort_values(by=index_option, ascending=True).copy()
elif sort_option == 'Descending sort':
    filtered_df = filtered_df.sort_values(by=index_option, ascending=False).copy()


tab1, tab2, tab3 = st.tabs(["📄 Table", "📈 Plot", "📊 Comparison"])

with tab1:
    st.subheader("Filtered Data Table")
    st.dataframe(filtered_df)

with tab2:
    st.subheader(f"{index_option} over time for {region_option}")

    # Якщо НЕ сортується — додаємо колонку дати для графіка по часу
    if sort_option == 'Don\'t sort':
        filtered_df['date'] = pd.to_datetime(
            filtered_df['Year'].astype(str) + '-W' + filtered_df['Week'].astype(str) + '-1',
            format='%Y-W%W-%w'
        )
        st.line_chart(data=filtered_df.set_index('date')[index_option])
    else:
        # Якщо є сортування — будуємо по порядковому номеру
        filtered_df = filtered_df.reset_index(drop=True)
        filtered_df['row_number'] = filtered_df.index + 1
        st.line_chart(data=filtered_df.set_index('row_number')[index_option])

with tab3:
    st.subheader(f"Average {index_option} across all regions")

    # Фільтруємо по часу
    comparison_df = df[
        (df['Week'].between(*week_range)) &
        (df['Year'].between(*year_range))
    ]

    # Групуємо по регіонах
    grouped_df = comparison_df.groupby('region_name')[index_option].mean().reset_index()

    # Сортуємо відповідно до обраного порядку
    if sort_option == 'Ascending sort':
        grouped_df = grouped_df.sort_values(by=index_option, ascending=True)
    elif sort_option == 'Descending sort':
        grouped_df = grouped_df.sort_values(by=index_option, ascending=False)
    else:
        grouped_df = grouped_df.sort_values(by='region_name')

    # Додаємо колонку для підсвітки обраного регіону
    grouped_df['highlight'] = grouped_df['region_name'] == region_option

    # Побудова барчарту з підсвіткою
    bar_chart = alt.Chart(grouped_df).mark_bar().encode(
        x=alt.X('region_name:N', sort=grouped_df['region_name'].tolist(), title='Region'),
        y=alt.Y(f'{index_option}:Q', title=f'Mean value {index_option}'),
        color=alt.condition(
            alt.datum.highlight,
            alt.value('orange'),       # Колір для обраної області
            alt.value('steelblue')     # Колір для всіх інших
        ),
        tooltip=['region_name', index_option]
    ).properties(
        width=800,
        height=400,
        title=f"Mean value {index_option} for regions"
    )

    st.altair_chart(bar_chart, use_container_width=True)