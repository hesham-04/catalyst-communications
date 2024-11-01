from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Div, Submit
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.forms import ModelForm
from django.utils import timezone

from src.accounts.models import User, Treasury
from src.administration.admins.models import StockIn, StockOut, Transfer, StockInJudicial, StockOutJudicial, \
    TransferJudicial


class Row(Div):
    css_class = "row"


non_judicial_field_names = [
    's100', 's150', 's200', 's250', 's300', 's400', 's500', 's750', 's1000', 's2000', 's3000', 's5000', 's10000',
    's25000', 's50000'
]

judicial_field_names = [
    'j25', 'j30', 'j35', 'j50', 'j60', 'j75', 'j100', 'j125', 'j150', 'j200', 'j500', 'j1000', 'j2000', 'j3000',
    'j5000',
    'j10000', 'j15000'
]


now i want to render it dynamically. so i would need to:
use the django crispy forms layout here:
i have example code here:


class UserForm(UserCreationForm):
    class Meta:
        model = User
        fields = [
            'profile_image', 'first_name', 'last_name', 'cnic', 'username', 'designation',
            'email', 'password1', 'password2', 'phone_number', 'treasury', 'dob', 'is_superuser', 'is_staff',
            'is_active'
        ]
        widgets = {
            'dob': forms.DateInput(attrs={'type': 'date'})
        }

    def _init_(self, *args, **kwargs):
        super()._init_(*args, **kwargs)
        self.fields['treasury'].widget.attrs.update({'class': 'form-control'})
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('profile_image', css_class='form-group col-sm-6 '),
                Column('treasury', css_class='form-group col-sm-6 '),
                Column('first_name', css_class='col-sm-6 '),
                Column('last_name', css_class='col-sm-6 '),
                Column('email', css_class='col-sm-4'),
                Column('username', css_class='col-sm-4 '),
                Column('designation', css_class='col-sm-4 '),
                Column('password1', css_class='col-sm-6 '),
                Column('password2', css_class='col-sm-6 '),
                Column('cnic', css_class='col-sm-4 '),
                Column('phone_number', css_class='col-sm-4 '),
                Column('dob', css_class='col-sm-4 '),
                Column('is_superuser', css_class='col-sm-4 '),
                Column('is_staff', css_class='col-sm-4 '),
                Column('is_active', css_class='col-sm-4 '),

            ),
            Submit('submit', 'Submit', css_class='btn btn-primary float-right')
        )


class UserUpdateForm(ModelForm):
    class Meta:
        model = User
        fields = [
            'profile_image', 'first_name', 'last_name', 'username', 'designation',
            'email', 'phone_number', 'cnic', 'treasury', 'dob', 'is_superuser', 'is_staff',
            'is_active'
        ]
        widgets = {
            'dob': forms.DateInput(attrs={'type': 'date'})
        }

    def _init_(self, *args, **kwargs):
        super()._init_(*args, **kwargs)
        self.fields['treasury'].widget.attrs.update({'class': 'form-control'})
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('profile_image', css_class='form-group col-sm-6 '),
                Column('treasury', css_class='form-group col-sm-6 '),
                Column('first_name', css_class='col-sm-6 '),
                Column('last_name', css_class='col-sm-6 '),
                Column('email', css_class='col-sm-4'),
                Column('username', css_class='col-sm-4 '),
                Column('designation', css_class='col-sm-4 '),
                Column('cnic', css_class='col-sm-4 '),
                Column('phone_number', css_class='col-sm-4 '),
                Column('dob', css_class='col-sm-4 '),
                Column('is_superuser', css_class='col-sm-4 '),
                Column('is_staff', css_class='col-sm-4 '),
                Column('is_active', css_class='col-sm-4 '),

            ),
            Submit('submit', 'Submit', css_class='btn btn-primary float-right')
        )


class TreasuryForm(ModelForm):
    class Meta:
        model = Treasury
        fields = [
            'name', 'city', 'phone_number', 'email', 'address', 'is_active'
        ]


