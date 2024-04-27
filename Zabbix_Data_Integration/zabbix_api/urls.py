from django.urls import path
from .views import SendDataToItemAPIView
urlpatterns= [
    # path('login/', LoginAPIView.as_view(), name="login"),
    # path('create_item/', CreateItemAPIView.as_view(), name="create-item"),
    # path('update_item/', UpdateItemAPIView.as_view(), name="update-item"),
    # path('get_host/', GetHostAPIView.as_view(), name="get-host"),
    path('send_data/',SendDataToItemAPIView.as_view(), name="send-data")


    
]