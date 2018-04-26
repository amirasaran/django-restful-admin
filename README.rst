
# Expose Django's admin as a RESTFUL service

- Support all of restful api
- Auto generat serializers
- Use [Django Rest Framework](http://www.django-rest-framework.org/)
- Fully customization support

## How To Install

	pip install django-restful-admin

add to `INSTALED_APPS`

	INSTALLED_APPS = [  
	  ...
	  'rest_framework',  
	  'django_restful_admin',  
	  ...
	]

## How To use
you need only add the bellow code to  `admin.py`  in your apps

	from django_restful_admin import site
	from yourapp.models improt FisrtModel, ScoundModel
	
	site.register(FisrtModel)  
	site.register(ScoundModel)  

add url to your project `urls.py`

	from django_restful_admin import site
	
	urlpatterns = [  
		  ... 
		  path('apiadmin/', admin.site.urls),
		  ...  
		]

Run project and open url `http://your-ip:port/apiadmin/`

enjoy!

# Customization 
add more documentation about customization very soon ....

# Contribute
if you think you can help me please let's start.