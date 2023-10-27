""" Handling users messaging """
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework import permissions
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView, ListAPIView, ListCreateAPIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q, Max
from django.contrib.auth.models import User

from ..models import Messages

from ..serializers import (
    MessageSerializer,
    MarkMessageAsReadSerializer
)


class SendMessageView(CreateAPIView):
    # queryset = Messages.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        recipient_id = serializer.validated_data['recipient'].id

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

        messages = Messages.objects.filter(
            Q(recipient=self.request.user, sender_id=user_id) | Q(
                sender=self.request.user, recipient_id=user_id)
        ).order_by('created_at')

        return messages
        # Retrieve messages sent to or received from the user
        # this code is reponsible for fetching messages between two users.
        # return Messages.objects.filter(
        #     recipient=self.request.user, sender_id=user_id
        # ) | Messages.objects.filter(
        #     sender=self.request.user, recipient_id=user_id
        # ).order_by('-create_at')
        # This is another option to handel the above code
        # return Messages.objects.filter(
        #     (Q(recipient=self.request.user) & Q(sender_id=user_id)) |
        #     (Q(sender=self.request.user) & Q(recipient_id=user_id))
        # )

        """
        If you're viewing a chat between "User A" and "User B," you want
        to see only messages sent between these two users. The condition
        ensures that messages are retrieved where the authenticated user
        (you, "User A") is either the sender or the recipient and the other
        user ("User B") is the corresponding sender or recipient.
        This way, we're effectively filtering the messages to show only
        the conversation between "User A" and "User B."
        """


class GetMostRecentMessageView(ListAPIView):
    """ This view returns the most recent messages from each sender """
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        # Annotate each message with the maximum created_at timestamp
        queryset = Messages.objects.filter(
            recipient=user
        ).values('sender').annotate(max_created_at=Max('created_at'))

        # Filter out the most recent message from each sender
        most_recent_message_ids = []
        for message in queryset:
            sender = message['sender']
            max_created_at = message['max_created_at']
            most_recent_message = Messages.objects.filter(
                recipient=user, sender=sender, created_at=max_created_at
            ).first()
            if most_recent_message:
                most_recent_message_ids.append(most_recent_message.id)

        return Messages.objects.filter(id__in=most_recent_message_ids).order_by('-created_at')


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
