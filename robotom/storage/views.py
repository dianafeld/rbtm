from django.shortcuts import render


def storage_view(request):
    # TODO
    return render(request, 'storage/storage_index.html', {
        "record_range": xrange(10)
    })


def storage_record_view(request, storage_record_id):
    # TODO
    return render(request, 'storage/storage_record.html', {
        "record_id": storage_record_id
    })