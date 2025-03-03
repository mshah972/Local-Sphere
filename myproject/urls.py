"""
URL configuration for myproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from . import views
from django.urls import path
from .views import logout_view, get_google_maps_api_key, get_restaurant_details

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),  # Homepage
    path('SphereAi/', views.SphereAi, name='SphereAi'),
    path('login/', views.user_login, name='login'),
    path('signup/', views.signup, name='signup'),
    path('planConfirmation/', views.planConfirmation, name='planConfirmation'),
    path('forgot/', views.forgot, name='forgot'),
    path('creation/', views.creation, name='creation'),
    path('account/', views.my_account, name='my_account'),
    path('logout/', logout_view, name='logout'),
    path("api/getRestaurantDetails/", get_restaurant_details, name="get_restaurant_details"),
    path("api/getGoogleMapsApiKey/", get_google_maps_api_key, name="get_google_maps_api_key"),
]