class StockInForm(forms.ModelForm):
    class Meta:
        model = StockIn
        fields = [
            'source_treasury', 's100', 's150', 's200', 's250', 's300', 's400', 's500',
            's750', 's1000', 's2000', 's3000', 's5000', 's10000', 's25000', 's50000', 'created_on'
        ]
        widgets = {
            'created_on': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def _init_(self, *args, **kwargs):
        super()._init_(*args, **kwargs)
        self.fields['source_treasury'].widget.attrs.update({'class': 'form-control'})
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('source_treasury', css_class='form-group col-sm-12 '),
                Column('s100', css_class='col-sm-4 '),
                Column('s150', css_class='col-sm-4 '),
                Column('s200', css_class='col-sm-4 '),
                Column('s250', css_class='col-sm-4 '),
                Column('s300', css_class='col-sm-4 '),
                Column('s400', css_class='col-sm-4 '),
                Column('s500', css_class='col-sm-4 '),
                Column('s750', css_class='col-sm-4 '),
                Column('s1000', css_class='col-sm-4 '),
                Column('s2000', css_class='col-sm-4 '),
                Column('s3000', css_class='col-sm-4 '),
                Column('s5000', css_class='col-sm-4 '),
                Column('s10000', css_class='col-sm-4 '),
                Column('s25000', css_class='col-sm-4 '),
                Column('s50000', css_class='col-sm-4 '),
                Column('created_on', css_class='col-sm-12 '),

            ),
            Submit('submit', 'Submit', css_class='btn btn-primary float-right')
        )

    def clean_created_on(self):
        created_on = self.cleaned_data['created_on']
        if created_on:
            if created_on.date() < timezone.now().date():
                raise forms.ValidationError("⏰🚀 Oops! Time-traveling detected! You can't add a record in the past.")
        return created_on

    def clean(self):
        cleaned_data = super().clean()

        if all(field_value == 0 for field_name, field_value in cleaned_data.items() if
               field_name.startswith('s') and field_name != 'source_treasury'):
            raise forms.ValidationError("At least one item is required to process this transaction")

        return cleaned_data


class StockOutForm(ModelForm):
    class Meta:
        model = StockOut
        fields = [
            'source_treasury',
            's100', 's150', 's200', 's250', 's300', 's400', 's500', 's750', 's1000',
            's2000', 's3000', 's5000', 's10000', 's25000', 's50000', 'created_on',
            'name', 'challan_number', 'challan_date', 'phone', 'type_of_transaction', 'serial_number'
        ]
        widgets = {
            'created_on': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'challan_date': forms.DateTimeInput(attrs={'type': 'date'}),
        }

    def _init_(self, *args, **kwargs):
        super()._init_(*args, **kwargs)
        self.fields['source_treasury'].widget.attrs.update({'class': 'form-control'})
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('source_treasury', css_class='form-group col-sm-12 '),
                Column('s100', css_class='col-sm-4 '),
                Column('s150', css_class='col-sm-4 '),
                Column('s200', css_class='col-sm-4 '),
                Column('s250', css_class='col-sm-4 '),
                Column('s300', css_class='col-sm-4 '),
                Column('s400', css_class='col-sm-4 '),
                Column('s500', css_class='col-sm-4 '),
                Column('s750', css_class='col-sm-4 '),
                Column('s1000', css_class='col-sm-4 '),
                Column('s2000', css_class='col-sm-4 '),
                Column('s3000', css_class='col-sm-4 '),
                Column('s5000', css_class='col-sm-4 '),
                Column('s10000', css_class='col-sm-4 '),
                Column('s25000', css_class='col-sm-4 '),
                Column('s50000', css_class='col-sm-4 '),
                Column('created_on', css_class='col-sm-12'),
                Column('name', css_class='col-sm-4'),
                Column('phone', css_class='col-sm-4'),
                Column('type_of_transaction', css_class='col-sm-4'),
                Column('challan_number', css_class='col-sm-4'),
                Column('challan_date', css_class='col-sm-4'),
                Column('serial_number', css_class='col-sm-4'),

            ),
            Submit('submit', 'Submit', css_class='btn btn-primary float-right')
        )

    def clean(self):
        cleaned_data = super().clean()
        source_treasury = cleaned_data.get('source_treasury')
        treasury = Treasury.objects.get(pk=source_treasury.pk)

        if all(field_value == 0 for field_name, field_value in cleaned_data.items() if
               field_name.startswith('s') and field_name != 'source_treasury'):
            raise forms.ValidationError("At least one item is required to process this transaction")

        for field_name in non_judicial_field_names:
            field_value = cleaned_data.get(field_name)
            treasury_field = getattr(treasury, field_name)
            if field_value > treasury_field:
                self.add_error(field_name, f"Requested Quantity is Greater than avaliable stock ( {treasury_field} )")
        return cleaned_data


