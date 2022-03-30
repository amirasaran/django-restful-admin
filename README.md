This is a fork of [django-restful-admin](https://github.com/amirasaran/django-restful-admin), all credits to [@amirasaran](https://github.com/amirasaran/).

# Expose Django's admin as a RESTFUL service
 
 - [x] Support all of restful api  
 - [x]  Auto generat serializers  
 - [x] Use [Django Rest Framework](http://www.django-rest-framework.org/)  
 - [x] Fully customization support  
 - [x] Using Django Rest Framework ViewSet as AdminModels
 - [x] Support default Django auth permission
 - [x] Support Django custom model permission with simple configuration
 - [x] Using Django Rest Framework Serializer(or ModelSerializer) as request validators
 - [x] Support Single Serializer class to customize your detail view
 - [x] Auto generate documentation for CURDs
 - [x] Pagination and ability to change paginator
 - [x] Support custom action with permission
 - [x] Support all features in DRF
 - [x] Support LogEntry (Log history of objects)

## Todo
 - [ ] Add some documentation
 - [ ] Add custom route Api documentation
 - [ ] Add list_display
 - [ ] Add Filter And Search
 - [ ] Add exlude
 - [ ] Add Fields
 - [ ] Example inline
 - [ ] Localization
 - [ ] Somethings that's need in future 

  
## How To Install  
  
 pip install django-restful-admin  
add to `INSTALED_APPS`  
  ```
 INSTALLED_APPS = [
      ...  
     'rest_framework',   
    'django_restful_admin',    
     ...  
 ]  
 ```
## How To use  
you need only add the bellow code to  `admin.py` in your apps  
  
  ```
 from django_restful_admin import admin
 from yourapp.models improt FisrtModel, ScoundModel   

admin.site.register(FisrtModel)    
admin.site.register(ScoundModel)   
```

Then add URL to your project `urls.py`  
  
  ```
 from django_restful_admin import admin as api_admin 
    urlpatterns = [    
        ...   
        path('apiadmin/', api_admin.site.urls),  
		 ...     
  ]  
```

Run the project and open URL `http://your-ip:port/apiadmin/`  
  
enjoy!  
  
## Change Log  
   - [x] export admin in __init__.py
   - [x] Add default django auth permissions support
   - [x] Add admin.register decorator
  
# Customization 

### Example
Create a new Django project
```
$ django-admin startproject example`
$ cd example
$ python manage.py startapp blog
```

Create blog app models in `blog/models.py`
```
from django.db import models

class Category(models.Model)
	title = models.CharField(  
	  max_length=255  
	)
	
class Post(models.Model):
	title = models.CharField(  
	  max_length=255  
	)
	summery = models.TextField()
	description = models.TextField()
	category = models.ForeignKey(  
		Category,  
		related_name='products',  
		on_delete=models.CASCADE  
	)
```

Add your blog app in `INSTALLED_APPS` in `example/settings.py`

```
INSTALLED_APPS = [
		# Django default apps...
		'rest_framework',
		'django_restful_admin',
		
		'blog'
]
```

Add admin URLs to django URLs in `example/urls.py`

```
from django.conf.urls import url  
from django.contrib import admin  
from django_restful_admin import admin as api_admin  
from django.urls import path  

  
urlpatterns = [  
  path('apiadmin/', api_admin.site.urls),  # this line added
  # path('admin/', admin.site.urls),
  # your apis custom must be set here  
]
```

Register your model to restful admin site in `blog/admin.py`

```
from django_restful_admin import admin as api_admin  
from blog.models import *    
  
api_admin.site.register(Post) 
api_admin.site.register(Category) 
```
 
Add View and use decorators `blog/admin.py`
```
...
@api_admin.register(Category, Product)  
class MyCustomApiAdmin(BaseRestFulModelAdmin):  
    authentication_classes = (CustomTokenAuthentication,)
	permission_classes = [IsAuthenticated] 
... 
```
Read more about authentication and permission DRF [Documentation](https://www.django-rest-framework.org/api-guide/authentication/#authentication).

## Customize serialization
At first, you must define your serializer class 
Make `serializers.py` file in `blog`
Open `blog/serializers.py` and make serializer like this:

```
from rest_framework import serializers
from .models import *
class ProductSerializer(serializers.ModelSerializer):
	class Meta:
		model = Product
		feilds = ('id', 'title')
class CategorySerializer(serializers.ModelSerializer):
	class Meta:
		model = Category
		fields = ('id','title)
		
class SingleProductSerializer(serializers.ModelSerializer):
	category = CategorySerializer(read_only=True)
	class Meta:
		model = Product
		feilds = ('id', 'title', 'summery', 'description', 'category')
```
```
from .serializers import ProductSerializer, SingleProductSerializer
@api_admin.register(Product)  
class ProductApiAdmin(BaseRestFulModelAdmin):  
    serializer_class = ProductSerializer
    single_serializer_class = SingleProductSerializer
```
`serializer_class` use for serialize list of objects but  `single_serializer_class` use for serializer **view signle object**, **update**, **partial update** and **create**.

## Add a custom route with permission
```
@api_admin.register(Product)  
class MyCustomApiAdmin(BaseRestFulModelAdmin):

	@api_admin.action(permission='product.view_product', detail=True, methods=['GET'], url_path=r'my-custom-action/(?P<another_key>[^/.]+)')  
	def my_custom_action(self, request, pk, another_key):
		pass
		## Do what you want to do
		## this action make url like this /apiadmin/blog/product/2/my-custom-action/XXX
```
If you want to except permission you just send permission=True, for creating custom permission you can pass **closure function** or **lambda** to permission like this `permission=lambda: view, action, request, obj=None: True`
  
# Contribute  
If you think you can help me please let's start.
