# Copyright 2016 Cloudbase Solutions Srl
# All Rights Reserved.

from webob import exc

from oslo_log import log as logging

from coriolis.api import wsgi as api_wsgi
from coriolis.api.v1.views import endpoint_view
from coriolis import exception
from coriolis.endpoints import api

LOG = logging.getLogger(__name__)


class EndpointController(api_wsgi.Controller):
    def __init__(self):
        self._endpoint_api = api.API()
        super(EndpointController, self).__init__()

    def show(self, req, id):
        endpoint = self._endpoint_api.get_endpoint(
            req.environ["coriolis.context"], id)
        if not endpoint:
            raise exc.HTTPNotFound()

        return endpoint_view.single(req, endpoint)

    def index(self, req):
        return endpoint_view.collection(
            req, self._endpoint_api.get_endpoints(
                req.environ['coriolis.context']))

    def _validate_create_body(self, body):
        try:
            endpoint = body["endpoint"]
            name = endpoint["name"]
            description = endpoint.get("description")
            endpoint_type = endpoint["type"]
            connection_info = endpoint["connection_info"]
            return name, endpoint_type, description, connection_info
        except Exception as ex:
            LOG.exception(ex)
            if hasattr(ex, "message"):
                msg = ex.message
            else:
                msg = str(ex)
            raise exception.InvalidInput(msg)

    def create(self, req, body):
        (name, endpoint_type, description,
         connection_info) = self._validate_create_body(body)
        return endpoint_view.single(req, self._endpoint_api.create(
            req.environ['coriolis.context'], name, endpoint_type, description,
            connection_info))

    def delete(self, req, id):
        try:
            self._endpoint_api.delete(req.environ['coriolis.context'], id)
            raise exc.HTTPNoContent()
        except exception.NotFound as ex:
            raise exc.HTTPNotFound(explanation=ex.msg)


def create_resource():
    return api_wsgi.Resource(EndpointController())