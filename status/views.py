from django.views.generic import ListView
from .models import Block, Blockchain, SegmentNode
from .forms import TimelineBlockchainForm
from django.http import JsonResponse, HttpResponse, HttpRequest
from blockchain.helpers import json_decoder
from blockchain.constants import NUMBER_OF_BLOCKS_ON_A_PAGE
from django.shortcuts import render
from django.contrib import messages
from typing import Any


class BlockListView(ListView):  # type: ignore
    paginate_by = NUMBER_OF_BLOCKS_ON_A_PAGE
    model = Block
    template_name = "index.html"

    def get_context_data(self, **kwargs: Any) -> HttpResponse:
        context = super().get_context_data(**kwargs)
        context["blockchain"] = Blockchain.objects.first()
        context["form"] = TimelineBlockchainForm()

        return context


def timeline_view(request: HttpRequest) -> JsonResponse:
    if request.method == "POST":
        form = TimelineBlockchainForm(data=json_decoder(request.body))
        if form.is_valid():
            start, end = form.cleaned_data.values()
            search_result = SegmentNode.objects.search_segment(
                time_start=start, time_end=end
            )
            return JsonResponse({"search_result": search_result})
        else:
            error = form.errors["__all__"][0]
            messages.error(request, error)
    return JsonResponse({}, status=400)


def about(request: HttpRequest) -> HttpResponse:
    return render(request, "about.html")
