#!/usr/bin/python
# -*- coding: utf-8 -*-
from django import forms

class DatePickerInput(forms.DateInput):
    def render(self, name, value, attrs=None):
        attrs.update({
            'class': 'form-control datepicker',
            'placeholder': 'dd/mm/yyyy'
        })

        return super(DatePickerInput, self).render(name, value, attrs)
