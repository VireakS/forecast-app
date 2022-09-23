import json

from .serializers import ForecastModel, ForecastSerializer
from rest_framework import viewsets
from prophet import Prophet
import pandas as pd
import io
import requests
from rest_framework.response import Response
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

# get input data and number of data points
url_list = [
    'https://disk-usage1.s3.ap-southeast-1.amazonaws.com/logical_disk_usage_daily.csv',
    'https://disk-usage1.s3.ap-southeast-1.amazonaws.com/logical_disk_usage_daily.csv'
]

final_data_list = []


class Predict:

    def get_input_data(self, url_source):
        url = url_source
        s = requests.get(url).content
        return pd.read_csv(io.StringIO(s.decode('utf-8')))

    def predict(self):
        for i in url_list:
            data = self.get_input_data(i)
            input_data_len = len(data)
            now = datetime.today()
            next_three_months = now + relativedelta(months=+3)
            next_six_months = now + relativedelta(months=+6)
            next_twelve_months = now + relativedelta(months=+12)
            days_in_three_months = (next_three_months - now).days
            days_in_six_months = (next_six_months - now).days
            days_in_twelve_months = (next_twelve_months - now).days

            # forecase the future for 12 months
            def forecast():
                period = days_in_twelve_months
                df_train = data[['Label', 'LogicalDisk % Free Space']]
                df_train = df_train.rename(columns={"Label": "ds", "LogicalDisk % Free Space": "y"})
                m = Prophet(growth='flat')
                m.fit(df_train)
                future = m.make_future_dataframe(periods=period)
                forecast = m.predict(future)
                return (pd.DataFrame(forecast[['ds', 'yhat_lower', 'yhat_upper', 'yhat']]).to_dict(orient='records'))

            forecast_lst = forecast()

            graph_data_arr = []

            def get_fluctuation_rate(today_val, final_val):
                if today_val >= final_val:
                    return ['decrease', ((today_val - final_val) / today_val) * 100]
                else:
                    return ['increase', ((final_val - today_val) / today_val) * 100]

                # generate list of date from today to next 3, 6, and 12 months

            def get_date_list(sdate, edate):
                return (pd.date_range(sdate, edate + relativedelta(days=+1) - timedelta(days=1), freq='d').strftime(
                    '%-m-%-d-%Y').to_list())

                # generate the visualization data

            def get_graph_data(forecast_lst):
                date_list = get_date_list(forecast_lst[0]['ds'], next_three_months)  # get list of date
                forecast_data_points = len(forecast_lst) - input_data_len  # get number of forecasted data points
                tick_amount = len(forecast_lst)  # get number of point in x axis
                today_date = now.strftime('%-m-%-d-%Y')  # set today date in mm-dd-yyyy
                fluctuation_rate = get_fluctuation_rate(forecast_lst[0]['yhat'],
                                                        forecast_lst[input_data_len - 1][
                                                            'yhat'])  # calculate fluctuation rate
                free_space = 0  # set free space amount
                used_space = 0  # set used space amount
                total_space = 0  # set total space amount

                # add data into graph visualization data
                tmp_dict = {"forecastData": forecast_lst, "duration": date_list,
                            "forcastDataPoint": forecast_data_points,
                            "tickAmount": tick_amount, "today": today_date, "fluctuation": fluctuation_rate,
                            "freeSpace": free_space,
                            "usedSpace": used_space, "totalSpace": total_space
                            }
                graph_data_arr.append(tmp_dict)

            def set_graph_data():
                for i in range(0, 3):
                    tmp_list = []
                    if i == 0:
                        tmp_list = list(forecast_lst[0:days_in_three_months + input_data_len])
                    if i == 1:
                        tmp_list = list(forecast_lst[0:days_in_six_months + input_data_len])
                    if i == 2:
                        tmp_list = list(forecast_lst)
                    get_graph_data(forecast_lst=tmp_list)

            set_graph_data()
            final_data_list.append(graph_data_arr)
            return json.dumps(final_data_list, indent=2, default=str)


class ForecastViewSet(viewsets.ModelViewSet):
    queryset = ForecastModel.objects.all()
    serializer_class = ForecastSerializer

    def create(self, request, *args, **kwargs):
        try:
            predict = Predict()
            data = predict.predict()
            forcast = ForecastModel()
            forcast.json = json.loads(data)
            forcast.created_at = datetime.now()

            forcast.save()
        except Exception as e:
            return Response({'msg': str(e)}, status=400)
        return Response({'msg': 'Done'})
