from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet,ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from .tokens import get_tokens



@api_view(['GET'])
def hello_world(request):
    return Response({"message": "Hello, world!"})


class Authentication(GenericViewSet):
    
    # /auth/login
    @action(['POST'] , False)
    def login(self,request):
        # serializer ...
        # login logic 
        from .models import User
        user = User.objects.get(id=1)
        tokens = get_tokens(user)
        return Response({"tokens":tokens})
        
    
    
    @action(['POST'] , False)
    def signup(self,request):
        pass
    # serializer.save()