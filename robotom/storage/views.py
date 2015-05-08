# coding=utf-8
import logging
import requests
import json
from django.shortcuts import render
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from requests.exceptions import Timeout
from robotom.settings import STORAGE_EXPERIMENTS_HOST_GET, STORAGE_FRAMES_HOST

rest_logger = logging.getLogger('rest_logger')


class ExperimentRecord:
    def __init__(self, record):
        self.specimen = record['specimen']
        self.dark_count = record['DARK']['count']
        self.dark_exposure = record['DARK']['exposure']
        self.experiment_id = record['experiment id']
        if record['finished']:
            self.finished = u'Завершен'
        else:
            self.finished = u'Не завершен'
        if record['advanced']:
            self.advanced = u'Продвинутый'
        else:
            self.advanced = u'Стандартный'
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


def make_info(post_args):
    for arg in post_args:
        rest_logger.debug(u'PostArgs: {} {}'.format(arg, post_args[arg]))
    # Внимание! Быдлокод!
    request = {}

    if post_args['DarkFromCount'] != '':
        request['DARK.count'] = {}
        request['DARK.count']['$gte'] = int(post_args['DarkFromCount'])
    if post_args['DarkToCount'] != '':
        if 'DARK.count' not in request:
            request['DARK.count'] = {}
        request['DARK.count']['$lte'] = int(post_args['DarkToCount'])
    if post_args['DarkFromExposure'] != '':
        request['DARK.exposure'] = {}
        request['DARK.exposure']['$gte'] = float(post_args['DarkFromExposure'])
    if post_args['DarkToExposure'] != '':
        if 'DARK.exposure' not in request:
            request['DARK.exposure'] = {}
        request['DARK.exposure']['$lte'] = float(post_args['DarkToExposure'])

    if post_args['EmptyFromCount'] != '':
        request['EMPTY.count'] = {}
        request['EMPTY.count']['$gte'] = int(post_args['EmptyFromCount'])
    if post_args['EmptyToCount'] != '':
        if 'EMPTY.count' not in request:
            request['EMPTY.count'] = {}
        request['EMPTY.count']['$lte'] = int(post_args['EmptyToCount'])
    if post_args['EmptyFromExposure'] != '':
        request['EMPTY.exposure'] = {}
        request['EMPTY.exposure']['$gte'] = float(post_args['EmptyFromExposure'])
    if post_args['EmptyToExposure'] != '':
        if 'EMPTY.exposure' not in request:
            request['EMPTY.exposure'] = {}
        request['EMPTY.exposure']['$lte'] = float(post_args['EmptyToExposure'])

    if post_args['Finished'] == u'Завершен':
        request['finished'] = True
    if post_args['Finished'] == u'Не завершен':
        request['finished'] = False

    if post_args['Advanced'] == u'Да':
        request['advanced'] = True
    if post_args['Advanced'] == u'Нет':
        request['advanced'] = False

    if post_args['DataFromExposure'] != '':
        request['DATA.exposure'] = {}
        request['DATA.exposure']['$gte'] = float(post_args['DataFromExposure'])
    if post_args['DataToExposure'] != '':
        if 'DATA.exposure' not in request:
            request['DATA.exposure'] = {}
        request['DATA.exposure']['$lte'] = float(post_args['DataToExposure'])
    if post_args['DataFromAngleStep'] != '':
        request['DATA.angle step'] = {}
        request['DATA.angle step']['$gte'] = int(post_args['DataFromAngleStep'])
    if post_args['DataToAngleStep'] != '':
        if 'DATA.angle step' not in request:
            request['DATA.angle step'] = {}
        request['DATA.angle step']['$lte'] = int(post_args['DataToAngleStep'])
    if post_args['DataFromCountPerStep'] != '':
        request['DATA.count per step'] = {}
        request['DATA.count per step']['$gte'] = int(post_args['DataFromCountPerStep'])
    if post_args['DataToCountPerStep'] != '':
        if 'DATA.count per step' not in request:
            request['DATA.count per step'] = {}
        request['DATA.count per step']['$lte'] = int(post_args['DataToCountPerStep'])
    if post_args['DataFromStepCount'] != '':
        request['DATA.step count'] = {}
        request['DATA.step count']['$gte'] = int(post_args['DataFromStepCount'])
    if post_args['DataToStepCount'] != '':
        if 'DATA.step count' not in request:
            request['DATA.step count'] = {}
        request['DATA.step count']['$lte'] = int(post_args['DataToStepCount'])

    rest_logger.debug(u'Текст запроса к базе {}'.format(json.dumps(request)))
    return json.dumps(request)


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
        info = make_info(request.POST)
        try:
            answer = requests.post(STORAGE_EXPERIMENTS_HOST_GET, info, timeout=1)
            if answer.status_code == 200:
                experiments = json.loads(answer.content)
                rest_logger.debug(u'Найденные эксперименты: {}'.format(experiments))
                page = 1
                records = create_pages(request, experiments, page)
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
    try:
        info = json.dumps({"experiment id": storage_record_id, "image_data.datetime": "30.04.2015 10:27:35"})
        answer = requests.post(STORAGE_FRAMES_HOST, info)
        if answer.status_code == 200:
            frames = json.loads(answer.content)
            rest_logger.debug(u'Найденные фреймы: {}'.format(frames))
            import pylab as plt
            plt.figure()
            plt.imshow(frames["image"], cmap=plt.cm.gray)
            plt.colorbar()
            plt.show()
        else:
            rest_logger.error(u'Не удается получить фреймы. Код ошибки: {}'.format(answer.status_code))
    except Timeout as e:
        rest_logger.error(u'Не удается получить фреймы. Ошибка: {}'.format(e.message))
        message = u'Не удается получить фреймы. Сервер хранилища не отвечает. Попробуйте позже.'

    return render(request, 'storage/storage_record.html', {
        "record_id": storage_record_id,
        'caption': 'Запись хранилища номер ' + str(storage_record_id),
        'image_range': xrange(1, 5),  # TODO
        'user': request.user,
    })
