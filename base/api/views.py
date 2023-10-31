from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework import permissions
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView, ListAPIView, ListCreateAPIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from django.contrib.auth.models import User

from base.api.Custom_views.user_register import register_user

from base.api.Custom_views.book_marks import (
    user_bookmarks,
    create_bookmark,
    delete_bookmark
)

from base.api.Custom_views.message import (
    SendMessageView,
    GetUserMessagesView,
    MarkMessageAsReadView,
    ClearUnreadMessagesCount,
    GetMostRecentMessageView
)

from base.api.Custom_views.notifications import (
    GetUserNotification,
    MarkNotificationAsRead
)
from base.api.Custom_views.profile import (
    GetUserProfile,
    UpdateProfile,
    ToggleFollowUserAPIView,
    GetProfileList,
    FollowStateAPIView
)

from base.api.Custom_views.community import (
    CommunityList,
    CommunityDetail,
    CommunityListForOwnerOrMember,
    TopCommunitiesView,
    JoinOrLeaveCommunityView,
    CommunityMembershipStatusView
)

from base.api.Custom_views.post import (
    CommunityPostList,
    PostDetail,
    PostList
)

from base.api.Custom_views.comment import (
    CommentList,
    CommentDetail
)


from .models import (
    Comment,
    CommentLike,
    CommentLove,
    CommentUpvoted,
    CommentDownvoted,
    Post,
    PostLike,
    PostLove,
    PostUpvoted,
    PostDownvoted,
)


from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['username'] = user.username
        token['notification_count'] = user.profile.unread_notifications_count
        print(token['notification_count'])

        return token


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


""" Handling post reactions """


class LikePost(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, post_id, format=None):
        user = request.user
        post = get_object_or_404(Post, pk=post_id)

        existing_like = PostLike.objects.filter(user=user, post=post).first()

        if existing_like:
            existing_like.delete()
            liked = False
        else:
            PostLike.objects.create(user=user, post=post)
            liked = True

        return Response({'liked': liked}, status=status.HTTP_200_OK)


class LovePost(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, post_id, format=None):
        user = request.user
        post = get_object_or_404(Post, pk=post_id)

        existing_love = PostLove.objects.filter(user=user, post=post).first()

        if existing_love:
            existing_love.delete()
            loved = False
        else:
            PostLove.objects.create(user=user, post=post)
            loved = True

        return Response({'loved': loved}, status=status.HTTP_200_OK)


class UpvotePost(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, post_id, format=None):
        user = request.user
        post = get_object_or_404(Post, pk=post_id)

        existing_upvote = PostUpvoted.objects.filter(
            user=user, post=post).first()

        if existing_upvote:
            existing_upvote.delete()
            upvoted = False
        else:
            existing_downvote = PostDownvoted.objects.filter(
                user=user, post=post).first()
            if existing_downvote:
                existing_downvote.delete()
            PostUpvoted.objects.create(user=user, post=post)
            upvoted = True

        return Response({'upvoted': upvoted}, status=status.HTTP_200_OK)


class DownvotePost(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, post_id, format=None):
        user = request.user
        post = get_object_or_404(Post, pk=post_id)

        existing_downvote = PostDownvoted.objects.filter(
            user=user, post=post).first()

        if existing_downvote:
            existing_downvote.delete()
            downvoted = False
        else:
            existing_upvote = PostUpvoted.objects.filter(
                user=user, post=post).first()
            if existing_upvote:
                existing_upvote.delete()
            PostDownvoted.objects.create(user=user, post=post)
            downvoted = True

        return Response({'downvoted': downvoted}, status=status.HTTP_200_OK)


""" Handling comment reactions """


class LikeComment(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, comment_id, format=None):
        user = request.user

        comment = get_object_or_404(Comment, pk=comment_id)
        existing_like = CommentLike.objects.filter(
            user=user, comment=comment).first()

        if existing_like:
            existing_like.delete()
            liked = False
        else:
            CommentLike.objects.create(user=user, comment=comment)
            liked = True

        return Response({'liked': liked}, status=status.HTTP_200_OK)


class LoveComment(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, comment_id, format=None):
        user = request.user

        comment = get_object_or_404(Comment, pk=comment_id)
        existing_love = CommentLove.objects.filter(
            user=user, comment=comment).first()

        if existing_love:
            existing_love.delete()
            loved = False
        else:
            CommentLove.objects.create(user=user, comment=comment)
            loved = True

        return Response({'loved': loved}, status=status.HTTP_200_OK)


class UpvoteComment(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, comment_id, format=None):
        user = request.user

        comment = get_object_or_404(Comment, pk=comment_id)
        existing_upvote = CommentUpvoted.objects.filter(
            user=user, comment=comment).first()

        if existing_upvote:
            existing_upvote.delete()
            upvoted = False
        else:
            existing_downvote = CommentDownvoted.objects.filter(
                user=user, comment=comment).first()
            if existing_downvote:
                existing_downvote.delete()
            CommentUpvoted.objects.create(user=user, comment=comment)
            upvoted = True

        return Response({'upvoted': upvoted}, status=status.HTTP_200_OK)


class DownvoteComment(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, comment_id, format=None):
        user = request.user

        comment = get_object_or_404(Comment, pk=comment_id)
        existing_downvote = CommentDownvoted.objects.filter(
            user=user, comment=comment).first()

        if existing_downvote:
            existing_downvote.delete()
            downvoted = False
        else:
            existing_upvote = CommentUpvoted.objects.filter(
                user=user, comment=comment).first()
            if existing_upvote:
                existing_upvote.delete()
            CommentDownvoted.objects.create(user=user, comment=comment)
            downvoted = True

        return Response({'downvoted': downvoted}, status=status.HTTP_200_OK)


class ClearUnreadNotificationsCount(APIView):
    def post(self, request):
        user = request.user
        user.profile.unread_notifications_count = 0
        user.profile.save()
        return Response({'message': 'Unread notification count cleared.'}, status=status.HTTP_200_OK)
