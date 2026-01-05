# -------------------- Imports --------------------
import streamlit as st
import snowflake.connector
import pandas as pd
import requests

# -------------------- Snowflake Connection --------------------
cnx = snowflake.connector.connect(
    user=st.secrets["snowflake"]["user"],
    password=st.secrets["snowflake"]["password"],
    account=st.secrets["snowflake"]["account"],
    warehouse=st.secrets["snowflake"]["warehouse"],
    database=st.secrets["snowflake"]["database"],
    schema=st.secrets["snowflake"]["schema"]
)

session = cnx.cursor()

# -------------------- Load Fruit Options --------------------
query = """
SELECT FRUIT_NAME, SEARCH_ON
FROM SMOOTHIES.PUBLIC.FRUIT_OPTIONS
"""
my_dataframe = pd.read_sql(query, cnx)

# ✅ FIX: create Pandas dataframe for loc()
pd_df = my_dataframe.copy()

# -------------------- App UI --------------------
st.title("🥤 Customize Your Smoothie! 🥤")

name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on your Smoothie will be:", name_on_order)

st.write("Choose the fruits you want in your custom Smoothie!")

ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    options=my_dataframe["FRUIT_NAME"].tolist(),
    max_selections=5
)

# -------------------- Ingredients & Nutrition --------------------
ingredients_string = ""

if ingredients_list:
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + " "

        # ✅ Look up SEARCH_ON value
        search_on = pd_df.loc[
            pd_df["FRUIT_NAME"] == fruit_chosen,
            "SEARCH_ON"
        ].iloc[0]

        st.subheader(f"{fruit_chosen} Nutrition Information")

        smoothiefruit_response = requests.get(
            f"https://my.smoothiefroot.com/api/fruit/{search_on.lower()}"
        )

        if smoothiefruit_response.status_code == 200:
            st.dataframe(
                smoothiefruit_response.json(),
                use_container_width=True
            )
        else:
            st.warning(f"Sorry, {fruit_chosen} is not in the SmoothieFroot database.")

    st.write("### Your Smoothie Ingredients:")
    st.write(ingredients_string)

# -------------------- Submit Order --------------------
time_to_insert = st.button("Submit Order")

if time_to_insert:
    if not name_on_order or not ingredients_string:
        st.error("Please enter your name and select at least one ingredient.")
    else:
        my_insert_stmt = f"""
            INSERT INTO smoothies.public.orders (ingredients, name_on_order)
            VALUES ('{ingredients_string}', '{name_on_order}')
        """
        session.execute(my_insert_stmt)
        cnx.commit()
        st.success(f"Your Smoothie is ordered, {name_on_order}! ✅")




