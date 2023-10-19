from django.db import models
from django.contrib.auth.models import User

# from django.contrib.auth.models import AbstractUser


# class User(AbstractUser):
#     name = models.CharField(max_length=200, null=True)
#     email = models.EmailField(unique=True, null=True)
#     bio = models.TextField(null=True)

class Community(models.Model):
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='communities_owened'
    )

    members = models.ManyToManyField(
        User, through='CommunityMembership', related_name='communities_joined'
    )

    moderators = models.ManyToManyField(
        User, related_name='communities_moderated', blank=True
    )

    def __str__(self):
        return self.name


class CommunityMembership(models.Model):
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    community = models.ForeignKey(Community, on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.community.name


class Post(models.Model):
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=255)
    content = models.TextField()

    community = models.ForeignKey(
        Community, on_delete=models.CASCADE, related_name='posts'
    )

    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='posts_authored'
    )

    upvoted_by = models.ManyToManyField(
        User, through="PostUpvoted", related_name='upvoted_posts', blank=True
    )

    downvoted_by = models.ManyToManyField(
        User, through="PostDownvoted", related_name='downvoted_posts', blank=True
    )

    bookmarks = models.ManyToManyField(
        User, related_name='bookmarked_posts', blank=True
    )

    liked_by = models.ManyToManyField(
        User, through='PostLike', related_name='liked_posts', blank=True
    )

    loved_by = models.ManyToManyField(
        User, through='PostLove', related_name='loved_posts', blank=True
    )

    def __str__(self):
        return self.title


class Comment(models.Model):
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    content = models.TextField()

    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name='comments'
    )

    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='comments_authored'
    )

    # Self-referential many-to-one relationship for parent comment (if a reply)
    parent_comment = models.ForeignKey(
        'self', on_delete=models.CASCADE, null=True, blank=True
    )

    upvoted_by = models.ManyToManyField(
        User, through="CommentUpvoted", related_name='upvoted_comments', blank=True
    )

    downvoted_by = models.ManyToManyField(
        User, through="CommentDownvoted", related_name='downvoted_comments', blank=True
    )

    likes = models.ManyToManyField(
        User, through='CommentLike', related_name='liked_comments', blank=True
    )

    loves = models.ManyToManyField(
        User, through='CommentLove', related_name='loved_comments', blank=True
    )

    def __str__(self):
        return self.content


class Profile(models.Model):
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='profile')

    profile_picture = models.ImageField(
        upload_to='profile_pictures/', blank=True, null=True
    )

    bio = models.TextField(null=True, blank=True)
    website = models.URLField(max_length=200, blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    birthdate = models.DateField(null=True, blank=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)

    unread_messages_count = models.IntegerField(default=0)

    unread_notifications_count = models.IntegerField(default=0)

    def __str__(self):
        return self.user.username


class Messages(models.Model):
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    sender = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='sent_messages'
    )

    recipient = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='received_messages'
    )

    # subject = models.CharField(max_length=255)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.sender.username.capitalize()} sends you a new message to {self.recipient.username.capitalize()}: {self.content}"


class Notifications(models.Model):
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    recipient = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='notifications_received'
    )

    sender = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True,
        blank=True, related_name='notifications_sent'
    )

    notification_type = models.CharField(max_length=255)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return self.content


class BookMarks(models.Model):
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='user_bookmarks'
    )

    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name='post_bookmarks'
    )

    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.post.content


class CommentLike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} liked comment {self.comment.id}"


class PostLike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} liked post {self.post.id}"


class PostLove(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} reacted comment {self.post.id}"


class PostUpvoted(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} upvoted post {self.post.id}"


class PostDownvoted(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} downvoted post {self.post.id}"


class CommentUpvoted(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} upvoted comment {self.comment.id}"


class CommentDownvoted(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} downvoted comment {self.comment.id}"


class CommentLove(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} downvoted comment {self.comment.id}"
