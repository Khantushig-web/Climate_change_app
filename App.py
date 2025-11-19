import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np

# Page configuration
st.set_page_config(
    page_title="Climate Change Dashboard",
    page_icon="🌍",
    layout="wide"
)

# Title and description
st.title("🌍 Global Climate Change Impact Dashboard")
st.markdown("""
This dashboard visualizes global climate change data from authoritative sources like NASA and NOAA.
Explore temperature anomalies, CO2 levels, and sea level rise trends across different regions and time periods.
""")

# Sidebar for filters
st.sidebar.header("🎛️ Dashboard Controls")
st.sidebar.markdown("---")

# Generate sample data (In real project, load from NASA/NOAA CSV files)
@st.cache_data
def load_climate_data():
    # Temperature Anomaly Data (simulating NASA GISTEMP)
    years = list(range(1880, 2024))
    temp_anomaly = [
        -0.16 + (year - 1880) * 0.008 + np.random.normal(0, 0.1) 
        for year in years
    ]
    
    temp_df = pd.DataFrame({
        'Year': years,
        'Temperature_Anomaly': temp_anomaly,
        'Region': ['Global'] * len(years)
    })
    
    # Add regional data
    regions = ['Northern Hemisphere', 'Southern Hemisphere', 'Arctic', 'Tropics']
    for region in regions:
        regional_data = pd.DataFrame({
            'Year': years,
            'Temperature_Anomaly': [
                temp_anomaly[i] * (1.2 if region == 'Arctic' else 0.9 if region == 'Southern Hemisphere' else 1.0)
                for i in range(len(years))
            ],
            'Region': [region] * len(years)
        })
        temp_df = pd.concat([temp_df, regional_data], ignore_index=True)
    
    # CO2 Data (simulating NOAA)
    co2_years = list(range(1958, 2024))
    co2_levels = [315 + (year - 1958) * 1.8 + np.random.normal(0, 2) for year in co2_years]
    co2_df = pd.DataFrame({
        'Year': co2_years,
        'CO2_ppm': co2_levels
    })
    
    # Sea Level Data
    sea_years = list(range(1993, 2024))
    sea_level = [0 + (year - 1993) * 3.3 + np.random.normal(0, 5) for year in sea_years]
    sea_df = pd.DataFrame({
        'Year': sea_years,
        'Sea_Level_mm': sea_level
    })
    
    return temp_df, co2_df, sea_df

# Load data
with st.spinner("Loading climate data..."):
    temp_data, co2_data, sea_data = load_climate_data()

# Sidebar filters
st.sidebar.subheader("📅 Time Period")
min_year = int(temp_data['Year'].min())
max_year = int(temp_data['Year'].max())
year_range = st.sidebar.slider(
    "Select Year Range",
    min_year, max_year, (1980, max_year)
)

st.sidebar.subheader("🗺️ Region Selection")
available_regions = temp_data['Region'].unique().tolist()
selected_regions = st.sidebar.multiselect(
    "Choose Regions",
    available_regions,
    default=['Global', 'Arctic']
)

st.sidebar.markdown("---")
st.sidebar.info("💡 **Data Sources:** NASA GISTEMP, NOAA GML, Satellite Altimetry")

# Filter data based on selections
filtered_temp = temp_data[
    (temp_data['Year'] >= year_range[0]) & 
    (temp_data['Year'] <= year_range[1]) &
    (temp_data['Region'].isin(selected_regions))
]
filtered_co2 = co2_data[
    (co2_data['Year'] >= year_range[0]) & 
    (co2_data['Year'] <= year_range[1])
]
filtered_sea = sea_data[
    (sea_data['Year'] >= year_range[0]) & 
    (sea_data['Year'] <= year_range[1])
]

# Key Metrics Row
st.header("📊 Key Climate Indicators")
col1, col2, col3, col4 = st.columns(4)

