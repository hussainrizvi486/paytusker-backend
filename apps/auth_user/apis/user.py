from rest_framework import views, response
from rest_framework.response import Response
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from ..models import LoginHistory, User
from ..serializers import LoginHistorySerializer, UserProfileSerializer


class UserLoginLogs(ListAPIView):
    # permission_classes = [IsAuthenticated]
    serializer_class = LoginHistorySerializer

    def get_queryset(self):
        # return LoginHistory.objects.filter(user=self.request.user)
        return LoginHistory.objects.all()




class UserProfileDetail(views.APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_queryset = User.objects.get(id=request.user.id)
        serializer = UserProfileSerializer(user_queryset)
        return Response(data=serializer.data)
        ...


# class UserProfile(views.)
