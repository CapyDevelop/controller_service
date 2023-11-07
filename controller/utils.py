def generate_response(status="Success", status_code=0, description="Success", data=None):
    if data is None:
        data = dict()
    return {
        "status": status,
        "status_code": status_code,
        "description": description,
        "data": data
    }