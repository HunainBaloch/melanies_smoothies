# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests
import pandas as pd

# Write directly to the app
st.title(":cup_with_straw: Customize your Smoothie! :cup_with_straw:")
st.write(
    """Choose the fruits you want in your custom Smoothie!"""
)

name_on_order = st.text_input('Name on Smoothie:')
st.write('The name on your smoothie will be:', name_on_order)

# Connect to Snowflake and fetch data
cnx = st.connection("snowflake")
session = cnx.session()
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON'))

# Convert Snowflake DataFrame to Pandas DataFrame
pd_df = my_dataframe.to_pandas()

# Display the DataFrame for debugging
st.dataframe(pd_df)

# Multi-select widget for choosing ingredients
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    pd_df['FRUIT_NAME'].tolist(),  # Use list of fruit names for selection
    max_selections=5
)

if ingredients_list:
    ingredients_string = ''
    
    for fruit_chosen in ingredients_list:
        # Clean up fruit names for matching
        fruit_chosen_clean = fruit_chosen.strip().lower()
        
        # Get the search value for the selected fruit
        search_on = pd_df.loc[pd_df['FRUIT_NAME'].str.lower() == fruit_chosen_clean, 'SEARCH_ON']
        
        if not search_on.empty:
            search_on_value = search_on.iloc[0]
            st.write(f'The search value for {fruit_chosen} is {search_on_value}.')
        else:
            st.write(f'No search value found for {fruit_chosen}.')
            continue

        # Fetch and display nutritional information
        st.subheader(f'{fruit_chosen} Nutrition Information')
        fruityvice_response = requests.get(f"https://fruityvice.com/api/fruit/{search_on_value}")
        
        if fruityvice_response.status_code == 200:
            fv_data = fruityvice_response.json()
            fv_df = pd.DataFrame(fv_data)  # Convert response to DataFrame
            st.dataframe(fv_df, use_container_width=True)
        else:
            st.write(f'Error fetching data for {fruit_chosen}.')
        
        ingredients_string += fruit_chosen + ', '

    # Remove trailing comma and space
    ingredients_string = ingredients_string.rstrip(', ')
    
    # SQL insert statement
    my_insert_stmt = f"""
    INSERT INTO smoothies.public.orders (ingredients, name_on_order)
    VALUES ('{ingredients_string}', '{name_on_order}')
    """
    
    st.write(my_insert_stmt)

    # Button to submit the order
    time_to_insert = st.button('Submit Order')

    if time_to_insert:
        try:
            session.sql(my_insert_stmt).collect()
            st.success(f'Your Smoothie is ordered, {name_on_order}', icon="✅")
        except Exception as e:
            st.error(f'Error submitting order: {e}')
