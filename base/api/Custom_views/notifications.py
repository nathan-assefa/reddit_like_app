from rest_framework.views import APIView
from rest_framework.response import Response
from ..models import Notifications
from ..serializers import NotificationSerializer
from rest_framework.generics import UpdateAPIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated


class GetUserNotification(APIView):
    def get(self, request, format=None):
        user = request.user

        # Fetch all notifications where the recipient is the current user
        notifications = Notifications.objects.filter(
            recipient=user).order_by('-updated_at')

        # Serialize the sorted notifications
        serialized_notifications = NotificationSerializer(
            notifications, many=True)

        return Response(serialized_notifications.data)


class MarkNotificationAsRead(UpdateAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Notifications.objects.filter(recipient=self.request.user, is_read=False)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_read = True
        instance.save()
        return Response({'message': 'Notification marked as read'}, status=status.HTTP_200_OK)
