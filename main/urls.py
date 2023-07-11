from django.urls import path
from . import views

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path

urlpatterns = [
    path("",views.home,name='home'),
    path("about/",views.about,name='about'),
    path("send_land/",views.send_land,name='send_land'),
    path("add_land/",views.add_land,name='add_land'),
    path("plot_history/",views.plot_history,name='plot_history'),
    path("block_search/",views.block_search,name='block_search'),
    # path('plot_history/<int:plot_code>/', views.plot_history, name='plot_history'),

]