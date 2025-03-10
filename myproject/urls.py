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
from .views import logout_view, get_google_maps_api_key, get_restaurant_details, get_mapbox_api_key, update_user_profile, get_location_image
from django.urls import path
from .views import generate_date_plan
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),  # Homepage
    path('SphereAi/', views.SphereAi, name='SphereAi'),
    path('login/', views.user_login, name='login'),
    path('signup/', views.signup, name='signup'),
    path('planConfirmation/', views.planConfirmation, name='planConfirmation'),
    path('forgot/', views.forgot, name='forgot'),
    path('about/', views.about, name='about'),
    path('creation/', views.creation, name='creation'),
    path('account/', views.my_account, name='my_account'),
    path('logout/', logout_view, name='logout'),
    path("api/getRestaurantDetails/", get_restaurant_details, name="get_restaurant_details"),
    path("api/getGoogleMapsApiKey/", get_google_maps_api_key, name="get_google_maps_api_key"),
    path('api/getMapboxApiKey/', get_mapbox_api_key, name='get-mapbox-api-key'),
    path("generate-date-plan/", generate_date_plan, name="generate_date_plan"),
    path('update-profile/', update_user_profile, name='update_user_profile'),
    path('api/getLocationImage/', get_location_image, name='get_location_image'),
    path('reset/<str:token>/', views.password_reset_confirm, name='password_reset_confirm'),
    path("test", views.password_reset_complete, name="password_reset_complete"),
    path('planPage/', views.planPage, name='planPage'),
    path('profileEdit/', views.profileEdit, name='profileEdit'),
    path('profilePage/', views.profilePage, name='profilePage'),
]

if settings.DEBUG:  # Only serve media files in development
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

