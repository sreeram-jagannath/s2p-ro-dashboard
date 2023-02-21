import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, JsCode
import math


st.set_page_config(layout="wide")


def get_random_cities_list():
    # Load random city data
    # to generate new random cities, run the notebook "select_cities.ipynb"
    random_cities = pd.read_csv("../data/random_cities.csv")
    random_cities_list = random_cities.filter(["city", "lat", "lng", "color"]).values.tolist()
    return random_cities, random_cities_list


def get_folium_map():

    # Create map
    m = folium.Map(location=[40, -95], zoom_start=5)

    # Add choropleth to the map
    folium.Choropleth(
        geo_data='../data/us-state-boundaries.geojson',
        line_opacity=0.8,
        fill_color="yellow",
        fill_opacity=0.1,
        highlight=True
    ).add_to(m)

    # plot all the cities
    if "optimal_dc_df" not in st.session_state:
        for city, lat, long, clr in random_cities_list:
            folium.CircleMarker(
                [lat, long], 
                radius=17,
                fill=True,
                fill_color=clr,
                color=False,
                fill_opacity=0.5,
                tooltip=city,
            ).add_to(m)
    
    else:
        opt_dc = st.session_state.get("optimal_dc_df")
        opt_dc["user_color"] = opt_dc["user_input_dc"].map(dc_colors)
        opt_dc2 = opt_dc.filter(["zone", "lat", "lng", "user_color"])


        for city, lat, long, clr in opt_dc2.values.tolist():
            folium.CircleMarker(
                [lat, long], 
                radius=15,
                fill=True,
                fill_color=clr,
                color=False,
                fill_opacity=0.5,
                tooltip=city,
            ).add_to(m)

    return m


def get_closest_dc(dc_lat_lng: dict, lat: float, lng: float):
    min_distance = 10e9
    closest_dc = ""
    for dc, (dc_lat, dc_lng) in dc_lat_lng.items():
        dist = math.dist([lat, lng], [dc_lat, dc_lng])
        if dist < min_distance:
            closest_dc = dc
            min_distance = dist

    return closest_dc
    ...

def get_optimal_dc(df):
    """function to return the optimal distribution center for each zone

    Args:
        df (pd.DataFrame): random city dataframe
    Returns:
        (pd.DataFrame)
    """

    closest_dc_list = []
    for _, row in df.iterrows():
        closest_dc = get_closest_dc(dc_lat_lng=dc_lat_lng, lat=row["lat"], lng=row["lng"])
        closest_dc_list.append(closest_dc)
        
    df["optimal_dc"] = closest_dc_list
    df["user_input_dc"] = closest_dc_list
    df["user_color"] = df["user_input_dc"].map(dc_colors)
    df["optimal_color"] = df["optimal_dc"].map(dc_colors)

    rename_cols = {
        "dc": "current_dc",
        "city": "zone",
    }
    df = df.rename(columns=rename_cols)
    st.session_state["optimal_dc_df"] = df

    return df


