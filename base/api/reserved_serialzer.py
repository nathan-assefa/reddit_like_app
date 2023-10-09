from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from .models import (
    Community,
    Post,
    PostLike,
    Comment,
    BookMarks,
    Messages
)
from django.contrib.auth.models import User


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']


class CommunitySerializer(ModelSerializer):
    members = UserSerializer(many=True, required=False)
    moderators = UserSerializer(many=True, required=False)

    class Meta:
        model = Community
        fields = '__all__'


class CommunityMembershipSerialzer(ModelSerializer):
    class Meta:
        model = Community
        fields = "__all__"


class CommentSerialization(ModelSerializer):
    # author = serializers.HiddenField(default=serializers.CurrentUserDefault())
    # Added
    # post = PostSerialization(many=False, required=False)
    class Meta:
        model = Comment
        fields = '__all__'


class PostSerialization(ModelSerializer):
    ''' Serializing post object '''
    author = serializers.HiddenField(default=serializers.CurrentUserDefault())

    comment_count = serializers.SerializerMethodField()
    voted_count = serializers.SerializerMethodField()
    like_count = serializers.SerializerMethodField()
    love_count = serializers.SerializerMethodField()

    upvoted_by = UserSerializer(many=True, read_only=True, required=False)
    downvoted_by = UserSerializer(many=True, read_only=True, required=False)
    bookmarks = UserSerializer(many=True, read_only=True, required=False)
    liked_by = UserSerializer(many=True, read_only=True, required=False)
    loved_by = UserSerializer(many=True, read_only=True, required=False)
    author = UserSerializer(many=False, read_only=True)
    community = CommunitySerializer(many=False, required=False)

    comments = CommentSerialization(many=True, read_only=True)

    class Meta:
        model = Post
        fields = '__all__'

    def get_comment_count(self, obj):
        # Calculate and return the count of comments for the post
        return obj.comments.count()

    def get_love_count(self, obj):
        # Calculage and return the count of love reaction for the post
        return obj.loved_by.count()

    def get_like_count(self, obj):
        # Calculate and return the count of likes for the post
        return obj.liked_by.count()

    def get_voted_count(self, obj):
        # Calculate and return the count of upvoted comments minus downvoted comments
        upvoted_count = obj.upvoted_by.count()
        downvoted_count = obj.downvoted_by.count()
        return upvoted_count - downvoted_count


class PostLikeSerializer(ModelSerializer):
    class Meta:
        model = PostLike
        fields = '__all__'


class BookMarksSerializer(ModelSerializer):
    user = UserSerializer(many=False)
    post = PostSerialization(many=False)

    class Meta:
        model = BookMarks
        fields = "__all__"


class MessageSerializer(serializers.ModelSerializer):
    sender = serializers.HiddenField(default=serializers.CurrentUserDefault())
    # recipient = UserSerializer(many=False)

    class Meta:
        model = Messages
        fields = "__all__"


class MarkMessageAsReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Messages
        fields = ('is_read',)
