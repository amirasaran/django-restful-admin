from django.contrib.admin.options import get_content_type_for_model
from django.contrib.auth import get_permission_codename
from django.db.models.base import ModelBase
from django.forms import model_to_dict
from django.utils.functional import cached_property
from rest_framework import viewsets, status
from rest_framework.permissions import BasePermission
from rest_framework.response import Response
from rest_framework.routers import DefaultRouter
from rest_framework.serializers import ModelSerializer
from rest_framework.decorators import action as base_action


class AlreadyRegistered(Exception):
    pass


class NotRegistered(Exception):
    pass


class ImproperlyConfigured(Exception):
    pass


class AuthPermissionViewSetMixin:
    NOT_FOUND_PERMISSION_DEFAULT = False
    permission_map = dict()

    def get_permission_map(self):
        permission_map = {
            'list': self._make_permission_key('view'),
            'retrieve': self._make_permission_key('view'),
            'create': self._make_permission_key('add'),
            'update': self._make_permission_key('change'),
            'partial_update': self._make_permission_key('change'),
            'delete': self._make_permission_key('delete'),
        }
        permission_map.update(self.permission_map)
        return permission_map

    @cached_property
    def _options(self):
        return self.get_queryset().model._meta

    def _make_permission_key(self, action):
        code_name = get_permission_codename(action, self._options)
        return "{0}.{1}".format(self._options.app_label, code_name)

    def _has_perm_action(self, action, request, obj=None):
        if not action:
            return False

        perm_map = self.get_permission_map()
        if hasattr(getattr(self, action), 'permission'):
            perm_map.update(**{action: getattr(self, action).permission})

        if action not in perm_map:
            return self.NOT_FOUND_PERMISSION_DEFAULT

        perm_code = perm_map[action]
        if callable(perm_code):
            return perm_code(self, action, request, obj)
        if isinstance(perm_code, bool):
            return perm_code

        return request.user.has_perm(
            perm_code
        )


