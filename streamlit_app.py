# Import python packages
import streamlit as st
import requests
from snowflake.snowpark.functions import col
import snowflake.connector
import pandas as pd

cnx = snowflake.connector.connect(
    user=st.secrets["snowflake"]["user"],
    password=st.secrets["snowflake"]["password"],
    account=st.secrets["snowflake"]["account"],
    warehouse=st.secrets["snowflake"]["warehouse"],
    database=st.secrets["snowflake"]["database"],
    schema=st.secrets["snowflake"]["schema"]
)

session = cnx.cursor()
query = "SELECT FRUIT_NAME FROM SMOOTHIES.PUBLIC.FRUIT_OPTIONS"
my_dataframe = pd.read_sql(query, cnx)

# Write directly to the app
st.title("🥤 Customize Your Smoothie! 🥤")
name_on_order = st.text_input('Name on Smoothie:')
st.write('The name on your Smoothie will be:', name_on_order)

st.write("Choose the fruits you want in your custom Smoothie!")



ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    my_dataframe["FRUIT_NAME"].tolist(),
    max_selections=5
)

if ingredients_list:
    ingredients_string = ''

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '

        st.subheader(fruit_chosen + " Nutrition Information")

        smoothiefruit_response = requests.get(
            f"https://my.smoothiefroot.com/api/fruit/{fruit_chosen.lower()}"
        )

        st.dataframe(
            data=smoothiefruit_response.json(),
            use_container_width=True
        )

    st.write(ingredients_string)



my_insert_stmt = """ insert into smoothies.public.orders
(ingredients, name_on_order)
values ('""" + ingredients_string + """','""" + name_on_order + """')"""

# st.write(my_insert_stmt)   

time_to_insert = st.button('Submit Order')

if time_to_insert:
    session.execute(my_insert_stmt)
    cnx.commit()
    st.success('Your Smoothie is ordered, ' + name_on_order + '!', icon='✅')


smoothiefroot_response = requests.get(
    "https://my.smoothiefroot.com/api/fruit/watermelon"
)

st.dataframe(
    smoothiefroot_response.json(),
    use_container_width=True
)



