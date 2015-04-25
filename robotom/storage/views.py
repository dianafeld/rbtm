# coding=utf-8
from django.shortcuts import render
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage


class Experiment_Record:
    def __init__(self, id, name, voltage, date, finished, owner):
        self.id = id
        self.name = name
        self.voltage = voltage
        self.date = date
        self.finished = finished
        self.owner = owner


def storage_view(request):
    # TODO
    records_list = [
        Experiment_Record(i, "Name" + str(i), i, "22.11.2000", "Да", "Экспериментатор" + str(i))
        for i in xrange(110)]
    pagin = Paginator(records_list, 15)
    page = request.GET.get('page')

    try:
        records = pagin.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        records = pagin.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        records = pagin.page(pagin.num_pages)

    to_show = True
    if request.method == "GET":
        if page is None:
            to_show = False
    elif request.method == "POST":
        for res in request.POST:
            print res
        records = pagin.page(1)

    return render(request, 'storage/storage_index.html', {
        'record_range': records,
        'caption': 'Хранилище',
        'toShowResult': to_show,
        'pages': xrange(1, pagin.num_pages + 1),
        'current_page': page,
    })


def storage_record_view(request, storage_record_id):
    # TODO
    return render(request, 'storage/storage_record.html', {
        "record_id": storage_record_id,
        'caption': 'Запись хранилища номер ' + str(storage_record_id),
        'image_range': xrange(1, 5),  # TODO
        'user': request.user,
    })