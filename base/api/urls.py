from . import views
from django.urls import path

from rest_framework_simplejwt.views import (
    # TokenObtainPairView,
    TokenRefreshView,
)


urlpatterns = [
    # path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/', views.MyTokenObtainPairView.as_view(),
         name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('communities/', views.CommunityList.as_view()),
    path('communities/<int:pk>', views.CommunityDetail.as_view()),
    path('communities/<int:user_id>/list/',
         views.CommunityListForOwnerOrMember.as_view(), name='community-list-owner-member'),
    path('top-communities/', views.TopCommunitiesView.as_view(),
         name='top-communities'),
    path('join_or_leave_community/<int:community_id>',
         views.JoinOrLeaveCommunityView.as_view(), name='join-leave-community'),
    path('get_membership_status/<int:community_id>',
         views.CommunityMembershipStatusView.as_view(), name='community-membership-status'),

    path('communities/<int:community_id>/posts/',
         views.CommunityPostList.as_view(), name='community-post-list'),
    path('posts/', views.PostList.as_view()),
    path('posts/<int:pk>', views.PostDetail.as_view()),
    path('like_posts/<int:post_id>', views.LikePost.as_view()),
    path('love_posts/<int:post_id>', views.LovePost.as_view()),
    path('upvote_posts/<int:post_id>', views.UpvotePost.as_view()),
    path('downvote_posts/<int:post_id>', views.DownvotePost.as_view()),


    #     path('comments/', views.CommentList.as_view()),
    path('comments/<int:pk>', views.CommentDetail.as_view()),
    path('like_comments/<int:comment_id>', views.LikeComment.as_view()),
    path('love_comments/<int:comment_id>', views.LoveComment.as_view()),
    path('upvote_comments/<int:comment_id>',
         views.UpvoteComment.as_view()),
    path('downvote_comments/<int:comment_id>',
         views.DownvoteComment.as_view()),
    path('posts/<int:post_id>/comments/',
         views.CommentList.as_view(), name='comment-list'),


    path('user_bookmarks/<int:user_id>/',
         views.user_bookmarks, name='user_bookmarks'),
    path('create_bookmark/', views.create_bookmark, name='create_bookmark'),
    path('bookmarks/<int:bookmark_id>',
         views.delete_bookmark, name='delete_bookmark'),

    path('send_message/', views.SendMessageView.as_view(), name='send_message'),
    path('get-user-messages/<int:user_id>/',
         views.GetUserMessagesView.as_view(), name='get_user_messages'),
    path('mark-message-as-read/<int:message_id>',
         views.MarkMessageAsReadView.as_view(), name='mark_message_as_read'),
    path('clear-unread-messages-count/', views.ClearUnreadMessagesCount.as_view(),
         name='clear_unread_message_count'),

    path('clear-unread-notifications/', views.ClearUnreadNotificationsCount.as_view(),
         name='clear_unread_notifications'),


    path('notifications/', views.GetUserNotification.as_view(),
         name="user_notifications"),

    path('profile/', views.GetUserProfile.as_view(), name="user_profile")
]
