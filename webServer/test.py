#!/usr/bin/python
# -*- coding: utf-8 -*-

from django import forms
ACTIVITY_STYLE = (('a', '1'), ('b', '2'), ('c', '3'))


class HobbiesForm(forms.Form):

    hobbies = forms.MultipleChoiceField(label=u'xxx',
            choices=ACTIVITY_STYLE,
            widget=forms.CheckboxSelectMultiple())


print HobbiesForm(data={'hobbies': ['a', 'b', 'c']}).as_p()
print HobbiesForm(data={'hobbies': ['b', 'c']}).as_p()
