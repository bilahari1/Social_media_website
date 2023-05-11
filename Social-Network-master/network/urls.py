
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("n/login", views.login_view, name="login"),
    path("n/logout", views.logout_view, name="logout"),
    path("n/register", views.register, name="register"),
    path("n/cregister", views.cregister, name="cregister"),
    path("<str:username>", views.profile, name='profile'),
    path("n/following", views.following, name='following'),
    path("n/postjobs", views.postjobs, name='postjobs'),
    path("n/jobposting", views.jobposting, name='jobposting'),
    path("n/job_delete/<int:jid>", views.job_delete, name="job_delete"),
    path("n/job_edit/<int:jid>", views.job_edit, name="job_edit"),
    path("n/userjobs", views.userjobs, name="userjobs"),
    path("n/payment", views.payment, name="payment"),
    path("n/confirm_payment", views.confirm_payment, name="confirm_payment"),
    path("n/jobapplication/<int:jid>", views.jobapplication, name="jobapplication"),
    path("n/jobapplicants/<int:jid>", views.jobapplicants, name="jobapplicants"),
    path('n/download_csv/<int:jid>', views.download_csv, name='download_csv'),
    path("n/saved", views.saved, name="saved"),
    path("n/search", views.search, name="search"),
    path("n/createpost", views.create_post, name="createpost"),
    path("n/post/<int:id>/like", views.like_post, name="likepost"),
    path("n/post/<int:id>/unlike", views.unlike_post, name="unlikepost"),
    path("n/post/<int:id>/save", views.save_post, name="savepost"),
    path("n/post/<int:id>/unsave", views.unsave_post, name="unsavepost"),
    path("n/post/<int:post_id>/comments", views.comment, name="comments"),
    path("n/post/<int:post_id>/write_comment",views.comment, name="writecomment"),
    path("n/post/<int:post_id>/delete", views.delete_post, name="deletepost"),
    path("<str:username>/follow", views.follow, name="followuser"),
    path("<str:username>/unfollow", views.unfollow, name="unfollowuser"),
    path("n/post/<int:post_id>/edit", views.edit_post, name="editpost")
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

