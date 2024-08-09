# Import python packages
import streamlit as st
import requests
from snowflake.snowpark.functions import col

# Write directly to the app
st.title(":cup_with_straw: Customize Your Smoothie!:cup_with_straw:")
st.write(
    """Choose the fruits you want in your custom smoothie!
    """
)
name = st.text_input('Name on Smoothie:', '')
st.write('The name on your smoothie will be:', name)

cnx = st.connection("snowflake")
session = cnx.session()
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'),col('SEARCH_ON'))
#st.dataframe(data=my_dataframe, use_container_width=True)
#st.stop()
pd_df=my_dataframe.to_pandas()
#st.dataframe(pd_df)
#st.stop()

ingredients_list = st.multiselect(
    'Choose upto 5 ingredients:'
    , my_dataframe
    , max_selections=5
)

if ingredients_list:

    ingredients_string = ''
    for x in ingredients_list:
        ingredients_string += x + ' '
        search_on=pd_df.loc[pd_df['FRUIT_NAME'] == x, 'SEARCH_ON'].iloc[0]
        st.write('The search value for ', x,' is ', search_on, '.')

        st.subheader(x + ' Nutrition Information')
        fruityvice_response = requests.get("https://fruityvice.com/api/fruit/" + x)
        fv_df = st.dataframe(data=fruityvice_response.json(), use_container_width=True)
    st.write(ingredients_string)

    my_insert_stmt = """ insert into smoothies.public.orders(ingredients, name_on_order)
            values ('""" + ingredients_string + """', '""" + name + """')"""

    time_to_insert = st.button('Submit Order')
    
    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success('Your Smoothie is ordered, ' + name + ' !', icon="✅")


