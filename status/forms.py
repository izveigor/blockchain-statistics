from django import forms
import time
from datetime import datetime
from django.core.exceptions import ValidationError
from status.models import SegmentNode


class TimelineBlockchainForm(forms.Form):
    """Form for search timeline blockchain ("form_time")"""

    date_start = forms.CharField(
        widget=forms.TextInput(
            attrs={"type": "date", "class": "form-control", "id": "form_date_start"}
        )
    )
    time_start = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "type": "time",
                "class": "form-control",
                "id": "form_time_start",
                "step": 1,
            }
        )
    )
    date_end = forms.CharField(
        widget=forms.TextInput(
            attrs={"type": "date", "class": "form-control", "id": "form_date_end"}
        )
    )
    time_end = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "type": "time",
                "class": "form-control",
                "id": "form_time_end",
                "step": 1,
            }
        )
    )

    def clean(self):
        cleaned_data = self.cleaned_data
        for field in ("date_start", "time_start", "date_end", "time_end"):
            if cleaned_data.get(field) is None:
                raise ValidationError('Field "{}" is empty!'.format(field))

        start = int(
            time.mktime(
                datetime.strptime(
                    cleaned_data["date_start"].replace("-", " ")
                    + " "
                    + cleaned_data["time_start"].replace(":", " "),
                    "%Y %m %d %H %M %S",
                ).timetuple()
            )
        )
        end = int(
            time.mktime(
                datetime.strptime(
                    cleaned_data["date_end"].replace("-", " ")
                    + " "
                    + cleaned_data["time_end"].replace(":", " "),
                    "%Y %m %d %H %M %S",
                ).timetuple()
            )
        )

        if start > end:
            raise ValidationError("Start time greater than end time!")

        if SegmentNode.objects.first().time_start > end:
            raise ValidationError("Server doesn't have data in this period!")

        if SegmentNode.objects.last().time_start < start:
            raise ValidationError("No one element doesn't falls within this period!")

        self.cleaned_data.clear()
        self.cleaned_data.update({"start": start, "end": end})
