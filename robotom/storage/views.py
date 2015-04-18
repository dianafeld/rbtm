# coding=utf-8
from django.shortcuts import render


def storage_view(request):
    # TODO
    if request.method == "GET":
        return render(request, 'storage/storage_index.html', {
            'record_range': xrange(10),
            'caption': 'Хранилище',
            'toShowResult': False,
        })
    elif request.method == "POST":
        return render(request, 'storage/storage_index.html', {
            'record_range': xrange(10),
            'caption': 'Хранилище',
            'toShowResult': True,
        })


def storage_record_view(request, storage_record_id):
    # TODO
    return render(request, 'storage/storage_record.html', {
        "record_id": storage_record_id,
        'caption': 'Запись хранилища номер ' + str(storage_record_id),
        'image_range': xrange(1, 5),  # TODO
        'user': request.user,
    })
