import pytest


class ValidationTestCase(object):
    '''Base class for validation test cases.'''

    def assert_result(self, data_text, results_classes, expected_classes):
        '''Check the expected validation errors were reported.

        If the results don't match what was expected, causes the current test
        to fail with a hopefully useful error message.

        '''
        not_raised = set(expected_classes).difference(results_classes)
        incorrectly_raised = results_classes.difference(expected_classes)

        if len(not_raised) != 0 or len(incorrectly_raised) != 0:
            message = ""
            if len(not_raised) != 0:
                not_raised_list = ', '.join(
                    repr(x) for x in not_raised)
                message += "Did not see expected " + not_raised_list + ". "
            if len(incorrectly_raised) != 0:
                incorrectly_raised_list = ', '.join(
                    repr(x) for x in incorrectly_raised)
                message += "Unexpected " + incorrectly_raised_list + ". "
            message += "Input was: '%s'" % data_text
            pytest.fail(message)



