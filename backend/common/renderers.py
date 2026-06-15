from rest_framework.renderers import JSONRenderer


class UnifiedResponseRenderer(JSONRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):
        response = renderer_context.get('response') if renderer_context else None
        status_code = response.status_code if response else 200

        if isinstance(data, dict) and 'code' in data and 'msg' in data:
            return super().render(data, accepted_media_type, renderer_context)

        if isinstance(data, dict) and 'results' in data:
            paginated_data = {
                'total': data.get('count', data.get('total', 0)),
                'page': data.get('page', None),
                'page_size': data.get('page_size', None),
                'results': data.get('results', []),
            }
            result = {
                'code': status_code,
                'msg': 'success',
                'data': paginated_data,
            }
        elif 200 <= status_code < 300:
            if data is None:
                result = {
                    'code': status_code,
                    'msg': 'success',
                    'data': None,
                }
            elif isinstance(data, dict) and any(k in data for k in ('detail', 'message')):
                msg = data.pop('detail', data.pop('message', 'success'))
                result = {
                    'code': status_code,
                    'msg': msg,
                    'data': data if data else None,
                }
            else:
                result = {
                    'code': status_code,
                    'msg': 'success',
                    'data': data,
                }
        else:
            if isinstance(data, dict) and 'detail' in data:
                msg = data['detail']
                data_rest = {k: v for k, v in data.items() if k != 'detail'}
            elif isinstance(data, str):
                msg = data
                data_rest = None
            else:
                msg = 'error'
                data_rest = data
            result = {
                'code': status_code,
                'msg': msg,
                'data': data_rest if data_rest else None,
            }

        return super().render(result, accepted_media_type, renderer_context)