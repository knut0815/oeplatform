
from api.tests import APITestCase
import json
from django.contrib.gis.geos import Point

class TestFields(APITestCase):

    @classmethod
    def setUpClass(cls):
        super(TestFields, cls).setUpClass()
        data = {"query": {"columns": [
            {"name": "id", "data_type": "bigserial", "is_nullable": "NO"},
            {"name": "name", "data_type": "varchar",
             "character_maximum_length": "50"},
            {"name": "geom", "data_type": "geometry(point)"}], "constraints": [
            {"constraint_type": "PRIMARY KEY", "constraint_parameter": "id"}]}}
        result = cls.client.put(
            '/api/v0/schema/test/tables/example_table/', data=json.dumps(data),
            HTTP_AUTHORIZATION='Token %s' % cls.token,
            content_type='application/json')
        assert result.status_code == 201, 'HTTP %d: %s'%(result.status_code,
                                                         result.content)

        cls.rows = [{"id": i, "name": "John Doe" + str(i),
                                "geom": str(Point(0, i, srid=32140).wkb)} for i in
                               range(10)]
        data = {"query": cls.rows}
        cls.client.post(
            '/api/v0/schema/test/tables/example_table/rows/new',
            data=json.dumps(data),
            HTTP_AUTHORIZATION='Token %s' % cls.token,
            content_type='application/json')
        assert result.status_code == 201, r'HTTP %d: %s'%(result.status_code,
                                                          result.content)


    def assertDataEqual(self, result, data):
        json_result = result.json()
        # Extract column names from description
        headers = [descr[0] for descr in json_result['description']]
        rows = [dict(zip(headers,x)) for x in json_result['data']]
        self.assertListEqual(rows, data)

    def post(self, data):
        return self.__class__.client.post(
            '/api/v0/advanced/search',
            data=json.dumps({'query': data}),
            HTTP_AUTHORIZATION='Token %s' % self.__class__.token,
            content_type='application/json')


    def test_simple(self):
        data = {'from': {
            'type': 'table',
            'table': 'example_table',
            'schema': 'test'
        }}
        result = self.post(data)
        self.assertStatus(result)
        self.assertDataEqual(result, self.rows)

    @classmethod
    def tearDownClass(cls):
        cls.client.requests.delete('/api/v0/schema/test/tables/example_table',
                                   HTTP_AUTHORIZATION='Token %s' % cls.token)
        super(TestFields, cls).tearDown()
