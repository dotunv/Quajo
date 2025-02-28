from django import forms
from .models import QueueMember


class PaymentConfirmationForm(forms.ModelForm):
    class Meta:
        model = QueueMember
        fields = ['payment_proof', 'payment_tx_id']

    def __init__(self, *args, **kwargs):
        super(PaymentConfirmationForm, self).__init__(*args, **kwargs)
        self.fields['payment_proof'].widget.attrs.update({
            'class': 'form-control',
            'accept': 'image/*',
        })
        self.fields['payment_tx_id'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter transaction ID',
        })
