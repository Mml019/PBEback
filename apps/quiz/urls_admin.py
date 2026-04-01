from django.urls import path, include
from .views_admin import *

# Django Endpoint is quiz-admin/
urlpatterns = [
    # path('login/', LoginView.as_view(), name='login-admin'),
    # path('logout/', LogoutView.as_view(), name='logout-admin'),
    # path('register/', Registration.as_view(), name='register-admin'),
    # path("accounts/", include("django.contrib.auth.urls")),  # new
    path("login/", LoginView.as_view(), name="login"),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('quizzes/', QuizViews.as_view(), name='quizzes'),
    path("answers/", ShowAnswers.as_view(), name="answers"),
    path("users/", ShowUsers.as_view(), name="users"),
    path("quiz/<int:idQ>/", QuizViews.as_view(), name="detailquiz"),
    # path('answerByRespondant/', ShowAnswersByRespondant.as_view(), name='answers_res' )

]