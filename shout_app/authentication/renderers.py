from shout_app.core.renderers import ShoutAppJSONRenderer

class UserJSONRenderer(ShoutAppJSONRenderer):
    charset = 'utf-8'
    object_label = 'data'
    pagination_object_label = 'users'
    pagination_count_label = 'usersCount'

    def render(self, data, media_type=None, renderer_context=None):
        return super(UserJSONRenderer, self).render(data)
