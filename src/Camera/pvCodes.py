'''

Error and result codes used by the Prosilica API

Created on Jun 4, 2012

@author: redwards
'''
import sys

class pvErrors(object):
    def __init__(self):
        self.error={
            '0' : ['ePvErrSuccess', 'No error'],
            '1' : ['ePvErrCameraFault', 'Unexpected camera fault'],
            '2' : ['ePvErrInternalFault', 'Unexpected fault in PvApi or driver'],
            '3' : ['ePvErrBadHandle', 'Camera handle is invalid'],
            '4' : ['ePvErrBadParameter', 'Bad parameter to API call'],
            '5' : ['ePvErrBadSequence', 'Sequence of API calls is incorrect'],
            '6' : ['ePvErrNotFound', 'Camera or attribute not found'],
            '7' : ['ePvErrAccessDenied', 'Camera cannot be opened in the specified mode'],
            '8' : ['ePvErrUnplugged', 'Camera was unplugged'],
            '9' : ['ePvErrInvalidSetup', 'Setup is invalid (an attribute is invalid)'],
            '10' : ['ePvErrResources', 'System/network resources or memory not available'],
            '11' : ['ePvErrBandwidth', '1394 bandwidth not available'],
            '12' : ['ePvErrQueueFull', 'Too many frames on queue'],
            '13' : ['ePvErrBufferTooSmall', 'Frame buffer is too small'],
            '14' : ['ePvErrCancelled', 'Frame cancelled by user'],
            '15' : ['ePvErrDataLost', 'The data for the frame was lost'],
            '16' : ['ePvErrDataMissing', 'Some data in the frame is missing'],
            '17' : ['ePvErrTimeout', 'Timeout during wait'],
            '18' : ['ePvErrOutOfRange', 'Attribute value is out of the expected range'],
            '19' : ['ePvErrWrongType', 'Attribute is not this type (wrong access function) '],
            '20' : ['ePvErrForbidden', 'Attribute write forbidden at this time'],
            '21' : ['ePvErrUnavailable', 'Attribute is not available at this time'],
            '22' : ['ePvErrFirewall', 'A firewall is blocking the traffic (Windows only)']
            }

    def printError(self, code):
        sys.stderr.write("The error was code: " + str(code) + "\nAbbreviated to: " + self.error[code][0])
        sys.stderr.write("Which means: " + self.error[code][1])