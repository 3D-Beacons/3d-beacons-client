# coding: utf-8

from __future__ import absolute_import

from flask import json
from six import BytesIO

from swagger_server.models.result import Result  # noqa: E501
from swagger_server.test import BaseTestCase


class TestDefaultController(BaseTestCase):
    """DefaultController integration test stubs"""

    def test_sequence_sequence_json_get(self):
        """Test case for sequence_sequence_json_get

        
        """
        query_string = [('provider', 'provider_example'),
                        ('template', 'template_example')]
        response = self.client.open(
            '/{basePath}/sequence/{sequence}.json'.format(sequence='sequence_example'),
            method='GET',
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_uniprot_qualifier_json_get(self):
        """Test case for uniprot_qualifier_json_get

        
        """
        query_string = [('provider', 'provider_example'),
                        ('template', 'template_example'),
                        ('range', 'range_example')]
        response = self.client.open(
            '/{basePath}/uniprot/{qualifier}.json'.format(qualifier='qualifier_example'),
            method='GET',
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_uniprot_qualifier_pdb_get(self):
        """Test case for uniprot_qualifier_pdb_get

        
        """
        query_string = [('sort', 'sort_example'),
                        ('provider', 'provider_example'),
                        ('template', 'template_example'),
                        ('range', 'range_example')]
        response = self.client.open(
            '/{basePath}/uniprot/{qualifier}.pdb'.format(qualifier='qualifier_example'),
            method='GET',
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