class TransferForm(ModelForm):
    class Meta:
        model = Transfer
        fields = ['source_treasury', 'destination_treasury', 's100', 's150', 's200', 's250', 's300', 's400', 's500',
                  's750', 's1000',
                  's2000', 's3000', 's5000', 's10000', 's25000', 's50000', 'created_on'
                  ]
        widgets = {
            'created_on': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def _init_(self, *args, **kwargs):
        super()._init_(*args, **kwargs)
        self.fields['source_treasury'].widget.attrs.update({'class': 'form-control'})
        self.fields['destination_treasury'].widget.attrs.update({'class': 'form-control'})
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('source_treasury', css_class='form-group col-sm-6 '),
                Column('destination_treasury', css_class='form-group col-sm-6 '),
                Column('s100', css_class='col-sm-4 '),
                Column('s150', css_class='col-sm-4 '),
                Column('s200', css_class='col-sm-4 '),
                Column('s250', css_class='col-sm-4 '),
                Column('s300', css_class='col-sm-4 '),
                Column('s400', css_class='col-sm-4 '),
                Column('s500', css_class='col-sm-4 '),
                Column('s750', css_class='col-sm-4 '),
                Column('s1000', css_class='col-sm-4 '),
                Column('s2000', css_class='col-sm-4 '),
                Column('s3000', css_class='col-sm-4 '),
                Column('s5000', css_class='col-sm-4 '),
                Column('s10000', css_class='col-sm-4 '),
                Column('s25000', css_class='col-sm-4 '),
                Column('s50000', css_class='col-sm-4 '),
                Column('created_on', css_class='col-sm-12 '),

            ),
            Submit('submit', 'Submit', css_class='btn btn-primary float-right')
        )

    def clean(self):
        cleaned_data = super().clean()
        source_treasury = cleaned_data.get('source_treasury')
        destination_treasury = cleaned_data.get('destination_treasury')

        treasury = Treasury.objects.get(pk=source_treasury.pk)
        destination_treasury = Treasury.objects.get(pk=destination_treasury.pk)

        if treasury == destination_treasury:
            self.add_error('destination_treasury', "Source and Destination Treasury should be different")

        if all(field_value == 0 for field_name, field_value in cleaned_data.items() if
               field_name.startswith('s') and field_name != 'source_treasury'):
            raise forms.ValidationError("At least one item is required to process this transaction")

        for field_name in non_judicial_field_names:
            field_value = cleaned_data.get(field_name)
            treasury_field = getattr(treasury, field_name)
            if field_value > treasury_field:
                self.add_error(field_name, f"Value should be less than or equal to {treasury_field}")

        return cleaned_data


