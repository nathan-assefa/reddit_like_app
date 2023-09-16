from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from .models import(
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

class PostSerialization(ModelSerializer):
    ''' Serializing post object '''
    author = serializers.HiddenField(default=serializers.CurrentUserDefault())

    upvoted_by = UserSerializer(many=True, read_only=True, required=False)
    downvoted_by = UserSerializer(many=True, read_only=True, required=False)
    bookmarks = UserSerializer(many=True, read_only=True, required=False)
    liked_by = UserSerializer(many=True, read_only=True, required=False)
    # author = UserSerializer(many=False, read_only=True)
    # community = CommunitySerializer(many=False, required=False)

    class Meta:
        model = Post
        fields = '__all__'

class PostLikeSerializer(ModelSerializer):
    class Meta:
        model = PostLike
        fields = '__all__'

class CommentSerialization(ModelSerializer):
    author = serializers.HiddenField(default=serializers.CurrentUserDefault())
    class Meta:
        model = Comment
        fields = '__all__'

class BookMarksSerializer(ModelSerializer):
    user = UserSerializer(many=False)
    post = PostSerialization(many=False)
    class Meta:
        model = BookMarks
        fields = "__all__"


class MessageSerializer(serializers.ModelSerializer):
    sender = serializers.HiddenField(default=serializers.CurrentUserDefault())
    # sender = serializers.ReadOnlyField(source='sender.username')
    # recipient = UserSerializer(many=False)

    class Meta:
        model = Messages
        fields = "__all__"


class MarkMessageAsReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Messages
        fields = ('is_read',)