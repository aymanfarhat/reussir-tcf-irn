from __future__ import annotations

from django.urls import path

from simulations.api import views


urlpatterns = [
    path("auth/csrf/", views.csrf, name="api_csrf"),
    path("auth/me/", views.me, name="api_me"),
    path("auth/login/", views.login_view, name="api_login"),
    path("auth/signup/", views.signup, name="api_signup"),
    path("auth/logout/", views.logout_view, name="api_logout"),
    path("test-definitions/", views.test_definitions, name="api_test_definitions"),
    path("practice-options/", views.practice_options, name="api_practice_options"),
    path("sessions/", views.sessions, name="api_sessions"),
    path("sessions/start/", views.start_session, name="api_start_session"),
    path("practice/start/", views.start_practice, name="api_start_practice"),
    path("sessions/<uuid:session_uuid>/", views.session_detail, name="api_session_detail"),
    path("sessions/<uuid:session_uuid>/report/", views.session_report, name="api_session_report"),
    path(
        "sessions/<uuid:session_uuid>/attempts/<int:order>/",
        views.attempt_detail,
        name="api_attempt_detail",
    ),
    path(
        "sessions/<uuid:session_uuid>/attempts/<int:order>/submit/",
        views.submit_attempt,
        name="api_submit_attempt",
    ),
    path(
        "sessions/<uuid:session_uuid>/attempts/<int:order>/grade/",
        views.attempt_grade,
        name="api_attempt_grade",
    ),
    path(
        "sessions/<uuid:session_uuid>/attempts/<int:order>/retry-grade/",
        views.retry_grade,
        name="api_retry_grade",
    ),
    path(
        "sessions/<uuid:session_uuid>/attempts/<int:order>/question-audio/",
        views.question_audio,
        name="api_question_audio",
    ),
]
