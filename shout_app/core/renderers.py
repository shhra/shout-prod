import json

from rest_framework.renderers import JSONRenderer

class ShoutAppJSONRenderer(JSONRenderer):
    charset = 'utf-8'
    object_label = 'data'
    pagination_object_label = 'objects'
    pagination_object_count = 'count'

    def render(self, data, media_type=None, renderer_context=None):
        if data.get('results', None) is not None:
            return json.dumps({
                self.pagination_object_label: data['results'],
                self.pagination_object_count: data['count'],
                })

        elif data.get('errors', None) is not None:
            return super(ShoutAppJSONRenderer, self).render(data)

        else:
            return json.dumps({
                self.object_label: data
            })

