# from curses.panel import top_panel
from prophet import Prophet
import pandas as pd
import io
import requests
import matplotlib.pyplot as plt


#
# url="https://disk-usage1.s3.ap-southeast-1.amazonaws.com/logical_disk_usage_daily.csv"
# s=requests.get(url).content
# data=pd.read_csv(io.StringIO(s.decode('utf-8')))
#
# def forecast_data(month):
#     # data = pd.read_csv('freespace.csv')
#     print(data.tail())
#     period = month*30
#
#     # Predict forecast with Prophet.
#     df_train = data[['Label','LogicalDisk % Free Space']]
#     df_train = df_train.rename(columns={"Label": "ds", "LogicalDisk % Free Space": "y"})
#
#     m = Prophet()
#     m.fit(df_train)
#     future = m.make_future_dataframe(periods=period)
#     forecast = m.predict(future)
#
#     save_data = pd.DataFrame(forecast[['ds', 'yhat']])
#     save_data.to_csv(f'{month}_forecast.csv')
#
# # forecast_data(3)
# # forecast_data(6)
# # forecast_data(12)
#
# import csv
# import json
#
# def csv_to_json(csvFilePath, jsonFilePath):
#     jsonArray = []
#
#     #read csv file
#     with open(csvFilePath, encoding='utf-8') as csvf:
#         #load csv file data using csv library's dictionary reader
#         csvReader = csv.DictReader(csvf)
#
#         #convert each csv row into python dict
#         for row in csvReader:
#             #add this python dict to json array
#             jsonArray.append(row)
#
#     #convert python jsonArray to JSON String and write to file
#     with open(jsonFilePath, 'w', encoding='utf-8') as jsonf:
#         jsonString = json.dumps(jsonArray, indent=4)
#         jsonf.write(jsonString)
#
#
# csvFilePath = r'12_forecast.csv'
# jsonFilePath = r'12_forecast.json'
# csv_to_json(csvFilePath, jsonFilePath)
#
#
# def plot_data(csv_file):
#     to_plot = pd.read_csv(csv_file, usecols=['ds','yhat'])
#     # to_plot = to_plot.filter([['Label', 'LogicalDisk % Free Space']])
#     print(to_plot)
#     to_plot.plot(['ds'], ['yhat'])
#     plt.show()

# plot_data('3_forecast.csv')

def forecast_data(month):
    url = "https://disk-usage1.s3.ap-southeast-1.amazonaws.com/logical_disk_usage_daily.csv"
    s = requests.get(url).content
    data = pd.read_csv(io.StringIO(s.decode('utf-8')))
    # data = pd.read_csv('freespace.csv')
    period = month * 30

    # Predict forecast with Prophet.
    df_train = data[['Label', 'LogicalDisk % Free Space']]
    df_train = df_train.rename(columns={"Label": "ds", "LogicalDisk % Free Space": "y"})

    m = Prophet()
    m.fit(df_train)
    future = m.make_future_dataframe(periods=period)
    forecast = m.predict(future)

    save_data = pd.DataFrame(forecast)
    save_data.to_csv(f'{month}_forecast.csv')


forecast_data(3)
forecast_data(6)
forecast_data(12)
