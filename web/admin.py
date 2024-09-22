from django.contrib import admin

from web.models import SignUpData, BanAppealData


@admin.register(SignUpData)
class SignUpDataAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email', 'reddit_username', 'subreddit_url',
                    'created_at')
    list_display_links = ('id', 'name')
    search_fields = ('name', )
    list_per_page = 20


@admin.register(BanAppealData)
class BanAppealDataAdmin(admin.ModelAdmin):
    list_display = ('id', 'reddit_username', 'subreddit', 'created_at')
    list_display_links = ('id', 'reddit_username')
    search_fields = ('reddit_username', )
    list_per_page = 20
