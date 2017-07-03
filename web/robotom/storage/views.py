# coding=utf-8
import logging
import os
import tempfile
from django.contrib import messages
from django.core.files.storage import default_storage
from django.http import HttpResponseBadRequest, HttpResponse
import requests
import json
from django.shortcuts import render
from requests.exceptions import Timeout
from robotom.settings import STORAGE_EXPERIMENTS_GET_HOST, STORAGE_FRAMES_INFO_HOST, MEDIA_ROOT, RECONSTRUCTION_ROOT, \
    STORAGE_FRAMES_PNG, STORAGE_EXPERIMENTS_HOST, STORAGE_RECONSTRUCTION, STORAGE_HDF5_FILE
from django.conf import settings
from django.contrib.auth.decorators import login_required, user_passes_test
import h5py

storage_logger = logging.getLogger('storage_logger')


def is_active(user):
    return user.is_active


class ExperimentRecord:
    def __init__(self, record):
        self.experiment_id = record['_id']
        if 'specimen' in record:
            self.specimen = record['specimen']
        else:
            self.specimen = ''
        self.dark_count = record['experiment parameters']['DARK']['count']
        self.dark_exposure = record['experiment parameters']['DARK']['exposure']

        if record['finished']:
            self.finished = u'Завершен'
        else:
            self.finished = u'Не завершен'
        if record['experiment parameters']['advanced']:
            self.advanced = u'Продвинутый'
        else:
            self.advanced = u'Стандартный'
        self.data_angle_step = record['experiment parameters']['DATA']['angle step']
        self.data_count_per_step = record['experiment parameters']['DATA']['count per step']
        self.data_step_count = record['experiment parameters']['DATA']['step count']
        self.data_exposure = record['experiment parameters']['DATA']['exposure']
        self.empty_count = record['experiment parameters']['EMPTY']['count']
        self.empty_exposure = record['experiment parameters']['EMPTY']['exposure']
        self.hdf_host = STORAGE_HDF5_FILE.format(exp_id=self.experiment_id)
        self.datetime = record['datetime']


def make_info(post_args):
    # for arg in post_args:
    #     storage_logger.debug(u'PostArgs: {} {}'.format(arg, post_args[arg]))
    # Внимание! Быдлокод!
    request = {}

    if post_args['DarkFromCount'] != '':
        request['experiment parameters.DARK.count'] = {}
        request['experiment parameters.DARK.count']['$gte'] = int(post_args['DarkFromCount'])
    if post_args['DarkToCount'] != '':
        if 'experiment parameters.DARK.count' not in request:
            request['experiment parameters.DARK.count'] = {}
        request['experiment parameters.DARK.count']['$lte'] = int(post_args['DarkToCount'])
    if post_args['DarkFromExposure'] != '':
        request['experiment parameters.DARK.exposure'] = {}
        request['experiment parameters.DARK.exposure']['$gte'] = float(post_args['DarkFromExposure'])
    if post_args['DarkToExposure'] != '':
        if 'experiment parameters.DARK.exposure' not in request:
            request['experiment parameters.DARK.exposure'] = {}
        request['experiment parameters.DARK.exposure']['$lte'] = float(post_args['DarkToExposure'])

    if post_args['EmptyFromCount'] != '':
        request['experiment parameters.EMPTY.count'] = {}
        request['experiment parameters.EMPTY.count']['$gte'] = int(post_args['EmptyFromCount'])
    if post_args['EmptyToCount'] != '':
        if 'experiment parameters.EMPTY.count' not in request:
            request['experiment parameters.EMPTY.count'] = {}
        request['experiment parameters.EMPTY.count']['$lte'] = int(post_args['EmptyToCount'])
    if post_args['EmptyFromExposure'] != '':
        request['experiment parameters.EMPTY.exposure'] = {}
        request['experiment parameters.EMPTY.exposure']['$gte'] = float(post_args['EmptyFromExposure'])
    if post_args['EmptyToExposure'] != '':
        if 'experiment parameters.EMPTY.exposure' not in request:
            request['experiment parameters.EMPTY.exposure'] = {}
        request['experiment parameters.EMPTY.exposure']['$lte'] = float(post_args['EmptyToExposure'])

    if post_args['Specimen'] != '':
        request['specimen'] = post_args['Specimen'].strip()

    if post_args['Finished'] == u'Завершен':
        request['finished'] = True
    if post_args['Finished'] == u'Не завершен':
        request['finished'] = False

    if post_args['Advanced'] == u'Да':
        request['experiment parameters.advanced'] = True
    if post_args['Advanced'] == u'Нет':
        request['experiment parameters.advanced'] = False

    if post_args['DataFromExposure'] != '':
        request['experiment parameters.DATA.exposure'] = {}
        request['experiment parameters.DATA.exposure']['$gte'] = float(post_args['DataFromExposure'])
    if post_args['DataToExposure'] != '':
        if 'experiment parameters.DATA.exposure' not in request:
            request['experiment parameters.DATA.exposure'] = {}
        request['experiment parameters.DATA.exposure']['$lte'] = float(post_args['DataToExposure'])
    if post_args['DataFromAngleStep'] != '':
        request['experiment parameters.DATA.angle step'] = {}
        request['experiment parameters.DATA.angle step']['$gte'] = int(post_args['DataFromAngleStep'])
    if post_args['DataToAngleStep'] != '':
        if 'experiment parameters.DATA.angle step' not in request:
            request['experiment parameters.DATA.angle step'] = {}
        request['experiment parameters.DATA.angle step']['$lte'] = int(post_args['DataToAngleStep'])
    if post_args['DataFromCountPerStep'] != '':
        request['experiment parameters.DATA.count per step'] = {}
        request['experiment parameters.DATA.count per step']['$gte'] = int(post_args['DataFromCountPerStep'])
    if post_args['DataToCountPerStep'] != '':
        if 'experiment parameters.DATA.count per step' not in request:
            request['experiment parameters.DATA.count per step'] = {}
        request['experiment parameters.DATA.count per step']['$lte'] = int(post_args['DataToCountPerStep'])
    if post_args['DataFromStepCount'] != '':
        request['experiment parameters.DATA.step count'] = {}
        request['experiment parameters.DATA.step count']['$gte'] = int(post_args['DataFromStepCount'])
    if post_args['DataToStepCount'] != '':
        if 'experiment parameters.DATA.step count' not in request:
            request['experiment parameters.DATA.step count'] = {}
        request['experiment parameters.DATA.step count']['$lte'] = int(post_args['DataToStepCount'])

    storage_logger.debug(u'Текст запроса к базе {}'.format(json.dumps(request)))
    return json.dumps(request)


