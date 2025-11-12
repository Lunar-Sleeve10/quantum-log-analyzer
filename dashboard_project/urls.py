from django.contrib import admin
from django.urls import path, include
from analyzer import views as analyzer_views
from users import views as user_views 

urlpatterns = [
    path('admin/', admin.site.urls),

    path('accounts/login/', user_views.login_signup_page, name='login'),
    
    path('accounts/signup/', user_views.login_signup_page, name='signup'), 

    path('accounts/', include('django.contrib.auth.urls')), 
    
    path('', analyzer_views.analyze_log, name='home'), 
]