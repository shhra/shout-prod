from rest_framework.views import exception_handler
from rest_framework import status


def core_exception_handler(exc, context):
    # Using default exception handler in django rest framework
    response = exception_handler(exc, context)
    # Definig custom handlers
    handlers = {
        'NotFound': _handle_not_found_error,
        'ValidationError': _handle_generic_error
    }

    #  getting the type of exception.
    exception_class = exc.__class__.__name__

    # checking if the exception is in our defined type
    if exception_class in handlers:
        return handlers[exception_class](exc, context, response)
    
    # returning default exception handler.
    return response


def _handle_generic_error(exc, context, response):
    response.data = {
            'validation_error': response.data
    }
    response.status_code = status.HTTP_400_BAD_REQUEST
    return response


def _handle_not_found_error(exc, context, response):
    view = context.get('view', None)

    if view and hasattr(view, 'queryset') and view.queryset is not None:
        error_key = view.queryset.model._meta.verbose_name

        response.data = {
                'error_message': {
                    error_key: response.data['detail']
                    }
            }
        response.status_code = status.HTTP_400_BAD_REQUEST
    else:
        response = _handle_generic_error(exc, context, response)

    return response

