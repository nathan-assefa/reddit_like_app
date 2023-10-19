from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from rest_framework.generics import ListAPIView, CreateAPIView
from django.db.models import Count

from rest_framework.permissions import IsAuthenticated

from base.api.serializers import (
    CommunitySerializer,
    PostSerialization,
    CommunityMembershipSerialzer
)
from base.api.models import (
    Community,
    Post,
    CommunityMembership
)
from ..permissions.community_auth import CommunityPermission


class CommunityList(APIView):
    '''
    This view has two purpose
    1. get method: to get all the community from the community table
    2. post method: to create a community and add it in the community table
    '''

    permission_classes = [CommunityPermission]

    def get(self, request, format=None):
        communities = Community.objects.all()

        serialized_communities = []

        for community in communities:
            posts = Post.objects.filter(
                community=community).order_by('-created_at')
            community_data = CommunitySerializer(community).data
            community_data['posts'] = PostSerialization(
                posts, many=True).data
            serialized_communities.append(community_data)

        return Response(serialized_communities)

    def post(self, request, format=None):
        serializer = CommunitySerializer(
            data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(owner=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CommunityDetail(APIView):
    '''
    This view perfoms four different operations
    1. get method: fetch a specific community based on its id
    2. put method: edit the whole fields of the rows of a community
    3. path method: edit the specific fields of the rows of a community
    4. delete: deletes a row
    '''

    permission_classes = [CommunityPermission]

    def get_object(self, pk):
        try:
            return Community.objects.get(id=pk)
        except:
            raise Http404

    def get(self, request, pk, format=False):
        community = self.get_object(pk)
        serializer = CommunitySerializer(community)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        community = self.get_object(pk)
        serializer = CommunitySerializer(community, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk, format=None):
        community = self.get_object(pk)
        serializer = CommunitySerializer(
            community, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=False):
        community = self.get_object(pk)

        community.delete()

        return Response('community deleted')


class CommunityListForOwnerOrMember(APIView):
    '''
    This view allows the owner and the member of the community to see
    only the communities they blong to
    '''

    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        user = User.objects.get(pk=user_id)

        # Fetch communities where the user is the owner
        owned_communities = Community.objects.filter(owner=user)

        # Fetch communities where the user is a member
        member_communities = Community.objects.filter(members=user)

        # Combine the two querysets to get unique communities
        communities = owned_communities.union(member_communities)

        serializer = CommunitySerializer(communities, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class TopCommunitiesView(ListAPIView):
    """ This view returns top communities based on their member"""
    serializer_class = CommunitySerializer

    def get_queryset(self):
        # Annotate the queryset with the count of members in each community
        queryset = Community.objects.annotate(
            member_count=Count('communitymembership'))

        # Order the communities by member count in descending order
        queryset = queryset.order_by('-member_count')

        # Get the top 10 communities
        top_communities = queryset[:10]

        return top_communities


class JoinOrLeaveCommunityView(CreateAPIView):
    """ This view lets a user to join and leave a community """
    serializer_class = CommunityMembershipSerialzer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        community_id = kwargs.get('community_id')
        user = request.user

        membership = CommunityMembership.objects.filter(
            user=user, community_id=community_id).first()
        if membership:
            # If the user is already a member, remove the membership
            membership.delete()
            # Indicate that the user is no longer a member
            member_status = False
        else:
            # If the user is not a member, create a new membership
            serializer = self.get_serializer(
                data={'user': user.id, 'community': community_id})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            # Indicate that the user is now a member
            member_status = True

        return Response({'member': member_status}, status=status.HTTP_201_CREATED)


class CommunityMembershipStatusView(APIView):
    """ This view gets the user status in a specific community """

    def get(self, request, community_id):
        user = request.user

        try:
            membership = CommunityMembership.objects.get(
                user=user, community_id=community_id)
            return Response({'member': True}, status=status.HTTP_200_OK)
        except CommunityMembership.DoesNotExist:
            return Response({'member': False}, status=status.HTTP_200_OK)
