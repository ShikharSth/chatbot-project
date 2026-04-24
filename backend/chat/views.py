import requests
from django.conf import settings
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Conversation, Message
from .serializers import ConversationSerializer
from .knowledge_loader import load_all_knowledge


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

        # Load knowledge files
        knowledge = load_all_knowledge()

        # Build messages for Ollama
        ollama_messages = [
            {
                "role": "system",
                "content": f"""
You are a helpful assistant.

Use company knowledge below to answer accurately.

COMPANY KNOWLEDGE:
{knowledge}

Rules:
1. If answer exists in company knowledge, use it accurately.
2. If answer is not found in company knowledge, politely say it is not available.
3. Do not invent company-related answers.
4. If question is unrelated to company knowledge, answer from your general knowledge.
5. Always return a meaningful response.
6. Never return an empty response.
7. Keep responses clear and professional.
"""
            }
        ]

        # Add only recent valid history
        recent_messages = (
            conversation.messages
            .exclude(content="")
            .order_by("-created_at")[:8][::-1]
        )

        for msg in recent_messages:
            if msg.role in ["user", "assistant", "system"] and msg.content.strip():
                ollama_messages.append(
                    {
                        "role": msg.role,
                        "content": msg.content.strip(),
                    }
                )

        payload = {
            "model": settings.OLLAMA_MODEL,
            "messages": ollama_messages,
            "stream": False,
        }

        try:
            r = requests.post(
                f"{settings.OLLAMA_BASE_URL}/api/chat",
                json=payload,
                timeout=300,
            )

            r.raise_for_status()

            data = r.json()

        except requests.RequestException as exc:
            return Response(
                {"detail": f"Ollama request failed: {str(exc)}"},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        assistant_text = data.get("message", {}).get("content", "").strip()

        # Prevent blank responses
        if not assistant_text:
            assistant_text = "Sorry, I could not generate a response."

        # Save assistant reply
        Message.objects.create(
            conversation=conversation,
            role="assistant",
            content=assistant_text,
        )

        conversation.refresh_from_db()

        return Response(ConversationSerializer(conversation).data)





# import requests
# from django.conf import settings
# from rest_framework import status, viewsets
# from rest_framework.decorators import action
# from rest_framework.response import Response
# from .knowledge_loader import load_all_knowledge

# from .models import Conversation, Message
# from .serializers import ConversationSerializer


# class ConversationViewSet(viewsets.ModelViewSet):
#     queryset = Conversation.objects.prefetch_related("messages").all().order_by("-created_at")
#     serializer_class = ConversationSerializer

#     def perform_create(self, serializer):
#         serializer.save()

#     @action(detail=True, methods=["post"], url_path="chat")
#     def chat(self, request, pk=None):
#         conversation = self.get_object()
#         user_text = (request.data.get("message") or "").strip()

#         if not user_text:
#             return Response(
#                 {"detail": "Message cannot be empty."},
#                 status=status.HTTP_400_BAD_REQUEST,
#             )

#         # Save user message
#         Message.objects.create(
#             conversation=conversation,
#             role="user",
#             content=user_text,
#         )

#         knowledge = load_all_knowledge()
#         # Build Ollama messages from history
#         ollama_messages = [
#             {
#                 "role": "system",
#                 "content": f"""
#                 You are a helpful assistant.

#                 Use company knowledge below to answer accurately.

#                 {knowledge}

#                 If answer not found, say politely not available. Do not make up answers for company related questions.

#                 Or in case of questions is not about knowledge, answer based on your general knowledge.

#                 Do not return empty response.
#                 """
#             }
#         ]

#             # {
#             #     "role": "system",
#             #     "content": "You are a helpful chatbot. Be concise and clear.",
#             # }

#         for msg in conversation.messages.all():
#             ollama_messages.append(
#                 {
#                     "role": msg.role,
#                     "content": msg.content,
#                 }
#             )

#         payload = {
#             "model": settings.OLLAMA_MODEL,
#             "messages": ollama_messages,
#             "stream": False,
#         }

#         try:
#             r = requests.post(
#                 f"{settings.OLLAMA_BASE_URL}/api/chat",
#                 json=payload,
#                 timeout=120,
#             )
#             r.raise_for_status()
#         except requests.RequestException as exc:
#             return Response(
#                 {"detail": f"Ollama request failed: {str(exc)}"},
#                 status=status.HTTP_502_BAD_GATEWAY,
#             )

#         data = r.json()
#         assistant_text = data["message"]["content"]

#         Message.objects.create(
#             conversation=conversation,
#             role="assistant",
#             content=assistant_text,
#         )

#         conversation.refresh_from_db()
#         return Response(ConversationSerializer(conversation).data)
    