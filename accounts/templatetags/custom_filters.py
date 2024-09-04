from datetime import date
from django import template
from django.urls import reverse

register = template.Library()


@register.filter
def gender_to_avatar(gender):
    value = 13 if gender == "Male" else 16
    return value


@register.filter
def get_grouped_questions(grouped_questions, section_header):
    return grouped_questions.get(section_header, [])


@register.filter
def get_section_header(counter, section_headers):
    index = counter // 6
    try:
        return section_headers[index]
    except IndexError:
        return ""


@register.simple_tag(takes_context=True)
def update_registration_session(context):
    request = context["request"]
    request.session["registration_success"] = False
    if "registration_success" in request.session:
        success = request.session.pop("registration_success")
        return success
    return False


@register.filter
def calculate_age(date_of_birth):
    try:
        today = date.today()
        age = (
            today.year
            - date_of_birth.year
            - ((today.month, today.day) < (date_of_birth.month, date_of_birth.day))
        )
    except:
        return 0
    return age


@register.filter
def ternary(value, arg):
    arg1, arg2 = arg.split(",")
    return arg1 if value else arg2


@register.simple_tag(takes_context=True)
def active_link_exclude_home(context, url_name):
    request = context["request"]
    url = reverse(url_name)

    if url_name == "home" and request.path != "/":
        return ""
    return "active" if request.path.startswith(url) else ""


@register.filter(name="add_class")
def add_class(field, css):
    """
    Add a CSS class to the given form field.
    """
    return field.as_widget(attrs={"class": css})


@register.filter
def conditional(value, arg):
    conditions = arg.split("|")
    for condition in conditions:
        try:
            cond, result = condition.split(":")
            if eval(cond):
                return result
        except ValueError:
            continue
    return ""
