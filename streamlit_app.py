# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
import snowflake.connector

cnx = snowflake.connector.connect(
    user=st.secrets["snowflake"]["user"],
    password=st.secrets["snowflake"]["password"],
    account=st.secrets["snowflake"]["account"],
    warehouse=st.secrets["snowflake"]["warehouse"],
    database=st.secrets["snowflake"]["database"],
    schema=st.secrets["snowflake"]["schema"]
)

session = cnx.cursor()


# Write directly to the app
st.title("🥤 Customize Your Smoothie! 🥤")
name_on_order = st.text_input('Name on Smoothie:')
st.write('The name on your Smoothie will be:', name_on_order)

st.write("Choose the fruits you want in your custom Smoothie!")

# Read fruit options table
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))

ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    my_dataframe,
    max_selections=5
)

ingredients_string = ''

if ingredients_list:
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '

    st.write(ingredients_string)

my_insert_stmt = """ insert into smoothies.public.orders
(ingredients, name_on_order)
values ('""" + ingredients_string + """','""" + name_on_order + """')"""

# st.write(my_insert_stmt)   # optional for debugging

time_to_insert = st.button('Submit Order')

if time_to_insert:
    session.sql(my_insert_stmt).collect()
    st.success('Your Smoothie is ordered, ' + name_on_order + '!', icon='✅')


