import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px

interest_data = pd.read_csv('iPhone_trends.csv')  # Replace with the actual path
region_data = pd.read_csv('iPhone_interest_by_region.csv')  # Replace with the actual path

st.title("Google Trends Dashboard")

# Add a sidebar with options to choose the product and country
st.sidebar.header('Select Options')
product = st.sidebar.selectbox('Select Product', options=['iPhone', 'Samsung', 'Google Pixel'])
country = st.sidebar.selectbox('Select Country', options=['US', 'DE', 'IN', 'GB'])

# Display a brief introduction
st.write(f"Showing data for **{product}** in **{country}**")

# Displaying interest over time plot
st.subheader(f"Interest Over Time for {product} in {country}")
fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(interest_data['date'], interest_data['iPhone'], marker='o', color='blue', label='Interest Over Time')
ax.set_title(f"Google Trends Interest for {product}")
ax.set_xlabel("Date")
ax.set_ylabel("Interest Level")
ax.legend()
ax.grid(True)
st.pyplot(fig)

# Calculate the percentage increase
interest_data["% Increase"] = interest_data["iPhone"].pct_change(periods=2) * 100  # Change over 2 days

# Display percentage increase plot
st.subheader(f"Percentage Increase in Search Interest for {product}")
fig2, ax2 = plt.subplots(figsize=(10, 6))
ax2.plot(interest_data['date'], interest_data['% Increase'], marker='o', color='red', label="Percentage Increase")
ax2.set_title(f"Percentage Increase in Google Trends for {product}")
ax2.set_xlabel("Date")
ax2.set_ylabel("Percentage Increase")
ax2.legend()
ax2.grid(True)
st.pyplot(fig2)

# Displaying interest by region plot
st.subheader(f"Interest by Region for {product} in {country}")
if 'geoName' in region_data.columns:
    region_data_sorted = region_data.sort_values(by="iPhone", ascending=False)
    fig3 = px.bar(region_data_sorted, x="geoName", y="iPhone", title=f"Interest by Region for {product}")
    st.plotly_chart(fig3)
else:
    st.write("⚠️ No region data available to plot.")

# Provide an option to download the data as CSV
st.sidebar.subheader('Download Data')
st.sidebar.markdown(f"Download the data for **{product}** in **{country}**:")
if st.sidebar.button('Download Interest Data'):
    interest_data.to_csv(f'{product}_{country}_interest_data.csv', index=False)
    st.sidebar.write(f"✅ Downloaded: {product}_{country}_interest_data.csv")

if st.sidebar.button('Download Region Data'):
    region_data.to_csv(f'{product}_{country}_region_data.csv', index=False)
    st.sidebar.write(f"✅ Downloaded: {product}_{country}_region_data.csv")

# short explanatory 
st.write("""
### Explanation:
This dashboard provides insights into the trends of a selected product in a specific country. 
- The **Interest Over Time** graph shows how the product's search interest has changed over the last three months.
- The **Percentage Increase** graph calculates the change in search interest over time.
- The **Interest by Region** map shows where the product is being searched most within the selected country.
""")

# Run the Streamlit app by saving this script as 'app.py' and then running `streamlit run app.py`
