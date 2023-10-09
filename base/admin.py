from django.contrib import admin
from base.api.models import (
    Community,
    CommunityMembership,
    Post,
    Comment,
    Profile,
    Messages,
    Notifications,
    BookMarks,
    CommentLike,
    PostLike,
    PostDownvoted,
    PostLove,
    PostUpvoted,
    CommentDownvoted,
    CommentLove,
    CommentUpvoted
)

# Register your models here.

admin.site.register(Community)
admin.site.register(CommunityMembership)
admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(Profile)
admin.site.register(Messages)
admin.site.register(Notifications)
admin.site.register(BookMarks)
admin.site.register(CommentLike)
admin.site.register(PostLike)
admin.site.register(PostDownvoted)
admin.site.register(PostLove)
admin.site.register(PostUpvoted)
admin.site.register(CommentDownvoted)
admin.site.register(CommentLove)
admin.site.register(CommentUpvoted)
