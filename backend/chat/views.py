import requests
from django.conf import settings
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Conversation, Message
from .serializers import ConversationSerializer


class ConversationViewSet(viewsets.ModelViewSet):
    queryset = Conversation.objects.prefetch_related("messages").all().order_by("-created_at")
    serializer_class = ConversationSerializer

    def perform_create(self, serializer):
        serializer.save()

    @action(detail=True, methods=["post"], url_path="chat")
    def chat(self, request, pk=None):
        conversation = self.get_object()
        user_text = (request.data.get("message") or "").strip()

        if not user_text:
            return Response(
                {"detail": "Message cannot be empty."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Save user message
        Message.objects.create(
            conversation=conversation,
            role="user",
            content=user_text,
        )

        # Build Ollama messages from history
        ollama_messages = [
            {
                "role": "system",
                "content": "You are a helpful chatbot. Be concise and clear.",
            }
        ]

        for msg in conversation.messages.all():
            ollama_messages.append(
                {
                    "role": msg.role,
                    "content": msg.content,
                }
            )

        payload = {
            "model": settings.OLLAMA_MODEL,
            "messages": ollama_messages,
        }

        try:
            r = requests.post(
                f"{settings.OLLAMA_BASE_URL}/api/chat",
                json=payload,
                timeout=120,
            )
            r.raise_for_status()
        except requests.RequestException as exc:
            return Response(
                {"detail": f"Ollama request failed: {str(exc)}"},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        data = r.json()
        assistant_text = data["message"]["content"]

        Message.objects.create(
            conversation=conversation,
            role="assistant",
            content=assistant_text,
        )

        conversation.refresh_from_db()
        return Response(ConversationSerializer(conversation).data)
    