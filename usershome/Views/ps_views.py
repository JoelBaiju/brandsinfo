



# DRF imports
from rest_framework import generics, filters, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.parsers import MultiPartParser, FormParser 
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated



# Local app imports
from ..models import *
from ..serializers import * 
from ..SearchEngines.searcher import find_closest 
from ..Tools_Utils.utils import *





@api_view(['GET'])
def search_products_category(request):
    query = request.GET.get('q', '')
    if not query:
        return Response({'error': 'Query parameter "q" is required'}, status=400)

    cats = find_closest('usershome_product_sub_category',query)
    return Response(cats)




class AddProductWithImagesView(generics.CreateAPIView):
    serializer_class = ProductSerializer
    queryset = Products.objects.all()
    parser_classes = [MultiPartParser, FormParser]
    def get(self, request):
        bid=request.GET.get('bid')
        if not bid :
            return Response(status=status.HTTP_400_BAD_REQUEST)
        queryset = Products.objects.filter(buisness=Buisnesses.objects.get(id=bid))
        print(queryset[0])
        return Response(ProductSerializer(queryset , many=True).data , status=status.HTTP_200_OK)
        
    def create(self, request, *args, **kwargs): 
        print('fffffffff')       
        data = request.data
        print(data)
        images = request.FILES.getlist('images[]')  
        data.setlist('images', images)  
        serializer = ProductSerializer(data=data)
        print(data)
        
        if serializer.is_valid():
            print(" ")
            product = serializer.save()
            return Response({'buisness_type':Buisnesses.objects.get(id=data.get('buisness')).buisness_type}, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

    

class ProductDelete(generics.DestroyAPIView):
    queryset = Products.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]  # Only authenticated users can access


class EditProductView(generics.UpdateAPIView):
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]
    queryset = Products.objects.all()
    lookup_field = 'id'

    def update(self, request, *args, **kwargs):
        product = self.get_object()
        if product.buisness.user != request.user:
            return Response({'error': 'Unauthorized to edit this offer'}, status=status.HTTP_403_FORBIDDEN)

        return super().update(request, *args, **kwargs)

class Add_product_images(generics.ListCreateAPIView):
    queryset = Product_pics.objects.all()
    serializer_class = ProductPicsSerializer
    permission_classes = [IsAuthenticated]  # Only authenticated users can access
    
    def post(self, request):
        print(request.data)
        pid = request.data.get('pid')  
        if not pid:
            print('id error')
            return Response({'error': 'Product ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            product = Products.objects.get(id=pid)
        except Products.DoesNotExist:
            print('buisness error')
            return Response({'error': 'Business not found'}, status=status.HTTP_404_NOT_FOUND)

        images = request.FILES.getlist('images[]')  

        if not images:
            print('image error')
            return Response({'error': 'No images uploaded'}, status=status.HTTP_400_BAD_REQUEST)

        created_images = []
        for img in images:
            product_pic = Product_pics.objects.create(product=product, image=img)
            created_images.append(product_pic)

        return Response(ProductPicsSerializer(created_images, many=True).data, status=status.HTTP_201_CREATED)
    
    
class ProductPics_Delete(generics.DestroyAPIView):
    queryset = Product_pics.objects.all()
    serializer_class = ProductPicsSerializer
    permission_classes = [IsAuthenticated]  

    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    

class ServiceListCreateView(generics.ListCreateAPIView):
    queryset = Services.objects.all()
    serializer_class = ServiceSerializer
    parser_classes = [MultiPartParser, FormParser]  # Allows image uploads
    filter_backends = [filters.SearchFilter]  
    search_fields = ['buisness']  # Enables filtering by business ID

    def get(self, request):
        bid=request.GET.get('bid')
        if not bid :
            return Response(status=status.HTTP_400_BAD_REQUEST)
        queryset = Services.objects.filter(buisness=Buisnesses.objects.get(id=bid))
        print(queryset[0])
        return Response(ServiceSerializer(queryset , many=True).data)
        
    def post(self, request, *args, **kwargs):
        print(request.data)
        images = request.FILES.getlist('images[]')
        data = request.data
        data.setlist('images', images)
        serializer = self.get_serializer(data=data) 
        return super().post(request, *args, **kwargs)

    

class EditServiceView(generics.UpdateAPIView):
    serializer_class = ServiceSerializer
    permission_classes = [IsAuthenticated]
    queryset = Services.objects.all()
    lookup_field = 'id'

    def update(self, request, *args, **kwargs):
        service = self.get_object()
        if service.buisness.user != request.user:
            return Response({'error': 'Unauthorized to edit this offer'}, status=status.HTTP_403_FORBIDDEN)

        return super().update(request, *args, **kwargs)


class ServicePics_Delete(generics.DestroyAPIView):
    queryset = Service_pics.objects.all()
    serializer_class = ServicePicsSerializer
    permission_classes = [IsAuthenticated]  

    

class Add_Services_images(generics.ListCreateAPIView):
    queryset = Service_pics.objects.all()
    serializer_class = ServicePicsSerializer
    permission_classes = [IsAuthenticated]  # Only authenticated users can access
    
    def post(self, request):
        print(request.data)
        sid = request.data.get('sid')  
        if not sid:
            print('id error')
            return Response({'error': 'Service ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            service = Services.objects.get(id=sid)
        except Services.DoesNotExist:
            print('buisness error')
            return Response({'error': 'Business not found'}, status=status.HTTP_404_NOT_FOUND)

        images = request.FILES.getlist('images[]')  

        if not images:
            print('image error')
            return Response({'error': 'No images uploaded'}, status=status.HTTP_400_BAD_REQUEST)

        created_images = []
        for img in images:
            service_pic = Service_pics.objects.create(service=service, image=img)
            created_images.append(service_pic)

        return Response(ServicePicsSerializer(created_images, many=True).data, status=status.HTTP_201_CREATED)

class ServiceCats(generics.ListCreateAPIView):
    queryset = Service_Cats.objects.all()
    serializer_class = ServiceCatsSerializer
        
    
    



class ServiceDelete(generics.DestroyAPIView):
    queryset = Services.objects.all()
    serializer_class = ServiceSerializer
    permission_classes = [IsAuthenticated]  # Only authenticated users can access

    
    
