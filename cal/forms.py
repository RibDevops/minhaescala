from django.forms import ModelForm, DateInput
from cal.models import Event

# class EventForm(ModelForm):
#   class Meta:
#     model = Event
#     # datetime-local is a HTML5 input type, format to make date time show on fields
#     widgets = {
#       'start_time': DateInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
#       'end_time': DateInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
#     }
#     fields = '__all__'

#   def __init__(self, *args, **kwargs):
#     super(EventForm, self).__init__(*args, **kwargs)
#     # input_formats parses HTML5 datetime-local input to datetime field
#     self.fields['start_time'].input_formats = ('%Y-%m-%dT%H:%M',)
#     self.fields['end_time'].input_formats = ('%Y-%m-%dT%H:%M',)


class EventForm(ModelForm):
    class Meta:
        model = Event
        widgets = {
            'start_time': DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),  # Somente data
            # 'end_time': DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),    # Somente data
        }
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(EventForm, self).__init__(*args, **kwargs)
        self.fields['title'].widget.attrs['placeholder'] = 'ex: SN - José'
        # Remove os input_formats com hora, pois agora só queremos a data
        self.fields['start_time'].input_formats = ('%Y-%m-%d',)  # Formato ISO para data
        # self.fields['end_time'].input_formats = ('%Y-%m-%d',)   # Formato ISO para data