@login_required
@user_passes_test(is_active)
def storage_view(request):
    records = []
    num_pages = 0
    to_show = False

    info = ""
    if request.method == "GET":
        info = json.dumps({})
    elif request.method == "POST":
        info = make_info(request.POST)
    try:
        answer = requests.post(STORAGE_EXPERIMENTS_GET_HOST, info, timeout=settings.TIMEOUT_DEFAULT)
        if answer.status_code == 200:
            experiments = json.loads(answer.content)
            storage_logger.debug(u'Найденные эксперименты: {}'.format(experiments))
            records = []
            for result in experiments:
                try:
                    record = ExperimentRecord(result)
                    records.append(record)
                except KeyError:
                    storage_logger.warning(u'Неверная запись об эксперименте {}'.format(result))

            if len(records) == 0:
                messages.error(request, u'Не найдено ни одной записи')
            else:
                to_show = True
            num_pages = len(records) / 8
        else:
            storage_logger.error(u'Не удается найти эксперименты. Код ошибки: {}'.format(answer.status_code))
            messages.error(request, u'Не удается найти эксперименты. Код ошибки: {}'.format(answer.status_code))
    except Timeout as e:
        storage_logger.error(u'Не удается найти эксперименты. Ошибка: {}'.format(e.message))
        messages.error(request, u'Не удается найти эксперименты. Сервер хранилища не отвечает. Попробуйте позже.')
    except BaseException as e:
        try:
            storage_logger.error(u'Не удается найти эксперименты1. Ошибка: {}'.format(e.message))
            storage_logger.error(u'Не удается найти эксперименты1. Ошибка: {}'.format(e.message))
            messages.error(request,
                           u'Не удается найти эксперименты. Сервер хранилища не отвечает. Попробуйте позже.')
        except BaseException as e2:
            storage_logger.error(u'Не удается найти эксперименты2. Ошибка: {}'.format(e2.message))
            messages.error(request,
                           u'Не удается найти эксперименты. Сервер хранилища не отвечает. Попробуйте позже.')

    return render(request, 'storage/storage_index.html', {
        'caption': 'Хранилище',
        'record_range': records,
        'toShowResult': to_show,
        'pages': range(1, num_pages + 2),
    })


