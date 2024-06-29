from rest_framework import views
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from ..models import LoginHistory, User
from ..serializers import LoginHistorySerializer


class UserLoginLogs(ListAPIView):
    # permission_classes = [IsAuthenticated]
    serializer_class = LoginHistorySerializer

    def get_queryset(self):
        # return LoginHistory.objects.filter(user=self.request.user)
        return LoginHistory.objects.all()


class UserDetailView(views.APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_object = User.objects.prefetch_related("userroles_set").get(request.user)

        ...
