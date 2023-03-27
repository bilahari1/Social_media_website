from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('settings', views.settings, name='settings'),
    path('upload', views.upload, name='upload'),
    path('follow', views.follow, name='follow'),
    path('search', views.search, name='search'),
    path('profile/<str:pk>', views.profile, name='profile'),
    path('like-post', views.like_post, name='like-post'),
    path('signup', views.signup, name='signup'),
    path('csignup', views.csignup, name='csignup'),
    path('signin', views.signin, name='signin'),
    path('cindex', views.cindex, name='cindex'),
    path('jobposting', views.jobposting, name='jobposting'),
    path('joblisting', views.joblisting, name='joblisting'),
    path('job_delete/<int:jid>', views.job_delete, name='job_delete'),
    path('job_edit/<int:jid>', views.job_edit, name='job_edit'),
    path('logout', views.logout, name='logout'),
    path('comment_list', views.comment_list, name='comment_list'),
]