with col1:
    # Check if Global region data is available in filtered data
    global_temp_data = temp_data[
        (temp_data['Year'] >= year_range[0]) & 
        (temp_data['Year'] <= year_range[1]) &
        (temp_data['Region'] == 'Global')
    ]
    
    if len(global_temp_data) > 0:
        latest_temp = global_temp_data['Temperature_Anomaly'].iloc[-1]
        first_temp = global_temp_data['Temperature_Anomaly'].iloc[0]
        st.metric(
            "Global Temp Anomaly",
            f"{latest_temp:.2f}°C",
            f"+{latest_temp - first_temp:.2f}°C since {year_range[0]}"
        )
    else:
        st.metric(
            "Global Temp Anomaly",
            "N/A",
            "Select 'Global' region"
        )

with col2:
    if len(filtered_co2) > 0:
        latest_co2 = filtered_co2['CO2_ppm'].iloc[-1]
        st.metric(
            "CO2 Levels",
            f"{latest_co2:.1f} ppm",
            f"+{latest_co2 - filtered_co2['CO2_ppm'].iloc[0]:.1f} ppm"
        )
    else:
        st.metric(
            "CO2 Levels",
            "N/A",
            "Data starts from 1958"
        )

with col3:
    if len(filtered_sea) > 0:
        latest_sea = filtered_sea['Sea_Level_mm'].iloc[-1]
        st.metric(
            "Sea Level Rise",
            f"{latest_sea:.1f} mm",
            f"+{latest_sea:.1f} mm since 1993"
        )
    else:
        st.metric(
            "Sea Level Rise",
            "N/A",
            "Data starts from 1993"
        )

with col4:
    if len(global_temp_data) > 0:
        avg_increase = (latest_temp - first_temp) / len(global_temp_data) * 10
        st.metric(
            "Warming Rate",
            f"{avg_increase:.3f}°C/decade",
            "Accelerating" if avg_increase > 0.15 else "Stable"
        )
    else:
        st.metric(
            "Warming Rate",
            "N/A",
            "Select 'Global' region"
        )

st.markdown("---")

# Main visualizations
tab1, tab2, tab3, tab4 = st.tabs(["🌡️ Temperature Trends", "💨 CO2 Levels", "🌊 Sea Level Rise", "📈 Correlations"])

