from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from base.api.serializers import CommunitySerializer, PostSerialization
from base.api.models import Community, Post
from .auth import IsAuthenticatedOrReadOnly


class CommunityList(APIView):
    '''
    This view has two purpose
    1. get method: to get all the community from the community table
    2. post method: to create a community and add it in the community table
    '''

    # permission_classes = [IsAuthenticatedOrReadOnly]

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
        serializer = CommunitySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
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

    permission_classes = [IsAuthenticatedOrReadOnly]

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
