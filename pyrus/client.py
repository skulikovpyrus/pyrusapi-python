'''
PyrusAPI library

This module allows you to call Pyrus API methods via python.
usage:

    >>> from pyrus import client
    >>> import pyrus.models
    >>> pyrus_client = client.PyrusAPI()
    >>> auth_response = pyrus_client.auth("login", "security_key")
    >>> if auth_response.success:
           forms_response = pyrus_client.get_forms()
           forms = forms_response.forms

Full documentation for PyrusAPI is at https://pyrus.com/en/help/api
'''

from enum import Enum
import jsonpickle
import os
import re
import requests
from .models import responses as resp, requests as req, entities as ent
import rfc6266

from .models.entities import Form, Catalog


class PyrusAPI(object):
    """
    PyrusApi client

    Args:
        login (:obj:`str`): User's login (email)
        security_key (:obj:`str`): User's Secret key
        access_token (:obj:`str`, optional): Users's access token. You can specify it if you already have one. (optional)
        proxy (:obj:`str`, optional): Proxy server url
    """
    MAX_FILE_SIZE_IN_BYTES = 250 * 1024 * 1024

    class HTTPMethod(Enum):
        GET = "GET"
        POST = "POST"
        PUT = "PUT"

    _host = 'api.pyrus.com'
    _base_path = '/v4'
    access_token = None
    _protocol = 'https'
    _api_name = 'Pyrus'
    _user_agent = 'Pyrus API python client v 1.31.0'
    proxy = None
    _download_file_base_url = 'https://files.pyrus.com/services/attachment?Id='

    def __init__(self, login=None, security_key=None, access_token=None, proxy=None):
        self.security_key = security_key
        self.access_token = access_token
        self.login = login
        if proxy:
            self.proxy = {'http': proxy}

    def auth(self, login=None, security_key=None):
        """
        Get access_token for user

        Args:
            login (:obj:`str`): User's login (email)
            security_key (:obj:`str`): User's Secret key

        Returns: 
            class:`models.responses.AuthResponse` object
        """
        if login:
            self.login = login
        if security_key:
            self.security_key = security_key
        response = self._auth()
        return resp.AuthResponse(**response)

    def get_forms(self):
        """
        Get all available form templates

        Returns: 
            class:`models.responses.FormsResponse` object
        """
        url = self._create_url('/forms')
        response = self._perform_get_request(url)
        return resp.FormsResponse(**response)

    def get_registry(self, form_id, form_register_request=None):
        """
        Get a list of tasks based on the form template

        Args:
            form_id (:obj:`int`): Form id
            form_register_request (:obj:`models.requests.FormRegisterRequest`, optional): Request filters.

        Returns: 
            class:`models.responses.FormRegisterResponse` object
        """
        url = self._create_url('/forms/{}/register'.format(form_id))
        if form_register_request:
            if not isinstance(form_register_request, req.FormRegisterRequest):
                raise TypeError('form_register_request must be an instance '
                                'of models.requests.FormRegisterRequest')
            response = self._perform_post_request(url, form_register_request)
        else:
            response = self._perform_get_request(url)

        if form_register_request and getattr(form_register_request, 'format', 'json') == "csv":
            return response

        return resp.FormRegisterResponse(**response)

    def get_contacts(self):
        """
        Get a list of contacts available to the current user and grouped by organization

        Returns: 
            class:`models.responses.ContactsResponse` object
        """
        url = self._create_url('/contacts')
        response = self._perform_get_request(url)
        return resp.ContactsResponse(**response)

    def get_catalog(self, catalog_id):
        """
        Get a catalog

        Args:
            catalog_id (:obj:`int`): Catalog id

        Returns: 
            class:`models.responses.CatalogResponse` object
        """
        if not isinstance(catalog_id, int):
            raise Exception("catalog_id should be valid int")

        url = self._create_url('/catalogs/{}'.format(catalog_id))
        response = self._perform_get_request(url)
        response = resp.CatalogResponse(**response)
        if response.error:
            raise Exception(response.error)
        print(response.catalog)
        return Catalog(response.catalog)

    def get_form(self, form_id) -> ent.Form:
        """
        Get the form template

        Args:
            form_id (:obj:`int`): form id

        Returns:
            class:`models.responses.FormResponse` object
        """
        if not isinstance(form_id, int):
            raise Exception("form_id should be valid int")

        url = self._create_url('/forms/{}'.format(form_id))
        response = self._perform_get_request(url)

        form_data = {
    "id": 904834,
    "name": "Opportunity",
    "default_person_id": 511948,
    "steps": {
        "1": "Quotations adding",
        "2": "Extended offer validity approval",
        "3": "BDM - Informing",
        "4": "COO + CCO",
        "5": "CEO",
        "6": "Print and send",
        "7": "Awaiting",
        "8": "Request for contract",
        "9": "COO",
        "10": "Quotations adding",
        "11": "Stock awaiting"
    },
    "workflow_advanced_steps": [
        {
            "is_queue_step": False,
            "additional_conditions": [
                {
                    "condition_item": {
                        "field_id": 0,
                        "condition_type": 11,
                        "value": "",
                        "catalog_column": 0,
                        "children": [
                            {
                                "field_id": 32,
                                "condition_type": 2,
                                "value": "",
                                "catalog_column": 0
                            },
                            {
                                "field_id": 107,
                                "condition_type": 8,
                                "value": "1",
                                "catalog_column": 0
                            }
                        ]
                    },
                    "external_access_only": False,
                    "role_ids": [
                        547943
                    ]
                }
            ]
        },
        {
            "is_queue_step": False,
            "additional_conditions": [
                {
                    "condition_item": {
                        "field_id": 0,
                        "condition_type": 11,
                        "value": "",
                        "catalog_column": 0,
                        "children": [
                            {
                                "field_id": 57,
                                "condition_type": 5,
                                "value": "1",
                                "catalog_column": 0
                            },
                            {
                                "field_id": 27,
                                "condition_type": 8,
                                "value": "1",
                                "catalog_column": 0
                            },
                            {
                                "field_id": 85,
                                "condition_type": 3,
                                "value": "",
                                "catalog_column": 0
                            },
                            {
                                "field_id": 107,
                                "condition_type": 8,
                                "value": "1",
                                "catalog_column": 0
                            }
                        ]
                    },
                    "external_access_only": False,
                    "role_ids": [
                        547907,
                        537634,
                        515736
                    ]
                },
                {
                    "condition_item": {
                        "field_id": 0,
                        "condition_type": 11,
                        "value": "",
                        "catalog_column": 0,
                        "children": [
                            {
                                "field_id": 57,
                                "condition_type": 5,
                                "value": "1",
                                "catalog_column": 0
                            },
                            {
                                "field_id": 27,
                                "condition_type": 5,
                                "value": "1",
                                "catalog_column": 0
                            },
                            {
                                "field_id": 85,
                                "condition_type": 3,
                                "value": "",
                                "catalog_column": 0
                            },
                            {
                                "field_id": 107,
                                "condition_type": 8,
                                "value": "1",
                                "catalog_column": 0
                            }
                        ]
                    },
                    "external_access_only": False,
                    "role_ids": [
                        511948
                    ]
                }
            ]
        },
        {
            "is_queue_step": False,
            "additional_conditions": [
                {
                    "condition_item": {
                        "field_id": 0,
                        "condition_type": 11,
                        "value": "",
                        "catalog_column": 0,
                        "children": [
                            {
                                "field_id": 27,
                                "condition_type": 8,
                                "value": "1",
                                "catalog_column": 0
                            },
                            {
                                "field_id": 85,
                                "condition_type": 3,
                                "value": "",
                                "catalog_column": 0
                            },
                            {
                                "field_id": 107,
                                "condition_type": 8,
                                "value": "1",
                                "catalog_column": 0
                            }
                        ]
                    },
                    "external_access_only": False
                },
                {
                    "condition_item": {
                        "field_id": 0,
                        "condition_type": 11,
                        "value": "",
                        "catalog_column": 0,
                        "children": [
                            {
                                "field_id": 27,
                                "condition_type": 5,
                                "value": "1",
                                "catalog_column": 0
                            },
                            {
                                "field_id": 85,
                                "condition_type": 3,
                                "value": "",
                                "catalog_column": 0
                            },
                            {
                                "field_id": 107,
                                "condition_type": 8,
                                "value": "1",
                                "catalog_column": 0
                            }
                        ]
                    },
                    "external_access_only": False,
                    "role_ids": [
                        511948
                    ]
                }
            ]
        },
        {
            "is_queue_step": False,
            "additional_conditions": [
                {
                    "condition_item": {
                        "field_id": 0,
                        "condition_type": 11,
                        "value": "",
                        "catalog_column": 0,
                        "children": [
                            {
                                "field_id": 27,
                                "condition_type": 8,
                                "value": "1",
                                "catalog_column": 0
                            },
                            {
                                "field_id": 85,
                                "condition_type": 3,
                                "value": "",
                                "catalog_column": 0
                            },
                            {
                                "field_id": 107,
                                "condition_type": 8,
                                "value": "1",
                                "catalog_column": 0
                            }
                        ]
                    },
                    "external_access_only": False,
                    "role_ids": [
                        547907,
                        537634
                    ]
                },
                {
                    "condition_item": {
                        "field_id": 0,
                        "condition_type": 11,
                        "value": "",
                        "catalog_column": 0,
                        "children": [
                            {
                                "field_id": 27,
                                "condition_type": 5,
                                "value": "1",
                                "catalog_column": 0
                            },
                            {
                                "field_id": 85,
                                "condition_type": 3,
                                "value": "",
                                "catalog_column": 0
                            },
                            {
                                "field_id": 107,
                                "condition_type": 8,
                                "value": "1",
                                "catalog_column": 0
                            }
                        ]
                    },
                    "external_access_only": False,
                    "role_ids": [
                        511948
                    ]
                }
            ]
        },
        {
            "is_queue_step": False,
            "additional_conditions": [
                {
                    "condition_item": {
                        "field_id": 0,
                        "condition_type": 11,
                        "value": "",
                        "catalog_column": 0,
                        "children": [
                            {
                                "field_id": 27,
                                "condition_type": 8,
                                "value": "1",
                                "catalog_column": 0
                            },
                            {
                                "field_id": 85,
                                "condition_type": 3,
                                "value": "",
                                "catalog_column": 0
                            },
                            {
                                "field_id": 107,
                                "condition_type": 8,
                                "value": "1",
                                "catalog_column": 0
                            }
                        ]
                    },
                    "external_access_only": False,
                    "role_ids": [
                        515736
                    ]
                },
                {
                    "condition_item": {
                        "field_id": 0,
                        "condition_type": 11,
                        "value": "",
                        "catalog_column": 0,
                        "children": [
                            {
                                "field_id": 27,
                                "condition_type": 5,
                                "value": "1",
                                "catalog_column": 0
                            },
                            {
                                "field_id": 85,
                                "condition_type": 3,
                                "value": "",
                                "catalog_column": 0
                            },
                            {
                                "field_id": 107,
                                "condition_type": 8,
                                "value": "1",
                                "catalog_column": 0
                            }
                        ]
                    },
                    "external_access_only": False,
                    "role_ids": [
                        511948
                    ]
                }
            ]
        },
        {
            "is_queue_step": False
        },
        {
            "is_queue_step": False,
            "additional_conditions": [
                {
                    "condition_item": {
                        "field_id": 0,
                        "condition_type": 11,
                        "value": "",
                        "catalog_column": 0,
                        "children": [
                            {
                                "field_id": 85,
                                "condition_type": 2,
                                "value": "",
                                "catalog_column": 0
                            },
                            {
                                "field_id": 27,
                                "condition_type": 8,
                                "value": "1",
                                "catalog_column": 0
                            },
                            {
                                "field_id": 107,
                                "condition_type": 8,
                                "value": "1",
                                "catalog_column": 0
                            }
                        ]
                    },
                    "external_access_only": False,
                    "role_ids": [
                        517328
                    ]
                },
                {
                    "condition_item": {
                        "field_id": 0,
                        "condition_type": 11,
                        "value": "",
                        "catalog_column": 0,
                        "children": [
                            {
                                "field_id": 27,
                                "condition_type": 8,
                                "value": "1",
                                "catalog_column": 0
                            },
                            {
                                "field_id": 85,
                                "condition_type": 3,
                                "value": "",
                                "catalog_column": 0
                            },
                            {
                                "field_id": 107,
                                "condition_type": 8,
                                "value": "1",
                                "catalog_column": 0
                            }
                        ]
                    },
                    "external_access_only": False
                }
            ]
        },
        {
            "is_queue_step": False,
            "additional_conditions": [
                {
                    "condition_item": {
                        "field_id": 0,
                        "condition_type": 11,
                        "value": "",
                        "catalog_column": 0,
                        "children": [
                            {
                                "field_id": 27,
                                "condition_type": 8,
                                "value": "1",
                                "catalog_column": 0
                            },
                            {
                                "field_id": 107,
                                "condition_type": 8,
                                "value": "1",
                                "catalog_column": 0
                            }
                        ]
                    },
                    "external_access_only": False,
                    "role_ids": [
                        587606
                    ]
                },
                {
                    "condition_item": {
                        "field_id": 0,
                        "condition_type": 11,
                        "value": "",
                        "catalog_column": 0,
                        "children": [
                            {
                                "field_id": 27,
                                "condition_type": 5,
                                "value": "1",
                                "catalog_column": 0
                            },
                            {
                                "field_id": 107,
                                "condition_type": 8,
                                "value": "1",
                                "catalog_column": 0
                            }
                        ]
                    },
                    "external_access_only": False,
                    "role_ids": [
                        511948
                    ]
                },
                {
                    "condition_item": {
                        "field_id": 0,
                        "condition_type": 11,
                        "value": "",
                        "catalog_column": 0,
                        "children": [
                            {
                                "field_id": 27,
                                "condition_type": 8,
                                "value": "1",
                                "catalog_column": 0
                            },
                            {
                                "field_id": 107,
                                "condition_type": 8,
                                "value": "1",
                                "catalog_column": 0
                            }
                        ]
                    },
                    "external_access_only": False
                },
                {
                    "condition_item": {
                        "field_id": 0,
                        "condition_type": 11,
                        "value": "",
                        "catalog_column": 0,
                        "children": [
                            {
                                "field_id": 27,
                                "condition_type": 8,
                                "value": "1",
                                "catalog_column": 0
                            },
                            {
                                "field_id": 107,
                                "condition_type": 8,
                                "value": "1",
                                "catalog_column": 0
                            }
                        ]
                    },
                    "external_access_only": False
                }
            ]
        },
        {
            "is_queue_step": False,
            "additional_conditions": [
                {
                    "condition_item": {
                        "field_id": 0,
                        "condition_type": 11,
                        "value": "",
                        "catalog_column": 0,
                        "children": [
                            {
                                "field_id": 107,
                                "condition_type": 5,
                                "value": "1",
                                "catalog_column": 0
                            },
                            {
                                "field_id": 27,
                                "condition_type": 8,
                                "value": "1",
                                "catalog_column": 0
                            }
                        ]
                    },
                    "external_access_only": False,
                    "role_ids": [
                        547907
                    ]
                },
                {
                    "condition_item": {
                        "field_id": 0,
                        "condition_type": 11,
                        "value": "",
                        "catalog_column": 0,
                        "children": [
                            {
                                "field_id": 107,
                                "condition_type": 5,
                                "value": "1",
                                "catalog_column": 0
                            },
                            {
                                "field_id": 27,
                                "condition_type": 5,
                                "value": "1",
                                "catalog_column": 0
                            }
                        ]
                    },
                    "external_access_only": False,
                    "role_ids": [
                        511948
                    ]
                }
            ]
        },
        {
            "is_queue_step": False,
            "additional_conditions": [
                {
                    "condition_item": {
                        "field_id": 0,
                        "condition_type": 11,
                        "value": "",
                        "catalog_column": 0,
                        "children": [
                            {
                                "field_id": 32,
                                "condition_type": 2,
                                "value": "",
                                "catalog_column": 0
                            },
                            {
                                "field_id": 107,
                                "condition_type": 5,
                                "value": "1",
                                "catalog_column": 0
                            }
                        ]
                    },
                    "external_access_only": False,
                    "role_ids": [
                        547943
                    ]
                }
            ]
        },
        {
            "is_queue_step": False,
            "additional_conditions": [
                {
                    "condition_item": {
                        "field_id": 0,
                        "condition_type": 11,
                        "value": "",
                        "catalog_column": 0,
                        "children": [
                            {
                                "field_id": 107,
                                "condition_type": 5,
                                "value": "1",
                                "catalog_column": 0
                            },
                            {
                                "field_id": 27,
                                "condition_type": 8,
                                "value": "1",
                                "catalog_column": 0
                            }
                        ]
                    },
                    "external_access_only": False,
                    "role_ids": [
                        513931
                    ]
                },
                {
                    "condition_item": {
                        "field_id": 0,
                        "condition_type": 11,
                        "value": "",
                        "catalog_column": 0,
                        "children": [
                            {
                                "field_id": 107,
                                "condition_type": 5,
                                "value": "1",
                                "catalog_column": 0
                            },
                            {
                                "field_id": 27,
                                "condition_type": 5,
                                "value": "1",
                                "catalog_column": 0
                            }
                        ]
                    },
                    "external_access_only": False,
                    "role_ids": [
                        511948
                    ]
                }
            ]
        },
        {
            "is_queue_step": False,
            "additional_conditions": [
                {
                    "condition_item": {
                        "field_id": 0,
                        "condition_type": 0,
                        "value": "",
                        "catalog_column": 0
                    },
                    "external_access_only": False,
                    "role_ids": [
                        513929
                    ]
                },
                {
                    "condition_item": {
                        "field_id": 0,
                        "condition_type": 0,
                        "value": "",
                        "catalog_column": 0
                    },
                    "external_access_only": False,
                    "role_ids": [
                        513908
                    ]
                },
                {
                    "condition_item": {
                        "field_id": 9,
                        "condition_type": 5,
                        "value": "UL",
                        "catalog_column": 2
                    },
                    "external_access_only": False,
                    "role_ids": [
                        513907
                    ]
                },
                {
                    "condition_item": {
                        "field_id": 9,
                        "condition_type": 5,
                        "value": "UL",
                        "catalog_column": 2
                    },
                    "external_access_only": False,
                    "role_ids": [
                        548730
                    ]
                },
                {
                    "condition_item": {
                        "field_id": 0,
                        "condition_type": 0,
                        "value": "",
                        "catalog_column": 0
                    },
                    "external_access_only": False,
                    "role_ids": [
                        567326
                    ]
                },
                {
                    "condition_item": {
                        "field_id": 0,
                        "condition_type": 0,
                        "value": "",
                        "catalog_column": 0
                    },
                    "external_access_only": False,
                    "role_ids": [
                        536633
                    ]
                },
                {
                    "condition_item": {
                        "field_id": 0,
                        "condition_type": 0,
                        "value": "",
                        "catalog_column": 0
                    },
                    "external_access_only": False,
                    "role_ids": [
                        536636
                    ]
                },
                {
                    "condition_item": {
                        "field_id": 0,
                        "condition_type": 0,
                        "value": "",
                        "catalog_column": 0
                    },
                    "external_access_only": False,
                    "role_ids": [
                        537624
                    ]
                },
                {
                    "condition_item": {
                        "field_id": 0,
                        "condition_type": 0,
                        "value": "",
                        "catalog_column": 0
                    },
                    "external_access_only": False,
                    "role_ids": [
                        536637
                    ]
                },
                {
                    "condition_item": {
                        "field_id": 0,
                        "condition_type": 0,
                        "value": "",
                        "catalog_column": 0
                    },
                    "external_access_only": False,
                    "role_ids": [
                        536638
                    ]
                },
                {
                    "condition_item": {
                        "field_id": 0,
                        "condition_type": 0,
                        "value": "",
                        "catalog_column": 0
                    },
                    "external_access_only": False,
                    "role_ids": [
                        517436
                    ]
                },
                {
                    "condition_item": {
                        "field_id": 0,
                        "condition_type": 0,
                        "value": "",
                        "catalog_column": 0
                    },
                    "external_access_only": False,
                    "role_ids": [
                        528102
                    ]
                },
                {
                    "condition_item": {
                        "field_id": 12,
                        "condition_type": 5,
                        "value": "CIS",
                        "catalog_column": 2
                    },
                    "external_access_only": False,
                    "role_ids": [
                        555547
                    ]
                },
                {
                    "condition_item": {
                        "field_id": 0,
                        "condition_type": 11,
                        "value": "",
                        "catalog_column": 0,
                        "children": [
                            {
                                "field_id": 0,
                                "condition_type": 10,
                                "value": "",
                                "catalog_column": 0,
                                "children": [
                                    {
                                        "field_id": 9,
                                        "condition_type": 5,
                                        "value": "CT",
                                        "catalog_column": 2
                                    },
                                    {
                                        "field_id": 9,
                                        "condition_type": 5,
                                        "value": "UL",
                                        "catalog_column": 2
                                    },
                                    {
                                        "field_id": 9,
                                        "condition_type": 5,
                                        "value": "VL",
                                        "catalog_column": 2
                                    },
                                    {
                                        "field_id": 9,
                                        "condition_type": 5,
                                        "value": "MR",
                                        "catalog_column": 2
                                    },
                                    {
                                        "field_id": 9,
                                        "condition_type": 5,
                                        "value": "XR",
                                        "catalog_column": 2
                                    },
                                    {
                                        "field_id": 9,
                                        "condition_type": 5,
                                        "value": "HIT",
                                        "catalog_column": 2
                                    }
                                ]
                            },
                            {
                                "field_id": 3,
                                "condition_type": 2,
                                "value": "",
                                "catalog_column": 0
                            },
                            {
                                "field_id": 9,
                                "condition_type": 3,
                                "value": "",
                                "catalog_column": 0
                            }
                        ]
                    },
                    "external_access_only": False,
                    "role_ids": [
                        515765
                    ]
                },
                {
                    "condition_item": {
                        "field_id": 3,
                        "condition_type": 5,
                        "value": "BYKOV ARKADIY",
                        "catalog_column": 0
                    },
                    "external_access_only": False,
                    "role_ids": [
                        513973
                    ]
                },
                {
                    "condition_item": {
                        "field_id": 3,
                        "condition_type": 5,
                        "value": "KAMNEVA ELENA",
                        "catalog_column": 0
                    },
                    "external_access_only": False,
                    "role_ids": [
                        513937
                    ]
                },
                {
                    "condition_item": {
                        "field_id": 3,
                        "condition_type": 5,
                        "value": "PETUKHOVA NATALIA",
                        "catalog_column": 0
                    },
                    "external_access_only": False,
                    "role_ids": [
                        513970
                    ]
                },
                {
                    "condition_item": {
                        "field_id": 3,
                        "condition_type": 5,
                        "value": "ILYASOV NAIL",
                        "catalog_column": 0
                    },
                    "external_access_only": False,
                    "role_ids": [
                        513974
                    ]
                },
                {
                    "condition_item": {
                        "field_id": 3,
                        "condition_type": 5,
                        "value": "SAFIULLIN RUSLAN",
                        "catalog_column": 0
                    },
                    "external_access_only": False,
                    "role_ids": [
                        513971
                    ]
                },
                {
                    "condition_item": {
                        "field_id": 3,
                        "condition_type": 5,
                        "value": "KRAVCHENKO DMITRY",
                        "catalog_column": 0
                    },
                    "external_access_only": False,
                    "role_ids": [
                        516071
                    ]
                },
                {
                    "condition_item": {
                        "field_id": 3,
                        "condition_type": 5,
                        "value": "ZIGANSHIN AYRAT",
                        "catalog_column": 0
                    },
                    "external_access_only": False,
                    "role_ids": [
                        517488
                    ]
                },
                {
                    "condition_item": {
                        "field_id": 0,
                        "condition_type": 0,
                        "value": "",
                        "catalog_column": 0
                    },
                    "external_access_only": False,
                    "role_ids": [
                        514010
                    ]
                },
                {
                    "condition_item": {
                        "field_id": 3,
                        "condition_type": 5,
                        "value": "GAUKHAR MUSSINA",
                        "catalog_column": 0
                    },
                    "external_access_only": False,
                    "role_ids": [
                        517477
                    ]
                },
                {
                    "condition_item": {
                        "field_id": 3,
                        "condition_type": 5,
                        "value": "SCHEGLOV ILYA",
                        "catalog_column": 0
                    },
                    "external_access_only": False,
                    "role_ids": [
                        562882
                    ]
                },
                {
                    "condition_item": {
                        "field_id": 0,
                        "condition_type": 0,
                        "value": "",
                        "catalog_column": 0
                    },
                    "external_access_only": False,
                    "role_ids": [
                        537634
                    ]
                },
                {
                    "condition_item": {
                        "field_id": 0,
                        "condition_type": 0,
                        "value": "",
                        "catalog_column": 0
                    },
                    "external_access_only": False,
                    "role_ids": [
                        515736
                    ]
                },
                {
                    "condition_item": {
                        "field_id": 0,
                        "condition_type": 0,
                        "value": "",
                        "catalog_column": 0
                    },
                    "external_access_only": False,
                    "role_ids": [
                        515748
                    ]
                },
                {
                    "condition_item": {
                        "field_id": 0,
                        "condition_type": 0,
                        "value": "",
                        "catalog_column": 0
                    },
                    "external_access_only": False,
                    "role_ids": [
                        513896
                    ]
                },
                {
                    "condition_item": {
                        "field_id": 0,
                        "condition_type": 0,
                        "value": "",
                        "catalog_column": 0
                    },
                    "external_access_only": False,
                    "role_ids": [
                        516073
                    ]
                },
                {
                    "condition_item": {
                        "field_id": 0,
                        "condition_type": 0,
                        "value": "",
                        "catalog_column": 0
                    },
                    "external_access_only": False,
                    "role_ids": [
                        554920
                    ]
                },
                {
                    "condition_item": {
                        "field_id": 0,
                        "condition_type": 0,
                        "value": "",
                        "catalog_column": 0
                    },
                    "external_access_only": False,
                    "role_ids": [
                        514178
                    ]
                }
            ]
        }
    ],
    "fields": [
        {
            "id": 11,
            "type": "creation_date",
            "name": "Дата создания",
            "tooltip": "",
            "info": {
                "code": "u_cdate"
            }
        },
        {
            "id": 1,
            "type": "text",
            "name": "Opportunity #",
            "tooltip": "",
            "info": {
                "immutable_step": 1,
                "code": "u_opportunity_id",
                "is_form_title": True,
                "multiline": False
            }
        },
        {
            "id": 3,
            "type": "catalog",
            "name": "BDM",
            "tooltip": "",
            "info": {
                "immutable_step": 1,
                "code": "u_bdm",
                "catalog_id": 102856,
                "multiple_choice": False
            }
        },
        {
            "id": 96,
            "type": "title",
            "name": "On stock",
            "tooltip": "",
            "visibility_condition": {
                "field_id": 0,
                "condition_type": 11,
                "value": "",
                "catalog_column": 0,
                "children": [
                    {
                        "field_id": 0,
                        "condition_type": 10,
                        "value": "",
                        "catalog_column": 0,
                        "children": [
                            {
                                "field_id": 3,
                                "condition_type": 5,
                                "value": "83176469",
                                "catalog_column": 0
                            }
                        ]
                    }
                ]
            },
            "info": {
                "fields": [
                    {
                        "id": 107,
                        "type": "multiple_choice",
                        "name": "Equipment on stock",
                        "tooltip": "",
                        "default_value": "2",
                        "parent_id": 96,
                        "info": {
                            "code": "u_eq_on_stock",
                            "large_view": False,
                            "options": [
                                {
                                    "choice_id": 0,
                                    "choice_value": "Не выбрано"
                                },
                                {
                                    "choice_id": 1,
                                    "choice_value": "Yes"
                                },
                                {
                                    "choice_id": 2,
                                    "choice_value": "No"
                                }
                            ]
                        }
                    },
                    {
                        "id": 108,
                        "type": "catalog",
                        "name": "Warehouse",
                        "tooltip": "",
                        "default_value": "84050646",
                        "parent_id": 96,
                        "info": {
                            "code": "u_warehouse",
                            "catalog_id": 124384,
                            "multiple_choice": False
                        }
                    },
                    {
                        "id": 109,
                        "type": "multiple_choice",
                        "name": "Shipping method",
                        "tooltip": "",
                        "parent_id": 96,
                        "info": {
                            "code": "u_shipping_method",
                            "large_view": False,
                            "options": [
                                {
                                    "choice_id": 0,
                                    "choice_value": "Не выбрано"
                                },
                                {
                                    "choice_id": 1,
                                    "choice_value": "AIR"
                                },
                                {
                                    "choice_id": 2,
                                    "choice_value": "SEA"
                                }
                            ]
                        }
                    }
                ]
            }
        },
        {
            "id": 37,
            "type": "checkmark",
            "name": "Add BDM #2",
            "tooltip": "",
            "visibility_condition": {
                "field_id": 0,
                "condition_type": 11,
                "value": "",
                "catalog_column": 0,
                "children": [
                    {
                        "field_id": 0,
                        "condition_type": 11,
                        "value": "",
                        "catalog_column": 0,
                        "children": [
                            {
                                "field_id": 107,
                                "condition_type": 8,
                                "value": "1",
                                "catalog_column": 0
                            }
                        ]
                    }
                ]
            },
            "info": {
                "code": "u_add_bdm"
            }
        },
        {
            "id": 38,
            "type": "catalog",
            "name": "BDM #2",
            "tooltip": "",
            "visibility_condition": {
                "field_id": 0,
                "condition_type": 11,
                "value": "",
                "catalog_column": 0,
                "children": [
                    {
                        "field_id": 37,
                        "condition_type": 3,
                        "value": "",
                        "catalog_column": 0
                    }
                ]
            },
            "info": {
                "code": "u_bdm2",
                "catalog_id": 102856,
                "multiple_choice": False
            }
        },
        {
            "id": 29,
            "type": "catalog",
            "name": "Project Manager",
            "tooltip": "",
            "visibility_condition": {
                "field_id": 0,
                "condition_type": 11,
                "value": "",
                "catalog_column": 0,
                "children": [
                    {
                        "field_id": 0,
                        "condition_type": 11,
                        "value": "",
                        "catalog_column": 0,
                        "children": [
                            {
                                "field_id": 107,
                                "condition_type": 8,
                                "value": "1",
                                "catalog_column": 0
                            }
                        ]
                    }
                ]
            },
            "info": {
                "code": "u_project_manager",
                "catalog_id": 113184,
                "multiple_choice": False
            }
        },
        {
            "id": 12,
            "type": "catalog",
            "name": "Region",
            "tooltip": "",
            "visibility_condition": {
                "field_id": 0,
                "condition_type": 11,
                "value": "",
                "catalog_column": 0,
                "children": [
                    {
                        "field_id": 0,
                        "condition_type": 11,
                        "value": "",
                        "catalog_column": 0,
                        "children": [
                            {
                                "field_id": 107,
                                "condition_type": 8,
                                "value": "1",
                                "catalog_column": 0
                            }
                        ]
                    }
                ]
            },
            "info": {
                "immutable_step": 1,
                "code": "u_reg",
                "catalog_id": 102955,
                "multiple_choice": False
            }
        },
        {
            "id": 23,
            "type": "form_link",
            "name": "Hospital",
            "tooltip": "",
            "visibility_condition": {
                "field_id": 0,
                "condition_type": 11,
                "value": "",
                "catalog_column": 0,
                "children": [
                    {
                        "field_id": 0,
                        "condition_type": 11,
                        "value": "",
                        "catalog_column": 0,
                        "children": [
                            {
                                "field_id": 107,
                                "condition_type": 8,
                                "value": "1",
                                "catalog_column": 0
                            }
                        ]
                    }
                ]
            },
            "info": {
                "code": "u_hospital",
                "form_id": 875510,
                "is_form_title": True
            }
        },
        {
            "id": 110,
            "type": "catalog",
            "name": "Hospital contacts",
            "tooltip": "",
            "visibility_condition": {
                "field_id": 0,
                "condition_type": 11,
                "value": "",
                "catalog_column": 0,
                "children": [
                    {
                        "field_id": 0,
                        "condition_type": 11,
                        "value": "",
                        "catalog_column": 0,
                        "children": [
                            {
                                "field_id": 107,
                                "condition_type": 8,
                                "value": "1",
                                "catalog_column": 0
                            }
                        ]
                    }
                ]
            },
            "info": {
                "code": "u_hospital_contacts",
                "catalog_id": 120886,
                "multiple_choice": False
            }
        },
        {
            "id": 39,
            "type": "checkmark",
            "name": "Private customer",
            "tooltip": "",
            "visibility_condition": {
                "field_id": 0,
                "condition_type": 11,
                "value": "",
                "catalog_column": 0,
                "children": [
                    {
                        "field_id": 0,
                        "condition_type": 11,
                        "value": "",
                        "catalog_column": 0,
                        "children": [
                            {
                                "field_id": 107,
                                "condition_type": 8,
                                "value": "1",
                                "catalog_column": 0
                            }
                        ]
                    }
                ]
            },
            "info": {
                "code": "u_private_customer"
            }
        },
        {
            "id": 41,
            "type": "form_link",
            "name": "Partner",
            "tooltip": "",
            "visibility_condition": {
                "field_id": 0,
                "condition_type": 11,
                "value": "",
                "catalog_column": 0,
                "children": [
                    {
                        "field_id": 0,
                        "condition_type": 11,
                        "value": "",
                        "catalog_column": 0,
                        "children": [
                            {
                                "field_id": 107,
                                "condition_type": 8,
                                "value": "1",
                                "catalog_column": 0
                            }
                        ]
                    }
                ]
            },
            "info": {
                "immutable_step": 1,
                "code": "u_partner_form",
                "form_id": 875513,
                "is_form_title": True
            }
        },
        {
            "id": 111,
            "type": "multiple_choice",
            "name": "Grade all eq",
            "tooltip": "",
            "visibility_condition": {
                "field_id": 0,
                "condition_type": 11,
                "value": "",
                "catalog_column": 0,
                "children": [
                    {
                        "field_id": 0,
                        "condition_type": 11,
                        "value": "",
                        "catalog_column": 0,
                        "children": [
                            {
                                "field_id": 107,
                                "condition_type": 8,
                                "value": "1",
                                "catalog_column": 0
                            }
                        ]
                    }
                ]
            },
            "info": {
                "immutable_step": 1,
                "code": "u_grade_all_eq",
                "large_view": False,
                "options": [
                    {
                        "choice_id": 0,
                        "choice_value": "Не выбрано"
                    },
                    {
                        "choice_id": 1,
                        "choice_value": "Strategic Partner"
                    },
                    {
                        "choice_id": 2,
                        "choice_value": "Senior Partner"
                    },
                    {
                        "choice_id": 3,
                        "choice_value": "Prime Partner"
                    },
                    {
                        "choice_id": 4,
                        "choice_value": "Spot Dealer"
                    }
                ]
            }
        },
        {
            "id": 112,
            "type": "multiple_choice",
            "name": "Grade UL only",
            "tooltip": "",
            "visibility_condition": {
                "field_id": 0,
                "condition_type": 11,
                "value": "",
                "catalog_column": 0,
                "children": [
                    {
                        "field_id": 0,
                        "condition_type": 11,
                        "value": "",
                        "catalog_column": 0,
                        "children": [
                            {
                                "field_id": 107,
                                "condition_type": 8,
                                "value": "1",
                                "catalog_column": 0
                            }
                        ]
                    }
                ]
            },
            "info": {
                "immutable_step": 1,
                "code": "u_grade_ul_only",
                "large_view": False,
                "options": [
                    {
                        "choice_id": 0,
                        "choice_value": "Не выбрано"
                    },
                    {
                        "choice_id": 1,
                        "choice_value": "Strategic Partner"
                    },
                    {
                        "choice_id": 2,
                        "choice_value": "Senior Partner"
                    },
                    {
                        "choice_id": 3,
                        "choice_value": "Prime Partner"
                    },
                    {
                        "choice_id": 4,
                        "choice_value": "Spot Dealer"
                    }
                ]
            }
        },
        {
            "id": 49,
            "type": "multiple_choice",
            "name": "Blocked",
            "tooltip": "",
            "visibility_condition": {
                "field_id": 0,
                "condition_type": 11,
                "value": "",
                "catalog_column": 0,
                "children": [
                    {
                        "field_id": 0,
                        "condition_type": 11,
                        "value": "",
                        "catalog_column": 0,
                        "children": [
                            {
                                "field_id": 107,
                                "condition_type": 8,
                                "value": "1",
                                "catalog_column": 0
                            }
                        ]
                    }
                ]
            },
            "info": {
                "code": "u_partner_blocked",
                "large_view": False,
                "options": [
                    {
                        "choice_id": 0,
                        "choice_value": "Не выбрано"
                    },
                    {
                        "choice_id": 1,
                        "choice_value": "ВНИМАНИЕ! ПАРТНЕР ЗАБЛОКИРОВАН! ПЕЧАТЬ КП НЕВОЗМОЖНА"
                    },
                    {
                        "choice_id": 2,
                        "choice_value": "Нет"
                    }
                ]
            }
        },
        {
            "id": 5,
            "type": "multiple_choice",
            "name": "Opportunity status",
            "tooltip": "",
            "default_value": "1",
            "visibility_condition": {
                "field_id": 0,
                "condition_type": 11,
                "value": "",
                "catalog_column": 0,
                "children": [
                    {
                        "field_id": 0,
                        "condition_type": 11,
                        "value": "",
                        "catalog_column": 0,
                        "children": [
                            {
                                "field_id": 107,
                                "condition_type": 8,
                                "value": "1",
                                "catalog_column": 0
                            }
                        ]
                    }
                ]
            },
            "info": {
                "large_view": False,
                "options": [
                    {
                        "choice_id": 0,
                        "choice_value": "Не выбрано"
                    },
                    {
                        "choice_id": 1,
                        "choice_value": "ACTIVE"
                    },
                    {
                        "choice_id": 2,
                        "choice_value": "SUSPENDED",
                        "deleted": True
                    },
                    {
                        "choice_id": 3,
                        "choice_value": "WON"
                    },
                    {
                        "choice_id": 9,
                        "choice_value": "PARTIALLY WON"
                    },
                    {
                        "choice_id": 4,
                        "choice_value": "CANCELED"
                    },
                    {
                        "choice_id": 5,
                        "choice_value": "STOCK",
                        "deleted": True
                    },
                    {
                        "choice_id": 6,
                        "choice_value": "DEMO",
                        "deleted": True
                    },
                    {
                        "choice_id": 7,
                        "choice_value": "CLOSED",
                        "deleted": True
                    },
                    {
                        "choice_id": 8,
                        "choice_value": "LOST"
                    }
                ]
            }
        },
        {
            "id": 6,
            "type": "date",
            "name": "Order intake date",
            "tooltip": "",
            "info": {
                "required_step": 1,
                "code": "u_order_intake_date",
                "is_required": True
            }
        },
        {
            "id": 98,
            "type": "catalog",
            "name": "City",
            "tooltip": "Заполняется автоматически из формы Hospital. Если это поле пустое, его необходимо заполнить в форме Hospital, после заполнения необходимо перевыбрать госпиталь",
            "visibility_condition": {
                "field_id": 0,
                "condition_type": 11,
                "value": "",
                "catalog_column": 0,
                "children": [
                    {
                        "field_id": 0,
                        "condition_type": 11,
                        "value": "",
                        "catalog_column": 0,
                        "children": [
                            {
                                "field_id": 107,
                                "condition_type": 8,
                                "value": "1",
                                "catalog_column": 0
                            }
                        ]
                    }
                ]
            },
            "info": {
                "immutable_step": 1,
                "code": "u_city",
                "catalog_id": 121277,
                "multiple_choice": False,
                "is_form_title": True
            }
        },
        {
            "id": 24,
            "type": "checkmark",
            "name": "KOL",
            "tooltip": "",
            "visibility_condition": {
                "field_id": 0,
                "condition_type": 11,
                "value": "",
                "catalog_column": 0,
                "children": [
                    {
                        "field_id": 0,
                        "condition_type": 11,
                        "value": "",
                        "catalog_column": 0,
                        "children": [
                            {
                                "field_id": 107,
                                "condition_type": 8,
                                "value": "1",
                                "catalog_column": 0
                            }
                        ]
                    }
                ]
            },
            "info": {
                "immutable_step": 1,
                "code": "u_kol"
            }
        },
        {
            "id": 32,
            "type": "checkmark",
            "name": "Отключить автоматическое создание Quotation по оборудованию, перечисленному в таблице ниже",
            "tooltip": ""
        },
        {
            "id": 8,
            "type": "table",
            "name": "Customer(s) and equipment",
            "tooltip": "",
            "info": {
                "required_step": 1,
                "code": "u_custandeq",
                "is_required": True,
                "columns": [
                    {
                        "id": 9,
                        "type": "catalog",
                        "name": "Model",
                        "tooltip": "",
                        "parent_id": 8,
                        "visibility_condition": {
                            "field_id": 0,
                            "condition_type": 11,
                            "value": "",
                            "catalog_column": 0
                        },
                        "info": {
                            "required_step": 1,
                            "code": "u_model",
                            "catalog_id": 102859,
                            "multiple_choice": False,
                            "is_required": True
                        }
                    },
                    {
                        "id": 16,
                        "type": "money",
                        "name": "Budget for system",
                        "tooltip": "",
                        "parent_id": 8,
                        "visibility_condition": {
                            "field_id": 0,
                            "condition_type": 11,
                            "value": "",
                            "catalog_column": 0
                        },
                        "info": {
                            "code": "u_sys_budget"
                        }
                    },
                    {
                        "id": 52,
                        "type": "checkmark",
                        "name": "For offer",
                        "tooltip": "",
                        "parent_id": 8,
                        "visibility_condition": {
                            "field_id": 0,
                            "condition_type": 11,
                            "value": "",
                            "catalog_column": 0
                        },
                        "info": {
                            "immutable_step": 4,
                            "code": "u_activeQuotation"
                        }
                    },
                    {
                        "id": 73,
                        "type": "money",
                        "name": "Current price",
                        "tooltip": "",
                        "parent_id": 8,
                        "visibility_condition": {
                            "field_id": 0,
                            "condition_type": 11,
                            "value": "",
                            "catalog_column": 0
                        },
                        "info": {
                            "code": "u_specification_total"
                        }
                    },
                    {
                        "id": 91,
                        "type": "money",
                        "name": "Total Price",
                        "tooltip": "",
                        "parent_id": 8,
                        "visibility_condition": {
                            "field_id": 0,
                            "condition_type": 11,
                            "value": "",
                            "catalog_column": 0
                        },
                        "info": {
                            "code": "u_total_price"
                        }
                    },
                    {
                        "id": 63,
                        "type": "text",
                        "name": "Quotation #",
                        "tooltip": "",
                        "parent_id": 8,
                        "visibility_condition": {
                            "field_id": 0,
                            "condition_type": 11,
                            "value": "",
                            "catalog_column": 0
                        },
                        "info": {
                            "code": "u_quotation_id",
                            "multiline": False
                        }
                    },
                    {
                        "id": 72,
                        "type": "multiple_choice",
                        "name": "Quotation status",
                        "tooltip": "",
                        "parent_id": 8,
                        "visibility_condition": {
                            "field_id": 0,
                            "condition_type": 11,
                            "value": "",
                            "catalog_column": 0
                        },
                        "info": {
                            "code": "u_quotstat",
                            "large_view": False,
                            "options": [
                                {
                                    "choice_id": 0,
                                    "choice_value": "Не выбрано"
                                },
                                {
                                    "choice_id": 1,
                                    "choice_value": "ACTIVE"
                                },
                                {
                                    "choice_id": 2,
                                    "choice_value": "SUSPENDED"
                                },
                                {
                                    "choice_id": 7,
                                    "choice_value": "WON"
                                },
                                {
                                    "choice_id": 3,
                                    "choice_value": "CANCELED"
                                },
                                {
                                    "choice_id": 4,
                                    "choice_value": "STOCK"
                                },
                                {
                                    "choice_id": 5,
                                    "choice_value": "DEMO"
                                },
                                {
                                    "choice_id": 6,
                                    "choice_value": "CLOSED"
                                },
                                {
                                    "choice_id": 8,
                                    "choice_value": "LOST"
                                },
                                {
                                    "choice_id": 9,
                                    "choice_value": "ALTERNATE"
                                }
                            ]
                        }
                    },
                    {
                        "id": 33,
                        "type": "text",
                        "name": "Specification #",
                        "tooltip": "",
                        "parent_id": 8,
                        "visibility_condition": {
                            "field_id": 0,
                            "condition_type": 11,
                            "value": "",
                            "catalog_column": 0
                        },
                        "info": {
                            "code": "u_specification_no",
                            "multiline": False
                        }
                    },
                    {
                        "id": 64,
                        "type": "text",
                        "name": "Specification status",
                        "tooltip": "",
                        "parent_id": 8,
                        "visibility_condition": {
                            "field_id": 0,
                            "condition_type": 11,
                            "value": "",
                            "catalog_column": 0
                        },
                        "info": {
                            "code": "u_specstatus",
                            "multiline": False
                        }
                    },
                    {
                        "id": 26,
                        "type": "text",
                        "name": "Comment",
                        "tooltip": "Short comment. Если госпиталь отличается, то надо это отметить в комментарии.",
                        "parent_id": 8,
                        "visibility_condition": {
                            "field_id": 0,
                            "condition_type": 11,
                            "value": "",
                            "catalog_column": 0
                        },
                        "info": {
                            "code": "u_001",
                            "multiline": False
                        }
                    },
                    {
                        "id": 30,
                        "type": "text",
                        "name": "Quotation link",
                        "tooltip": "",
                        "parent_id": 8,
                        "visibility_condition": {
                            "field_id": 0,
                            "condition_type": 11,
                            "value": "",
                            "catalog_column": 0
                        },
                        "info": {
                            "code": "u_quotlink",
                            "multiline": False
                        }
                    },
                    {
                        "id": 58,
                        "type": "text",
                        "name": "Specification link",
                        "tooltip": "",
                        "parent_id": 8,
                        "visibility_condition": {
                            "field_id": 0,
                            "condition_type": 11,
                            "value": "",
                            "catalog_column": 0
                        },
                        "info": {
                            "code": "u_specification_link",
                            "multiline": False
                        }
                    },
                    {
                        "id": 65,
                        "type": "text",
                        "name": "Related quotation link",
                        "tooltip": "",
                        "parent_id": 8,
                        "visibility_condition": {
                            "field_id": 0,
                            "condition_type": 11,
                            "value": "",
                            "catalog_column": 0
                        },
                        "info": {
                            "code": "u_related_quotation_link",
                            "multiline": False
                        }
                    },
                    {
                        "id": 19,
                        "type": "date",
                        "name": "Sales recognition date",
                        "tooltip": "",
                        "parent_id": 8,
                        "visibility_condition": {
                            "field_id": 0,
                            "condition_type": 11,
                            "value": "",
                            "catalog_column": 0
                        },
                        "info": {
                            "code": "u_rdd"
                        }
                    },
                    {
                        "id": 74,
                        "type": "money",
                        "name": "Current VAT",
                        "tooltip": "",
                        "parent_id": 8,
                        "visibility_condition": {
                            "field_id": 0,
                            "condition_type": 11,
                            "value": "",
                            "catalog_column": 0
                        },
                        "info": {
                            "code": "u_specification_VAT"
                        }
                    },
                    {
                        "id": 81,
                        "type": "money",
                        "name": "Price not including VAT",
                        "tooltip": "",
                        "parent_id": 8,
                        "visibility_condition": {
                            "field_id": 0,
                            "condition_type": 11,
                            "value": "",
                            "catalog_column": 0
                        },
                        "info": {
                            "code": "u_price_no_vat"
                        }
                    },
                    {
                        "id": 92,
                        "type": "money",
                        "name": "Total VAT",
                        "tooltip": "",
                        "parent_id": 8,
                        "visibility_condition": {
                            "field_id": 0,
                            "condition_type": 11,
                            "value": "",
                            "catalog_column": 0
                        },
                        "info": {
                            "code": "u_total_vat"
                        }
                    }
                ],
                "is_table": True
            }
        },
        {
            "id": 20,
            "type": "money",
            "name": "Project Budget",
            "tooltip": "",
            "visibility_condition": {
                "field_id": 0,
                "condition_type": 11,
                "value": "",
                "catalog_column": 0,
                "children": [
                    {
                        "field_id": 0,
                        "condition_type": 11,
                        "value": "",
                        "catalog_column": 0,
                        "children": [
                            {
                                "field_id": 107,
                                "condition_type": 8,
                                "value": "1",
                                "catalog_column": 0
                            }
                        ]
                    }
                ]
            }
        },
        {
            "id": 99,
            "type": "money",
            "name": "Project budget (calculated)",
            "tooltip": "",
            "visibility_condition": {
                "field_id": 0,
                "condition_type": 11,
                "value": "",
                "catalog_column": 0,
                "children": [
                    {
                        "field_id": 0,
                        "condition_type": 11,
                        "value": "",
                        "catalog_column": 0,
                        "children": [
                            {
                                "field_id": 107,
                                "condition_type": 8,
                                "value": "1",
                                "catalog_column": 0
                            }
                        ]
                    }
                ]
            },
            "info": {
                "code": "u_budget_calculated"
            }
        },
        {
            "id": 100,
            "type": "money",
            "name": "Project budget (actual)",
            "tooltip": "",
            "visibility_condition": {
                "field_id": 0,
                "condition_type": 11,
                "value": "",
                "catalog_column": 0,
                "children": [
                    {
                        "field_id": 0,
                        "condition_type": 11,
                        "value": "",
                        "catalog_column": 0,
                        "children": [
                            {
                                "field_id": 107,
                                "condition_type": 8,
                                "value": "1",
                                "catalog_column": 0
                            }
                        ]
                    }
                ]
            },
            "info": {
                "code": "u_budget_actual"
            }
        },
        {
            "id": 101,
            "type": "text",
            "name": "Budget validation",
            "tooltip": "",
            "visibility_condition": {
                "field_id": 0,
                "condition_type": 11,
                "value": "",
                "catalog_column": 0,
                "children": [
                    {
                        "field_id": 0,
                        "condition_type": 11,
                        "value": "",
                        "catalog_column": 0,
                        "children": [
                            {
                                "field_id": 107,
                                "condition_type": 8,
                                "value": "1",
                                "catalog_column": 0
                            }
                        ]
                    }
                ]
            },
            "info": {
                "code": "u_budget_validation",
                "multiline": False
            }
        },
        {
            "id": 40,
            "type": "title",
            "name": "Offer Data",
            "tooltip": "",
            "visibility_condition": {
                "field_id": 0,
                "condition_type": 11,
                "value": "",
                "catalog_column": 0,
                "children": [
                    {
                        "field_id": 0,
                        "condition_type": 11,
                        "value": "",
                        "catalog_column": 0,
                        "children": [
                            {
                                "field_id": 107,
                                "condition_type": 8,
                                "value": "1",
                                "catalog_column": 0
                            }
                        ]
                    }
                ]
            },
            "info": {
                "fields": [
                    {
                        "id": 42,
                        "type": "text",
                        "name": "Сounterpart name",
                        "tooltip": "",
                        "parent_id": 40,
                        "info": {
                            "code": "u_counterpart_name",
                            "multiline": False
                        }
                    },
                    {
                        "id": 43,
                        "type": "text",
                        "name": "Сounterpart address",
                        "tooltip": "",
                        "parent_id": 40,
                        "info": {
                            "code": "u_counterpart_address",
                            "multiline": False
                        }
                    },
                    {
                        "id": 45,
                        "type": "text",
                        "name": "Сounterpart contact name",
                        "tooltip": "",
                        "parent_id": 40
                    },
                    {
                        "id": 46,
                        "type": "text",
                        "name": "Сounterpart contact name (4 header)",
                        "tooltip": "",
                        "parent_id": 40
                    },
                    {
                        "id": 44,
                        "type": "text",
                        "name": "Сounterpart contact title",
                        "tooltip": "",
                        "parent_id": 40
                    },
                    {
                        "id": 51,
                        "type": "catalog",
                        "name": "Gender",
                        "tooltip": "",
                        "parent_id": 40,
                        "info": {
                            "catalog_id": 115647,
                            "multiple_choice": False
                        }
                    },
                    {
                        "id": 60,
                        "type": "checkmark",
                        "name": "Offer issued",
                        "tooltip": "",
                        "parent_id": 40,
                        "info": {
                            "code": "u_offer_issued"
                        }
                    },
                    {
                        "id": 47,
                        "type": "number",
                        "name": "Valid days",
                        "tooltip": "",
                        "default_value": "30,0000000000",
                        "parent_id": 40,
                        "info": {
                            "code": "u_offer_valid_days",
                            "decimal_places": 0
                        }
                    },
                    {
                        "id": 57,
                        "type": "multiple_choice",
                        "name": "Extended offer validity",
                        "tooltip": "",
                        "parent_id": 40,
                        "info": {
                            "code": "u_extended_offer_validity",
                            "large_view": False,
                            "options": [
                                {
                                    "choice_id": 0,
                                    "choice_value": "Не выбрано"
                                },
                                {
                                    "choice_id": 1,
                                    "choice_value": "Да"
                                },
                                {
                                    "choice_id": 2,
                                    "choice_value": "Нет"
                                }
                            ]
                        }
                    },
                    {
                        "id": 53,
                        "type": "text",
                        "name": "Warning",
                        "tooltip": "",
                        "parent_id": 40,
                        "visibility_condition": {
                            "field_id": 0,
                            "condition_type": 11,
                            "value": "",
                            "catalog_column": 0,
                            "children": [
                                {
                                    "field_id": 0,
                                    "condition_type": 10,
                                    "value": "",
                                    "catalog_column": 0,
                                    "children": [
                                        {
                                            "field_id": 57,
                                            "condition_type": 5,
                                            "value": "1",
                                            "catalog_column": 0
                                        }
                                    ]
                                }
                            ]
                        },
                        "info": {
                            "code": "u_valid_warning",
                            "multiline": True
                        }
                    },
                    {
                        "id": 86,
                        "type": "text",
                        "name": "Reason for extention",
                        "tooltip": "Напишите обоснование для увеличения срока действия КП",
                        "parent_id": 40,
                        "visibility_condition": {
                            "field_id": 0,
                            "condition_type": 11,
                            "value": "",
                            "catalog_column": 0,
                            "children": [
                                {
                                    "field_id": 0,
                                    "condition_type": 10,
                                    "value": "",
                                    "catalog_column": 0,
                                    "children": [
                                        {
                                            "field_id": 57,
                                            "condition_type": 5,
                                            "value": "1",
                                            "catalog_column": 0
                                        }
                                    ]
                                }
                            ]
                        },
                        "info": {
                            "required_step": 1,
                            "is_required": True,
                            "multiline": True
                        }
                    },
                    {
                        "id": 61,
                        "type": "note",
                        "name": "Consolidated commercial offer",
                        "tooltip": "Consolidated commercial offer",
                        "parent_id": 40,
                        "visibility_condition": {
                            "field_id": 0,
                            "condition_type": 11,
                            "value": "",
                            "catalog_column": 0,
                            "children": [
                                {
                                    "field_id": 0,
                                    "condition_type": 11,
                                    "value": "",
                                    "catalog_column": 0,
                                    "children": [
                                        {
                                            "field_id": 49,
                                            "condition_type": 8,
                                            "value": "1",
                                            "catalog_column": 0
                                        }
                                    ]
                                }
                            ]
                        }
                    },
                    {
                        "id": 66,
                        "type": "table",
                        "name": "Offer Data",
                        "tooltip": "",
                        "parent_id": 40,
                        "visibility_condition": {
                            "field_id": 0,
                            "condition_type": 11,
                            "value": "",
                            "catalog_column": 0,
                            "children": [
                                {
                                    "field_id": 0,
                                    "condition_type": 11,
                                    "value": "",
                                    "catalog_column": 0,
                                    "children": [
                                        {
                                            "field_id": 107,
                                            "condition_type": 8,
                                            "value": "1",
                                            "catalog_column": 0
                                        }
                                    ]
                                }
                            ]
                        },
                        "info": {
                            "code": "u_offer_data_table",
                            "columns": [
                                {
                                    "id": 75,
                                    "type": "checkmark",
                                    "name": "Active Offer",
                                    "tooltip": "",
                                    "parent_id": 66,
                                    "visibility_condition": {
                                        "field_id": 0,
                                        "condition_type": 11,
                                        "value": "",
                                        "catalog_column": 0
                                    },
                                    "info": {
                                        "code": "u_active_offer"
                                    }
                                },
                                {
                                    "id": 67,
                                    "type": "date",
                                    "name": "Offer creation date",
                                    "tooltip": "",
                                    "parent_id": 66,
                                    "visibility_condition": {
                                        "field_id": 0,
                                        "condition_type": 11,
                                        "value": "",
                                        "catalog_column": 0
                                    },
                                    "info": {
                                        "immutable_step": 1,
                                        "code": "u_offer_creation_date"
                                    }
                                },
                                {
                                    "id": 69,
                                    "type": "date",
                                    "name": "Offer expire date",
                                    "tooltip": "",
                                    "parent_id": 66,
                                    "visibility_condition": {
                                        "field_id": 0,
                                        "condition_type": 11,
                                        "value": "",
                                        "catalog_column": 0
                                    },
                                    "info": {
                                        "immutable_step": 1,
                                        "code": "u_offer_expire_date"
                                    }
                                },
                                {
                                    "id": 70,
                                    "type": "text",
                                    "name": "Specifications list",
                                    "tooltip": "",
                                    "parent_id": 66,
                                    "visibility_condition": {
                                        "field_id": 0,
                                        "condition_type": 11,
                                        "value": "",
                                        "catalog_column": 0
                                    },
                                    "info": {
                                        "immutable_step": 1,
                                        "code": "u_specifications_list",
                                        "multiline": False
                                    }
                                },
                                {
                                    "id": 68,
                                    "type": "file",
                                    "name": "Offer file",
                                    "tooltip": "",
                                    "parent_id": 66,
                                    "visibility_condition": {
                                        "field_id": 0,
                                        "condition_type": 11,
                                        "value": "",
                                        "catalog_column": 0
                                    },
                                    "info": {
                                        "immutable_step": 1,
                                        "code": "u_offer_file"
                                    }
                                },
                                {
                                    "id": 106,
                                    "type": "checkmark",
                                    "name": "Offer Discount Applied",
                                    "tooltip": "",
                                    "parent_id": 66,
                                    "visibility_condition": {
                                        "field_id": 0,
                                        "condition_type": 11,
                                        "value": "",
                                        "catalog_column": 0
                                    },
                                    "info": {
                                        "code": "u_offer_discount_applied"
                                    }
                                }
                            ],
                            "is_table": True
                        }
                    }
                ]
            }
        },
        {
            "id": 21,
            "type": "title",
            "name": "Win/Loss",
            "tooltip": "",
            "visibility_condition": {
                "field_id": 0,
                "condition_type": 11,
                "value": "",
                "catalog_column": 0,
                "children": [
                    {
                        "field_id": 0,
                        "condition_type": 10,
                        "value": "",
                        "catalog_column": 0,
                        "children": [
                            {
                                "field_id": 5,
                                "condition_type": 5,
                                "value": "3",
                                "catalog_column": 0
                            },
                            {
                                "field_id": 5,
                                "condition_type": 5,
                                "value": "9",
                                "catalog_column": 0
                            },
                            {
                                "field_id": 5,
                                "condition_type": 5,
                                "value": "8",
                                "catalog_column": 0
                            }
                        ]
                    }
                ]
            },
            "info": {
                "fields": [
                    {
                        "id": 22,
                        "type": "money",
                        "name": "Contract Price",
                        "tooltip": "",
                        "parent_id": 21,
                        "info": {
                            "code": "u_contract_price"
                        }
                    }
                ]
            }
        },
        {
            "id": 13,
            "type": "title",
            "name": "Technical Data",
            "tooltip": "",
            "info": {
                "fields": [
                    {
                        "id": 27,
                        "type": "multiple_choice",
                        "name": "TESTFORM",
                        "tooltip": "",
                        "parent_id": 13,
                        "info": {
                            "code": "u_testform",
                            "large_view": True,
                            "display_as": 1,
                            "options": [
                                {
                                    "choice_id": 0,
                                    "choice_value": "Не выбрано"
                                },
                                {
                                    "choice_id": 1,
                                    "choice_value": "Да"
                                },
                                {
                                    "choice_id": 2,
                                    "choice_value": "Нет",
                                    "deleted": True
                                }
                            ]
                        }
                    },
                    {
                        "id": 80,
                        "type": "text",
                        "name": "Partner name (English)",
                        "tooltip": "",
                        "parent_id": 13,
                        "visibility_condition": {
                            "field_id": 0,
                            "condition_type": 11,
                            "value": "",
                            "catalog_column": 0,
                            "children": [
                                {
                                    "field_id": 0,
                                    "condition_type": 10,
                                    "value": "",
                                    "catalog_column": 0,
                                    "children": [
                                        {
                                            "field_id": 27,
                                            "condition_type": 5,
                                            "value": "1",
                                            "catalog_column": 0
                                        }
                                    ]
                                },
                                {
                                    "field_id": 0,
                                    "condition_type": 11,
                                    "value": "",
                                    "catalog_column": 0,
                                    "children": [
                                        {
                                            "field_id": 107,
                                            "condition_type": 8,
                                            "value": "1",
                                            "catalog_column": 0
                                        }
                                    ]
                                }
                            ]
                        }
                    },
                    {
                        "id": 14,
                        "type": "text",
                        "name": "Responsible person",
                        "tooltip": "",
                        "parent_id": 13,
                        "visibility_condition": {
                            "field_id": 0,
                            "condition_type": 11,
                            "value": "",
                            "catalog_column": 0,
                            "children": [
                                {
                                    "field_id": 0,
                                    "condition_type": 10,
                                    "value": "",
                                    "catalog_column": 0,
                                    "children": [
                                        {
                                            "field_id": 27,
                                            "condition_type": 5,
                                            "value": "1",
                                            "catalog_column": 0
                                        }
                                    ]
                                },
                                {
                                    "field_id": 0,
                                    "condition_type": 11,
                                    "value": "",
                                    "catalog_column": 0,
                                    "children": [
                                        {
                                            "field_id": 107,
                                            "condition_type": 8,
                                            "value": "1",
                                            "catalog_column": 0
                                        }
                                    ]
                                }
                            ]
                        }
                    },
                    {
                        "id": 28,
                        "type": "text",
                        "name": "City.",
                        "tooltip": "Заполняется автоматически из Hospital",
                        "parent_id": 13,
                        "info": {
                            "immutable_step": 1,
                            "multiline": False
                        }
                    },
                    {
                        "id": 85,
                        "type": "checkmark",
                        "name": "Новая маршрутизация (КП по Opportunity)",
                        "tooltip": "",
                        "default_value": "True",
                        "parent_id": 13,
                        "info": {
                            "code": "u_new_opp_route"
                        }
                    },
                    {
                        "id": 88,
                        "type": "step",
                        "name": "Этап",
                        "tooltip": "",
                        "parent_id": 13
                    },
                    {
                        "id": 10,
                        "type": "text",
                        "name": "Number",
                        "tooltip": "",
                        "default_value": "",
                        "parent_id": 13,
                        "info": {
                            "code": "Form Task Sequence",
                            "multiline": False
                        }
                    },
                    {
                        "id": 78,
                        "type": "checkmark",
                        "name": "Request for additional or non-standart discount",
                        "tooltip": "",
                        "parent_id": 13,
                        "visibility_condition": {
                            "field_id": 0,
                            "condition_type": 11,
                            "value": "",
                            "catalog_column": 0,
                            "children": [
                                {
                                    "field_id": 0,
                                    "condition_type": 10,
                                    "value": "",
                                    "catalog_column": 0,
                                    "children": [
                                        {
                                            "field_id": 27,
                                            "condition_type": 5,
                                            "value": "1",
                                            "catalog_column": 0
                                        }
                                    ]
                                }
                            ]
                        },
                        "info": {
                            "code": "u_discount_request"
                        }
                    },
                    {
                        "id": 105,
                        "type": "text",
                        "name": "Justification",
                        "tooltip": "Обоснуйте, почему необходимо применить спеццену",
                        "parent_id": 13,
                        "visibility_condition": {
                            "field_id": 0,
                            "condition_type": 11,
                            "value": "",
                            "catalog_column": 0,
                            "children": [
                                {
                                    "field_id": 78,
                                    "condition_type": 3,
                                    "value": "",
                                    "catalog_column": 0
                                }
                            ]
                        },
                        "info": {
                            "required_step": 1,
                            "code": "u_justification",
                            "is_required": True,
                            "multiline": True
                        }
                    },
                    {
                        "id": 79,
                        "type": "form_link",
                        "name": "Request for discount task",
                        "tooltip": "Заполняется автоматически ботом",
                        "parent_id": 13,
                        "visibility_condition": {
                            "field_id": 0,
                            "condition_type": 11,
                            "value": "",
                            "catalog_column": 0,
                            "children": [
                                {
                                    "field_id": 0,
                                    "condition_type": 10,
                                    "value": "",
                                    "catalog_column": 0,
                                    "children": [
                                        {
                                            "field_id": 27,
                                            "condition_type": 5,
                                            "value": "1",
                                            "catalog_column": 0
                                        }
                                    ]
                                },
                                {
                                    "field_id": 78,
                                    "condition_type": 3,
                                    "value": "",
                                    "catalog_column": 0
                                }
                            ]
                        },
                        "info": {
                            "immutable_step": 1,
                            "code": "u_discount_request_task",
                            "form_id": 945069
                        }
                    },
                    {
                        "id": 104,
                        "type": "checkmark",
                        "name": "Discount Applied",
                        "tooltip": "",
                        "parent_id": 13,
                        "visibility_condition": {
                            "field_id": 0,
                            "condition_type": 11,
                            "value": "",
                            "catalog_column": 0,
                            "children": [
                                {
                                    "field_id": 78,
                                    "condition_type": 3,
                                    "value": "",
                                    "catalog_column": 0
                                }
                            ]
                        },
                        "info": {
                            "code": "u_discount_applied"
                        }
                    },
                    {
                        "id": 97,
                        "type": "text",
                        "name": "Номер договора",
                        "tooltip": "",
                        "parent_id": 13,
                        "visibility_condition": {
                            "field_id": 0,
                            "condition_type": 11,
                            "value": "",
                            "catalog_column": 0,
                            "children": [
                                {
                                    "field_id": 0,
                                    "condition_type": 11,
                                    "value": "",
                                    "catalog_column": 0,
                                    "children": [
                                        {
                                            "field_id": 107,
                                            "condition_type": 8,
                                            "value": "1",
                                            "catalog_column": 0
                                        }
                                    ]
                                }
                            ]
                        },
                        "info": {
                            "code": "u_agreement_id",
                            "multiline": False
                        }
                    },
                    {
                        "id": 102,
                        "type": "multiple_choice",
                        "name": "Договор подписан",
                        "tooltip": "",
                        "parent_id": 13,
                        "visibility_condition": {
                            "field_id": 0,
                            "condition_type": 11,
                            "value": "",
                            "catalog_column": 0,
                            "children": [
                                {
                                    "field_id": 0,
                                    "condition_type": 11,
                                    "value": "",
                                    "catalog_column": 0,
                                    "children": [
                                        {
                                            "field_id": 107,
                                            "condition_type": 8,
                                            "value": "1",
                                            "catalog_column": 0
                                        }
                                    ]
                                }
                            ]
                        },
                        "info": {
                            "code": "u_agr_stat",
                            "large_view": False,
                            "options": [
                                {
                                    "choice_id": 0,
                                    "choice_value": "Не выбрано"
                                },
                                {
                                    "choice_id": 1,
                                    "choice_value": "Да"
                                },
                                {
                                    "choice_id": 2,
                                    "choice_value": "Нет"
                                }
                            ]
                        }
                    }
                ]
            }
        }
    ],
    "access_levels": [
        {
            "person_id": 513907,
            "access_level": 3
        },
        {
            "person_id": 548730,
            "access_level": 3
        },
        {
            "person_id": 513908,
            "access_level": 3
        },
        {
            "person_id": 588793,
            "access_level": 4
        },
        {
            "person_id": 514010,
            "access_level": 3
        },
        {
            "person_id": 563577,
            "access_level": 4
        },
        {
            "person_id": 514012,
            "access_level": 4
        },
        {
            "person_id": 514013,
            "access_level": 2
        },
        {
            "person_id": 515765,
            "access_level": 3
        },
        {
            "person_id": 513929,
            "access_level": 3
        },
        {
            "person_id": 513931,
            "access_level": 2
        },
        {
            "person_id": 517328,
            "access_level": 2
        },
        {
            "person_id": 555547,
            "access_level": 3
        },
        {
            "person_id": 536633,
            "access_level": 3
        },
        {
            "person_id": 513937,
            "access_level": 3
        },
        {
            "person_id": 585038,
            "access_level": 4
        },
        {
            "person_id": 516071,
            "access_level": 3
        },
        {
            "person_id": 536636,
            "access_level": 3
        },
        {
            "person_id": 536637,
            "access_level": 3
        },
        {
            "person_id": 516073,
            "access_level": 3
        },
        {
            "person_id": 536638,
            "access_level": 3
        },
        {
            "person_id": 528102,
            "access_level": 3
        },
        {
            "person_id": 517436,
            "access_level": 3
        },
        {
            "person_id": 581948,
            "access_level": 4
        },
        {
            "person_id": 537624,
            "access_level": 3
        },
        {
            "person_id": 547907,
            "access_level": 2
        },
        {
            "person_id": 562947,
            "access_level": 4
        },
        {
            "person_id": 537634,
            "access_level": 3
        },
        {
            "person_id": 513970,
            "access_level": 3
        },
        {
            "person_id": 566447,
            "access_level": 4
        },
        {
            "person_id": 513971,
            "access_level": 3
        },
        {
            "person_id": 513973,
            "access_level": 3
        },
        {
            "person_id": 513974,
            "access_level": 3
        },
        {
            "person_id": 298344,
            "access_level": 2
        },
        {
            "person_id": 567326,
            "access_level": 3
        },
        {
            "person_id": 597785,
            "access_level": 4
        },
        {
            "person_id": 587606,
            "access_level": 4
        },
        {
            "person_id": 514178,
            "access_level": 3
        },
        {
            "person_id": 511948,
            "access_level": 4
        },
        {
            "person_id": 517477,
            "access_level": 3
        },
        {
            "person_id": 591101,
            "access_level": 4
        },
        {
            "person_id": 554920,
            "access_level": 3
        },
        {
            "person_id": 511949,
            "access_level": 4
        },
        {
            "person_id": 547940,
            "access_level": 4
        },
        {
            "person_id": 515736,
            "access_level": 3
        },
        {
            "person_id": 513896,
            "access_level": 3
        },
        {
            "person_id": 547943,
            "access_level": 2
        },
        {
            "person_id": 562882,
            "access_level": 3
        },
        {
            "person_id": 517488,
            "access_level": 3
        },
        {
            "person_id": 515748,
            "access_level": 3
        }
    ],
    "external_form_settings": {
        "header": "",
        "button_subject": "",
        "button_color": "",
        "success_message": "",
        "locale": 0,
        "density": 1
    },
    "helpdesk_settings": {},
    "deleted_or_closed": False,
    "is_datacenter_version": False,
    "skip_sms_channel": False
}
        response = resp.FormResponse(**form_data)
        if response.error:
            raise Exception(response.error)
        return Form(**form_data)

    def get_task(self, task_id):
        """
        Get the task

        Args:
            task_id (:obj:`int`): Task id

        Returns: 
            class:`models.responses.TaskResponse` object
        """
        if not isinstance(task_id, int):
            raise Exception("task_id should be valid int")
        url = self._create_url('/tasks/{}'.format(task_id))
        response = self._perform_get_request(url)
        return resp.TaskResponse(**response)

    def comment_task(self, task_id, task_comment_request):
        """
        Add task comment. This method returns a task with all comments, including the added one.
        Args:
            task_id (:obj:`int`): Task id
            task_comment_request (:obj:`models.requests.TaskCommentRequest`): Comment data.

        Returns:
            class:`models.responses.TaskResponse` object
        """
        if not isinstance(task_id, int):
            raise Exception("task_id should be valid int")
        url = self._create_url('/tasks/{}/comments'.format(task_id))
        if not isinstance(task_comment_request, req.TaskCommentRequest):
            raise TypeError('form_register_request must be an instance '
                            'of models.requests.TaskCommentRequest')
        response = self._perform_post_request(url, task_comment_request)
        return resp.TaskResponse(**response)

    def create_task(self, create_task_request):
        """
        Create task. This method returns a created task with a comment.

        Args:
            create_task_request (:obj:`models.requests.CreateTaskRequest`)

        Returns: 
            class:`models.responses.TaskResponse` object
        """
        url = self._create_url('/tasks')
        if not isinstance(create_task_request, req.CreateTaskRequest):
            raise TypeError('create_task_request must be an instance '
                            'of models.requests.CreateTaskRequest')
        response = self._perform_post_request(url, create_task_request)
        return resp.TaskResponse(**response)

    def upload_file(self, file_path):
        """
        Upload files for subsequent attachment to tasks.

        Args:
            file_path (:obj:`str`): Path to the file

        Returns: 
            class:`models.responses.UploadResponse` object
        """
        url = self._create_url('/files/upload')
        response = self._perform_request_with_retry(url, self.HTTPMethod.POST, file_path=file_path)
        return resp.UploadResponse(**response)

    def get_lists(self):
        """
        Get all the lists that are available to the user.

        Returns: 
            class:`models.responses.ListsResponse` object
        """
        url = self._create_url('/lists')
        response = self._perform_get_request(url)
        return resp.ListsResponse(**response)

    def get_task_list(self, list_id, item_count=200, include_archived=False):
        """
        Get all tasks in the list.

        Args:
            list_id (:obj:`int`): List id
            item_count (:obj:`int`, optional): The maximum number of tasks in the response, the default is 200
            include_archived (:obj:`bool`, optional): Should archived tasks be included to the response, the default is False

        Returns: 
            class:`models.responses.TaskListResponse` object
        """
        if not isinstance(list_id, int):
            raise TypeError('list_id must be an instance of int')
        if not isinstance(item_count, int):
            raise TypeError('item_count must be an instance of int')
        if not isinstance(include_archived, bool):
            raise TypeError('include_archived must be an instance of bool')

        url_suffix = '/lists/{}/tasks?item_count={}'.format(list_id, item_count)
        if include_archived:
            url_suffix += '&include_archived=y'

        url = self._create_url(url_suffix)
        response = self._perform_get_request(url)
        return resp.TaskListResponse(**response)

    def download_file(self, file_id):
        """
        Download the file.

        Args:
            file_id (:obj:`int`): File id

        Returns: 
            class:`models.responses.DownloadResponse` object
        """
        if not isinstance(file_id, int):
            raise TypeError('file_id must be an instance of int')
        url = self._download_file_base_url + str(file_id)
        response = self._perform_get_file_request(url)
        if response.status_code == 200:
            try:
                filename = rfc6266.parse_headers(response.headers['Content-Disposition']).filename_unsafe
            except:
                filename = re.findall('filename=(.+)', response.headers['Content-Disposition'])
            return resp.DownloadResponse(filename, response.content)
        else:
            if response.status_code == 401:
                return resp.BaseResponse(**{'error_code': 'authorization_error'})
            if response.status_code == 403 or response.status_code == 404:
                return resp.BaseResponse(**{'error_code': 'access_denied_file'})
            else:
                return resp.BaseResponse(**{'error_code': 'ServerError'})

    def create_catalog(self, create_catalog_request):
        """
        Create a catalog. This request returns created catalog with all elements

        Args:
            create_catalog_request (:obj:`models.requests.CreateCatalogRequest`): Catalog data.

        Returns: 
            class:`models.responses.CatalogResponse` object
        """
        url = self._create_url('/catalogs')
        if not isinstance(create_catalog_request, req.CreateCatalogRequest):
            raise TypeError('create_catalog_request must be an instance '
                            'of models.requests.CreateCatalogRequest')
        response = self._perform_put_request(url, create_catalog_request)
        return resp.CatalogResponse(**response)

    def sync_catalog(self, catalog_id, sync_catalog_request):
        """
        Sync a catalog. This method updates catalog headers and items. 
        You must define all the values and text columns that need to remain in the catalog.
        All unspecified items and text columns will be deleted.
        This method returns a list of items that have been added, modified, or deleted

        Args:
            sync_catalog_request (:obj:`models.requests.SyncCatalogRequest`): Catalog data.

        Returns: 
            class:`models.responses.SyncCatalogResponse` object
        """
        if not isinstance(catalog_id, int):
            raise TypeError("catalog_id must be an instance of int")
        url = self._create_url('/catalogs/{}'.format(catalog_id))
        if not isinstance(sync_catalog_request, req.SyncCatalogRequest):
            raise TypeError('sync_catalog_request must be an instance '
                            'of models.requests.SyncCatalogRequest')
        response = self._perform_post_request(url, sync_catalog_request)
        return resp.SyncCatalogResponse(**response)

    def serialize_request(self, body):
        return jsonpickle.encode(body, unpicklable=False).encode('utf-8')

    def _auth(self):
        url = self._create_url('/auth')
        headers = {
            'User-Agent': '{}'.format(self._user_agent),
            'Content-Type': 'application/json'
        }
        auth_request = req.AuthRequest(login=self.login, security_key=self.security_key)

        data = self.serialize_request(auth_request)

        auth_response = requests.post(url, headers=headers, data=data)
        # pylint: disable=no-member
        if auth_response.status_code == requests.codes.ok:
            response = auth_response.json()
            self.access_token = response['access_token']
        else:
            response = auth_response.json()
            self.access_token = None

        return response

    def _create_url(self, url):
        return '{}://{}{}{}'.format(self._protocol, self._host, self._base_path, url)

    def _perform_get_request(self, url):
        return self._perform_request_with_retry(url, self.HTTPMethod.GET)

    def _perform_get_file_request(self, url):
        return self._perform_request_with_retry(url, self.HTTPMethod.GET, get_file=True)

    def _perform_post_request(self, url, body=None):
        return self._perform_request_with_retry(url, self.HTTPMethod.POST, body)

    def _perform_put_request(self, url, body=None):
        return self._perform_request_with_retry(url, self.HTTPMethod.PUT, body)

    def _perform_request_with_retry(self, url, method, body=None, file_path=None, get_file=False):
        if not isinstance(method, self.HTTPMethod):
            raise TypeError('method must be an instanse of HTTPMethod Enum.')

        # try auth if no access token
        if not self.access_token:
            response = self._auth()
            if not self.access_token:
                return response

        # try to call api method
        response = self._perform_request(url, method, body, file_path, get_file)
        # if 401 try auth and call method again
        if response.status_code == 401:
            response = self._auth()
            # if failed return auth response
            if not self.access_token:
                return response

            response = self._perform_request(url, method, body, file_path, get_file)

        return self._get_response(response, get_file, body)

    def _perform_request(self, url, method, body, file_path, get_file):
        if method == self.HTTPMethod.POST:
            if file_path:
                return self._post_file_request(url, file_path)
            return self._post_request(url, body)
        if method == self.HTTPMethod.PUT:
            return self._put_request(url, body)
        if get_file:
            return self._get_file_request(url)
        return self._get_request(url)

    def _get_request(self, url):
        headers = self._create_default_headers()
        return requests.get(url, headers=headers, proxies=self.proxy)

    def _get_file_request(self, url):
        headers = self._create_default_headers()
        return requests.get(url, headers=headers, proxies=self.proxy, stream=True)

    def _post_request(self, url, body):
        headers = self._create_default_headers()
        if body:
            data = self.serialize_request(body)
        return requests.post(url, headers=headers, data=data, proxies=self.proxy)

    def _put_request(self, url, body):
        headers = self._create_default_headers()
        if body:
            data = self.serialize_request(body)
        return requests.put(url, headers=headers, data=data, proxies=self.proxy)

    def _post_file_request(self, url, file_path):
        headers = self._create_default_headers()
        del headers['Content-Type']
        if file_path:
            size = os.path.getsize(file_path)
            if size > self.MAX_FILE_SIZE_IN_BYTES:
                raise Exception("File size should not exceed {} MB".format(self.MAX_FILE_SIZE_IN_BYTES / 1024 / 1024))
            files = {'file': open(file_path, 'rb')}
        return requests.post(url, headers=headers, files=files, proxies=self.proxy)

    def _create_default_headers(self):
        headers = {
            'User-Agent': '{}'.format(self._user_agent),
            'Authorization': 'Bearer {}'.format(self.access_token),
            'Content-Type': 'application/json'
        }
        return headers

    def _get_response(self, response, get_file, request):
        if isinstance(request, req.FormRegisterRequest) and getattr(request, 'format', 'json') == "csv":
            res = resp.FormRegisterResponse()
            res.csv = response.text
            return res
        if get_file:
            return response
        return response.json()
