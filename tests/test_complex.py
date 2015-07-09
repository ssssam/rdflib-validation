# Copyright (C) 2015  Codethink Limited
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; version 2 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program.  If not, see <http://www.gnu.org/licenses/>.


'''Real testcases for rdflib_validation.

These tests aim to weed out weaknesses and false positives in the validator.

FIXME: Using an OWL reasoner it should be possible to generate a 'complete'
set of valid and invalid triples ...

'''


import pytest
import rdflib

import rdflib_validation
from rdflib_validation import (
    DisjointClassMembership, DomainMismatch, RangeMismatch)

from base import ValidationTestCase
import test_basic


# This is boilerplate that gets prepended to every test case before parsing.
STANDARD_PREFIXES = '''
@prefix : <http://example.com/> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .

'''

class TestPropertiesWithNoDomainOrRange(object):
    pass


class TestObjectPropertiesWithSubclassing(ValidationTestCase):
    '''See test_basic.TestObjectProperties for the basic axiom.

    Validation should take the class heirarchy into account when checking if a
    resource is valid within the domain or range of a property.

    '''

    SCHEMA = test_basic.TestObjectProperties.SCHEMA + '''
    :ClassAsubclass a owl:Class ;
        rdfs:subClassOf :ClassA .
    :ClassBsubclass a owl:Class ;
        rdfs:subClassOf :ClassB .

    :instanceAA1 a :ClassAsubclass .
    :instanceBB1 a :ClassBsubclass.
    '''

    TESTCASES = {
        ''':instanceAA1 :relatedTo :instanceAA1 .''':
            [RangeMismatch],
        ''':instanceAA1 :relatedTo :instanceBB1 .''':
            [DomainMismatch],
        ''':instanceAA1 :relatedTo :instanceBB1 .''':
            []
    }

    @pytest.mark.parametrize("data,expected", TESTCASES.items())
    def test_all(self, data, expected):
        # FIXME: parsing the schema each time is dumb. Use a fixture.
        data_graph = rdflib.Graph()
        data_graph.parse(data=STANDARD_PREFIXES + data, format='turtle')

        schema_graph = rdflib.Graph()
        schema_graph.parse(data=STANDARD_PREFIXES + self.SCHEMA, format='turtle')

        results = rdflib_validation.validate(data_graph, schema_graph)

        results_classes = set(type(x) for x in results)
        self.assert_result(data, results_classes, expected)


class TestPropertyDomainAndRangeThroughSubproperties(object):
    pass
