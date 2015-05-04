# coding=utf-8
import logging
import requests
import json
from django.shortcuts import render
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from requests.exceptions import Timeout
from robotom.settings import STORAGE_EXPERIMENTS_HOST_GET

rest_logger = logging.getLogger('rest_logger')


class ExperimentRecord:
    def __init__(self, record):
        self.specimen = record['specimen']
        self.dark_count = record['DARK']['count']
        self.dark_exposure = record['DARK']['exposure']
        self.experiment_id = record['experiment id']
        self.finished = record['finished']
        self.advanced = record['advanced']
        self.data_angle_step = record['DATA']['angle step']
        self.data_count_per_step = record['DATA']['count per step']
        self.data_step_count = record['DATA']['step count']
        self.data_exposure = record['DATA']['exposure']
        self.empty_count = record['EMPTY']['count']
        self.empty_exposure = record['EMPTY']['exposure']


def create_pages(request, results, page):
    record_list = [ExperimentRecord(result) for result in results]
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


def storage_view(request):
    # TODO

    page = request.GET.get('page')
    records = []
    num_pages = 0
    message = u''
    has_message = False
    to_show = False

    if request.method == "GET":
        if page is not None:
            to_show = True
    elif request.method == "POST":
        info = json.dumps({'select': 'all'})
        try:
            answer = requests.post(STORAGE_EXPERIMENTS_HOST_GET, info, timeout=1)
            if answer.status_code == 200:
                experiments = json.loads(answer.content)
                rest_logger.debug(experiments)
                page = 1
                records = create_pages(request, experiments, page)
                print
                to_show = True
                num_pages = len(experiments) / 15
            else:
                rest_logger.error(u'Не удается найти эксперименты. Код ошибки: {}'.format(answer.status_code))
                has_message = True
                message = u'Не удается найти эксперименты. Код ошибки: {}'.format(answer.status_code)
        except Timeout as e:
            rest_logger.error(u'Не удается найти эксперименты. Ошибка: {}'.format(e.message))
            has_message = True
            message = u'Не удается найти эксперименты. Сервер хранилища не отвечает. Попробуйте позже.'

    return render(request, 'storage/storage_index.html', {
        'caption': 'Хранилище',
        'record_range': records,
        'toShowResult': to_show,
        'pages': xrange(1, num_pages + 1),
        'current_page': page,
        'has_message': has_message,
        'message': message,
    })


def storage_record_view(request, storage_record_id):
    # TODO
    return render(request, 'storage/storage_record.html', {
        "record_id": storage_record_id,
        'caption': 'Запись хранилища номер ' + str(storage_record_id),
        'image_range': xrange(1, 5),  # TODO
        'user': request.user,
    })
