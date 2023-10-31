from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from .models import (
    Community,
    Post,
    PostLike,
    Comment,
    BookMarks,
    Messages,
    Notifications,
    Profile,
    CommunityMembership
)
from django.contrib.auth.models import User


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = "__all__"


class UserSerializer(ModelSerializer):
    profile = ProfileSerializer(many=False, required=False)

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email', 'profile']


class CommunitySerializer(ModelSerializer):
    members = UserSerializer(many=True, required=False)
    moderators = UserSerializer(many=True, required=False)

    member_count = serializers.SerializerMethodField()

    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Community
        fields = '__all__'

    def get_member_count(self, obj):
        return obj.members.count()


class CommunityMembershipSerialzer(ModelSerializer):
    class Meta:
        model = CommunityMembership
        fields = "__all__"


class CommentSerialization(ModelSerializer):
    # author = serializers.HiddenField(default=serializers.CurrentUserDefault())
    author = UserSerializer(many=False, required=False)

    upvoted_by = UserSerializer(many=True, read_only=True, required=False)
    downvoted_by = UserSerializer(many=True, read_only=True, required=False)
    likes = UserSerializer(many=True, read_only=True, required=False)
    loves = UserSerializer(many=True, read_only=True, required=False)

    voted_count = serializers.SerializerMethodField()
    like_count = serializers.SerializerMethodField()
    love_count = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = '__all__'
        ordering = ['-created_at']

    def get_love_count(self, obj):
        # Calculage and return the count of love reaction for the post
        return obj.loves.count()

    def get_like_count(self, obj):
        # Calculate and return the count of likes for the post
        return obj.likes.count()

    def get_voted_count(self, obj):
        # Calculate and return the count of upvoted comments minus downvoted comments
        upvoted_count = obj.upvoted_by.count()
        downvoted_count = obj.downvoted_by.count()
        return upvoted_count - downvoted_count


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

    # comments = CommentSerialization(many=True, read_only=True)

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

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get('request')

        # Include the sender in the serialized data when retrieving messages
        if request and not request.method == 'POST':
            data['sender'] = UserSerializer(instance.sender).data
            data['recipient'] = UserSerializer(instance.recipient).data

        return data


class MarkMessageAsReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Messages
        fields = ('is_read',)


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notifications
        fields = "__all__"


class ProfileSerializer(serializers.ModelSerializer):
    # user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    user = UserSerializer(many=False)

    followers_count = serializers.SerializerMethodField()
    following_count = serializers.SerializerMethodField()

    bookmarks = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = "__all__"

    def get_followers_count(self, obj):
        # Calculate and return the count of comments for the post
        return obj.followers.count()

    def get_following_count(self, obj):
        # Calculate and return the count of comments for the post
        return obj.following.count()

    def get_bookmarks(self, obj):
        # Retrieve all bookmarks for the associated user
        user = obj.user
        bookmarks = BookMarks.objects.filter(user=user)
        bookmark_data = BookMarksSerializer(bookmarks, many=True).data
        return bookmark_data
