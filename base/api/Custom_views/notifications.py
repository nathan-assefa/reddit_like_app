# from rest_framework.generics import ListAPIView
# from rest_framework.permissions import IsAuthenticated
# from ..models import Notifications
# from ..serializers import NotificationSerializer


# class GetUserNotification(ListAPIView):
#     serializer_class = NotificationSerializer
#     permission_classes = [IsAuthenticated]

#     def get_queryset(self):
#         user = self.request.user

#         # Fetch all notifications where the recipient is the current user
#         return Notifications.objects.filter(recipient=user)

from rest_framework.views import APIView
from rest_framework.response import Response
from ..models import Notifications
from ..serializers import NotificationSerializer


class GetUserNotification(APIView):
    def get(self, request, format=None):
        user = request.user

        # Fetch all notifications where the recipient is the current user
        notifications = Notifications.objects.filter(
            recipient=user).order_by('-created_at')

        # Serialize the sorted notifications
        serialized_notifications = NotificationSerializer(
            notifications, many=True)

        return Response(serialized_notifications.data)
