from rest_framework.renderers import JSONRenderer


class UnifiedResponseRenderer(JSONRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):
        response = renderer_context.get('response') if renderer_context else None
        status_code = response.status_code if response else 200

        if isinstance(data, dict) and 'code' in data and 'msg' in data:
            return super().render(data, accepted_media_type, renderer_context)

        if isinstance(data, dict) and 'results' in data and ('count' in data or 'total' in data):
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
        else:
            if 200 <= status_code < 300:
                result = {
                    'code': status_code,
                    'msg': 'success',
                    'data': data,
                }
            else:
                result = {
                    'code': status_code,
                    'msg': data if isinstance(data, str) else 'error',
                    'data': None,
                }

        return super().render(result, accepted_media_type, renderer_context)