class FrameRecord:
    def __init__(self, frame):
        self.id = ""
        self.num = "0"
        self.type = ""
        self.date_time = ""
        self.detector_model = ""
        self.exposure = ""
        self.shutter_open = ""
        self.angle_position = ""
        self.current = ""
        self.voltage = ""
        self.horizontal_position = ""
        self.present = ""
        self.mode = ""

        if "_id" in frame:
            if "$oid" in frame['_id']:
                self.id = str(frame["_id"]['$oid'])
            else:
                self.id = str(frame["_id"])

        if "type" in frame:
            self.type = frame["type"]
        if "frame" in frame:
            if "mode" in frame["frame"]:
                self.mode = frame["frame"]["mode"]
            if "number" in frame['frame']:
                self.num = frame["frame"]["number"]
            if "image_data" in frame["frame"]:
                if "datetime" in frame["frame"]["image_data"]:
                    self.date_time = frame["frame"]["image_data"]["datetime"]
                if "detector" in frame["frame"]["image_data"]:
                    if "model" in frame["frame"]["image_data"]["detector"]:
                        self.detector_model = frame["frame"]["image_data"]["detector"]["model"]
                if "exposure" in frame["frame"]["image_data"]:
                    self.exposure = frame["frame"]["image_data"]["exposure"]
            if "shutter" in frame["frame"]:
                if "open" in frame["frame"]["shutter"]:
                    self.shutter_open = frame["frame"]["shutter"]["open"]
            if "object" in frame["frame"]:
                if "angle position" in frame["frame"]["object"]:
                    self.angle_position = frame["frame"]["object"]["angle position"]
                if "horizontal position" in frame["frame"]["object"]:
                    self.horizontal_position = frame["frame"]["object"]["horizontal position"]
                if "present" in frame["frame"]["object"]:
                    if frame["frame"]["object"]["present"]:
                        self.present = u"Да"
                    else:
                        self.present = u"Нет"
            if "X-ray source" in frame["frame"]:
                if "current" in frame["frame"]["X-ray source"]:
                    self.current = frame["frame"]["X-ray source"]["current"]
                if "voltage" in frame["frame"]["X-ray source"]:
                    self.voltage = frame["frame"]["X-ray source"]["voltage"]


@login_required
@user_passes_test(is_active)
def storage_record_view(request, storage_record_id):
    record = {}
    to_show = True
    try:
        exp_info = json.dumps({"_id": storage_record_id})
        experiment = requests.post(STORAGE_EXPERIMENTS_GET_HOST, exp_info, timeout=settings.TIMEOUT_DEFAULT)
        if experiment.status_code == 200:
            experiment_info = json.loads(experiment.content)
            storage_logger.debug(u'Страница записи: Данные эксперимента: {}'.format(experiment_info))
            if len(experiment_info) == 0:
                messages.error(request, u'Эксперимент с данным идентификатором не найден')
                to_show = False
            else:
                record = ExperimentRecord(experiment_info[0])
        else:
            storage_logger.error(u'Не удается получить эксперимент. Ошибка: {}'.format(experiment.status_code))
            messages.error(request, u'Не удается получить эксперимент. Ошибка: {}'.format(experiment.status_code))
            to_show = False
    except Timeout as e:
        storage_logger.error(u'Не удается получить эксперимент. Ошибка: {}'.format(e.message))
        messages.error(request, u'Не удается получить эксперимент. Сервер хранилища не отвечает. Попробуйте позже.')
        to_show = False
    except BaseException as e:
        storage_logger.error(u'Не удается получить эксперимент. Ошибка: {}'.format(e.message))
        messages.error(request, u'Не удается получить эксперимент. Сервер хранилища не отвечает. Попробуйте позже.')
        to_show = False

    frames_list = []

    try:
        frame_info = json.dumps({"exp_id": storage_record_id})
        # storage_logger.debug(u'Страница записи: {}'.format(frame_info))
        frames = requests.post(STORAGE_FRAMES_INFO_HOST, frame_info, timeout=settings.TIMEOUT_DEFAULT)
        if frames.status_code == 200:
            frames_info = json.loads(frames.content)
            storage_logger.debug(u'Страница записи: Список изображений: {}'.format(frames_info))
            frames_list = [FrameRecord(frame) for frame in frames_info]
        else:
            storage_logger.error(
                u'Страница записи: Не удается получить список изображений. Ошибка: {}'.format(frames.status_code))
            messages.error(request, u'Не удается получить список изображений. Ошибка: {}'.format(frames.status_code))
            to_show = False
    except Timeout as e:
        storage_logger.error(u'Страница записи: Не удается получить список изображений. Ошибка: {}'.format(e.message))
        messages.error(request,
                       u'Не удается получить список изображений. Сервер хранилища не отвечает. Попробуйте позже.')
        to_show = False
    except BaseException as e:
        storage_logger.error(u'Страница записи: Не удается получить список изображений. Ошибка: {}'.format(e))
        messages.error(request,
                       u'Не удается получить список изображений. Сервер хранилища не отвечает. Попробуйте позже.')
        to_show = False

    return render(request, 'storage/storage_record.html', {
        "record_id": storage_record_id,
        'caption': 'Запись хранилища ' + str(storage_record_id),
        'to_show': to_show,
        'info': record,
        'frames_list': frames_list,
    })


