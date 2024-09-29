# for API view Decorator
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Person
from .serializers import PersonSerializer, LoginSerializer, RegisterSerializer

# for API view class
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Person
from .serializers import PersonSerializer

# for model view sets
from rest_framework import viewsets


# for signup and login
from django.contrib.auth import authenticate
from rest_framework.permissions import AllowAny
from django.views.decorators.csrf import csrf_exempt
from rest_framework.authtoken.models import Token


# For Authentication and showing data only to authorized users
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication, BasicAuthentication


# For Pagination
from django.core.paginator import Paginator
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


# For Actions
from rest_framework.decorators import action 


class RegisterAPI(APIView):
    permission_classes = [AllowAny]

    @csrf_exempt


    def post(self, request):
        data = request.data 
        serializer = RegisterSerializer(data=data)

        # Check if serializer is valid
        if serializer.is_valid():
            serializer.save()  # Save user data
            return Response({
                'status': True,
                'message': 'User Created'
            }, status=status.HTTP_201_CREATED)
        
        # If serializer is not valid, return errors
        return Response({
            'status': False,
            'message': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
        

class LoginAPI(APIView):
    def post(self, request):
        data= request.data 
        serializer = LoginSerializer(data =data)
        if not serializer.is_valid():
            return Response({
                'status' : False,
                'message' : serializer.errors
            }, status.HTTP_400_BAD_REQUEST)
        
        user = authenticate(username = serializer.data['username'],
                           password = serializer.data['password'])
        
        if not user:
            return Response({
                'status' : False,
                'message' : 'Invalid Credentials'
            }, status.HTTP_400_BAD_REQUEST)
        
        token, _ = Token.objects.get_or_create(user=user)
        return Response({
                'status': True,
                'message': 'User Successfully Logged In',
                'token' : str(token)
            }, status=status.HTTP_201_CREATED)



@api_view(['GET', 'POST', 'PUT', 'PATCH', 'DELETE'])
def person(request, id=None):
    if request.method == 'GET':
        if id:
            try:
                # Fetch the specific person with a given id
                person = Person.objects.get(id=id)
                serializer = PersonSerializer(person)
                return Response(serializer.data)
            except Person.DoesNotExist:
                return Response({'error': 'Person not found'}, status=status.HTTP_404_NOT_FOUND)
        else:
            # Fetch all persons
            persons = Person.objects.all()
            serializer = PersonSerializer(persons, many=True)
            return Response(serializer.data)

    elif request.method == 'POST':
        serializer = PersonSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'PUT':
        if not id:
            return Response({'error': 'ID is required for PUT requests'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            person = Person.objects.get(id=id)
        except Person.DoesNotExist:
            return Response({'error': 'Person not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = PersonSerializer(person, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'PATCH':
        if not id:
            return Response({'error': 'ID is required for PATCH requests'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            person = Person.objects.get(id=id)
        except Person.DoesNotExist:
            return Response({'error': 'Person not found'}, status=status.HTTP_404_NOT_FOUND)

        # Partial update
        serializer = PersonSerializer(person, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        if not id:
            return Response({'error': 'ID is required for DELETE requests'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            person = Person.objects.get(id=id)
            person.delete()
            return Response({'message': 'Person deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
        except Person.DoesNotExist:
            return Response({'error': 'Person not found'}, status=status.HTTP_404_NOT_FOUND)



@api_view(['POST'])
def login(request):
    data=request.data 
    serializer = LoginSerializer(data=data)

    if serializer.is_valid():
        data = serializer.validated_data
        print(data)
        return Response({'message' : 'Success'})

    return Response(serializer.errors)




class PersonAPI(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get(self, request):
        # Get the 'id' query parameter if provided
        id = request.query_params.get('id')
        
        if id:
            try:
                # Fetch the specific person with a given id
                person = Person.objects.get(id=id)
                serializer = PersonSerializer(person)
                return Response(serializer.data)
            except Person.DoesNotExist:
                return Response({'error': 'Person not found'}, status=status.HTTP_404_NOT_FOUND)
        else:
            # Get all persons and apply pagination
            persons = Person.objects.all()
            page = request.query_params.get('page', 1)  # Default page is 1
            page_size = request.query_params.get('page_size', 3)  # Default page size is 3

            paginator = Paginator(persons, page_size)

            try:
                paginated_persons = paginator.page(page)
            except PageNotAnInteger:
                # If the page parameter is not an integer, show the first page
                paginated_persons = paginator.page(1)
            except EmptyPage:
                # If the page is out of range (e.g., 9999), show the last existing page
                paginated_persons = paginator.page(paginator.num_pages)

            # Serialize the paginated results
            serializer = PersonSerializer(paginated_persons, many=True)
            # Include pagination details in the response
            return Response({
                'count': paginator.count,
                'num_pages': paginator.num_pages,
                'current_page': paginated_persons.number,
                'results': serializer.data
            })

    def post(self, request):
        serializer = PersonSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):
        id = request.query_params.get('id')
        if not id:
            return Response({'error': 'ID is required for PATCH requests'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            person = Person.objects.get(id=id)
        except Person.DoesNotExist:
            return Response({'error': 'Person not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = PersonSerializer(person, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        id = request.query_params.get('id')
        if not id:
            return Response({'error': 'ID is required for PUT requests'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            person = Person.objects.get(id=id)
        except Person.DoesNotExist:
            return Response({'error': 'Person not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = PersonSerializer(person, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        id = request.query_params.get('id')
        if not id:
            return Response({'error': 'ID is required for DELETE requests'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            person = Person.objects.get(id=id)
            person.delete()
            return Response({'message': 'Person deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
        except Person.DoesNotExist:
            return Response({'error': 'Person not found'}, status=status.HTTP_404_NOT_FOUND)




class PeopleViewSet(viewsets.ModelViewSet):

    # After applying the below line, only 'get' and 'post' methods will be allowed

    # http_method_names = ['get', 'post']
    
    serializer_class = PersonSerializer
    queryset = Person.objects.all()

    def list(self, request):
        search = request.GET.get('search')
        queryset = self.queryset

        if search:
            # queryset = queryset.filter(name__istartswith=search)
            queryset = queryset.filter(name__icontains=search)
        
        serializer = PersonSerializer(queryset, many=True)
        return Response({'status' : 200, 'data' : serializer.data})
    



    # @action(detail=True, methods=['post'])
    # def send_mail_to_person(self, request):
    #     return Response({
    #         'status' : True ,
    #         'message' : 'Email Sent successfully'

    #     })
    