class RequestUpdateForm(ModelForm):
    class Meta:
        model = Transfer
        fields = ['status', 'source_treasury', 'destination_treasury', 's100', 's150', 's200', 's250', 's300', 's400',
                  's500',
                  's750', 's1000',
                  's2000', 's3000', 's5000', 's10000', 's25000', 's50000', 'created_on']
        widgets = {
            'created_on': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def _init_(self, *args, **kwargs):
        super()._init_(*args, **kwargs)
        self.fields['source_treasury'].widget.attrs.update({'class': 'form-control'})
        self.fields['destination_treasury'].widget.attrs.update({'class': 'form-control'})
        self.fields['status'].widget.attrs.update({'class': 'form-control'})
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('status', css_class='form-group col-sm-4 '),
                Column('source_treasury', css_class='form-group col-sm-4 '),
                Column('destination_treasury', css_class='form-group col-sm-4'),
                Column('s100', css_class='col-sm-4 '),
                Column('s150', css_class='col-sm-4 '),
                Column('s200', css_class='col-sm-4 '),
                Column('s250', css_class='col-sm-4 '),
                Column('s300', css_class='col-sm-4 '),
                Column('s400', css_class='col-sm-4 '),
                Column('s500', css_class='col-sm-4 '),
                Column('s750', css_class='col-sm-4 '),
                Column('s1000', css_class='col-sm-4 '),
                Column('s2000', css_class='col-sm-4 '),
                Column('s3000', css_class='col-sm-4 '),
                Column('s5000', css_class='col-sm-4 '),
                Column('s10000', css_class='col-sm-4 '),
                Column('s25000', css_class='col-sm-4 '),
                Column('s50000', css_class='col-sm-4 '),
                Column('created_on', css_class='col-sm-12 '),

            ),
            Submit('submit', 'Submit', css_class='btn btn-primary float-right')
        )

    def clean(self):
        cleaned_data = super().clean()
        status = cleaned_data.get('status')
        if status == 'complete':
            source_treasury = cleaned_data.get('source_treasury')
            treasury = Treasury.objects.get(pk=source_treasury.pk)
            destination_treasury = cleaned_data.get('destination_treasury')
            s100 = cleaned_data.get('s100')
            destination_treasury = Treasury.objects.get(pk=destination_treasury.pk)
            if treasury == destination_treasury:
                self.add_error('source_treasury', "Source and Destination Treasury should be different")

            for field_name in non_judicial_field_names:
                field_value = cleaned_data.get(field_name)
                treasury_field = getattr(treasury, field_name)
                if field_value > treasury_field:
                    self.add_error(field_name, f"Value should be less than or equal to {treasury_field}")

        return cleaned_data


class StockInJudicialForm(forms.ModelForm):
    class Meta:
        model = StockInJudicial
        fields = [
            'source_treasury',
            'j25', 'j30', 'j35', 'j50', 'j60', 'j75', 'j100', 'j125', 'j150', 'j200',
            'j500', 'j1000', 'j2000', 'j3000', 'j5000', 'j10000', 'j15000', 'created_on'
        ]
        widgets = {
            'created_on': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def _init_(self, *args, **kwargs):
        super()._init_(*args, **kwargs)
        self.fields['source_treasury'].widget.attrs.update({'class': 'form-control'})
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('source_treasury', css_class='form-group col-sm-12 '),
                Column('j25', css_class='col-sm-4 '),
                Column('j30', css_class='col-sm-4 '),
                Column('j35', css_class='col-sm-4 '),
                Column('j50', css_class='col-sm-4 '),
                Column('j60', css_class='col-sm-4 '),
                Column('j75', css_class='col-sm-4 '),
                Column('j100', css_class='col-sm-4 '),
                Column('j125', css_class='col-sm-4 '),
                Column('j150', css_class='col-sm-4 '),
                Column('j200', css_class='col-sm-4 '),
                Column('j500', css_class='col-sm-4 '),
                Column('j1000', css_class='col-sm-4 '),
                Column('j2000', css_class='col-sm-4 '),
                Column('j3000', css_class='col-sm-4 '),
                Column('j5000', css_class='col-sm-4 '),
                Column('j10000', css_class='col-sm-4 '),
                Column('j15000', css_class='col-sm-4 '),

                Column('created_on', css_class='col-sm-12 '),

            ),
            Submit('submit', 'Submit', css_class='btn btn-primary float-right')
        )

    def clean_created_on(self):
        created_on = self.cleaned_data['created_on']
        if created_on:
            if created_on.date() < timezone.now().date():
                raise forms.ValidationError("⏰🚀 Oops! Time-traveling detected! You can't add a record in the past.")
        return created_on

    def clean(self):
        cleaned_data = super().clean()

        if all(field_value == 0 for field_name, field_value in cleaned_data.items() if
               field_name.startswith('j') and field_name != 'source_treasury'):
            raise forms.ValidationError("At least one item is required to process this transaction")

        return cleaned_data


