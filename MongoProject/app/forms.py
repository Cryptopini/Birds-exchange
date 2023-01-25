from django import forms

class FormforOrders(forms.Form):
    want_to_sell = forms.FloatField(label='BTC')
    want_to_buy = forms.FloatField(label='BTC')
    price = forms.FloatField(label='$')
    
    def clean(self):
        cleaned_data = super().clean()
        want_to_sell = self.cleaned_data.get('want_to_sell')
        want_to_buy = self.cleaned_data.get('want_to_buy')
        price = self.cleaned_data.get('price')
        if price < 0:
            raise forms.ValidationError(message='Price must be > or = to 0')
        elif want_to_sell < 0 or want_to_buy < 0:
            raise forms.ValidationError(message='The quantity of BTC must be > or = to 0')
        return cleaned_data
    