from django.contrib.auth.views import LogoutView
from django.urls import path, include

urlpatterns = [
    # ... other URL patterns ...
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    # ... other URL patterns ...
] 