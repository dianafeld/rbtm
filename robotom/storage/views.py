# coding=utf-8
from django.shortcuts import render
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage


def storage_view(request):
    # TODO

    if request.method == "GET":
        return render(request, 'storage/storage_index.html', {
            'caption': 'Хранилище',
            'toShowResult': False,
        })
    elif request.method == "POST":
        records_list = range(110)
        pagin = Paginator(records_list, 20)
        page = request.GET.get('page')

        try:
            records = pagin.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            records = pagin.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            records = pagin.page(pagin.num_pages)
        return render(request, 'storage/storage_index.html', {
            'record_range': records,
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