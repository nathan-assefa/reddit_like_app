from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from ..models import Profile
from ..serializers import ProfileSerializer


class GetUserProfile(RetrieveAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user.profile


'''
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Profile
from .serializers import ProfileSerializer  # You need to create this serializer

class GetAuthenticatedUserProfile(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        # Get the authenticated user's profile
        try:
            profile = Profile.objects.get(user=request.user)
        except Profile.DoesNotExist:
            # Handle the case where the profile does not exist
            return Response(
                {"detail": "Profile does not exist."},
                status=status.HTTP_NOT_FOUND
            )

        # Serialize the profile data
        serializer = ProfileSerializer(profile)

        return Response(serializer.data, status=status.HTTP_200_OK)

'''