def frames_downloading(request, storage_record_id):
    try:
        frame_request = json.dumps({"exp_id": storage_record_id})
        storage_logger.debug(u'Получение изображений: Запрос списка изображений {}'.format(frame_request))
        frames = requests.post(STORAGE_FRAMES_INFO_HOST, frame_request, timeout=settings.TIMEOUT_DEFAULT)
        if frames.status_code == 200:
            frames_info = json.loads(frames.content)
            storage_logger.debug(u'Получение изображений: Список изображений: {}'.format(frames_info))
            frames_list = [FrameRecord(frame) for frame in frames_info]
        else:
            storage_logger.error(
                u'Получение изображений: Не удается получить список изображений. Ошибка: {}'.format(frames.status_code))
            messages.error(request, u'Не удается получить список изображений. Ошибка: {}'.format(frames.status_code))
            return HttpResponseBadRequest(u'Ошибкa {} при получении списка изображений'.format(frames.status_code),
                                          content_type='text/plain')
    except Timeout as e:
        storage_logger.error(
            u'Получение изображений: Не удается получить список изображений. Ошибка: {}'.format(e.message))
        messages.error(request,
                       u'Не удается получить список изображений. Сервер хранилища не отвечает. Попробуйте позже.')
        return HttpResponseBadRequest(u"Не удалось получить список изображений. Истекло время ожидания ответа",
                                      content_type='text/plain')
    except BaseException as e:
        storage_logger.error(
            u'Получение изображений: Не удается получить список изображений. Ошибка: {}'.format(e))
        messages.error(request,
                       u'Не удается получить список изображений. Сервер хранилища не отвечает. Попробуйте позже.')
        return HttpResponseBadRequest(u'Не удалось получить список изображений. Сервер хранилища не отвечает.',
                                      content_type='text/plain')

    for frame in frames_list:
        file_name = frame.id + '.png'
        if not os.path.exists(os.path.join(MEDIA_ROOT, file_name)):
            try:
                storage_logger.debug(
                    u'Получение изображений: Запрос на получение изображения номер {}'.format(frame.id))
                frame_response = requests.get(STORAGE_FRAMES_PNG.format(exp_id=storage_record_id, frame_id=frame.id),
                                              timeout=settings.TIMEOUT_DEFAULT, stream=True)
                if frame_response.status_code == 200:
                    temp_file = tempfile.TemporaryFile()
                    for block in frame_response.iter_content(1024 * 8):
                        if not block:
                            break
                        temp_file.write(block)
                    default_storage.save(os.path.join(MEDIA_ROOT, file_name), temp_file)
                else:
                    storage_logger.error(u'Не удается получить изображениe {}. Ошибка: {}'.format(
                        frame.num, frame_response.status_code))
                    return HttpResponseBadRequest(
                        u'Ошибкa {} при получении изображения'.format(frame_response.status_code),
                        content_type='text/plain')
            except Timeout as e:
                storage_logger.error(
                    u'Получение изображений: Не удается получить изображения. Ошибка: {}'.format(e.message))
                return HttpResponseBadRequest(
                    u'Не удалось получить изображение номер {}. Истекло время ожидания ответа'.format(frame.num),
                    content_type='text/plain')
            except BaseException as e:
                storage_logger.error(
                    u'Получение изображений: Не удается получить изображения. Ошибка: {}'.format(e.message))
                return HttpResponseBadRequest(
                    u'Не удалось получить изображение номер {}. Сервер хранилища не отвечает.'.format(frame.num),
                    content_type='text/plain')

    return HttpResponse(u'Изображения получены успешно', content_type='text/plain')


