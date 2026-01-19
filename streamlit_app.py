import streamlit as st
import requests
import pandas as pd
import snowflake.connector
from snowflake.snowpark import Session
from snowflake.snowpark.functions import col

conn = st.connection("snowflake")
session = conn.session()

st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write(requests.get("https://api.ipify.org").text)
st.write("Choose the fruits you want in your custom Smoothie!")

name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on your Smoothie will be:", name_on_order)


my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'),col('SEARCH_ON'))
# st.dataframe(data=my_dataframe, use_container_width=True)
# st.stop()

pd_df=my_dataframe.to_pandas()
# st.dataframe(pd_df)
# st.stop()

ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    my_dataframe,
    max_selections=5
)

if ingredients_list:
    ingredients_string = ""
    st.write(ingredients_list)
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '

        search_on=pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        st.write('The search value for ', fruit_chosen,' is ', search_on, '.')
        
        st.subheader(fruit_chosen + ' Nutrition Information')
        smoothiefroot_response = requests.get(f"https://my.smoothiefroot.com/api/fruit/{search_on}")
        sf_df = st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)
        
    time_to_insert = st.button("Submit Order")

    if time_to_insert:
        session.sql(
            """
            INSERT INTO smoothies.public.orders (ingredients, name_on_order)
            VALUES (?, ?)
            """,
            [ingredients_string, name_on_order]
        ).collect()

        st.success(f"Your Smoothie is ordered, {name_on_order}!", icon="✅")