if __name__ == "__main__":

    st.title("S2P Route Optimization")

    dc_lat_lng = {
        "Fresno": (36.74773, -119.77237),
        "SLC": (40.76078, -111.89105),
        "Olathe": (38.8814, -94.81913),
        "Indy": (39.997263, -86.345830),
        "Hamburg": (40.5009, -75.9699),
        "Macon": (32.84069, -83.6324),
        "Charlotte": (35.22709, -80.84313),
    }

    dc_colors = {
        "Fresno": "red" ,
        "SLC": "blue",
        "Olathe": "green",
        "Indy": "purple",
        "Hamburg": "orange",
        "Macon": "pink",
        "Charlotte": "gray",
    }

    random_cities, random_cities_list = get_random_cities_list()

    us_map = get_folium_map()

    dc_capacity = pd.DataFrame({
        "DC": ['Fresno', 'SLC', 'Olathe', 'Indy', 'Hamburg', 'Macon', 'Charlotte'],
        "Capacity": [100, 150, 3000, 20000, 1000, 300, 10]
    })

    # Display map in Streamlit app
    folium_static(us_map, width=1200)

    grid_options = {
        "defaultColDef": {
            "minWidth": 5
        },
        "columnDefs": [
            {
                "headerName": "DC",
                "field": "DC",
                "editable": False,
            },
            {
                "headerName": "Capacity",
                "field": "Capacity",
                "editable": True,
            },
        ],
    }

    # _, col1, col2, _ = st.columns(4)
    # with col1:
    #     st.subheader("DC capacity")
    #     # create aggrid component
    #     grid_return = AgGrid(dc_capacity, grid_options, fit_columns_on_grid_load=True)
    #     new_df = grid_return["data"]

    # with col2:
    #     # st.title("")
    #     st.subheader("Customer SLA")
    #     customer_sla_days = st.number_input(label="No. of days", value=2)

    # _, button_col, _ = st.columns([2.5, 2, 1])
    # optimize_button = button_col.button(label="Optimize", on_click=get_optimal_dc, args=(random_cities, ))

    st.sidebar.subheader("DC Capacities")
    dc1_cap = st.sidebar.number_input(label="Frenco", value=5000)
    dc2_cap = st.sidebar.number_input(label="SLC", value=100)
    dc3_cap = st.sidebar.number_input(label="Olathe", value=150)
    dc4_cap = st.sidebar.number_input(label="Indy", value=2000)
    dc5_cap = st.sidebar.number_input(label="Hamburg", value=300)
    dc6_cap = st.sidebar.number_input(label="Macon", value=800)
    dc6_cap = st.sidebar.number_input(label="Charlotte", value=10)

    st.sidebar.subheader("Customer SLA (Days)")
    days = st.sidebar.number_input(label="Days", value=2)

    st.sidebar.button(label="Optimize", on_click=get_optimal_dc, args=(random_cities, ))

    if st.session_state.get("optimal_dc_df", None) is not None:
    # if optimize_button:
        optimal_df = st.session_state["optimal_dc_df"]

        grid_options2 = {
            "defaultColDef": {
                "minWidth": 5,
                "editable": False,
                "height": 200,
                "scrollable": True,
                "sortable": True,
            },
            "columnDefs": [
                {
                    "headerName": "Zone Name",
                    "field": "zone",
                    # "width": 120,
                },
                {
                    "headerName": "Current DC",
                    "field": "current_dc",
                    "width": 150,
                },
                {
                    "headerName": "Optimal DC",
                    "field": "optimal_dc",
                    "width": 150,
                },
                {
                    "headerName": "User Input DC",
                    "field": "user_input_dc",
                    "editable": True,
                    "width": 150,
                },
            ],
        }

        
        gd2 = GridOptionsBuilder.from_dataframe(optimal_df)
        gd2.configure_default_column(hide=True, editable=False)
        gd2.configure_column(field="zone", header_name="Zone Name", hide=False, width=170)
        gd2.configure_column(field="current_dc", header_name="Current DC", hide=False, width=150)
        gd2.configure_column(field="optimal_dc", header_name="Optimal DC", hide=False, width=150)

        cs = JsCode("""
            function(params){
                if (params.data.user_input_dc != params.data.optimal_dc) {
                    return {
                        'backgroundColor' : '#FFCCCB'
                }
                }
            };
        """)
        gd2.configure_column(field="user_input_dc", header_name="User Input DC", editable=True, cellStyle=cs, hide=False)
        grid_options2 = gd2.build()


        _, opt_col, _ = st.columns([1, 2, 1])
        with opt_col:
            # st.subheader("Optimal DC", )
            st.markdown("<h2 style='text-align: center; color: black;'>Optimal DC</h2>", unsafe_allow_html=True)

            #Define custom CSS
            custom_css = {
                ".ag-header-cell-label": {"background-color": "gray !important"}
            }

            optimal_df2 = AgGrid(
                optimal_df, 
                grid_options2, 
                height=500, 
                allow_unsafe_jscode=True,
                fit_columns_on_grid_load=True,  
                theme="alpine",
            )["data"]

        optimal_df2["user_color"] = optimal_df2["user_input_dc"].map(dc_colors)

        if not st.session_state["optimal_dc_df"].equals(optimal_df2):
            st.session_state["optimal_dc_df"] = optimal_df2
            st.experimental_rerun()
