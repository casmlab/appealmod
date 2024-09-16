from django.views.generic import TemplateView


class DebugView(TemplateView):
    template_name = "debug.html"

    def dispatch(self, request, *args, **kwargs):
        # BanAppealData.objects.create('vitalik-vitalik', 'umsiexperiments')
        return super().dispatch(request, *args, **kwargs)
