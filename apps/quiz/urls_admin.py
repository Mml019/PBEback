from django.urls import include, path

from .views_admin import *

# Django Endpoint is quiz-admin/<
urlpatterns = [
    # path('login/', LoginView.as_view(), name='login-admin'),
    # path('logout/', LogoutView.as_view(), name='logout-admin'),
    # path('register/', Registration.as_view(), name='register-admin'),
    # path("accounts/", include("django.contrib.auth.urls")),  # new
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("quizzes/", QuizListView.as_view(), name="quizzes_list"),
    path("quizzes/", QuizListView.as_view(), name="quizzes"),
    path("answers/", ShowAnswers.as_view(), name="answers"),
    path("answers/download/", export_answers, name="answers_donwload"),
    path("answers/<int:idQ>/", ShowAnswersByQuiz.as_view(), name="answers_by_quiz"),
    path("answers/<int:idRes>/",ShowAnswersFromRespondant.as_view(), name="answers_by_respondant"),
    path("answers/by_user/", ShowAnswersByRespondant.as_view(), name="answers_respondants"),  
    path("ansewrs/by_user/donwload/", export_by_user_quiz, name='export_by_user'),
    path("users/", ShowUsers.as_view(), name="users"),
    path("users/donwload/", export_users, name="users_donwload"),
    path("quiz/<int:idQ>/", QuizDetailView.as_view(), name="detailquiz"),
    path("quiz/<int:idQ>/delete/", QuizDeleteView.as_view(), name="delete")
]