class IsStaffAccess(BasePermission):
    """
    Allows access only to authenticated Trainee users.
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_staff)

    def has_object_permission(self, request, view, obj):
        """
        Return `True` if permission is granted, `False` otherwise.
        """
        return self.has_permission(request, view)


class HasPermissionAccess(BasePermission):
    """
    Allows access only to authenticated Trainee users.
    """

    def has_permission(self, request, view):
        assert hasattr(view, 'get_permission_map'), """
        Must be inherit from RestFulModelAdmin to use this permission
        """
        return view._has_perm_action(view.action, request)

    def has_object_permission(self, request, view, obj):
        """
        Return `True` if permission is granted, `False` otherwise.
        """
        return view._has_perm_action(view.action, request, obj)


class ModelDiffHelper(object):
    def __init__(self, initial):
        self.__initial = self._dict(initial)
        self._new_object = None

    def set_changed_model(self, new_object):
        data = self._dict(new_object)
        if self._new_object is not None:
            self.__initial = data
        self._new_object = data
        return self

    @property
    def diff(self):
        if not self._new_object:
            return {}
        d1 = self.__initial
        d2 = self._new_object
        diffs = [(k, (v, d2[k])) for k, v in d1.items() if v != d2[k]]
        return dict(diffs)

    @property
    def has_changed(self):
        return bool(self.diff)

    @property
    def changed_fields(self):
        return list(self.diff.keys())

    def get_field_diff(self, field_name):
        """
        Returns a diff for field if it's changed and None otherwise.
        """
        return self.diff.get(field_name, None)

    def _dict(self, model):
        return model_to_dict(model, fields=[field.name for field in
                                           model._meta.fields])


class RestFulModelAdmin(AuthPermissionViewSetMixin, viewsets.ModelViewSet):
    queryset = None
    single_serializer_class = None
    permission_classes = (IsStaffAccess, HasPermissionAccess)

    @staticmethod
    def get_doc():
        return 'asd'

    def get_urls(self):
        return []

    def get_permission_map(self):
        permission_map = {
            'list': self._make_permission_key('view'),
            'retrieve': self._make_permission_key('view'),
            'create': self._make_permission_key('add'),
            'update': self._make_permission_key('change'),
            'partial_update': self._make_permission_key('change'),
            'delete': self._make_permission_key('delete'),
        }
        permission_map.update(self.permission_map)
        return permission_map

    def log_addition(self, request, object, message):
        """
        Log that an object has been successfully added.

        The default implementation creates an admin LogEntry object.
        """
        from django.contrib.admin.models import LogEntry, ADDITION
        return LogEntry.objects.log_action(
            user_id=request.user.pk,
            content_type_id=get_content_type_for_model(object).pk,
            object_id=object.pk,
            object_repr=str(object),
            action_flag=ADDITION,
            change_message=message,
        )

    def log_change(self, request, object, message):
        """
        Log that an object has been successfully changed.

        The default implementation creates an admin LogEntry object.
        """
        from django.contrib.admin.models import LogEntry, CHANGE
        return LogEntry.objects.log_action(
            user_id=request.user.pk,
            content_type_id=get_content_type_for_model(object).pk,
            object_id=object.pk,
            object_repr=str(object),
            action_flag=CHANGE,
            change_message=message,
        )

    def log_deletion(self, request, object, object_repr):
        """
        Log that an object will be deleted. Note that this method must be
        called before the deletion.

        The default implementation creates an admin LogEntry object.
        """
        from django.contrib.admin.models import LogEntry, DELETION
        return LogEntry.objects.log_action(
            user_id=request.user.pk,
            content_type_id=get_content_type_for_model(object).pk,
            object_id=object.pk,
            object_repr=object_repr,
            action_flag=DELETION,
        )

    def get_single_serializer_class(self):
        return self.single_serializer_class if self.single_serializer_class else self.get_serializer_class()

    def get_single_serializer(self, *args, **kwargs):
        """
        Return the serializer instance that should be used for validating and
        deserializing input, and for serializing output.
        """
        serializer_class = self.get_single_serializer_class()
        kwargs['context'] = self.get_serializer_context()
        return serializer_class(*args, **kwargs)

    def list(self, request, *args, **kwargs):
        """list all of objects"""
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, **kwargs):
        """Create new object"""
        serializer = self.get_single_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        self.log_addition(request, serializer.instance, [{'added': {
            'name': str(serializer.instance._meta.verbose_name),
            'object': str(serializer.instance),
        }}])
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def retrieve(self, request, pk=None, **kwargs):
        """Get object Details"""
        instance = self.get_object()
        serializer = self.get_single_serializer(instance)
        return Response(serializer.data)

    def update(self, request, pk=None, **kwargs):
        """Update object"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_single_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        helper = ModelDiffHelper(instance)
        self.perform_update(serializer)

        self.log_change(
            request,
            serializer.instance,
            [{'changed': {
                'name': str(serializer.instance._meta.verbose_name),
                'object': str(serializer.instance),
                'fields': helper.set_changed_model(serializer.instance).changed_fields
            }}]
        )

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    def partial_update(self, request, pk=None, **kwargs):
        """Partial Update"""
        return super().partial_update(request, pk=pk, **kwargs)

    def destroy(self, request, pk=None, **kwargs):
        """Delete object"""
        instance = self.get_object()
        self.log_deletion(request, instance, [{
            'deleted': {
                'name': str(instance._meta.verbose_name),
                'object': str(instance),
            }
        }])
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class BaseModelSerializer(ModelSerializer):
    class Meta:
        pass


