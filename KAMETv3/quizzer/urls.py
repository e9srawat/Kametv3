from django.urls import path
from . import views

urlpatterns = [
    path("", views.login_user, name="login"),
    path('logout/', views.LogoutUser.as_view(), name='logout'),

    path("control/", views.AdminPanel.as_view(), name="control"),
    
    path('all_papers/', views.AllPapers.as_view(), name='all_papers'),
    path('add_paper/', views.AddPaper.as_view(), name='add_paper'),
    path('edit_paper/<int:paper_id>', views.EditPaper.as_view(), name='edit_paper'),
    path('delete_paper/<int:pk>/', views.DeletePaper.as_view(), name='delete_paper'),


    path('questions/<int:paper_id>', views.PaperQuestions.as_view(), name='questions'),    
    path('edit_question/<int:question_id>/', views.EditQuestion.as_view(), name='edit_question'),
    path('delete_question/<int:pk>/', views.DeleteQuestion.as_view(), name='delete_question'),

    
    path('add_question/<int:paper_id>', views.AddQuestion.as_view(), name='add_question'),

    
    path('all_usernames/', views.AllUsernames.as_view(), name='all_usernames'),
    path("register/", views.Register.as_view(), name="register"),
    path('edit_settings/<int:pk>/', views.EditSettings.as_view(), name='edit_settings'),
    path('delete_user/<int:pk>/', views.DeleteUser.as_view(), name='delete_user'),
    path('user_solutions/<int:pk>/', views.UserSolutions.as_view(), name='user_solutions_detail'),
    path("update_status/<int:pk>/", views.UpdateStatus.as_view(), name="update_status"),


    path("subs", views.Subjects.as_view(), name="subs"),
    path("dash/<int:paper_id>/", views.Base.as_view(), name="base"),
    path('paper/<int:paper_id>/', views.RandomQuestionsView.as_view(), name='paper_questions'),
    path('submit_all_solutions/', views.SubmitAllSolutionsView.as_view(), name='submit_all_solutions'),
    path('result/<int:pk>/', views.ResultView.as_view(), name='result'),

]