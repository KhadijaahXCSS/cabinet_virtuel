from .models import User
from .serializers import UserSerializer
from rest_framework import viewsets
from django.shortcuts import get_object_or_404
from rest_framework.response import Response


class UserViewSet(viewsets.ViewSet):

    """ViewSet pour gerer les utilisateurs."""

    def list(self, request):
        """Liste tous les utilisateurs."""
        queryset = User.objects.all()
        serializer = UserSerializer(queryset, many=True)
        return Response(serializer.data)
    
    def retrieve(self, request, pk=None):
        """Recupere un utilisateur par son ID."""
        queryset = User.objects.all()
        user = get_object_or_404(queryset, pk=pk)
        serializer = UserSerializer(user)
        return Response(serializer.data)
    def create(self, request):
        """Creer un nouvel utilisateur."""
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(UserSerializer(user).data, status=201)
        return Response(serializer.errors, status=400)

    def update(self, request, pk=None):
        """Met a jour un utilisateur existant."""
        user = get_object_or_404(User, pk=pk)
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            user = serializer.save()
            return Response(UserSerializer(user).data)
        return Response(serializer.errors, status=400)
    def destroy(self, request, pk=None):
        """Supprime un utilisateur."""
        user = get_object_or_404(User, pk=pk)
        user.delete()
        return Response(status=204)
    