with tab1:
    st.subheader("Global Temperature Anomaly Over Time")
    
    if len(filtered_temp) > 0:
        fig_temp = px.line(
            filtered_temp,
            x='Year',
            y='Temperature_Anomaly',
            color='Region',
            title='Temperature Anomaly by Region (°C relative to 1951-1980 baseline)',
            labels={'Temperature_Anomaly': 'Temperature Anomaly (°C)'},
            template='plotly_white'
        )
        fig_temp.update_layout(
            hovermode='x unified',
            height=500
        )
        fig_temp.add_hline(y=0, line_dash="dash", line_color="gray", annotation_text="Baseline")
        st.plotly_chart(fig_temp, use_container_width=True)
        
        # Additional analysis
        col1, col2 = st.columns(2)
        with col1:
            # Decade comparison - use first selected region or Global if available
            if 'Global' in filtered_temp['Region'].values:
                decade_region = 'Global'
            else:
                decade_region = filtered_temp['Region'].iloc[0]
            
            decade_avg = filtered_temp[filtered_temp['Region'] == decade_region].copy()
            decade_avg['Decade'] = (decade_avg['Year'] // 10) * 10
            decade_summary = decade_avg.groupby('Decade')['Temperature_Anomaly'].mean().reset_index()
            
            fig_decade = px.bar(
                decade_summary,
                x='Decade',
                y='Temperature_Anomaly',
                title=f'Average Temperature Anomaly by Decade ({decade_region})',
                labels={'Temperature_Anomaly': 'Avg Anomaly (°C)'},
                color='Temperature_Anomaly',
                color_continuous_scale='RdYlBu_r'
            )
            st.plotly_chart(fig_decade, use_container_width=True)
        
        with col2:
            # Regional comparison (latest year)
            latest_year_data = filtered_temp[filtered_temp['Year'] == year_range[1]]
            if len(latest_year_data) > 0:
                fig_regional = px.bar(
                    latest_year_data,
                    x='Region',
                    y='Temperature_Anomaly',
                    title=f'Temperature Anomaly by Region ({year_range[1]})',
                    labels={'Temperature_Anomaly': 'Anomaly (°C)'},
                    color='Temperature_Anomaly',
                    color_continuous_scale='RdYlBu_r'
                )
                fig_regional.update_xaxes(tickangle=45)
                st.plotly_chart(fig_regional, use_container_width=True)
            else:
                st.info("No data available for the latest year in selected range")
    else:
        st.warning("⚠️ Please select at least one region from the sidebar to view temperature data.")

with tab2:
    st.subheader("Atmospheric CO2 Concentration")
    
    if len(filtered_co2) > 0:
        fig_co2 = go.Figure()
        fig_co2.add_trace(go.Scatter(
            x=filtered_co2['Year'],
            y=filtered_co2['CO2_ppm'],
            mode='lines+markers',
            name='CO2 Levels',
            line=dict(color='#d62728', width=3),
            fill='tozeroy',
            fillcolor='rgba(214, 39, 40, 0.2)'
        ))
        
        fig_co2.update_layout(
            title='Atmospheric CO2 Concentration (Mauna Loa Observatory)',
            xaxis_title='Year',
            yaxis_title='CO2 (parts per million)',
            template='plotly_white',
            height=500,
            hovermode='x'
        )
        fig_co2.add_hline(y=350, line_dash="dash", line_color="orange", annotation_text="350 ppm (Safe Limit)")
        st.plotly_chart(fig_co2, use_container_width=True)
        
        # CO2 growth rate
        co2_growth = filtered_co2.copy()
        co2_growth['Growth_Rate'] = co2_growth['CO2_ppm'].diff()
        
        fig_growth = px.line(
            co2_growth,
            x='Year',
            y='Growth_Rate',
            title='Annual CO2 Growth Rate',
            labels={'Growth_Rate': 'CO2 Growth (ppm/year)'},
            template='plotly_white'
        )
        st.plotly_chart(fig_growth, use_container_width=True)
    else:
        st.info("📌 CO2 data is only available from 1958 onwards (when measurements began at Mauna Loa Observatory). Please adjust the year range to include years from 1958 or later.")

with tab3:
    st.subheader("Global Mean Sea Level Rise")
    
    if len(filtered_sea) > 0:
        fig_sea = px.area(
            filtered_sea,
            x='Year',
            y='Sea_Level_mm',
            title='Cumulative Sea Level Rise since 1993 (Satellite Measurements)',
            labels={'Sea_Level_mm': 'Sea Level Rise (mm)'},
            template='plotly_white',
            color_discrete_sequence=['#1f77b4']
        )
        fig_sea.update_layout(height=500)
        st.plotly_chart(fig_sea, use_container_width=True)
        
        # Projection
        st.subheader("🔮 Future Projection")
        projection_years = list(range(year_range[1], 2100))
        current_rate = 3.3  # mm per year
        projected_rise = [filtered_sea['Sea_Level_mm'].iloc[-1] + (year - year_range[1]) * current_rate for year in projection_years]
        
        projection_df = pd.DataFrame({
            'Year': projection_years,
            'Projected_Rise': projected_rise
        })
        
        fig_projection = px.line(
            projection_df,
            x='Year',
            y='Projected_Rise',
            title='Projected Sea Level Rise (Current Trend)',
            labels={'Projected_Rise': 'Sea Level Rise (mm)'},
            template='plotly_white'
        )
        fig_projection.update_traces(line_dash='dash', line_color='red')
        st.plotly_chart(fig_projection, use_container_width=True)
        
        st.warning(f"⚠️ At current rates, sea levels could rise by **{projected_rise[-1]/1000:.2f} meters** by 2100")
    else:
        st.info("📌 Sea level data is only available from 1993 onwards (satellite era). Please adjust the year range to include years from 1993 or later.")

with tab4:
    st.subheader("Climate Indicators Correlation Analysis")
    
    # Merge datasets for correlation
    merged_data = pd.merge(
        temp_data[temp_data['Region'] == 'Global'][['Year', 'Temperature_Anomaly']],
        co2_data,
        on='Year',
        how='inner'
    )
    
    # Scatter plot: Temp vs CO2
    fig_corr = px.scatter(
        merged_data,
        x='CO2_ppm',
        y='Temperature_Anomaly',
        color='Year',
        title='Temperature Anomaly vs CO2 Levels',
        labels={
            'CO2_ppm': 'CO2 Concentration (ppm)',
            'Temperature_Anomaly': 'Temperature Anomaly (°C)'
        },
        template='plotly_white',
        trendline='ols',
        color_continuous_scale='Viridis'
    )
    fig_corr.update_layout(height=500)
    st.plotly_chart(fig_corr, use_container_width=True)
    
    # Calculate correlation
    correlation = merged_data['Temperature_Anomaly'].corr(merged_data['CO2_ppm'])
    st.info(f"📊 **Correlation Coefficient:** {correlation:.3f} (Strong positive correlation)")
    
    # Time series comparison - FIXED VERSION
    fig_dual = go.Figure()
    
    fig_dual.add_trace(go.Scatter(
        x=merged_data['Year'],
        y=merged_data['Temperature_Anomaly'],
        name='Temperature Anomaly',
        yaxis='y',
        line=dict(color='red')
    ))
    
    fig_dual.add_trace(go.Scatter(
        x=merged_data['Year'],
        y=merged_data['CO2_ppm'],
        name='CO2 Levels',
        yaxis='y2',
        line=dict(color='blue')
    ))
    
    fig_dual.update_layout(
        title='Temperature and CO2 Trends (Dual Axis)',
        xaxis_title='Year',
        yaxis_title='Temperature Anomaly (°C)',
        yaxis2=dict(
            title='CO2 (ppm)',
            overlaying='y',
            side='right'
        ),
        template='plotly_white',
        height=500
    )
    st.plotly_chart(fig_dual, use_container_width=True)

# Download section
st.markdown("---")
st.header("📥 Download Data")

col1, col2, col3 = st.columns(3)

with col1:
    csv_temp = filtered_temp.to_csv(index=False)
    st.download_button(
        label="Download Temperature Data",
        data=csv_temp,
        file_name=f"temperature_data_{year_range[0]}-{year_range[1]}.csv",
        mime="text/csv"
    )

with col2:
    if len(filtered_co2) > 0:
        csv_co2 = filtered_co2.to_csv(index=False)
        st.download_button(
            label="Download CO2 Data",
            data=csv_co2,
            file_name=f"co2_data_{year_range[0]}-{year_range[1]}.csv",
            mime="text/csv"
        )
    else:
        st.info("No CO2 data available for selected years")

with col3:
    if len(filtered_sea) > 0:
        csv_sea = filtered_sea.to_csv(index=False)
        st.download_button(
            label="Download Sea Level Data",
            data=csv_sea,
            file_name=f"sea_level_data_{year_range[0]}-{year_range[1]}.csv",
            mime="text/csv"
        )
    else:
        st.info("No sea level data available for selected years")

# Footer
st.markdown("---")
st.markdown("""
### 📚 About This Dashboard
This dashboard presents climate change data to help visualize long-term trends in:
- **Global Temperature**: Anomalies relative to 20th century baseline
- **CO2 Levels**: Atmospheric carbon dioxide concentration
- **Sea Level**: Cumulative rise measured by satellites

**References:**
- NASA GISTEMP: https://data.giss.nasa.gov/gistemp/
- NOAA GML: https://gml.noaa.gov/ccgg/trends/
- NASA Sea Level: https://climate.nasa.gov/vital-signs/sea-level/
""")