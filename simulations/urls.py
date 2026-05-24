from django.urls import path

from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("signup/", views.signup, name="signup"),
    path("practice/", views.practice_start, name="practice_start"),
    path("tests/history/", views.history, name="history"),
    path(
        "tests/history/<uuid:session_uuid>/delete/",
        views.delete_history_session,
        name="delete_history_session",
    ),
    path("tests/start/<str:mode>/", views.start_test, name="start_test"),
    path("tests/<uuid:session_uuid>/tasks/<int:order>/", views.task_detail, name="task_detail"),
    path(
        "tests/<uuid:session_uuid>/tasks/<int:order>/question-audio/",
        views.question_audio,
        name="question_audio",
    ),
    path(
        "tests/<uuid:session_uuid>/tasks/<int:order>/submit/",
        views.submit_task,
        name="submit_task",
    ),
    path(
        "tests/<uuid:session_uuid>/tasks/<int:order>/grade/",
        views.task_grade,
        name="task_grade",
    ),
    path(
        "tests/<uuid:session_uuid>/tasks/<int:order>/retry-grade/",
        views.retry_grade,
        name="retry_grade",
    ),
    path("tests/<uuid:session_uuid>/report/", views.report, name="report"),
]
