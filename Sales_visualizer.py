import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os

file_path = os.path.join(os.getcwd(), "CSV_Files/Normalized_JustDial_sales_data.csv")

# Read the file using pandas
df = pd.read_csv(file_path)

def preprocess_data(df):
    # Perform any necessary data preprocessing steps
    df["Date"] = pd.to_datetime(df["Date"])
    df.sort_values("Date", inplace=True)
    return df

def filter_data(df, cities, date_range):
    filtered_df = df[df["City"].isin(cities)]
    start_date = datetime.combine(date_range[0], datetime.min.time())
    end_date = datetime.combine(date_range[1], datetime.max.time())
    filtered_df = filtered_df[(filtered_df["Date"] >= start_date) & (filtered_df["Date"] <= end_date)]
    return filtered_df

def calculate_percentage_change(current_total, previous_total):
    if previous_total == 0.0:
        return float('inf')  # Handle division by zero
    return ((current_total - previous_total) / previous_total) * 100

def get_percentage_change_status(percentage_change):
    if percentage_change > 0:
        return "increased", "green"
    elif percentage_change < 0:
        return "decreased", "red"
    else:
        return "remained unchanged", "black"

def plot(file_path):
    df = pd.read_csv(file_path)

    df = preprocess_data(df)

    clist = df["City"].unique().tolist()

    st.set_page_config(page_title="JD CONTENT REPORT", layout="wide")
    
    st.title("JD CONTENT REPORT")
        
    st.sidebar.subheader("Select Options")
    cities = st.sidebar.multiselect("Select City", clist, default=["Total"])

    st.sidebar.markdown("---")
    date_range = st.sidebar.date_input("Select Date Range", [df["Date"].min().date(), df["Date"].max().date()])

    # Check if both start and end dates are selected
    if date_range[0] is not None and date_range[1] is not None:
        st.sidebar.markdown("---")
        y_columns = st.sidebar.multiselect("Select Data Columns for Comparison", df.columns, default=["total_active"])

        st.sidebar.markdown("---")
        if not y_columns:
            st.warning("Please select at least one column for comparison.")
            return

        st.header("Selected Cities: {}".format(", ".join(cities)))

        # Calculate the start and end dates for the selected date range
        start_selected = date_range[0]
        end_selected = date_range[1]

        # Calculate the start and end dates for the previous date range
        days_difference = (end_selected - start_selected).days
        start_previous = start_selected - timedelta(days=days_difference)
        end_previous = start_selected - timedelta(days=1)

        # Filter data for both date ranges
        selected_df = filter_data(df, cities, [start_selected, end_selected])
        previous_df = filter_data(df, cities, [start_previous, end_previous])

        # Display the date range of available records in bold and red
        min_date = df["Date"].min().date()
        max_date = df["Date"].max().date()
        available_date_range = f"<h4>Records are available from <font color='red'><b>{min_date}</b></font> to <font color='red'><b>{max_date}</b></font></h4>"
        st.markdown(available_date_range, unsafe_allow_html=True)

        # Calculate and display percentage change for each data column
        for column in y_columns:
            selected_total = selected_df[column].sum()
            previous_total = previous_df[column].sum()
            percentage_change = calculate_percentage_change(selected_total, previous_total)
            change_status, color = get_percentage_change_status(percentage_change)

            st.write(f"{column} Percentage Change for the Last {days_difference} Days :  {percentage_change:.2f} %", unsafe_allow_html=True)
            st.write(f"Current {column} Total : {selected_total}")
            st.write(f"Previous {column} Total : {previous_total}")
            change_status_message = f"<h5><b><font color='{color}'>The {column} has {change_status} by  :  {abs(percentage_change):.2f} %</font></b></h5>"
            st.markdown(change_status_message, unsafe_allow_html=True)

        # Line Chart
        fig_line = go.Figure()
        for city in cities:
            city_df = selected_df[selected_df["City"] == city]
            for column in y_columns:
                fig_line.add_trace(go.Scatter(x=city_df["Date"], y=city_df[column], mode='lines+markers',
                                              name=f"{city} - {column}"))

        fig_line.update_layout(
            title='Data for Cities',
            xaxis_title='Date',
            yaxis_title='Selected Data',
            yaxis=dict(
                tickformat=".2f"
            ),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            margin=dict(l=20, r=20, t=60, b=20)
        )

        # Bar Chart
        fig_bar = go.Figure()
        for city in cities:
            city_df = selected_df[selected_df["City"] == city]
            for column in y_columns:
                fig_bar.add_trace(go.Bar(x=city_df["Date"], y=city_df[column], name=f"{city} - {column}"))

        fig_bar.update_layout(
            title='Bar Chart for Cities',
            xaxis_title='Date',
            yaxis_title='Selected Data',
            barmode='stack',
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            margin=dict(l=20, r=20, t=60, b=20)
        )

        # Pie Chart
        labels = []
        data_values = []

        for column in y_columns:
            total_users = selected_df[column].sum()
            label = f"{column} ({total_users})"
            labels.append(label)
            data_values.append(total_users)

        fig_pie = go.Figure(data=[go.Pie(labels=labels, values=data_values)])
        fig_pie.update_layout(title='Data Distribution')

        # Display the charts side by side with appropriate sizes
        st.plotly_chart(fig_line, use_container_width=True)
        st.plotly_chart(fig_bar, use_container_width=True)
        st.plotly_chart(fig_pie, use_container_width=True)

    else:
        st.warning("Please choose both a start date and an end date.")

if __name__ == "__main__":
    file_path = r"CSV_Files/Normalized_JustDial_sales_data.csv"  # Update the file path accordingly
    plot(file_path)
