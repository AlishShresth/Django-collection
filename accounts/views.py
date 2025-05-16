from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import CustomUser, Profile
from .serializers import UserSerializer, ProfileSerializer, RegisterSerializer
from .permissions import IsOwnerOrReadOnly, IsAdminUser


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.select_related("user").all()
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        if self.request.user.is_superuser or self.request.user.is_staff:
            return Profile.objects.select_related("user").all()
        return Profile.objects.select_related("user").filter(user=self.request.user)

    def perform_update(self, serializer):
        serializer.save(user=self.request.user)


class UserListView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        users = CustomUser.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)


# from django.shortcuts import render, redirect
# from .forms import RegisterForm


# def register(request):
#     if request.method == "POST":
#         form = RegisterForm(request.POST)
#         if form.is_valid():
#             form.save()
#             return redirect("login")
#     else:
#         form = RegisterForm()
#     return render(request, "accounts/register.html", {"form": form})


# def home(request):
#     return render(request, "home.html")
