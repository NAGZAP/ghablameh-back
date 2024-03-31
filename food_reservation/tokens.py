from rest_framework_simplejwt.tokens import RefreshToken


def get_tokens(user):
    refresh = RefreshToken.for_user(user)
    return {
        "access":str(refresh.access_token),
        "refresh":str(refresh)
    }