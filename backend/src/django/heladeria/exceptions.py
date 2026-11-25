from django.core.exceptions import ValidationError as DjangoValidationError
from django.db.models import ProtectedError, RestrictedError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler


def manejar_excepciones(exc, context):
    """Traduce errores de dominio de Django a respuestas HTTP en lugar de un 500."""
    response = exception_handler(exc, context)
    if response is not None:
        return response

    if isinstance(exc, DjangoValidationError):
        if hasattr(exc, 'error_dict'):
            return Response(exc.message_dict, status=status.HTTP_400_BAD_REQUEST)
        return Response({'detail': ' '.join(exc.messages)}, status=status.HTTP_400_BAD_REQUEST)

    if isinstance(exc, (ProtectedError, RestrictedError)):
        return Response(
            {'detail': 'No se puede eliminar el registro porque tiene datos relacionados.'},
            status=status.HTTP_409_CONFLICT,
        )

    return None
