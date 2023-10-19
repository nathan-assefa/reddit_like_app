from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

import random

from ..permissions.comment_auth import (
    IsAuthenticatedUser,
    IsCommnentOwner
)
from base.api.serializers import CommentSerialization
from .notification_content import comment_notification_sentences
from base.api.models import (
    Post,
    Comment,
    Notifications
)


class CommentList(APIView):
    ''' Implementing get and post request for comments '''

    permission_classes = [IsAuthenticatedUser]

    def get(self, request, post_id, format=None):
        # Get comments related to a specific post
        comments = Comment.objects.filter(post_id=post_id)
        serializer = CommentSerialization(comments, many=True)
        return Response(serializer.data)

    def post(self, request, post_id, format=None):
        # Ensure the post with post_id exists
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return Response({'error': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)

        mutable_data = request.data.copy()
        mutable_data['post'] = post_id

        serializer = CommentSerialization(
            data=mutable_data, context={'request': request})

        if serializer.is_valid():
            # Set the post and author for the comment
            serializer.save(post=post, author=request.user)

            # Check if this is a reply to an existing comment
            if serializer.validated_data.get('parent_comment'):
                parent_comment = serializer.validated_data['parent_comment']
                parent_comment_owner = parent_comment.author

                # Notify the owner of the parent comment about the reply
                Notifications.objects.create(
                    recipient=parent_comment_owner,
                    sender=request.user,
                    notification_type="NewCommentReply",
                    content=f'Your comment on "{post.title}" has a new reply by {request.user.username.capitalize()}. "{post.content}"'
                )

            else:
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

    permission_classes = [IsCommnentOwner]

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
