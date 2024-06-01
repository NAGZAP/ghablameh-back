import jwt
from django.conf import settings


async def get_user_id(token):
    try:
        decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        return  decoded_token.get('user_id')
    
    except jwt.ExpiredSignatureError:
        raise Exception('Token has expired')
    
    except jwt.InvalidTokenError:
        raise Exception('Invalid token')