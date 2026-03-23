from django.urls import path
from .views import (
    OpenSessionView, CloseSessionView,
    CurrentSessionView, SessionListView, SessionDetailView
)

urlpatterns = [
    path('sessions/open/', OpenSessionView.as_view(), name='session-open'),
    path('sessions/current/', CurrentSessionView.as_view(), name='session-current'),
    path('sessions/', SessionListView.as_view(), name='session-list'),
    path('sessions/<int:pk>/close/', CloseSessionView.as_view(), name='session-close'),
    path('sessions/<int:pk>/', SessionDetailView.as_view(), name='session-detail'),
]