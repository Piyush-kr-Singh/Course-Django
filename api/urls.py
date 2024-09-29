from django.urls import path, include
from home import views
from home.views import PeopleViewSet, RegisterAPI, LoginAPI
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'people', PeopleViewSet, basename='people')

urlpatterns = [
    path('', include(router.urls)),  # All 'people/' related operations
    path('register/', RegisterAPI.as_view()),  # Use as_view() correctly here
    path('login/', LoginAPI.as_view()),
    path('person/', views.person), 
    path('person/<int:id>/', views.person),  
    path('login/', views.login),
    path('persons/', views.PersonAPI.as_view()), 
]

