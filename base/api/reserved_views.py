from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from django.contrib.auth.models import User

from .serializers import (
    CommunitySerializer,
    PostSerialization,
    CommentSerialization,
    BookMarksSerializer,
    MessageSerializer,
    MarkMessageAsReadSerializer
)

from .models import (
    Community,
    Comment,
    BookMarks,
    Messages,
    CommentLike,
    CommentLove,
    CommentUpvoted,
    CommentDownvoted,
    Post,
    PostLike,
    PostLove,
    PostUpvoted,
    PostDownvoted,
    Notifications
)

import random

from .Custom_views.notification_content import (
    comment_notification_sentences,
    post_notification_sentences
)

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['username'] = user.username

        return token


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


class CommunityList(APIView):
    ''' Defining get and post request '''

    def get(self, request, format=None):
        user = request.user
        print("User:", user.id)

        communities = Community.objects.all()
        serializer = CommunitySerializer(communities, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = CommunitySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CommunityDetail(APIView):
    def get_object(self, pk):
        try:
            return Community.objects.get(id=pk)
        except:
            raise Http404

    def get(self, request, pk, format=False):
        community = self.get_object(pk)
        serializer = CommunitySerializer(community)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        community = self.get_object(pk)
        serializer = CommunitySerializer(community, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk, format=None):
        community = self.get_object(pk)
        serializer = CommunitySerializer(
            community, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=False):
        community = self.get_object(pk)

        community.delete()

        return Response('community deleted')


class PostList(APIView):
    ''' implementing get and post request '''

    def get(self, request, format=None):
        posts = Post.objects.all()
        serializer = PostSerialization(posts, many=True)
        return Response(serializer.data)

    # permission_classes = [IsAuthenticated]
    def post(self, request, format=None):
        serializer = PostSerialization(
            data=request.data, context={'request': request})
        if serializer.is_valid():
            post = serializer.save()

            # Get the community for this post
            community = post.community

            # Get all members of the community
            community_members = community.members.all()

            # Create a notification for each community member
            for member in community_members:
                # Make sure the creator of the post does not receive the notification
                if member != request.user:
                    # Randomly select a notification sentence
                    random_sentence = random.choice(
                        post_notification_sentences)

                    # Replace placeholders with actual values
                    notification_content = random_sentence.format(
                        recipient=member.username.capitalize(),
                        sender=request.user.username.capitalize(),
                        community=community.name.upper(),
                        post_title=post.title,
                    )

                    Notifications.objects.create(
                        recipient=member,
                        sender=request.user,
                        notification_type="NewPost",
                        content=notification_content,
                    )

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PostDetail(APIView):
    ''' implementing get, put, and delete request '''

    def get_object(self, pk):
        try:
            return Post.objects.get(id=pk)
        except:
            raise Http404

    def get(self, request, pk, format=False):
        post = self.get_object(pk)
        serializer = PostSerialization(post)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        post = self.get_object(pk)
        serializer = PostSerialization(post, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk, format=None):
        post = self.get_object(pk)
        serializer = PostSerialization(post, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=False):
        post = self.get_object(pk)

        post.delete()

        return Response('community deleted')


class CommentList(APIView):
    ''' implementing get and post request '''

    def get(self, request, format=None):
        comments = Comment.objects.all()
        serializer = CommentSerialization(comments, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = CommentSerialization(
            data=request.data, context={'request': request})

        if serializer.is_valid():
            comment = serializer.save()

            # Get the post associated with this comment
            post = comment.post

            # Check if this is a reply to an existing comment
            if comment.parent_comment:
                # This is a reply
                parent_comment = comment.parent_comment
                parent_comment_owner = parent_comment.author

                # Notify the owner of the parent comment about the reply
                Notifications.objects.create(
                    recipient=parent_comment_owner,
                    sender=request.user,
                    notification_type="NewCommentReply",
                    content=f'Your comment on "{post.title}" has a new reply by {request.user.username.capitalize()}. "{post.content}"'
                )

            else:
                # This is a new top-level comment

                # Get the community for this post
                community = post.community

                # Get all members of the community
                community_members = community.members.all()

                # Create a notification for each community member
                for member in community_members:
                    # Ensure the commenter is not the same as the community member
                    if member != request.user:
                        # Choose a random notification sentence
                        if member == post.author:
                            # Customize the notification for the post owner
                            notification_content = f'Your post has been commented by {request.user.username.capitalize()}. "{post.content}"'
                        else:
                            # Choose a random notification sentence for other community members
                            notification_content = random.choice(comment_notification_sentences).format(
                                recipient=member.username.capitalize(),
                                sender=request.user.username.capitalize(),
                                community=community.name.upper(),
                                post_title=post.title.capitalize()
                            )

                        Notifications.objects.create(
                            recipient=member,
                            sender=request.user,
                            notification_type="NewComment",
                            content=notification_content
                        )

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CommentDetail(APIView):
    ''' implementing get, put, and delete request '''

    def get_object(self, pk):
        try:
            return Comment.objects.get(id=pk)
        except:
            raise Http404

    def get(self, request, pk, format=False):
        comment = self.get_object(pk)
        serializer = CommentSerialization(comment, many=False)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        comment = self.get_object(pk)
        serializer = CommentSerialization(comment, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk, format=None):
        comment = self.get_object(pk)
        serializer = CommentSerialization(
            comment, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=False):
        comment = self.get_object(pk)

        comment.delete()

        return Response('community deleted')


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_bookmarks(request, user_id):
    try:
        bookmarks = BookMarks.objects.filter(user_id=user_id)
    except BookMarks.DoesNotExist:
        return Response({'error': 'Bookmarks not found for this user'}, status=404)

    serializer = BookMarksSerializer(bookmarks, many=True)
    return Response(serializer.data, status=200)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_bookmark(request):
    post_id = request.data.get('post_id')

    # Check if the post exists
    try:
        post = Post.objects.get(pk=post_id)
    except Post.DoesNotExist:
        return Response({'error': 'Post not found'}, status=404)

    # Check if a bookmark for this post already exists for the user
    existing_bookmark = BookMarks.objects.filter(
        user=request.user, post=post).first()

    if existing_bookmark:
        return Response({'message': 'This post is already bookmarked'}, status=400)

    # Create a new bookmark
    bookmark = BookMarks.objects.create(
        user=request.user,
        post=post
    )

    serializer = BookMarksSerializer(bookmark)
    return Response(serializer.data, status=201)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_bookmark(request, bookmark_id):
    try:
        bookmark = BookMarks.objects.get(id=bookmark_id, user=request.user)
    except BookMarks.DoesNotExist:
        return Response({'error': 'Bookmark not found'}, status=404)

    bookmark.delete()
    return Response({'message': 'Bookmark deleted successfully'}, status=204)


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
            CommentDownvoted.objects.create(user=user, comment=comment)
            downvoted = True

        return Response({'downvoted': downvoted}, status=status.HTTP_200_OK)


""" Handling users messaging """


class SendMessageView(CreateAPIView):
    queryset = Messages.objects.first()
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        recipient_id = serializer.validated_data['recipient'].id

        print("sender: ", self.request.user.username)
        print("recipient: ", serializer.validated_data['recipient'].username)
        # Check if the recipient is the same as the sender
        if recipient_id == self.request.user.id:
            return Response(
                {'error': 'You cannot send a message to yourself.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer.save(sender=self.request.user)


class GetUserMessagesView(ListAPIView):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        print(self.request.user.id)
        user_id = self.kwargs['user_id']
        # Retrieve messages sent to or received from the user
        # this code is reponsible for fetching messages between two users.
        return Messages.objects.filter(
            recipient=self.request.user, sender_id=user_id
        ) | Messages.objects.filter(
            sender=self.request.user, recipient_id=user_id
        )
        # return Messages.objects.filter(
        #     (Q(recipient=self.request.user) & Q(sender_id=user_id)) |
        #     (Q(sender=self.request.user) & Q(recipient_id=user_id))
        # )

        '''
        If you're viewing a chat between "User A" and "User B," you want
        to see only messages sent between these two users. The condition
        ensures that messages are retrieved where the authenticated user
        (you, "User A") is either the sender or the recipient and the other
        user ("User B") is the corresponding sender or recipient.
        This way, you're effectively filtering the messages to show only
        the conversation between "User A" and "User B."
        '''


class MarkMessageAsReadView(CreateAPIView):
    queryset = Messages.objects.all()
    serializer_class = MarkMessageAsReadSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        message_id = self.kwargs['message_id']
        try:
            message = Messages.objects.get(
                pk=message_id, recipient=self.request.user
            )
        except Messages.DoesNotExist:
            raise Http404
        message.is_read = True
        message.save()


class ClearUnreadMessagesCount(APIView):
    def post(self, request):
        # Get the authenticated user or user ID from the session
        user = request.user
        # Update the unread_messages_count to zero
        user.profile.unread_messages_count = 0
        user.profile.save()
        return Response({'message': 'Unread message count cleared.'}, status=status.HTTP_200_OK)


class ClearUnreadNotificationsCount(APIView):
    def post(self, request):
        user = request.user
        user.profile.unread_notifications_count = 0
        user.profile.save()
        return Response({'message': 'Unread notification count cleared.'}, status=status.HTTP_200_OK)