class StockOutJudicialForm(ModelForm):
    class Meta:
        model = StockOutJudicial
        fields = [
            'source_treasury',
            'j25', 'j30', 'j35', 'j50', 'j60', 'j75', 'j100', 'j125', 'j150', 'j200',
            'j500', 'j1000', 'j2000', 'j3000', 'j5000', 'j10000', 'j15000', 'created_on',
            'name', 'challan_number', 'challan_date', 'phone', 'type_of_transaction', 'serial_number'
        ]
        widgets = {
            'created_on': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'challan_date': forms.DateTimeInput(attrs={'type': 'date'}),
        }

    def _init_(self, *args, **kwargs):
        super()._init_(*args, **kwargs)
        self.fields['source_treasury'].widget.attrs.update({'class': 'form-control'})
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('source_treasury', css_class='form-group col-sm-12 '),
                Column('j25', css_class='col-sm-4 '),
                Column('j30', css_class='col-sm-4 '),
                Column('j35', css_class='col-sm-4 '),
                Column('j50', css_class='col-sm-4 '),
                Column('j60', css_class='col-sm-4 '),
                Column('j75', css_class='col-sm-4 '),
                Column('j100', css_class='col-sm-4 '),
                Column('j125', css_class='col-sm-4 '),
                Column('j150', css_class='col-sm-4 '),
                Column('j200', css_class='col-sm-4 '),
                Column('j500', css_class='col-sm-4 '),
                Column('j1000', css_class='col-sm-4 '),
                Column('j2000', css_class='col-sm-4 '),
                Column('j3000', css_class='col-sm-4 '),
                Column('j5000', css_class='col-sm-4 '),
                Column('j10000', css_class='col-sm-4 '),
                Column('j15000', css_class='col-sm-4 '),

                Column('created_on', css_class='col-sm-12'),
                Column('name', css_class='col-sm-4'),
                Column('phone', css_class='col-sm-4'),
                Column('type_of_transaction', css_class='col-sm-4'),
                Column('challan_number', css_class='col-sm-4'),
                Column('challan_date', css_class='col-sm-4'),
                Column('serial_number', css_class='col-sm-4'),

            ),
            Submit('submit', 'Submit', css_class='btn btn-primary float-right')
        )

    def clean(self):
        cleaned_data = super().clean()
        source_treasury = cleaned_data.get('source_treasury')
        treasury = Treasury.objects.get(pk=source_treasury.pk)

        if all(field_value == 0 for field_name, field_value in cleaned_data.items() if
               field_name.startswith('j') and field_name != 'source_treasury'):
            raise forms.ValidationError("At least one item is required to process this transaction")

        for field_name in judicial_field_names:
            field_value = cleaned_data.get(field_name)
            treasury_field = getattr(treasury, field_name)
            if field_value > treasury_field:
                self.add_error(field_name, f"Requested Quantity is Greater than avaliable stock ( {treasury_field} )")
        return cleaned_data


class TransferJudicialForm(ModelForm):
    class Meta:
        model = TransferJudicial
        fields = ['source_treasury', 'destination_treasury',
                  'j25', 'j30', 'j35', 'j50', 'j60', 'j75', 'j100', 'j125', 'j150', 'j200',
                  'j500', 'j1000', 'j2000', 'j3000', 'j5000', 'j10000', 'j15000', 'created_on'
                  ]
        widgets = {
            'created_on': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def _init_(self, *args, **kwargs):
        super()._init_(*args, **kwargs)
        self.fields['source_treasury'].widget.attrs.update({'class': 'form-control'})
        self.fields['destination_treasury'].widget.attrs.update({'class': 'form-control'})
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('source_treasury', css_class='form-group col-sm-6 '),
                Column('destination_treasury', css_class='form-group col-sm-6 '),
                Column('j25', css_class='col-sm-4 '),
                Column('j30', css_class='col-sm-4 '),
                Column('j35', css_class='col-sm-4 '),
                Column('j50', css_class='col-sm-4 '),
                Column('j60', css_class='col-sm-4 '),
                Column('j75', css_class='col-sm-4 '),
                Column('j100', css_class='col-sm-4 '),
                Column('j125', css_class='col-sm-4 '),
                Column('j150', css_class='col-sm-4 '),
                Column('j200', css_class='col-sm-4 '),
                Column('j500', css_class='col-sm-4 '),
                Column('j1000', css_class='col-sm-4 '),
                Column('j2000', css_class='col-sm-4 '),
                Column('j3000', css_class='col-sm-4 '),
                Column('j5000', css_class='col-sm-4 '),
                Column('j10000', css_class='col-sm-4 '),
                Column('j15000', css_class='col-sm-4 '),
                Column('created_on', css_class='col-sm-12 '),

            ),
            Submit('submit', 'Submit', css_class='btn btn-primary float-right')
        )

    def clean(self):
        cleaned_data = super().clean()
        source_treasury = cleaned_data.get('source_treasury')
        destination_treasury = cleaned_data.get('destination_treasury')

        treasury = Treasury.objects.get(pk=source_treasury.pk)
        destination_treasury = Treasury.objects.get(pk=destination_treasury.pk)

        if treasury == destination_treasury:
            self.add_error('destination_treasury', "Source and Destination Treasury should be different")

        if all(field_value == 0 for field_name, field_value in cleaned_data.items() if
               field_name.startswith('j') and field_name != 'source_treasury'):
            raise forms.ValidationError("At least one item is required to process this transaction")

        for field_name in judicial_field_names:
            field_value = cleaned_data.get(field_name)
            treasury_field = getattr(treasury, field_name)
            if field_value > treasury_field:
                self.add_error(field_name, f"Value should be less than or equal to {treasury_field}")

        return cleaned_data