class RestFulAdminSite:
    def __init__(self, view_class=RestFulModelAdmin):
        self._registry = {}
        self._url_patterns = []
        self.default_view_class = view_class

    def register_decorator(self, *model_or_iterable, **options):
        def wrapper(view_class):
            self.register(model_or_iterable, view_class, **options)
            return view_class

        return wrapper

    def register(self, model_or_iterable, view_class=None, **options):
        if not view_class:
            view_class = self.default_view_class

        if isinstance(model_or_iterable, ModelBase):
            model_or_iterable = [model_or_iterable]
        for model in model_or_iterable:
            if model._meta.abstract:
                raise ImproperlyConfigured(
                    'The model %s is abstract, so it cannot be registered with admin.' % model.__name__
                )

            if model in self._registry:
                raise AlreadyRegistered('The model %s is already registered' % model.__name__)
            options.update({
                "__doc__": self.generate_docs(model)
            })
            view_class = type("%sAdmin" % model.__name__, (view_class,), options)
            # self.set_docs(view_class, model)
            # Instantiate the admin class to save in the registry
            self._registry[model] = view_class

    def register_url_pattern(self, url_pattern):
        self._url_patterns.append(url_pattern)

    @classmethod
    def generate_docs(cls, model):
        return """
    ### The APIs include:


    > `GET`  {app}/{model} ===> list all `{verbose_name_plural}` page by page;

    > `POST`  {app}/{model} ===> create a new `{verbose_name}`

    > `GET` {app}/{model}/123 ===> return the details of the `{verbose_name}` 123

    > `PATCH` {app}/{model}/123 and `PUT` {app}/{model}/123 ==> update the `{verbose_name}` 123

    > `DELETE` {app}/{model}/123 ===> delete the `{verbose_name}` 123

    > `OPTIONS` {app}/{model} ===> show the supported verbs regarding endpoint `{app}/{model}`

    > `OPTIONS` {app}/{model}/123 ===> show the supported verbs regarding endpoint `{app}/{model}/123`

            """.format(
            app=model._meta.app_label,
            model=model._meta.model_name,
            verbose_name=model._meta.verbose_name,
            verbose_name_plural=model._meta.verbose_name_plural
        )

    def unregister(self, model_or_iterable):
        """
        Unregister the given model(s).

        If a model isn't already registered, raise NotRegistered.
        """
        if isinstance(model_or_iterable, ModelBase):
            model_or_iterable = [model_or_iterable]
        for model in model_or_iterable:
            if model not in self._registry:
                raise NotRegistered('The model %s is not registered' % model.__name__)
            del self._registry[model]

    def is_registered(self, model):
        """
        Check if a model class is registered with this `AdminSite`.
        """
        return model in self._registry

    def get_model_basename(self, model):
        return None

    def get_model_url(self, model):
        return '%s/%s' % (model._meta.app_label, model._meta.model_name)

    def get_urls(self):
        router = DefaultRouter()
        view_sets = []
        for model, view_set in self._registry.items():
            if view_set.queryset is None:
                view_set.queryset = model.objects.all()
            if view_set.serializer_class is None:
                serializer_class = type("%sModelSerializer" % model.__name__, (ModelSerializer,), {
                    "Meta": type("Meta", (object,), {
                        "model": model,
                        "fields": "__all__"
                    }),
                })
                view_set.serializer_class = serializer_class

            view_sets.append(view_set)
            router.register(self.get_model_url(model), view_set, self.get_model_basename(model))

        return router.urls + self._url_patterns

    @property
    def urls(self):
        return self.get_urls(), 'django_restful_admin', 'django_restful_admin'


site = RestFulAdminSite()


def register(*model_or_iterable, **options):
    return site.register_decorator(*model_or_iterable, **options)


def action(permission=None, methods=None, detail=None, url_path=None, url_name=None, **kwargs):
    def decorator(func):
        base_func = base_action(methods, detail, url_path, url_name, **kwargs)(func)
        base_func.permission = permission
        return base_func

    return decorator


# set package level vars for usability
import django_restful_admin
django_restful_admin.site = site
django_restful_admin.RestFulAdminSite = RestFulAdminSite
django_restful_admin.RestFulModelAdmin = RestFulModelAdmin
