from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import random

from ..permissions.post_auth import IsCommunityMemberOrOwner, IsPostOwner
from base.api.serializers import (
    PostSerialization,
    CommentSerialization
)
from .notification_content import post_notification_sentences
from base.api.models import (
    Post,
    Notifications,
    Comment
)


class CommunityPostList(APIView):
    permission_classes = [IsCommunityMemberOrOwner]

    def get(self, request, community_id, format=None):
        # Filter posts by community_id
        posts = Post.objects.filter(community_id=community_id)
        serializer = PostSerialization(posts, many=True)
        return Response(serializer.data)

    def post(self, request, community_id, format=None):
        # Add the community_id to the request data before serializing
        # request.data['community'] = community_id
        # serializer = PostSerialization(
        #     data=request.data, context={'request': request})

        # if serializer.is_valid():
        #     post = serializer.save(author=request.user)

        mutable_data = request.data.copy()

        serializer = PostSerialization(
            data=mutable_data, context={'request': request})

        if serializer.is_valid():
            post = serializer.save(author=request.user,
                                   community_id=community_id)

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

    permission_classes = [IsPostOwner]

    def get_object(self, pk):
        try:
            return Post.objects.get(id=pk)
        except:
            raise Http404

    def get(self, request, pk, format=False):
        post = self.get_object(pk)
        comments = Comment.objects.filter(
            post=post).order_by('-created_at')
        post_data = PostSerialization(post).data
        post_data['comments'] = CommentSerialization(
            comments, many=True).data
        return Response(post_data)

        # serializer = PostSerialization(post)
        # return Response(serializer.data)

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


class PostList(APIView):
    ''' getting all the posts '''

    def get(self, request, format=None):
        posts = Post.objects.all()
        posts = Post.objects.order_by('-created_at')

        serialized_posts = []

        for post in posts:
            comments = Comment.objects.filter(
                post=post).order_by('-created_at')
            post_data = PostSerialization(post).data
            post_data['comments'] = CommentSerialization(
                comments, many=True).data
            serialized_posts.append(post_data)

        return Response(serialized_posts)