class RequestUpdateJudicialForm(ModelForm):
    class Meta:
        model = TransferJudicial
        fields = ['status', 'source_treasury', 'destination_treasury',
                  'j25', 'j30', 'j35', 'j50', 'j60', 'j75', 'j100', 'j125', 'j150', 'j200',
                  'j500', 'j1000', 'j2000', 'j3000', 'j5000', 'j10000', 'j15000', 'created_on'
                  ]
        widgets = {
            'created_on': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def _init_(self, *args, **kwargs):
        super()._init_(*args, **kwargs)
        self.fields['source_treasury'].widget.attrs.update({'class': 'form-control'})
        self.fields['destination_treasury'].widget.attrs.update({'class': 'form-control'})
        self.fields['status'].widget.attrs.update({'class': 'form-control'})
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('status', css_class='form-group col-sm-4 '),
                Column('source_treasury', css_class='form-group col-sm-4 '),
                Column('destination_treasury', css_class='form-group col-sm-4'),
                Column('j25', css_class='col-sm-4 '),
                Column('j30', css_class='col-sm-4 '),
                Column('j35', css_class='col-sm-4 '),
                Column('j50', css_class='col-sm-4 '),
                Column('j60', css_class='col-sm-4 '),
                Column('j75', css_class='col-sm-4 '),
                Column('j100', css_class='col-sm-4 '),
                Column('j125', css_class='col-sm-4 '),
                Column('j150', css_class='col-sm-4 '),
                Column('j200', css_class='col-sm-4 '),
                Column('j500', css_class='col-sm-4 '),
                Column('j1000', css_class='col-sm-4 '),
                Column('j2000', css_class='col-sm-4 '),
                Column('j3000', css_class='col-sm-4 '),
                Column('j5000', css_class='col-sm-4 '),
                Column('j10000', css_class='col-sm-4 '),
                Column('j15000', css_class='col-sm-4 '),
                Column('created_on', css_class='col-sm-12 '),

            ),
            Submit('submit', 'Submit', css_class='btn btn-primary float-right')
        )

    def clean(self):
        cleaned_data = super().clean()
        status = cleaned_data.get('status')
        if status == 'complete':
            source_treasury = cleaned_data.get('source_treasury')
            treasury = Treasury.objects.get(pk=source_treasury.pk)
            destination_treasury = cleaned_data.get('destination_treasury')
            destination_treasury = Treasury.objects.get(pk=destination_treasury.pk)
            if treasury == destination_treasury:
                self.add_error('source_treasury', "Source and Destination Treasury should be different")

            for field_name in judicial_field_names:
                field_value = cleaned_data.get(field_name)
                treasury_field = getattr(treasury, field_name)
                if field_value > treasury_field:
                    self.add_error(field_name, f"Value should be less than or equal to {treasury_field}")

        return cleaned_data