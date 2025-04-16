# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests
import pandas as pd

# Write directly to the app
st.title(f"Customize Your Smoothie! :cup_with_straw:")
st.write(
  """Choose the friuts you want in your custom Smoothie!
  """
)

name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on your Smoothie will be:", name_on_order)

cnx = st.connection("snowflake")
session = cnx.session()

my_dataframe = session.table("smoothies.public.fruit_options").select(col("FRUIT_NAME"),col("SEARCH_ON")).collect()
# st.dataframe(data=my_dataframe, use_container_width=True)
ingridients_list = st.multiselect(
    'Choose up to 5 ingridients:',
    my_dataframe,
    max_selections=5
)

if ingridients_list:
    
    ingredients_string = ''

    for fruit_chosen in ingridients_list:
        ingredients_string += fruit_chosen + " "
        st.subheader(fruit_chosen + ' Nutrition Information')
        smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/" + fruit_chosen)
        pd_df = pd.dataframe(data=smoothiefroot_response.json(), use_container_width=True).to_pandas()

        search_on=pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        st.write('The search value for ', fruit_chosen,' is ', search_on, '.')
        
    st.write(ingredients_string)

    my_insert_stmt = """ insert into smoothies.public.orders(ingredients, name_on_order)
            values ('""" + ingredients_string + """','""" + name_on_order +"""')"""

    time_to_insert = st.button("Submit Order")
    
    # st.write(my_insert_stmt)
    # st.stop()
    
    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        
        st.success('Your Smoothie is ordered!', icon="✅")

    