def delete_experiment(request, experiment_id):
    try:
        storage_logger.debug(u'Удаление эксперимента: {}'.format(experiment_id))
        response = requests.delete(STORAGE_EXPERIMENTS_HOST + '/' + experiment_id, timeout=settings.TIMEOUT_DEFAULT)

        if response.status_code == 200:
            response_content = json.loads(response.content)
            storage_logger.debug(u'Удаление эксперимента: Результат: {}'.format(response_content))
            result = response_content[u'deleted']

            if result != u'success':
                storage_logger.error(u'Удаление эксперимента: сервер не смог удалить эксперимент')
                return HttpResponseBadRequest(u'Не удается удалить эксперимент.', content_type='text/plain')
            else:
                return HttpResponse(u'Эксперимент {} успешно удален'.format(experiment_id))
        else:
            storage_logger.error(
                u'Удаление эксперимента: Не удается удалить эксперимент. response.status_code: {}'.format(
                    response.status_code))
            return HttpResponseBadRequest(
                u'Не удается удалить эксперимент. Ошибка {}'.format(response.status_code),
                content_type='text/plain')
    except Timeout as e:
        storage_logger.error(
            u'Удаление эксперимента: Не удается удалить эксперимент. Ошибка: {}'.format(e.message))
        return HttpResponseBadRequest(
            u'Не удается удалить эксперимент. Истекло время ожидания ответа',
            content_type='text/plain')
    except BaseException as e:
        storage_logger.error(
            u'Удаление эксперимента: Не удается удалить эксперимент. Ошибка: {}'.format(e.message))
        return HttpResponseBadRequest(
            u'Не удается удалить эксперимент.',
            content_type='text/plain')


def record_reconstruction(request, storage_record_id):
    with h5py.File(os.path.join(RECONSTRUCTION_ROOT, storage_record_id + '.hdf5')) as f:
        return render(request, 'storage/record_reconstruction.html', {
            "record_id": storage_record_id,
            'caption': 'Реконструкция эксперимента ' + str(storage_record_id),
            "n": f["8"].attrs["n"],
            "m": f["8"].attrs["m"],
            "k": f["8"].attrs["k"],
            "R_arr": map(int, f["8"]["R"].value.tolist()),
            "G_arr": map(int, f["8"]["G"].value.tolist()),
            "B_arr": map(int, f["8"]["B"].value.tolist()),
            "A_arr": map(int, f["8"]["A"].value.tolist()),
            "X_arr": map(int, f["8"]["X"].value.tolist()),
            "Y_arr": map(int, f["8"]["Y"].value.tolist()),
            "Z_arr": map(int, f["8"]["Z"].value.tolist()),
            "num_vertices": f["8"].attrs["num_vertices"]
        })


def record_reconstruction_loading(request, storage_record_id):
    return render(request, 'storage/record_reconstruction_loading.html', {
        'record_id': storage_record_id
    })


def record_reconstruction_downloading(request, storage_record_id):
    file_name = storage_record_id + '.hdf5'
    if not os.path.exists(os.path.join(RECONSTRUCTION_ROOT, file_name)):
        try:
            storage_logger.debug(
                u'Получение реконструции: {}'.format(storage_record_id))
            reconstruction_response = requests.get(STORAGE_RECONSTRUCTION.format(exp_id=storage_record_id,
                                                                                 rarefaction=1, level1=8, level2=8),
                                                   timeout=settings.TIMEOUT_DEFAULT, stream=True)
            if reconstruction_response.status_code == 200:
                temp_file = tempfile.TemporaryFile()
                for block in reconstruction_response.iter_content(1024 * 8):
                    if not block:
                        break
                    temp_file.write(block)
                default_storage.save(os.path.join(RECONSTRUCTION_ROOT, file_name), temp_file)
            else:
                storage_logger.error(u'Не удается получить реконструкцию {}. Ошибка: {}'.format(
                    storage_record_id, reconstruction_response.status_code))
                return HttpResponseBadRequest(
                    u'Ошибкa {} при получении реконструкции'.format(reconstruction_response.status_code),
                    content_type='text/plain')
        except Timeout as e:
            storage_logger.error(
                u'Получение реконструкции: Не удается получить реконструкцию. Ошибка: {}'.format(e.message))
            return HttpResponseBadRequest(
                u'Не удалось получить реконструкцию. Истекло время ожидания ответа'.format(storage_record_id),
                content_type='text/plain')
        except BaseException as e:
            storage_logger.error(
                u'Получение реконструкции: Не удается получить реконструкцию. Ошибка: {}'.format(e.message))
            return HttpResponseBadRequest(
                u'Не удалось получить реконструкцию. Сервер хранилища не отвечает.'.format(storage_record_id),
                content_type='text/plain')

    return HttpResponse(u'Реконструкция получена успешно', content_type='text/plain')
