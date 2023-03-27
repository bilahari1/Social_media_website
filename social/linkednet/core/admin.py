from django.contrib import admin
from .models import Profile, Post, LikePost, FollowersCount, Company, Comment, JobPosting

# Register your models here.
admin.site.register(Profile)
admin.site.register(Post)
admin.site.register(LikePost)
admin.site.register(FollowersCount)
admin.site.register(Company)
admin.site.register(Comment)


class JobPostingAdmin(admin.ModelAdmin):
    list_display = (
        'jid', 'title', 'company', 'location', 'description', 'requirements', 'responsibilities', 'created_at',
        'updated_at')


admin.site.register(JobPosting, JobPostingAdmin)
