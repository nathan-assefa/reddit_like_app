from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ..models import BookMarks, Post
from ..serializers import BookMarksSerializer


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_bookmarks(request, user_id):
    try:
        bookmarks = BookMarks.objects.filter(user_id=user_id)
    except BookMarks.DoesNotExist:
        return Response({'error': 'Bookmarks not found for this user'}, status=404)

    serializer = BookMarksSerializer(bookmarks, many=True)
    return Response(serializer.data, status=200)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_bookmark(request):
    post_id = request.data.get('post_id')

    # Check if the post exists
    try:
        post = Post.objects.get(pk=post_id)
    except Post.DoesNotExist:
        return Response({'error': 'Post not found'}, status=404)

    # Check if a bookmark for this post already exists for the user
    existing_bookmark = BookMarks.objects.filter(
        user=request.user, post=post).first()

    if existing_bookmark:
        return Response({'message': 'This post is already bookmarked'}, status=400)

    # Create a new bookmark
    bookmark = BookMarks.objects.create(
        user=request.user,
        post=post
    )

    serializer = BookMarksSerializer(bookmark)
    return Response(serializer.data, status=201)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_bookmark(request, bookmark_id):
    try:
        bookmark = BookMarks.objects.get(id=bookmark_id, user=request.user)
    except BookMarks.DoesNotExist:
        return Response({'error': 'Bookmark not found'}, status=404)

    bookmark.delete()
    return Response({'message': 'Bookmark deleted successfully'}, status=204)
