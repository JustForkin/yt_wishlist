def get_request_json_args(request):
    return request.get_json() if request.get_json() is not None else {}