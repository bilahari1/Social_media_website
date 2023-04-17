from django.contrib import admin

from .models import *

# Register your models here.

admin.site.register(User)
admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(Follower)
admin.site.register(JobApplication)
# admin.site.register(Like)
# admin.site.register(Saved)

class CompanyAdmin(admin.ModelAdmin):
    list_display = ('cid', 'cname', 'location', 'email', 'website')
    search_fields = ('cname', 'location', 'email', 'website')

admin.site.register(Company, CompanyAdmin)

class JobPostingAdmin(admin.ModelAdmin):
    list_display = ('jid', 'title', 'company', 'location', 'website')
    search_fields = ('title', 'company', 'locaation', 'website')

admin.site.register(JobPosting, JobPostingAdmin)