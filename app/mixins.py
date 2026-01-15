from django.contrib.auth.mixins import AccessMixin

class NotLoginRequiredMixin(AccessMixin):
    
    def dispatch(self, request, *args, **kwargs):
        if  request.user.is_authenticated:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)