from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import PostLike, CommentLike, Notifications
from django.contrib.auth.models import User
from .models import (
    PostLike,
    CommentLike,
    PostDownvoted,
    PostLove,
    PostUpvoted,
    CommentDownvoted,
    CommentLove,
    CommentUpvoted,
    Notifications,
    Messages,
    Profile
)

def create_notification(sender, instance, created, notification_type, content_fn):
    if created:
        recipient = None
        content = content_fn(instance)

        if sender == PostLike:
            # If it's a PostLike, set the recipient to the author of the post
            recipient = instance.post.author
        elif sender == PostLove:
            recipient = instance.post.author
        elif sender == PostUpvoted:
            recipient = instance.post.author
        elif sender == PostDownvoted:
            recipient = instance.post.author


        elif sender == CommentLike:
            """ This is to handle the comment event """
            recipient = instance.comment.author
        elif sender == CommentLove:
            recipient = instance.comment.author
        elif sender == CommentUpvoted:
            recipient = instance.comment.author
        elif sender == CommentDownvoted:
            recipient = instance.comment.author


        if recipient:
            Notifications.objects.create(
                recipient=recipient,
                sender=instance.user,
                notification_type=notification_type,
                content=content,
            )


""" ****** This is to handle post reactions ******** """
@receiver(post_save, sender=PostLike)
def create_post_like_notification(sender, instance, created, **kwargs):
    def get_post_like_content(post_like):
        return f"{post_like.user.username} liked your post: '{post_like.post.title}'"

    create_notification(sender, instance, created, "PostLike", get_post_like_content)


@receiver(post_save, sender=PostLove)
def create_comment_love_notification(sender, instance, created, **kwargs):
    def get_post_love_content(post_love):
        return f"{post_love.user.username} reacted to your post: '{post_love.post.content}'"

    create_notification(sender, instance, created, "PostLove", get_post_love_content)


@receiver(post_save, sender=PostUpvoted)
def create_post_upvote_notification(sender, instance, created, **kwargs):
    def get_post_upvote_content(post_upvote):
        return f"{post_upvote.user.username} upvoted your post: '{post_upvote.post.content}'"

    create_notification(sender, instance, created, "PostUpvoted", get_post_upvote_content)


@receiver(post_save, sender=PostDownvoted)
def create_post_downvote_notification(sender, instance, created, **kwargs):
    def get_post_downvote_content(post_downvote):
        return f"{post_downvote.user.username} downvoted your post: '{post_downvote.post.content}'"

    create_notification(sender, instance, created, "PostDownvoted", get_post_downvote_content)



""" ****** This is to handle comment reactions ******** """
@receiver(post_save, sender=CommentLike)
def create_comment_like_notification(sender, instance, created, **kwargs):
    def get_comment_like_content(comment_like):
        return f"{comment_like.user.username} liked your comment: '{comment_like.comment.content}'"

    create_notification(sender, instance, created, "CommentLike", get_comment_like_content)


@receiver(post_save, sender=CommentLove)
def create_comment_love_notification(sender, instance, created, **kwargs):
    def get_comment_love_content(comment_love):
        return f"{comment_love.user.username} reacted to your comment: '{comment_love.comment.content}'"

    create_notification(sender, instance, created, "CommentLove", get_comment_love_content)


@receiver(post_save, sender=CommentUpvoted)
def create_comment_upvote_notification(sender, instance, created, **kwargs):
    def get_comment_upvote_content(comment_upvote):
        return f"{comment_upvote.user.username} upvoted your comment: '{comment_upvote.comment.content}'"

    create_notification(sender, instance, created, "CommentUpvoted", get_comment_upvote_content)


@receiver(post_save, sender=CommentDownvoted)
def create_comment_downvote_notification(sender, instance, created, **kwargs):
    def get_comment_downvote_content(comment_downvote):
        return f"{comment_downvote.user.username} downvoted your comment: '{comment_downvote.comment.content}'"

    create_notification(sender, instance, created, "CommentDownvoted", get_comment_downvote_content)

# Create a profile for each new user
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

# Save the user's profile when the user is saved
@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

# @receiver(post_save, sender=Messages)
# def update_unread_message_count(sender, instance, created, **kwargs):
#     if created:
#         # Increment the unread_messages_count for the recipient's profile
#         recipient_profile = instance.recipient.profile
#         recipient_profile.unread_messages_count += 1
#         recipient_profile.save()

@receiver(post_save, sender=Messages)
def update_unread_message_count(sender, instance, created, **kwargs):
    if created and instance.recipient != instance.sender:
        # Increment the unread_messages_count for the recipient's profile
        recipient_profile = instance.recipient.profile
        recipient_profile.unread_messages_count += 1
        recipient_profile.save()