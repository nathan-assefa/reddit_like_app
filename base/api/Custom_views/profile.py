from rest_framework.generics import RetrieveAPIView, UpdateAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated
from ..models import Profile
from ..serializers import ProfileSerializer
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404


class GetUserProfile(RetrieveAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user.profile


class GetProfileList(ListAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Return all profiles
        return Profile.objects.all()


class UpdateProfile(UpdateAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user.profile


class ToggleFollowUserAPIView(UpdateAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer

    def update(self, request, *args, **kwargs):
        user_to_toggle = get_object_or_404(Profile, id=self.kwargs['user_id'])
        current_user_profile = self.request.user.profile

        if current_user_profile.following.filter(id=user_to_toggle.id).exists():
            # User is already following, so unfollow
            current_user_profile.following.remove(user_to_toggle)
            return Response({'message': 'You have unfollowed this user.', 'following': False}, status=status.HTTP_200_OK)
        else:
            # User is not following, so follow
            current_user_profile.following.add(user_to_toggle)
            return Response({'message': f'You are now following {user_to_toggle.user.username}.', 'following': True}, status=status.HTTP_200_OK)


class FollowStateAPIView(RetrieveAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer

    def retrieve(self, request, user_id):
        current_user_profile = self.request.user.profile
        user_to_check = get_object_or_404(Profile, id=user_id)

        is_following = current_user_profile.following.filter(
            id=user_to_check.id).exists()

        return Response({'is_following': is_following}, status=status.HTTP_200_OK)
