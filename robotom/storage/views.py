# coding=utf-8
import logging
from django.core.context_processors import csrf
from django.views.decorators.csrf import csrf_protect
import requests
import json
from django.shortcuts import render
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from requests.exceptions import Timeout

rest_logger = logging.getLogger('rest_logger')


class ExperimentRecord:
    def __init__(self, record_id, name, voltage, current, date, finished, owner):
        self.id = record_id
        self.name = name
        self.voltage = voltage
        self.current = current
        self.date = date
        self.finished = finished
        self.owner = owner


def create_pages(request, results, page):
    record_list = [
        ExperimentRecord(i, "Name" + str(i), i, i, "22.11.2000", "Да", "Экспериментатор" + str(i))
        for i in xrange(110)]

    # record_list = [Experiment_Record(result) for result in results]
    pagin = Paginator(record_list, 15)

    try:
        records = pagin.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        records = pagin.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        records = pagin.page(pagin.num_pages)

    return records


@csrf_protect
def storage_view(request):
    # TODO

    page = request.GET.get('page')
    records = []
    num_pages = 0

    to_show = True
    if request.method == "GET":
        if page is None:
            to_show = False
    elif request.method == "POST":
        for res in request.POST:
            rest_logger.debug("Post args: " + res + " " + request.POST[res])
        info = json.dumps({'select': 'all'})
        experiments = requests.post('http://109.234.34.140:5006/storage/experiments', info)
        rest_logger.debug('Experiments status', experiments.status_code)

        # experiments = requests.post('http://127.0.0.1:8000/storage/debug', info)
        rest_logger.debug('Experiments content: ', experiments.content)
        page = 1
        experiments = []
        records = create_pages(request, experiments, page)
        rest_logger.debug('Loaded info: ', json.loads(info))
        # num_pages = len(experiments) / 15 + 2

    return render(request, 'storage/storage_index.html', {
        'record_range': records,
        'caption': 'Хранилище',
        'toShowResult': to_show,
        'pages': xrange(1, num_pages + 1),
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


@csrf_protect
def storage_debug(request):
    record_list = [{"name": i, "current": i} for i in xrange(100)]
    return json.dumps(record_list)
