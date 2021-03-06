# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.http import Http404
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import View

from configurations.models import Option
from schedule.helpers import export_to_pentabarf, export_to_xcal, export_to_icalendar
from schedule.models import Schedule, Slot


def check_schedule_view(request):
    is_schedule_opened = bool(Option.objects.get_value("schedule_opened", 0))
    if not is_schedule_opened and not (request.user.is_authenticated() and request.user.is_superuser):
        raise Http404()


class ShowSchedule(View):
    """Shows the schedule of the event."""
    template_name = "schedule/show.html"

    def get(self, request):
        check_schedule_view(request)
        schedule = Schedule.objects.filter(published=True, hidden=False).first()
        if not schedule:
            raise Http404()
        data = {"days": []}
        for day in schedule.day_set.all():
            data["days"].append({
                "tracks": day.track_set.order_by("order"),
                "date": day.date,
                "slots": day.slot_set.all().select_related(),
                "slot_groups": day.slot_groups(),
            })
        return render(request, self.template_name, data)


class ShowSlot(View):
    template_name = "schedule/details.html"

    def get(self, request, slot):
        check_schedule_view(request)
        try:
            slot_id = int(slot)
            slot = get_object_or_404(Slot, pk=slot_id)
            if slot.content_ptr.slug:
                return redirect(slot.get_absolute_url(), permanent=True)
        except ValueError:
            slot = get_object_or_404(Slot, content_ptr__slug=slot)
        data = {
            "slot": slot
        }
        return render(request, self.template_name, data)


def pentabarf_view(request):
    """Download Pentabarf calendar file.
    :param request:
    """
    check_schedule_view(request)
    schedule = Schedule.objects.filter(published=True, hidden=False).first()
    pentabarf_xml = export_to_pentabarf(schedule)
    return HttpResponse(pentabarf_xml, content_type="application/xml")


def xcal_view(request):
    """Download xCal file.
    :param request:
    """
    check_schedule_view(request)
    schedule = Schedule.objects.filter(published=True, hidden=False).first()
    xcal_xml = export_to_xcal(schedule)
    return HttpResponse(xcal_xml, content_type="application/xml")


def icalendar_view(request):
    """Download iCalendar file.
    :param request:
    """
    check_schedule_view(request)
    schedule = Schedule.objects.filter(published=True, hidden=False).first()
    calendar_text = export_to_icalendar(schedule)
    return HttpResponse(calendar_text, content_type="text/calendar")