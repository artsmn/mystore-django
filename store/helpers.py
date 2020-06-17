from rest_framework.response import Response


def approve_session(func):
    def wrapper(*args, **kwargs):

        request = args[1]

        if request.META.get('HTTP_SESSION_KEY'):
            return func(*args, *kwargs)
        else:
            return Response({"error": "header not specified"}, 400)

    return wrapper
