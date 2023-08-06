from django.contrib import admin
from .models import VotingEvent, Team, Competitor, Vote

class VotingEventAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'start_time', 'end_time']
    search_fields = ['name']

class TeamAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    search_fields = ['name']

class CompetitorAdmin(admin.ModelAdmin):
    list_display = ['id', 'voting_event', 'team', 'score']
    list_filter = ['voting_event', 'team']
    search_fields = ['team__name']

class VoteAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'competitor', 'voted_at']
    list_filter = ['competitor__team', 'competitor__voting_event', 'voted_at']
    search_fields = ['user__username']

admin.site.register(VotingEvent, VotingEventAdmin)
admin.site.register(Team, TeamAdmin)
admin.site.register(Competitor, CompetitorAdmin)
admin.site.register(Vote, VoteAdmin)
