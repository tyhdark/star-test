# -*- coding: utf-8 -*-

from __future__ import print_function

import swagger_client

from config.config import app_chain


class Api:
    def __init__(self):
        configuration = swagger_client.Configuration()
        configuration.host = f"http://{app_chain.Host.ip}:1317/"

        self.query = swagger_client.QueryApi(swagger_client.ApiClient(configuration))
        self.service = swagger_client.ServiceApi(swagger_client.ApiClient(configuration))


api_instance = Api()

__all__ = ["api_instance"]
