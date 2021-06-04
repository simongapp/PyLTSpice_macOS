#!/usr/bin/env python
# ---------------------------------------------------------------------------------------------------
# Name:        DefinesDefault.py
# Purpose:     Implementation of the default values of the project
#
# Author:      Simon Gapp
#
# Created:     31.05.2018
# Licence:
# ---------------------------------------------------------------------------------------------------
""" Implementation of the default values of the project
"""
import getpass


def get_user():
    """Function to get the current user

    :parameter: None
    :return: login name of the user.
    """
    return getpass.getuser()


class Defines:
    """ Class for defines."""

    def get_define(self, key):
        """Function to retrieve a define

        :parameter key: Key to be searched in the dictionary
        :type key: str
        :return: The dictionary entry"""
        try:
            return self.total_dict[key]
        except KeyError as err:
            print(err)
            return

    def set_define(self, key, value):
        """Function to change a value of a default define

        :parameter key: Key of the default define
        :type key: str
        :parameter value: Value of the key
        :type value: various
        """
        try:
            self.total_dict[key] = value
        except KeyError as err:
            print(err)

    def __init__(self):
        """Generates a hardcoded dictionary for all LTSpice parameters"""
        self.total_dict = {
            # Default location of the LTSpice App
            'LTSPICE_APP_DEFAULT_LOC': '/Applications/LTspice.app',
            'LTSPICE_LIBRARY_DEFAULT_LOC': '/Users/' + get_user() + '/Library/Application Support/LTspice/lib/sym/',

            # Parameters of a sinus source
            'SOURCE_PARAMETERS_SINE': {'DC_Offset': 0,
                                       'Amplitude': 1,
                                       'Frequency': 2,
                                       'Delay': 3,
                                       'Dampfing_factor': 4,
                                       'Phase': 5,
                                       'Cycles': 6},

            'SOURCE_TYPES': ['SINE'],

            'ASC_COMPONENT_NAME_START': 'InstName',

            'ASC_COMPONENT_VALUE_START': 'Value',

            'SPICE_DIRECTIVES': ['.tran',
                                 '.ac',
                                 '.dc',
                                 '.noise',
                                 '.tf',
                                 '.op'],

            'LTSPICE_RUN_TIME': 1,

            'DEFAULT_ALIGNMENT_MAPPER': {'LEFT': 'Left',
                                         'CENTER': 'Center',
                                         'RIGHT': 'Right',
                                         'TOP': 'Top',
                                         'BOTTOM': 'Bottom',
                                         'VLEFT': 'VLeft',
                                         'VCENTER': 'VCenter',
                                         'VRIGHT': 'VRight',
                                         'VTOP': 'VTop',
                                         'VBOTTOM': 'VBottom'},

            'DEFAULT_LINE_STYLES': {0: '-',
                                    1: '--',
                                    2: ':',
                                    3: '-.',
                                    4: '-..'},

            'DEFAULT_FIG_SIZE': (20, 10),

            'DEFAULT_FONT_SIZE': 14,

            'LTSPICE_FONTSIZES': {0: 0.625,
                                  1: 1.0,
                                  2: 1.5,
                                  3: 2.0,
                                  4: 2.5,
                                  5: 3.5,
                                  6: 5.0,
                                  7: 7.0},

            'DEFAULT_JUNCTION_SIZE': 12,

            'PLOT_NO_OF_COORDINATES': {'WINDOW': 4,
                                       'PIN': 3,
                                       'Version': 1,
                                       'CIRCLE': 4,
                                       'LINE': 5,
                                       'RECTANGLE': 4,
                                       'ARC': 9,
                                       'TEXT': 2},

            'PLOT_KEYS': ['LINE',
                          'CIRCLE',
                          'ARC',
                          'RECTANGLE',
                          'WINDOW',
                          'TEXT',
                          'PIN'],

            'WINDOW_TYPES': {0: 'Prefix',
                             3: 'Value',
                             123: 'Value2',
                             39: 'SpiceLine'},

            'TEXT_VERTICAL_ALIGNMENTS': {'Left': {'R0': 'center',
                                                  'R90': 'top',
                                                  'R180': 'center',
                                                  'R270': 'bottom',  # ver 25.04

                                                  'M0': 'center',
                                                  'M90': 'top',
                                                  'M180': 'center',
                                                  'M270': 'bottom',  # ver 25.04

                                                  'R0ML': 'top',
                                                  'R90ML': 'top',
                                                  'R180ML': 'center',
                                                  'R270ML': 'bottom',

                                                  'M0ML': 'top',
                                                  'M90ML': 'top',
                                                  'M180ML': 'center',
                                                  'M270ML': 'center'
                                                  },

                                         'Center': {'R0': 'center',
                                                    'R90': 'center',
                                                    'R180': 'center',
                                                    'R270': 'center',

                                                    'M0': 'center',
                                                    'M90': 'center',
                                                    'M180': 'center',
                                                    'M270': 'center',

                                                    'R0ML': 'center',
                                                    'R90ML': 'center',
                                                    'R180ML': 'center',
                                                    'R270ML': 'center',

                                                    'M0ML': 'center',
                                                    'M90ML': 'center',
                                                    'M180ML': 'center',
                                                    'M270ML': 'center'
                                                    },

                                         'Right': {'R0': 'center',
                                                   'R90': 'bottom',
                                                   'R180': 'center',
                                                   'R270': 'top',  # ver 25.04

                                                   'M0': 'center',
                                                   'M90': 'bottom',  # ver 25.04
                                                   'M180': 'center',
                                                   'M270': 'top',  # ver 25.04

                                                   'R0ML': 'center',
                                                   'R90ML': 'bottom',
                                                   'R180ML': 'center',
                                                   'R270ML': 'top',

                                                   'M0ML': 'center',
                                                   'M90ML': 'bottom',
                                                   'M180ML': 'center',
                                                   'M270ML': 'top'
                                                   },

                                         'Top': {'R0': 'top',
                                                 'R90': 'center',  # ver 25.04
                                                 'R180': 'bottom',  # ver 25.04
                                                 'R270': 'center',  # ver 25.04

                                                 'M0': 'top',  # ver 25.04
                                                 'M90': 'center',  # ver 25.04
                                                 'M180': 'bottom',  # ver 25.04
                                                 'M270': 'center',

                                                 'R0ML': 'top',
                                                 'R90ML': 'top',
                                                 'R180ML': 'center',
                                                 'R270ML': 'bottom',

                                                 'M0ML': 'center',
                                                 'M90ML': 'top',
                                                 'M180ML': 'center',
                                                 'M270ML': 'bottom'
                                                 },

                                         'Bottom': {'R0': 'bottom',
                                                    'R90': 'bottom',
                                                    'R180': 'top',
                                                    'R270': 'center',  # ver 25.04

                                                    'M0': 'bottom',  # ver 25.04
                                                    'M90': 'center',
                                                    'M180': 'top',  # ver 25.04
                                                    'M270': 'center',  # ver 25.04

                                                    'R0ML': 'bottom',
                                                    'R90ML': 'bottom',
                                                    'R180ML': 'center',
                                                    'R270ML': 'top',

                                                    'M0ML': 'center',
                                                    'M90ML': 'bottom',
                                                    'M180ML': 'center',
                                                    'M270ML': 'top'
                                                    },

                                         'VLeft': {'R0': 'bottom',
                                                   'R90': 'top',
                                                   'R180': 'center',
                                                   'R270': 'center',

                                                   'M0': 'center',
                                                   'M90': 'top',
                                                   'M180': 'bottom',
                                                   'M270': 'center',

                                                   'R0ML': 'bottom',
                                                   'R90ML': 'top',
                                                   'R180ML': 'center',
                                                   'R270ML': 'center',

                                                   'M0ML': 'center',
                                                   'M90ML': 'top',
                                                   'M180ML': 'bottom',
                                                   'M270ML': 'center'
                                                   },

                                         'VCenter': {'R0': 'center',
                                                     'R90': 'center',
                                                     'R180': 'center',
                                                     'R270': 'center',

                                                     'M0': 'center',
                                                     'M90': 'center',
                                                     'M180': 'center',
                                                     'M270': 'center',

                                                     'R0ML': 'center',
                                                     'R90ML': 'center',
                                                     'R180ML': 'center',
                                                     'R270ML': 'center',

                                                     'M0ML': 'center',
                                                     'M90ML': 'center',
                                                     'M180ML': 'center',
                                                     'M270ML': 'center'
                                                     },

                                         'VRight': {'R0': 'top',
                                                    'R90': 'center',
                                                    'R180': 'bottom',
                                                    'R270': 'center',

                                                    'M0': 'top',
                                                    'M90': 'center',
                                                    'M180': 'bottom',
                                                    'M270': 'center',

                                                    'R0ML': 'top',
                                                    'R90ML': 'center',
                                                    'R180ML': 'bottom',
                                                    'R270ML': 'center',

                                                    'M0ML': 'top',
                                                    'M90ML': 'center',
                                                    'M180ML': 'bottom',
                                                    'M270ML': 'center'
                                                    },

                                         'VTop': {'R0': 'center',
                                                  'R90': 'top',
                                                  'R180': 'center',
                                                  'R270': 'bottom',

                                                  'M0': 'center',
                                                  'M90': 'top',
                                                  'M180': 'center',
                                                  'M270': 'bottom',

                                                  'R0ML': 'center',
                                                  'R90ML': 'top',
                                                  'R180ML': 'center',
                                                  'R270ML': 'bottom',

                                                  'M0ML': 'center',
                                                  'M90ML': 'top',
                                                  'M180ML': 'center',
                                                  'M270ML': 'bottom'
                                                  },

                                         'VBottom': {'R0': 'center',
                                                     'R90': 'bottom',
                                                     'R180': 'center',
                                                     'R270': 'top',

                                                     'M0': 'center',
                                                     'M90': 'bottom',
                                                     'M180': 'center',
                                                     'M270': 'top',

                                                     'R0ML': 'center',
                                                     'R90ML': 'bottom',
                                                     'R180ML': 'center',
                                                     'R270ML': 'top',

                                                     'M0ML': 'center',
                                                     'M90ML': 'bottom',
                                                     'M180ML': 'center',
                                                     'M270ML': 'top'
                                                     }
                                         },

            'TEXT_HORIZONTAL_ALIGNMENTS': {'Left': {'R0': 'left',
                                                    'R90': 'center',
                                                    'R180': 'right',
                                                    'R270': 'center',  # ver 25.04

                                                    'M0': 'right',  # ver 25.04
                                                    'M90': 'center',
                                                    'M180': 'left',  # ver 25.04
                                                    'M270': 'center',  # ver 25.04

                                                    'R0ML': 'left',
                                                    'R90ML': 'center',
                                                    'R180ML': 'right',
                                                    'R270ML': 'left',

                                                    'M0ML': 'right',
                                                    'M90ML': 'center',
                                                    'M180ML': 'left',
                                                    'M270ML': 'left'
                                                    },

                                           'Center': {'R0': 'center',
                                                      'R90': 'center',
                                                      'R180': 'center',
                                                      'R270': 'center',

                                                      'M0': 'center',
                                                      'M90': 'center',
                                                      'M180': 'center',
                                                      'M270': 'center',

                                                      'R0ML': 'center',
                                                      'R90ML': 'center',
                                                      'R180ML': 'center',
                                                      'R270ML': 'center',

                                                      'M0ML': 'center',
                                                      'M90ML': 'center',
                                                      'M180ML': 'center',
                                                      'M270ML': 'center'
                                                      },

                                           'Right': {'R0': 'right',
                                                     'R90': 'center',
                                                     'R180': 'left',
                                                     'R270': 'center',  # ver 25.04

                                                     'M0': 'left',  # ver 25.04
                                                     'M90': 'center',  # ver 25.04
                                                     'M180': 'right',
                                                     'M270': 'center',  # ver 25.04

                                                     'R0ML': 'right',
                                                     'R90ML': 'right',
                                                     'R180ML': 'right',
                                                     'R270ML': 'right',

                                                     'M0ML': 'right',
                                                     'M90ML': 'right',
                                                     'M180ML': 'right',
                                                     'M270ML': 'right'
                                                     },

                                           'Top': {'R0': 'center',
                                                   'R90': 'right',  # ver 25.04
                                                   'R180': 'center',
                                                   'R270': 'left',  # ver 25.04

                                                   'M0': 'center',
                                                   'M90': 'left',  # ver 25.04
                                                   'M180': 'center',
                                                   'M270': 'right',

                                                   'R0ML': 'center',
                                                   'R90ML': 'center',
                                                   'R180ML': 'center',
                                                   'R270ML': 'center',

                                                   'M0ML': 'center',
                                                   'M90ML': 'center',
                                                   'M180ML': 'center',
                                                   'M270ML': 'center'
                                                   },

                                           'Bottom': {'R0': 'center',
                                                      'R90': 'left',
                                                      'R180': 'center',
                                                      'R270': 'right',

                                                      'M0': 'center',
                                                      'M90': 'right',  # ver 25.04
                                                      'M180': 'center',
                                                      'M270': 'left',

                                                      'R0ML': 'center',
                                                      'R90ML': 'center',
                                                      'R180ML': 'center',
                                                      'R270ML': 'center',

                                                      'M0ML': 'center',
                                                      'M90ML': 'center',
                                                      'M180ML': 'center',
                                                      'M270ML': 'center'
                                                      },

                                           'VLeft': {'R0': 'center',
                                                     'R90': 'center',
                                                     'R180': 'right',
                                                     'R270': 'right',  # ver 01.05

                                                     'M0': 'right',
                                                     'M90': 'center',
                                                     'M180': 'left',
                                                     'M270': 'left',

                                                     'R0ML': 'center',
                                                     'R90ML': 'center',
                                                     'R180ML': 'right',
                                                     'R270ML': 'left',

                                                     'M0ML': 'right',
                                                     'M90ML': 'center',
                                                     'M180ML': 'left',
                                                     'M270ML': 'left'
                                                     },

                                           'VCenter': {'R0': 'center',
                                                       'R90': 'center',
                                                       'R180': 'center',
                                                       'R270': 'center',

                                                       'M0': 'center',
                                                       'M90': 'center',
                                                       'M180': 'center',
                                                       'M270': 'center',

                                                       'R0ML': 'center',
                                                       'R90ML': 'center',
                                                       'R180ML': 'center',
                                                       'R270ML': 'center',

                                                       'M0ML': 'center',
                                                       'M90ML': 'center',
                                                       'M180ML': 'center',
                                                       'M270ML': 'center'
                                                       },

                                           'VRight': {'R0': 'center',
                                                      'R90': 'right',
                                                      'R180': 'center',
                                                      'R270': 'left',

                                                      'M0': 'center',
                                                      'M90': 'left',  # ver 01.05
                                                      'M180': 'center',
                                                      'M270': 'left',

                                                      'R0ML': 'center',
                                                      'R90ML': 'left',
                                                      'R180ML': 'center',
                                                      'R270ML': 'left',

                                                      'M0ML': 'center',
                                                      'M90ML': 'left',
                                                      'M180ML': 'center',
                                                      'M270ML': 'left'
                                                      },

                                           'VTop': {'R0': 'left',
                                                    'R90': 'center',
                                                    'R180': 'right',
                                                    'R270': 'center',

                                                    'M0': 'right',
                                                    'M90': 'center',
                                                    'M180': 'left',
                                                    'M270': 'center',

                                                    'R0ML': 'left',
                                                    'R90ML': 'center',
                                                    'R180ML': 'right',
                                                    'R270ML': 'center',

                                                    'M0ML': 'right',
                                                    'M90ML': 'center',
                                                    'M180ML': 'left',
                                                    'M270ML': 'center'
                                                    },

                                           'VBottom': {'R0': 'right',
                                                       'R90': 'center',
                                                       'R180': 'left',
                                                       'R270': 'center',

                                                       'M0': 'left',  # ver 25.04
                                                       'M90': 'center',
                                                       'M180': 'right',  # ver 25.04
                                                       'M270': 'center',

                                                       'R0ML': 'left',
                                                       'R90ML': 'center',
                                                       'R180ML': 'right',
                                                       'R270ML': 'center',

                                                       'M0ML': 'right',
                                                       'M90ML': 'center',
                                                       'M180ML': 'left',
                                                       'M270ML': 'center'
                                                       }
                                           },

            'TEXT_ROTATION_ANGLES': {'Left': {'R0': 0,
                                              'R90': 90,
                                              'R180': 0,
                                              'R270': 90,

                                              'M0': 0,
                                              'M90': 90,
                                              'M180': 0,
                                              'M270': 90,

                                              'R0ML': 0,
                                              'R90ML': 90,
                                              'R180ML': 0,
                                              'R270ML': 0,

                                              'M0ML': 0,
                                              'M90ML': 90,
                                              'M180ML': 0,
                                              'M270ML': 90
                                              },

                                     'Center': {'R0': 0,
                                                'R90': 90,  # ver 25.04
                                                'R180': 0,
                                                'R270': 90,

                                                'M0': 0,
                                                'M90': 90,
                                                'M180': 0,
                                                'M270': 90,

                                                'R0ML': 0,
                                                'R90ML': 90,
                                                'R180ML': 0,
                                                'R270ML': 90,

                                                'M0ML': 0,
                                                'M90ML': 90,
                                                'M180ML': 0,
                                                'M270ML': 90
                                                },

                                     'Right': {'R0': 0,
                                               'R90': 90,  # ver 25.04
                                               'R180': 0,
                                               'R270': 90,

                                               'M0': 0,
                                               'M90': 90,
                                               'M180': 0,
                                               'M270': 90,  # ver 25.04

                                               'R0ML': 0,
                                               'R90ML': 90,
                                               'R180ML': 0,
                                               'R270ML': 90,

                                               'M0ML': 0,
                                               'M90ML': 90,
                                               'M180ML': 0,
                                               'M270ML': 90
                                               },

                                     'Top': {'R0': 0,
                                             'R90': 90,  # ver 25.04
                                             'R180': 0,
                                             'R270': 90,

                                             'M0': 0,
                                             'M90': 90,  # ver 25.04
                                             'M180': 0,
                                             'M270': 90,

                                             'R0ML': 0,
                                             'R90ML': 0,
                                             'R180ML': 0,
                                             'R270ML': 0,

                                             'M0ML': 0,
                                             'M90ML': 0,
                                             'M180ML': 0,
                                             'M270ML': 0
                                             },

                                     'Bottom': {'R0': 0,
                                                'R90': 90,
                                                'R180': 0,
                                                'R270': 90,

                                                'M0': 0,
                                                'M90': 90,  # ver 25.04
                                                'M180': 0,
                                                'M270': 90,  # ver 25.04

                                                'R0ML': 0,
                                                'R90ML': 90,
                                                'R180ML': 0,
                                                'R270ML': 90,

                                                'M0ML': 0,
                                                'M90ML': 90,
                                                'M180ML': 0,
                                                'M270ML': 90
                                                },

                                     'VLeft': {'R0': 90,
                                               'R90': 0,
                                               'R180': 0,
                                               'R270': 0,

                                               'M0': 0,
                                               'M90': 0,
                                               'M180': 0,
                                               'M270': 0,

                                               'R0ML': 90,
                                               'R90ML': 0,
                                               'R180ML': 0,
                                               'R270ML': 0,

                                               'M0ML': 0,
                                               'M90ML': 0,
                                               'M180ML': 0,
                                               'M270ML': 0
                                               },

                                     'VCenter': {'R0': 90,
                                                 'R90': 0,
                                                 'R180': 0,
                                                 'R270': 0,

                                                 'M0': 0,
                                                 'M90': 0,
                                                 'M180': 0,
                                                 'M270': 0,

                                                 'R0ML': 90,
                                                 'R90ML': 0,
                                                 'R180ML': 0,
                                                 'R270ML': 0,

                                                 'M0ML': 0,
                                                 'M90ML': 0,
                                                 'M180ML': 0,
                                                 'M270ML': 0
                                                 },

                                     'VRight': {'R0': 90,
                                                'R90': 0,
                                                'R180': 90,
                                                'R270': 0,

                                                'M0': 90,
                                                'M90': 0,
                                                'M180': 90,
                                                'M270': 0,

                                                'R0ML': 90,
                                                'R90ML': 0,
                                                'R180ML': 0,
                                                'R270ML': 0,

                                                'M0ML': 90,
                                                'M90ML': 0,
                                                'M180ML': 0,
                                                'M270ML': 0
                                                },

                                     'VTop': {'R0': 90,  # ver 25.04
                                              'R90': 0,
                                              'R180': 90,  # ver 25.04
                                              'R270': 0,

                                              'M0': 90,  # ver 25.04
                                              'M90': 0,
                                              'M180': 90,  # ver 25.04
                                              'M270': 0,

                                              'R0ML': 0,
                                              'R90ML': 0,
                                              'R180ML': 0,
                                              'R270ML': 0,

                                              'M0ML': 0,
                                              'M90ML': 0,
                                              'M180ML': 0,
                                              'M270ML': 0
                                              },

                                     'VBottom': {'R0': 90,  # ver 25.04
                                                 'R90': 0,
                                                 'R180': 90,  # ver 25.04
                                                 'R270': 0,

                                                 'M0': 90,  # ver 25.04
                                                 'M90': 0,
                                                 'M180': 90,  # ver 25.04
                                                 'M270': 0,

                                                 'R0ML': 0,
                                                 'R90ML': 0,
                                                 'R180ML': 0,
                                                 'R270ML': 0,

                                                 'M0ML': 0,
                                                 'M90ML': 0,
                                                 'M180ML': 0,
                                                 'M270ML': 0
                                                 }
                                     }
        }
