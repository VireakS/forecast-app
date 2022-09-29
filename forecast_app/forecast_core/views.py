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
from django.shortcuts import render

url_list = [
    'https://disk-usage1.s3.ap-southeast-1.amazonaws.com/logical_disk_usage_daily.csv',
    'https://disk-usage1.s3.ap-southeast-1.amazonaws.com/logical_disk_usage_daily2.csv'
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
            print(data.tail())
            input_data_len = len(data)
            # create today date and get prediction duration
            now = datetime.today()

            # get date in next 3, 6, and 12 months
            next_three_months = now + relativedelta(months=+3)
            next_six_months = now + relativedelta(months=+6)
            next_twelve_months = now + relativedelta(months=+12)

            # get numbers of days in next 3, 6, and 12 months
            days_in_three_months = (next_three_months - now).days
            days_in_six_months = (next_six_months - now).days
            days_in_twelve_months = (next_twelve_months - now).days

            # forecase the future
            def forecast():
                period = days_in_twelve_months

                # Predict forecast with Prophet.
                # create data for training
                df_train = data[['Label', 'LogicalDisk % Free Space']]
                df_train = df_train.rename(columns={"Label": "ds", "LogicalDisk % Free Space": "y"})
                # create the model
                m = Prophet(growth='flat')
                # train the model
                m.fit(df_train)
                # make prediction
                future = m.make_future_dataframe(periods=period)
                forecast_df = m.predict(future)
                # return the predicted data
                return (pd.DataFrame(forecast_df[['ds', 'yhat_lower', 'yhat_upper', 'yhat']]).to_dict(orient='records'),
                        forecast_df['yhat'].to_list(), forecast_df['yhat_lower'].to_list(),
                        forecast_df['yhat_upper'].to_list())

            forecast_lst, yhat, lower, upper = forecast()

            # prepare data for visualization
            graph_data_arr = []

            # calculate fluctuation rate
            def get_fluctuation_rate(today_val, final_val):
                if today_val >= final_val:
                    return (['Decrease', ((today_val - final_val) / today_val) * 100])
                else:
                    return (['Increase', ((final_val - today_val) / today_val) * 100])

            # generate list of date from today to next 3, 6, and 12 months
            def get_date_list(sdate, edate):
                return (pd.date_range(sdate, edate + relativedelta(days=+1), freq='d').strftime('%-m-%-d-%Y').to_list())

            # def get_forecast_data_list():
            # generate the visualization data
            def get_graph_data(forecast_lst, yhat, lower, upper, edate):
                date_list = get_date_list(forecast_lst[0]['ds'], edate)  # get list of date
                forecast_data_points = len(forecast_lst) - input_data_len  # get number of forecasted data points
                tick_amount = input_data_len  # get number of point in x axis
                today_date = now.strftime('%-m-%-d-%Y')  # set today date in mm-dd-yyyy
                fluctuation_rate = get_fluctuation_rate(forecast_lst[0]['yhat'], forecast_lst[input_data_len - 1][
                    'yhat'])  # calculate fluctuation rate
                free_space = forecast_lst[input_data_len - 1]['yhat']  # set free space amount
                used_space = 100 - free_space  # set used space amount
                total_space = 0  # set total space amount

                # add data into graph visualization data
                tmp_dict = {"duration": date_list, "forecastDataPoint": forecast_data_points,
                            "tickAmount": tick_amount, "today": today_date, "fluctuation": fluctuation_rate,
                            "freeSpace": free_space,
                            "usedSpace": used_space, "totalSpace": total_space, "yhat": yhat[0:len(forecast_lst)],
                            "lower": lower[0:len(forecast_lst)], "upper": upper[0:len(forecast_lst)]
                            }
                graph_data_arr.append(tmp_dict)

            # set data into the array for visualization
            def set_graph_data(yhat, lower, upper):
                # loop to get data for 3, 6, and 12 months
                for i in range(0, 3):
                    tmp_edate = datetime.today()
                    tmp_list = []
                    if i == 0:
                        tmp_list = list(forecast_lst[0:days_in_three_months + input_data_len])
                        tmp_edate = next_three_months
                    if i == 1:
                        tmp_list = list(forecast_lst[0:days_in_six_months + input_data_len])
                        tmp_edate = next_six_months
                    if i == 2:
                        tmp_list = list(forecast_lst)
                        tmp_edate = next_twelve_months
                    get_graph_data(forecast_lst=tmp_list, yhat=yhat, lower=lower, upper=upper, edate=tmp_edate)

            set_graph_data(yhat, lower, upper)
            final_data_list.append(graph_data_arr)
        return json.dumps(final_data_list, indent=2, sort_keys=True, default=str)


def index(request):
    return render(request, 'build/index.html')


class ForecastViewSet(viewsets.ModelViewSet):
    queryset = ForecastModel.objects.all()
    serializer_class = ForecastSerializer

    def create(self, request, *args, **kwargs):
        try:
            predict = Predict()
            data = predict.predict()
            forcast = ForecastModel()
            print(len(json.loads(data)))
            forcast.json = json.loads(data)
            forcast.created_at = datetime.now()

            forcast.save()
        except Exception as e:
            return Response({'msg': str(e)}, status=400)
        return Response({'msg': 'Done'})
