from django.utils import timezone
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import POSSession
from .serializers import POSSessionSerializer, OpenSessionSerializer, CloseSessionSerializer

class OpenSessionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Block if user already has an open session
        existing = POSSession.objects.filter(
            user=request.user, status='open'
        ).first()
        if existing:
            return Response(
                {'error': f'You already have an open session (ID: {existing.id}). Close it first.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = OpenSessionSerializer(data=request.data)
        if serializer.is_valid():
            session = serializer.save(user=request.user, status='open')
            return Response(
                POSSessionSerializer(session).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CloseSessionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            session = POSSession.objects.get(pk=pk, user=request.user)
        except POSSession.DoesNotExist:
            return Response({'error': 'Session not found.'}, status=status.HTTP_404_NOT_FOUND)

        if session.status == 'closed':
            return Response({'error': 'Session is already closed.'}, status=status.HTTP_400_BAD_REQUEST)

        session.status = 'closed'
        session.closed_at = timezone.now()
        if request.data.get('note'):
            session.note = request.data.get('note')
        session.save()

        return Response(POSSessionSerializer(session).data, status=status.HTTP_200_OK)


class CurrentSessionView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        session = POSSession.objects.filter(
            user=request.user, status='open'
        ).first()
        if not session:
            return Response({'message': 'No open session.'}, status=status.HTTP_200_OK)
        return Response(POSSessionSerializer(session).data, status=status.HTTP_200_OK)


class SessionListView(generics.ListAPIView):
    serializer_class = POSSessionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return POSSession.objects.filter(user=request.user).order_by('-opened_at')

    def get_queryset(self):
        return POSSession.objects.filter(
            user=self.request.user
        ).order_by('-opened_at')


class SessionDetailView(generics.RetrieveAPIView):
    serializer_class = POSSessionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return POSSession.objects.filter(user=self.request.user)