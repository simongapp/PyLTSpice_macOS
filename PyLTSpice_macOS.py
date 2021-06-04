#!/usr/bin/env python
# ---------------------------------------------------------------------------------------------------
# Name:        PyLTSpice_macOS.py
# Purpose:     Implementation of a toolchain for controlling LTSpice on Apple devices in Python
#
# Author:      Simon Gapp
#
# Created:     31.05.2018
# Licence:
# ---------------------------------------------------------------------------------------------------
""" Implementation of a toolchain for controlling LTSpice on Apple devices in Python
"""
import getpass
import os
import re
import numpy as np
import matplotlib.pyplot as plt
from collections import Counter

import filecmp
import shutil
import psutil
import subprocess
import time
#from PyLTSpice.LTSpice_RawRead import RawRead as RawRead
from LTSpice_RawRead import RawRead as RawRead
import DebugHelpers as debug

import DefinesDefault


def check_if_path_exists(path_to_file):
    return os.path.exists(path_to_file)


class LTC:
    """Class to generate the LTSpice object

    :param path_to_asc_file: Absolute or relative path to the ``.asc`` file
    :type path_to_asc_file: str
    :param path_to_ltspice_app: Path to LTSpice.app. Default: ``/Applications/LTSpice.app``
    :type path_to_ltspice_app: str, optional
    :param path_to_ltspice_library: Path to LTSpice library.
        Default: ``/Users/<user name>/Library/Application Support/LTSpice/lib/sym``
    :type path_to_ltspice_library: str, optional
    :param simulate_data: Boolean whether a simulation is required. This can be used to create a single plot of
        the schematic or if a ``.raw`` file already exists. Default: True
    :type simulate_data: Bool, optional
    :param ltspice_run_time: Time before LTSpice is terminated. Useful for longer simulations. Default: 1s
    :type ltspice_run_time: int, optional
    :param verbose: Boolean to determine the verbose output of the LTC object. Default: False
    :type verbose: Bool, optional
    """

    def __init__(self, path_to_asc_file,
                 path_to_ltspice_app=None,
                 path_to_ltspice_library=None,
                 simulate_data=True,
                 ltspice_run_time=None,
                 verbose=False):
        """Constructor method"""

        # Attempt to have C/C++ style defines file
        self.__defs = DefinesDefault.Defines()

        # Configure LTC object
        self.simulate_data = simulate_data
        # If the schematic shall be simulated check if the default LTSpice directory is used or a custom directory
        if self.simulate_data:
            if path_to_ltspice_app:
                self.path_to_ltspice_app = path_to_ltspice_app
                if not check_if_path_exists(self.path_to_ltspice_app):
                    print('Specified location: ' + self.path_to_ltspice_app + ' not found.')
                    print('Trying default location: ' + self.__defs.get_define('LTSPICE_APP_DEFAULT_LOC'))
                    self.path_to_ltspice_app = self.__defs.get_define('LTSPICE_APP_DEFAULT_LOC')
            else:
                print('Using LTSpice App from default location')
                self.path_to_ltspice_app = self.__defs.get_define('LTSPICE_APP_DEFAULT_LOC')
            # Check if path exists
            if not check_if_path_exists(self.path_to_ltspice_app):
                print('Did not find the LTSpice App! Abort.')
                print('Path to LTSpice App: ' + self.path_to_ltspice_app)
                return
        # Check whether to use the default path to the LTSpice library or a custom path
        if path_to_ltspice_library:
            self.path_to_ltspice_library = path_to_ltspice_library
            if not check_if_path_exists(self.path_to_ltspice_library):
                print('Specified location: ' + self.path_to_ltspice_library + ' not found.')
                print('Trying default location: ' + self.__defs.get_define('LTSPICE_LIBRARY_DEFAULT_LOC'))
                self.path_to_ltspice_library = self.__defs.get_define('LTSPICE_LIBRARY_DEFAULT_LOC')
        else:
            print('Using LTSpice Library from default location')
            self.path_to_ltspice_library = self.__defs.get_define('LTSPICE_LIBRARY_DEFAULT_LOC')
        if not check_if_path_exists(self.path_to_ltspice_library):
            print('Did not find the LTSpice Library! Abort.')
            print('Path to LTSpice Library: ' + self.path_to_ltspice_library)
            return

        # Set spice directives
        self.__spiceDirectives = self.__defs.get_define('SPICE_DIRECTIVES')
        self.verbose = verbose

        # Generate absolute path
        tmp_complete_path = os.path.abspath(path_to_asc_file)

        # Check if file exists
        if not check_if_path_exists(tmp_complete_path):
            print('LTC init: File: ' + tmp_complete_path + ' not found. Aborting!')
        else:
            print("Generating object")
            # Define run time for LTSpice in seconds, default: 1s
            if ltspice_run_time:
                try:
                    self.LtSpiceRunTime = int(ltspice_run_time)
                except ValueError:
                    print('Parameter: LtSpiceRunTime is not a number. Setting default value of: ' +
                          str(self.__defs.get_define('LTSPICE_RUN_TIME')))
                    self.LtSpiceRunTime = self.__defs.get_define('LTSPICE_RUN_TIME')
            else:
                self.LtSpiceRunTime = self.__defs.get_define('LTSPICE_RUN_TIME')
            # Store path and filename of .asc file
            self.PathToAscFile = tmp_complete_path
            # Extract path and filename without file ending
            self.__PathOnly, self.__FilenameOnly = os.path.split(self.PathToAscFile)
            self.__FilenameOnly = self.__FilenameOnly[:-4]
            # Create a backup file of the original
            self.__create_backup_file()
            # Read asc file and check for simulation directive
            self.__get_asc_file_content()
            # check for simulation directive
            if self.simulate_data:
                if not (self.__check_for_simulation_directive()):
                    print("Did not find a simulation directive in the form of " + str(self.__spiceDirectives))
                    return
                else:
                    # Check if an instance of LTspice is running, should be terminated before we continue
                    # since running LTspice on an already open file really messes with the encoding of the asc file
                    if self.__check_if_process_running("LTSpice"):
                        print(
                            "Found at least one LTSpice instance running. Please quit the instance before continuning")
                        print("Abort.")
                        return
                    else:
                        print("Running LTSpice to generate simulation files")
                        self.run_ltspice()
            else:
                print('+++')
                print('Simulation disabled.')
                print('If you wish to simulate run the call with \'simulate_data=True\'')
                print('+++')

            if self.verbose:
                print("Creating dictionaries")
            self.__asc_create_component_dicts()
            # Generate schematic object
            self.schematic = Schematic(self.rawData, path_to_symbol_library=self.path_to_ltspice_library)

    def get_trace_data(self, trace_name):
        """ Retrieve simulation data of a trace

        :parameter trace_name: Name of the trace to be retrieved
        :type trace_name: str
        :return: values
        :rtype: list
        """
        # Check if the simulation is enabled
        if self.simulate_data:
            return self.simulationData.get_trace(trace_name).data
        else:
            print('Simulation was disabled.')
            print('Initialize with \'simulate_data=True\' to get simulation results')

    # Method for creating a backup file before heavy editing in the original
    def __create_backup_file(self):
        """Creating a backup file of the original .asc file

        :parameter: None
        :return: void"""
        if os.path.isfile(self.__PathOnly + '/' + self.__FilenameOnly + '.asc_bak'):
            if (not filecmp.cmp(self.__PathOnly + '/' + self.__FilenameOnly + '.asc',
                                self.__PathOnly + '/' + self.__FilenameOnly + '.asc_bak')):
                if self.verbose:
                    print("Updating backup file in: " + self.__PathOnly + self.__FilenameOnly + '.asc_bak')
                shutil.copyfile(self.PathToAscFile, self.__PathOnly + '/' + self.__FilenameOnly + '.asc_bak')
            else:
                if self.verbose:
                    print("Backup file detected. No new backup file created.")
        else:
            if self.verbose:
                print("Creating backup file in: " + self.__PathOnly + self.__FilenameOnly + '.asc_bak')
            shutil.copyfile(self.PathToAscFile, self.__PathOnly + '/' + self.__FilenameOnly + '.asc_bak')

    # Method to read the asc file into a list
    def __get_asc_file_content(self):
        """Reads in the content of the asc file

        :param: None
        :return: void
        """
        try:
            schematic = debug.get_raw_asc_data(self.PathToAscFile)
            print('utf-16-le')
            if len(schematic) == 1:
                print('latin9')
                schematic = debug.get_raw_asc_data(self.PathToAscFile, encoding='ISO-8859-1')
        except UnicodeDecodeError as err:
            try:
                schematic = debug.get_raw_asc_data(self.PathToAscFile, encoding='ISO-8859-1')
                print('latin9')
            except Exception as err:
                print('In :' + str(self.PathToAscFile))
                print(err)

        self.rawData = schematic

    # Helper to check if a process is still running
    def __check_if_process_running(self, processName="LTSpice"):
        """Check if a LTSpice process is running. Running LTSpice and running a new simulation can really mess with the .asc file encoding.

        :param processName: processName which is LTSpice. Default: LTSpice
        :type processName: str, optional
        :return: True if LTSpice runs already, False if no LTSpice process is found
        :rtype: Bool
        """
        # Loop through currently running proesses
        for proc in psutil.process_iter():
            try:
                # Check if process name contains the given name string.
                if processName.lower() in proc.name().lower():
                    # Ignore zombie processes
                    if proc.status() == psutil.STATUS_ZOMBIE:
                        return False
                    else:
                        return True
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        return False

    # Run LTSpice
    def run_ltspice(self):
        """Start LTSpice and run the simulation

        :parameter: None
        :return: void
        """
        if self.simulate_data:
            # Open LTSpice with file and run simulation to generate .raw files
            proc = subprocess.Popen([self.path_to_ltspice_app + '/Contents/MacOS/LTspice',
                                     '-Run',
                                     self.PathToAscFile])
            # Let some time pass in order to generate the .raw file etc.
            time.sleep(self.LtSpiceRunTime)
            # Killing the process prevents the .net file from being deleted
            proc.terminate()
            self.simulationData = RawRead(self.__PathOnly + '/' + self.__FilenameOnly + '.raw')
        else:
            print('Simulation was disabled.')
            print('Initialize with \'simulate_data=True\' to run simulation.')

    # Create dictionaries for value changes etc
    def __asc_create_component_dicts(self):
        """Function to create a dictionary for the single components and the assigned values

        :param: None
        :return: void
        """
        self.__AscComponentNameIdx = {}
        self.__AscComponentRawLine = {}
        self.__AscComponentValue = {}
        counter = 0
        # TODO: Add separate line for simulation directive
        # tmp_sim = line[line.find('!*') + 2:].replace('\\n', '\n')
        # if tmp_sim[0] == ' ':
        #     tmp_sim = tmp_sim[1:]
        # self.simulation_command = tmp_sim
        for line in self.rawData:
            if (idx := line.find(self.__defs.get_define('ASC_COMPONENT_NAME_START'))) >= 0:
                identifier = line[idx + len(self.__defs.get_define('ASC_COMPONENT_NAME_START')) + 1:-1]
                value_idx = self.rawData[counter + 1].find(self.__defs.get_define('ASC_COMPONENT_VALUE_START'))

                value = self.rawData[counter + 1][
                        value_idx + len(self.__defs.get_define('ASC_COMPONENT_VALUE_START')) + 1:-1]

                if len(self.__AscComponentNameIdx) == 0:
                    self.__AscComponentNameIdx[identifier] = counter
                    self.__AscComponentValue[identifier] = value
                    self.__AscComponentRawLine[identifier] = self.rawData[counter + 1]
                else:
                    self.__AscComponentNameIdx.update({identifier: counter})
                    self.__AscComponentValue.update({identifier: value})
                    self.__AscComponentRawLine.update({identifier: self.rawData[counter + 1]})
            counter += 1

        self.get_component_names_and_values()

    def change_component(self, component_name, component_value, parameter=None):
        """Call to change the value of a component

        :parameter component_name: Name of the component that is changed
        :type component_name: str
        :parameter component_value: New value of the component
        :type component_value: str
        :parameter parameter: If component is a multi value component, specify what will be changed. E.g. amplitude of a sinus. Default: None
        :type parameter: str, optional"""
        component_value_str = str(component_value)
        # Get old value
        self.__component_old_val = self.__AscComponentValue[component_name]
        for source_type in self.__defs.get_define('SOURCE_TYPES'):
            if self.__component_old_val.upper().find(source_type) >= 0:
                self.__change_sinusoidal_source(component_name, component_value, parameter)
            # TODO: Cover other formats
            else:
                # Update new value
                self.__AscComponentValue[component_name] = component_value_str
                # Update raw line
                self.__AscComponentRawLine[component_name] = self.__AscComponentRawLine[component_name].replace(
                    self.__component_old_val, component_value_str)

    def __change_sinusoidal_source(self, component_name, component_value, parameter):
        # TODO: Add support for all parameters of a voltage source (AC etc)
        """Function to change the DC parameters

        :param component_name: Name of the component to be changed
        :type component_name: str
        :param component_value: Value to be changed
        :type component_value: str
        :param parameter: The parameter to be changed. Currently supported: 'DC_Offset', 'Amplitude', 'Frequency',
            'Delay', 'Dampfing_factor', 'Phase',  'Cycles'
        :type parameter: str
        """
        # Split into single fields
        # tmp_vals = [s for s in re.findall(r'\b\d+\b', self.__component_old_val)]
        tmp_vals = self.__component_old_val[len('SINE') + 1:-1].split(' ')
        # Sanity check
        if len(tmp_vals) > len(self.__defs.get_define('SOURCE_PARAMETERS_SINE').keys()):
            print('SINE source: More parameters detected than available.')
            return
        # Assign new value to respecitve parameter
        else:
            tmp_vals[self.__defs.get_define('SOURCE_PARAMETERS_SINE')[parameter]] = component_value
            # Generate value string
            value_string = str(tmp_vals[0])
            for i in range(1, len(tmp_vals)):
                value_string = value_string + ' ' + str(tmp_vals[i])
            component_value_str = 'SINE(' + value_string + ')'
        # Update new value
        self.__AscComponentValue[component_name] = component_value_str
        # Update raw line
        self.__AscComponentRawLine[component_name] = self.__AscComponentRawLine[component_name].replace(
            self.__component_old_val, component_value_str)

    # Write asc file
    def update(self):
        """Update the schematic an run the LTSpice simulation with new values again.

        :parameter: None
        :return: Void
        """
        # Update the value lines in a temporary file
        old_asc_file = self.rawData
        new_asc_file = old_asc_file
        for key in self.__AscComponentRawLine.keys():
            new_asc_file[self.__AscComponentNameIdx[key] + 1] = self.__AscComponentRawLine[key]
        # Copy temporary file into actual file
        self.rawData = new_asc_file
        # Write into .asc file
        f = open(self.PathToAscFile, "w", encoding='utf-16-le')
        f.writelines(self.rawData)
        f.close()
        self.schematic = Schematic(self.rawData, self.path_to_ltspice_library)
        self.run_ltspice()

    def get_component_names_and_values(self, verbose=False):
        """Get component names and values in the schematic.

        :parameter verbose: verbose output. Default: False
        :type verbose: Bool
        :return: void
        """
        if self.verbose or verbose:
            print("Components in this schematic:")
            for component in sorted(self.__AscComponentValue):
                print(component + ": " + self.__AscComponentValue[component])

    # Method to check for simulation directives
    def __check_for_simulation_directive(self):
        """Checks the ``.asc`` file for a simulation directive. Without a directive no simulation can be performed.

        :parameter: None
        :return: True if directive is found, False if no directive is found.
        :rtype: Bool
        """
        # Loop from the last line, since the directive is usually at the end
        for line in self.rawData[::-1]:
            if line.find('TEXT') >= 0:
                if line.find('!') >= 0:
                    if any(simulation_command in line for simulation_command in self.__spiceDirectives):
                        return True
        return False


class Schematic:
    """Class to generate the Schematic object

    :param raw_data: Raw data of the ``.asc`` file
    :type raw_data: str list
    :param path_to_symbol_library: Path to symbol library, Default: ``/Users/<user name>/Library/Application Support/
        LTSpice/lib/sym``
    :type path_to_symbol_library: str, optional
    :param defines: Defines object, Default: ``DefinesDefault.Defines()``
    :type defines: Defines, optional
    :param verbose: Boolean for verbose output, Default: False
    :type verbose: Bool, optional
    """

    def __init__(self, raw_data, path_to_symbol_library=None, defines=None, verbose=False):
        """Constructor method"""
        # Check if raw_data is not None
        if raw_data:
            if path_to_symbol_library:
                self.path_to_symbol_library = path_to_symbol_library
            self.plot_data = {}
            tmp_schematic = [w.replace('\n', '') for w in raw_data]
            self.raw_schematic = tmp_schematic

            # Attempt to have C/C++ style defines file
            if defines:
                self.__defs = defines
            else:
                self.__defs = DefinesDefault.Defines()

            tmp_scaling = self.raw_schematic[1].split(' ')
            factor_1 = int(tmp_scaling[-2])
            factor_2 = int(tmp_scaling[-1])
            if factor_1 > factor_2:
                self.text_scaling = factor_2 / factor_1
            elif factor_1 < factor_2:
                self.text_scaling = factor_1 / factor_2
            else:
                self.text_scaling = 1

            self.verbose = verbose

            self.__create_plot_data()
            self.__find_junctions()
        else:
            print('Raw data appears to be empty. Aborting.')

    def __find_junctions(self):
        # TODO: Add support for symbol connections directly to a wire
        """Function to find all junctions on the schematic level

        :parameter: None
        :return: void
        """
        if 'WIRE' in self.plot_data:
            x = []
            y = []
            for elem in self.plot_data['WIRE']:
                x.extend(elem[::2])
                y.extend(elem[1::2])

            x_indices = {}

            self.__junction_coord = []

            for elem in x:
                tmp = [i for i, x in enumerate(x) if x == elem]
                if len(tmp) >= 3:
                    x_indices[elem] = tmp

            keys = x_indices.keys()

            for key in keys:
                selected_elements = [y[index] for index in x_indices[key]]
                tmp_occurences = Counter(selected_elements)
                tmp_keys = tmp_occurences.keys()
                for tmp_key in tmp_keys:
                    if (tmp_occurences[tmp_key] >= 3):
                        self.__junction_coord.append([key, tmp_key])
        else:
            self.__junction_coord = []

    def __find_attributes(self, idx, no_of_lines_after_idx=6):
        """Function to find all attributes of a component

        :param idx: Index where to start searching in the ``.asc`` file
        :type idx: int
        :param no_of_lines_after_idx: Maximum number of lines to search after the idx. Default: 6
        :type no_of_lines_after_idx: int, optional

        :Returns:
            - **name** (str) -  name of the component
            - **value** (str) - value of the component
            - **value2** (str) - value2 of the component
            - **spice_line** (str) - spice line of the component
        """
        counter = 0
        name = ''
        value = ''
        value2 = ''
        spice_line = ''

        found_name = False
        found_value = False
        found_value2 = False
        found_spice_line = False
        if self.verbose:
            print('+++++++++')

        for line in self.raw_schematic[idx + 1:]:
            if self.verbose:
                print(line)
            if line.split(' ')[0] == 'SYMBOL':
                break
            elif (counter >= no_of_lines_after_idx) or \
                    (found_name and found_value and found_value2 and found_spice_line):
                if self.verbose:
                    print('#############')
                    print('No of lines after idx: ' + str(no_of_lines_after_idx))
                    print('Counter: ' + str(counter))
                    print('Counter if: ' + str(counter >= no_of_lines_after_idx))
                    print('Found all: ' + str(found_name and found_value and found_value2 and found_spice_line))
                    print('Name: ' + str(name))
                    print('Value: ' + str(value))
                    print('Value2: ' + str(value2))
                    print('Spice Line: ' + str(spice_line))
                return name, value, value2, spice_line
            elif line.find('SYMATTR') >= 0:
                if (line.find('InstName') >= 0) and (not found_name):
                    name = self.__extract_attributes(line)
                    found_name = True
                elif (line.find('Value2') >= 0) and (not found_value2):
                    value2 = self.__extract_attributes(line)
                    found_value2 = True
                elif (line.find('Value') >= 0) and (not found_value):
                    value = self.__extract_attributes(line)
                    found_value = True
                elif (line.find('SpiceLine') >= 0) and (not found_spice_line):
                    spice_line = self.__extract_attributes(line)
                    found_spice_line = True

            counter += 1
        return name, value, value2, spice_line

    def __extract_attributes(self, line):
        """ Function to extract attributes

        :param line: Line to extract the attribute from
        :type line: str
        :return: list of strings
        :rtype: str list
        """
        return ' '.join(line.split(' ')[2:]).replace('\"', '')

    def __create_plot_data(self):
        """Function to create the plot data

        :parameter: None
        :return: void
        """
        for i in range(2, len(self.raw_schematic)):
            tmp_line = self.raw_schematic[i].split(' ')

            # TODO: Separate function for line and line styles
            if tmp_line[0] == 'WIRE' or tmp_line[0] == 'LINE':
                identifier = tmp_line[0]
                if identifier == 'WIRE':
                    position = [int(x) for x in tmp_line[1:]]
                else:
                    position = [int(x) for x in tmp_line[2:-1]]
                    # TODO: LoopGain.asc requires different Line positions
                    if len(position) < 4:
                        position = [int(x) for x in tmp_line[2:]]

                self.__write_to_PlotData_dict(key=identifier, value=position)

            elif tmp_line[0] == 'FLAG':
                identifier = tmp_line[0]
                position = [int(x) for x in tmp_line[1:3]]
                position.append(' '.join(tmp_line[3:]))

                self.__write_to_PlotData_dict(key=identifier, value=position)

            elif tmp_line[0] == 'SYMBOL':
                tmp_window = []
                # A maximum number of 4 windows will be declared after symbol
                for j in range(4):
                    try:
                        tmp_preview_line = self.raw_schematic[i + 1 + j]
                        # New symbol will start with SYMBOL break the loop then
                        if tmp_preview_line.split(' ')[0] == 'SYMBOL':
                            break
                        elif tmp_preview_line.split(' ')[0] == 'WINDOW':
                            tmp_window.append(tmp_preview_line)
                            # print('Found: ' + str(tmp_preview_line))
                    except IndexError:
                        pass
                # print('tmp_window: ' + str(tmp_window))
                identifier = tmp_line[1]
                position = [int(x) for x in tmp_line[2:4]]
                rotation = tmp_line[4]
                if len(tmp_window) > 0:
                    name, value, value2, spice_line = self.__find_attributes(idx=i + len(tmp_window))
                else:
                    name, value, value2, spice_line = self.__find_attributes(idx=i)
                # print('+++++')
                # print('Identifier: ' + str(identifier))
                # print('Name: ' + str(name))
                # print('Value: ' + str(value))
                # print('Value2: ' + str(value2))
                # print('Spice line: ' + str(spice_line))
                # print('Window: ' + str(tmp_window))

                if name == '':
                    name = 'tbd'
                if value == '':
                    value = ''

                tmp_symbol = Symbol(symbol_model=identifier, symbol_name=name, symbol_value=value, symbol_value2=value2,
                                    symbol_spice_line=spice_line,
                                    symbol_position=position, symbol_rotation=rotation,
                                    window=tmp_window,
                                    text_scaling_factor=self.text_scaling,
                                    path_to_symbol_library=self.path_to_symbol_library,
                                    defines=self.__defs,
                                    verbose=self.verbose)

                self.__write_to_PlotData_dict(name, tmp_symbol)

            elif tmp_line[0] == 'TEXT':
                # print(tmp_line)
                identifier = tmp_line[0]
                position = [int(x) for x in tmp_line[1:3]]
                position.append(tmp_line[3])
                position.append(int(tmp_line[4]))
                position.append(' '.join(tmp_line[5:])[1:])

                self.__write_to_PlotData_dict(key=identifier, value=position)

    def __write_to_PlotData_dict(self, key, value):
        """Function to write the plot data to the ``plot_data`` dict

        :param key: Key of the value
        :type key: str
        :param value: Value of the key
        :type value: str
        """
        try:
            self.plot_data[key].append(value)
        except:
            self.plot_data[key] = [value]

    def __read_schematic(self):
        """ Function to read the schematic in

        :parameter: None
        :return: void
        """
        fid = open(self.path_to_file, 'r', encoding='utf-16-le')
        tmp_schematic = fid.readlines()
        fid.close()
        tmp_schematic = [w.replace('\n', '') for w in tmp_schematic]
        self.raw_schematic = tmp_schematic

    def __plot_gnd(self, x_pos, y_pos):
        """ Function to plot the GND symbol

        :param x_pos: x position of the GND symbol
        :type x_pos: int
        :param y_pos: y position of the GND symbol
        :type y_pos: int
        """
        horizontal_line_length = 24
        vertical_line_length = 16
        lines = [[x_pos - horizontal_line_length / 2, y_pos, x_pos + horizontal_line_length / 2, y_pos],
                 [x_pos, y_pos + vertical_line_length, x_pos - horizontal_line_length / 2, y_pos],
                 [x_pos, y_pos + vertical_line_length, x_pos + horizontal_line_length / 2, y_pos]]

        for line in lines:
            plt.plot(line[::2], line[1::2], color='tab:blue')

    def plot_schematic(self, figsize=None, verbose=False):
        """ Function to plot the entire schematic

        :param figsize: figsize, default: None
        :type figsize: tuple, optional
        :param verbose: verbose for plotting
        :type verbose: Bool
        """
        keys = self.plot_data.keys()

        if figsize:
            plt.figure(figsize=figsize)
        else:
            plt.figure(figsize=self.__defs.get_define('DEFAULT_FIG_SIZE'))
        for key in keys:
            for elem in self.plot_data[key]:
                # print(elem)
                try:
                    elem.plot_symbol(verbose=verbose)
                except AttributeError:
                    if key == 'WIRE' or key == 'LINE':
                        if key == 'WIRE':
                            plt.plot(elem[::2], elem[1::2], color='tab:blue')
                        else:
                            plt.plot(elem[::2], elem[1::2], '--', color='tab:blue')
                    elif key == 'FLAG':
                        if elem[2] == '0':
                            self.__plot_gnd(x_pos=elem[0], y_pos=elem[1])
                        else:
                            plot_text(x_y_coordinates=[elem[0], elem[1] - 5], label=elem[2],
                                      text_alignment='Center',
                                      font_size=2,
                                      symbol_rotation='R0',
                                      text_scaling_factor=self.text_scaling,
                                      defines=self.__defs,
                                      verbose=verbose)

                    elif key == 'TEXT':
                        # print(elem)
                        # Drawing the dots draws the plot frame around the entire plot
                        # Otherwise far out text elements would be outside the frame
                        plt.plot(elem[0], elem[1], color='w')
                        # Plot the actual text
                        try:
                            if elem[2].lower() == 'top' or elem[2].lower() == 'bottom':
                                plot_text(x_y_coordinates=[elem[0], elem[1]], label=elem[4].replace('\\n', '\n'),
                                          text_alignment=elem[2],
                                          font_size=elem[3],
                                          symbol_rotation='R0',
                                          text_scaling_factor=self.text_scaling,
                                          defines=self.__defs,
                                          verbose=verbose)
                            else:
                                # TODO: Finish this
                                plot_text(x_y_coordinates=[elem[0], elem[1]], label=elem[4].replace('\\n', '\n'),
                                          text_alignment=elem[2],
                                          font_size=elem[3],
                                          symbol_rotation='R0',
                                          text_scaling_factor=self.text_scaling,
                                          defines=self.__defs,
                                          verbose=verbose)
                        # TODO: Add some kind of error log for easier debug
                        except AttributeError:
                            pass
                        except ValueError:
                            pass

        if len(self.__junction_coord) > 0:
            for elem in self.__junction_coord:
                plt.plot(elem[0], elem[1], 'o',
                         markersize=self.__defs.get_define('DEFAULT_JUNCTION_SIZE') * self.text_scaling,
                         color='tab:blue')

        plt.gca().invert_yaxis()
        plt.axis('equal')
        plt.tick_params(left=False,
                        labelleft=False,
                        bottom=False,
                        labelbottom=False)

    def set_define(self, key, value):
        """Wrapper for :meth:`DefinesDefault.Defines.set_define`"""
        self.__defs.set_define(key=key, value=value)

    def set_font_size(self, value):
        """Function to adapt the fontsize manually

        :param value: Value to set the fontsize to
        :type value: int or float
        :return: void
        """
        self.__defs.set_define(key='DEFAULT_FONT_SIZE', value=value)

    def set_junction_size(self, value):
        """Function to adapt the junction size manually

        :param value: Value to set the junction size to
        :type value: int or float"""
        self.__defs.set_define(key='DEFAULT_JUNCTION_SIZE', value=value)


def plot_text(x_y_coordinates, label, text_alignment, font_size, symbol_rotation, text_scaling_factor, defines,
              verbose=False):
    """Function to plot the labels of a component

    :param x_y_coordinates: x and y coordinate of the label
    :type x_y_coordinates: list
    :param label: label of the component
    :type label: str
    :param text_alignment: Alignment of the text
    :type text_alignment: str
    :param font_size: Font size of the label
    :type font_size: int
    :param symbol_rotation: Rotation of the symbol
    :type symbol_rotation: str
    :param text_scaling_factor: Scaling factor of the text
    :type text_scaling_factor: float
    :param defines: Defines object
    :type defines: Defines"""
    if verbose:
        try:
            print('*******************')
            print('plot_text(): label: ' + str(label))
            print('plot_text(): X: ' + str(x_y_coordinates[0]))
            print('plot_text(): Y: ' + str(x_y_coordinates[1]))
            print('plot_text(): text alignment: ' + str(text_alignment))
            print('plot_text(): symbol rotation: ' + str(symbol_rotation))
            print('plot_text(): HA: ' + str(
                defines.get_define('TEXT_HORIZONTAL_ALIGNMENTS')[text_alignment][symbol_rotation]))
            print('plot_text(): VA: ' + str(
                defines.get_define('TEXT_VERTICAL_ALIGNMENTS')[text_alignment][symbol_rotation]))
            print(
                'plot_text(): ROT: ' + str(
                    defines.get_define('TEXT_ROTATION_ANGLES')[text_alignment][symbol_rotation]))
            print('plot_text(): FONTSIZE: ' + str(
                defines.get_define('DEFAULT_FONT_SIZE') * defines.get_define('LTSPICE_FONTSIZES')[font_size] *
                text_scaling_factor))

            plt.plot(x_y_coordinates[0], x_y_coordinates[1], '*', markersize=4)
        except Exception as excp:
            print(excp)
    # Check if the label contains more than one line
    # Multi Lines have different requirements
    if label.count('\n') > 0:
        symbol_rotation = symbol_rotation + 'ML'
    if label[0] == '_':
        string = '$\overline{' + label[1:] + '}$'
        plt.text(x_y_coordinates[0], x_y_coordinates[1], string,
                 horizontalalignment=defines.get_define('TEXT_HORIZONTAL_ALIGNMENTS')[text_alignment][
                     symbol_rotation],
                 verticalalignment=defines.get_define('TEXT_VERTICAL_ALIGNMENTS')[text_alignment][symbol_rotation],
                 rotation=defines.get_define('TEXT_ROTATION_ANGLES')[text_alignment][symbol_rotation],
                 fontsize=defines.get_define('DEFAULT_FONT_SIZE') * defines.get_define('LTSPICE_FONTSIZES')[
                     font_size] *
                          text_scaling_factor)
    else:
        plt.text(x_y_coordinates[0], x_y_coordinates[1], label,
                 horizontalalignment=defines.get_define('TEXT_HORIZONTAL_ALIGNMENTS')[text_alignment][
                     symbol_rotation],
                 verticalalignment=defines.get_define('TEXT_VERTICAL_ALIGNMENTS')[text_alignment][symbol_rotation],
                 rotation=defines.get_define('TEXT_ROTATION_ANGLES')[text_alignment][symbol_rotation],
                 fontsize=defines.get_define('DEFAULT_FONT_SIZE') * defines.get_define('LTSPICE_FONTSIZES')[
                     font_size] *
                          text_scaling_factor)


class Symbol:
    """Class to generate the Symbol objects

    :param symbol_model: Name of the ``.asy`` file
    :type symbol_model: str
    :param symbol_name: Name of the symbol aka component
    :type symbol_name: str
    :param symbol_value: Value of the symbol
    :type symbol_value: str
    :param symbol_position: x- and y-coordinates of the absolute position of the symbol
    :type symbol_position: int list
    :param symbol_rotation: Rotation of the symbol
    :type symbol_rotation: str
    :param symbol_value2: Value of the second value field
    :type symbol_value2: str
    :param symbol_spice_line: Spice line of the symbol
    :type symbol_spice_line: str
    :param defines: Defines object, Default: None
    :type defines: Defines, optional
    :param window: Sets the window position of the value fields, default: None
    :type window: int list, optional
    :param text_scaling_factor: Text scaling factor, default: 1
    :type text_scaling_factor: float, optional
    :param verbose: Verbose output
    :type verbose: Bool
    :param path_to_symbol_library: Path to symbol library, default: None
    :type path_to_symbol_library: Bool, optional
    """
    def __init__(self, symbol_model, symbol_name, symbol_value, symbol_position, symbol_rotation,
                 symbol_value2=None, symbol_spice_line=None, defines=None, window=None, text_scaling_factor=1,
                 verbose=False, path_to_symbol_library=None):

        # Store path to symbol library which is either default or can be customized
        if path_to_symbol_library:
            self.path_to_symbol_library = path_to_symbol_library
        else:
            self.path_to_symbol_library = self.__defs.get_define('LTSPICE_LIBRARY_DEFAULT_LOC')

        # Create path to symbol and check if it exists
        self.path_to_symbol = self.__find_file(symbol_model + '.asy')
        if not os.path.isfile(self.path_to_symbol):
            print('File: ' + str(self.path_to_symbol) + ' not found! Abort.')
            self.path_to_symbol = None
            return
        else:
            # Store symbol properties
            self.verbose = verbose
            self.symbol_model = symbol_model
            self.symbol_labels = {0: symbol_name,
                                  3: symbol_value,
                                  123: symbol_value2,
                                  39: symbol_spice_line}
            self.symbol_position = symbol_position
            self.symbol_rotation = symbol_rotation
            self.text_scaling_factor = text_scaling_factor
            if defines:
                self.__defs = defines
            else:
                self.__defs = DefinesDefault.defines()

            self.window = None
            if window:
                self.window = window

            # Store symbol
            self.raw_symbol = None
            self.__read_symbol()
            # Get symbol type
            self.symbol_type = None
            self.__get_symbol_type()

            # Generate plot data.
            # Data needs to be handled according to type
            self.plot_data = {}
            self.plot_texts = {}
            self.create_plot_data()

    def __find_file(self, filename):
        """ Function to retrieve the corrct ``.asy`` file

        :param filename: Name of the ``.asy`` file
        :type filename: str
        :return: void"""
        filename_internal = filename.replace('\\\\', '/')
        if (idx := filename_internal.rfind('/')) > 0:
            raw_file = '/' + filename_internal[idx + 1:]
        else:
            raw_file = '/' + filename_internal
        for root, dirnames, filenames in os.walk(self.path_to_symbol_library):
            for file in filenames:
                tmp_path = os.path.join(root, file.lower())
                if raw_file.lower() in tmp_path:
                    return os.path.join(root, file)

        print('find_file(): File: ' + filename_internal + ' not found! Abort.')

    def __coordinate_mapper(self, tmp_coordinates):
        """ Function to map the relative symbol coordinates to the absolute position coordinates

        :param tmp_coordinates: List of x- and y- coordinates
        :type tmp_coordinates: int list
        :returns:
            - **x_coordinates** (int) - x coordinate of the input
            - **y_coordinates** (int) -  y coordinate of the input
         """
        # Non mirrored x and y values
        if self.symbol_rotation == 'R0':
            x_coordinates = np.array(tmp_coordinates[::2]) + self.symbol_position[0]
            y_coordinates = np.array(tmp_coordinates[1::2]) + self.symbol_position[1]
        elif self.symbol_rotation == 'R90':
            x_coordinates = -np.array(tmp_coordinates[1::2]) + self.symbol_position[0]
            y_coordinates = np.array(tmp_coordinates[::2]) + self.symbol_position[1]
        elif self.symbol_rotation == 'R180':
            x_coordinates = -np.array(tmp_coordinates[::2]) + self.symbol_position[0]
            y_coordinates = -np.array(tmp_coordinates[1::2]) + self.symbol_position[1]
        elif self.symbol_rotation == 'R270':
            x_coordinates = np.array(tmp_coordinates[1::2]) + self.symbol_position[0]
            y_coordinates = -np.array(tmp_coordinates[::2]) + self.symbol_position[1]

        # Mirrored x and y values
        elif self.symbol_rotation == 'M0':
            x_coordinates = -np.array(tmp_coordinates[::2]) + self.symbol_position[0]
            y_coordinates = np.array(tmp_coordinates[1::2]) + self.symbol_position[1]
        elif self.symbol_rotation == 'M270':
            x_coordinates = -np.array(tmp_coordinates[1::2]) + self.symbol_position[0]
            y_coordinates = -np.array(tmp_coordinates[::2]) + self.symbol_position[1]
        elif self.symbol_rotation == 'M180':
            x_coordinates = np.array(tmp_coordinates[::2]) + self.symbol_position[0]
            y_coordinates = -np.array(tmp_coordinates[1::2]) + self.symbol_position[1]
        elif self.symbol_rotation == 'M90':
            x_coordinates = np.array(tmp_coordinates[1::2]) + self.symbol_position[0]
            y_coordinates = np.array(tmp_coordinates[::2]) + self.symbol_position[1]

        # Debug function. Print unrecognized rotation command
        else:
            print('create_plot_data: Rotation ' + self.symbol_rotation + ' not recognized')
            x_coordinates = 0
            y_coordinates = 0

        return x_coordinates, y_coordinates

    def __offset_corrector(self, x_coordinates, y_coordinates, text_alignment, offset):
        # TODO: Make sure all labels are corrected
        """Function to correct the offset of labels

        :param x_coordinates: x coordinate of the label
        :type x_coordinates: int
        :param y_coordinates: y coordinate of the label
        :type y_coordinates: int
        :param text_alignment: Text alignment of the label
        :type text_alignment: str
        :parameter offset: offset of the label
        :type offset: int
        :returns:
            - **x_coordinates** (int) - Corrected x-coordinate
            - **y_coordinates** (int) - Corrected y-coordinate
        """
        if self.symbol_rotation.find('R0') >= 0 or self.symbol_rotation.find('M180') >= 0:
            if text_alignment.upper() == 'RIGHT':
                # print('offset_corrector(): R Right, ' + str(offset))
                x_coordinates -= offset
            elif text_alignment.upper() == 'LEFT':
                # print('offset_corrector(): R Left, ' + str(offset))
                x_coordinates += offset
            elif text_alignment.upper() == 'TOP':
                # print('offset_corrector(): R Top, ' + str(offset))
                y_coordinates += offset
            elif text_alignment.upper() == 'BOTTOM':
                # print('offset_corrector(): R Bottom, ' + str(offset))
                y_coordinates -= offset

            elif text_alignment.upper() == 'VRIGHT':
                # print('offset_corrector(): R VRight, ' + str(offset))
                y_coordinates += offset
            elif text_alignment.upper() == 'VLEFT':
                # print('offset_corrector(): R VLeft, ' + str(offset))
                y_coordinates -= offset

        elif self.symbol_rotation.find('R90') >= 0 or self.symbol_rotation.find('M90') >= 0:
            if text_alignment.upper() == 'RIGHT':
                # print('offset_corrector(): R Right, ' + str(offset))
                y_coordinates -= offset
            elif text_alignment.upper() == 'LEFT':
                # print('offset_corrector(): R Left, ' + str(offset))
                y_coordinates += offset
            elif text_alignment.upper() == 'TOP':
                # print('offset_corrector(): R Top, ' + str(offset))
                x_coordinates += offset
            elif text_alignment.upper() == 'BOTTOM':
                # print('offset_corrector(): R Bottom, ' + str(offset))
                x_coordinates -= offset

            elif text_alignment.upper() == 'VRIGHT':
                # print('offset_corrector(): R VRight, ' + str(offset))
                y_coordinates += offset
            elif text_alignment.upper() == 'VLEFT':
                # print('offset_corrector(): R VLeft, ' + str(offset))
                y_coordinates -= offset

        elif self.symbol_rotation.find('R270') >= 0 or self.symbol_rotation.find('M270') >= 0:
            if text_alignment.upper() == 'RIGHT':
                # print('offset_corrector(): R Right, ' + str(offset))
                y_coordinates += offset
            elif text_alignment.upper() == 'LEFT':
                # print('offset_corrector(): R Left, ' + str(offset))
                y_coordinates -= offset
            elif text_alignment.upper() == 'TOP':
                # print('offset_corrector(): R Top, ' + str(offset))
                x_coordinates -= offset
            elif text_alignment.upper() == 'BOTTOM':
                # print('offset_corrector(): R Bottom, ' + str(offset))
                x_coordinates += offset

            elif text_alignment.upper() == 'VRIGHT':
                # print('offset_corrector(): R VRight, ' + str(offset))
                y_coordinates += offset
            elif text_alignment.upper() == 'VLEFT':
                # print('offset_corrector(): R VLeft, ' + str(offset))
                y_coordinates -= offset

        elif self.symbol_rotation.find('R180') >= 0 or self.symbol_rotation.find('M0') >= 0:
            if text_alignment.upper() == 'RIGHT':
                # print('offset_corrector(): M Right, ' + str(offset))
                x_coordinates += offset
            elif text_alignment.upper() == 'LEFT':
                # print('offset_corrector(): M Left, ' + str(offset))
                x_coordinates -= offset
            elif text_alignment.upper() == 'TOP':
                # print('offset_corrector(): M Top, ' + str(offset))
                y_coordinates -= offset
            elif text_alignment.upper() == 'BOTTOM':
                # print('offset_corrector(): M Bottom, ' + str(offset))
                y_coordinates += offset

            elif text_alignment.upper() == 'VRIGHT':
                # print('offset_corrector(): M VRight, ' + str(offset))
                y_coordinates -= offset
            elif text_alignment.upper() == 'VLEFT':
                # print('offset_corrector(): M VLeft, ' + str(offset))
                y_coordinates += offset

        return x_coordinates, y_coordinates

    def create_plot_data(self):
        """ Function to create the plot data of a symbol

        :parameter: None
        :return: void
        """
        for i in range(2, len(self.raw_symbol)):
            # for line in self.raw_symbol:
            # Extract identifier
            line = self.raw_symbol[i]
            identifier = line.split(' ')[0]

            if line.find('SYMATTR Value2') >= 0:
                tmp = ' '.join(line.split(' ')[2:])
                self.symbol_labels[123] = tmp
            elif self.symbol_labels[3] == '' and self.symbol_labels[123] == '' and line.find('SYMATTR Value') >= 0:
                self.symbol_labels[3] = ' '.join(line.split(' ')[-1:])

            try:
                # Extract coordinates only
                # TODO: Handle other numbers that float around in the lines
                if self.verbose:
                    print('create plot data: ' + line)
                tmp_coordinates = self.__get_coordinates(line)[
                                  :self.__defs.get_define('PLOT_NO_OF_COORDINATES')[identifier]]

                if identifier == 'WINDOW':
                    # print(line)
                    # print(tmp_coordinates)
                    tmp_type = tmp_coordinates[0]
                    tmp_coordinates = tmp_coordinates[1:-1]
                    tmp_split_line = line.split(' ')
                    text_alignment = tmp_split_line[-2]
                    font_size = int(tmp_split_line[-1])

                    x_coordinates, y_coordinates = self.__coordinate_mapper(tmp_coordinates)
                    self.__write_to_plot_data_dict(key=identifier, value=[tmp_type, text_alignment,
                                                                          x_coordinates, y_coordinates, font_size])

                elif identifier == 'TEXT':
                    tmp_split_line = line.split(' ')
                    tmp_label = ' '.join(tmp_split_line[5:])
                    text_alignment = tmp_split_line[3]
                    font_size = int(tmp_split_line[4])

                    x_coordinates, y_coordinates = self.__coordinate_mapper(tmp_coordinates)

                    self.__write_to_plot_data_dict(key=identifier, value=[tmp_label, text_alignment,
                                                                          x_coordinates, y_coordinates, font_size])
                elif identifier == 'PIN' and self.raw_symbol[i + 1].find('PINATTR PinName') >= 0:
                    # print('PIN: ' + str(line))
                    # print(str(self.raw_symbol[i+1]))
                    tmp_split_line = line.split(' ')
                    tmp_label = ' '.join(self.raw_symbol[i + 1].split(' ')[2:])
                    text_alignment = self.__defs.get_define('DEFAULT_ALIGNMENT_MAPPER')[tmp_split_line[3]]
                    font_size = 2

                    x_coordinates, y_coordinates = self.__coordinate_mapper(tmp_coordinates[:2])
                    x_coordinates, y_coordinates = self.__offset_corrector(x_coordinates, y_coordinates,
                                                                           text_alignment, tmp_coordinates[2])

                    self.__write_to_plot_data_dict(key=identifier, value=[tmp_label, text_alignment,
                                                                          x_coordinates, y_coordinates, font_size])
                # Catches pins that don't have a description
                elif identifier == 'PIN' and not self.raw_symbol[i + 1].find('PINATTR PinName') >= 0:
                    pass

                elif identifier == 'LINE':
                    # Line style is only specified if not dashed
                    if len(tmp_coordinates) > 4:
                        tmp_line_style = tmp_coordinates[-1]
                        tmp_coordinates = tmp_coordinates[:-1]
                    else:
                        tmp_line_style = 0

                    x_coordinates, y_coordinates = self.__coordinate_mapper(tmp_coordinates)

                    self.__write_to_plot_data_dict(key=identifier, value=[x_coordinates, y_coordinates, tmp_line_style])

                elif identifier == 'ARC':
                    if len(tmp_coordinates) > 8:
                        tmp_line_style = tmp_coordinates[-1]
                        tmp_coordinates = tmp_coordinates[:-1]
                    else:
                        tmp_line_style = 0

                    x_coordinates, y_coordinates = self.__coordinate_mapper(tmp_coordinates)

                    self.__write_to_plot_data_dict(key=identifier, value=[x_coordinates, y_coordinates, tmp_line_style])
                else:
                    x_coordinates, y_coordinates = self.__coordinate_mapper(tmp_coordinates)
                    self.__write_to_plot_data_dict(key=identifier, value=[x_coordinates, y_coordinates])

            except KeyError:
                pass

        # If window is defined in schematic, overwrite the symbol window
        if self.window:
            identifier = 'WINDOW'
            for line in self.window:
                # print('Update: ' + str(line))

                tmp_coordinates = self.__get_coordinates(line)[
                                  :self.__defs.get_define('PLOT_NO_OF_COORDINATES')[identifier]]
                tmp_type = tmp_coordinates[0]
                tmp_coordinates = tmp_coordinates[1:-1]

                x_coordinates, y_coordinates = self.__coordinate_mapper(tmp_coordinates)

                tmp_split_line = line.split(' ')
                text_alignment = tmp_split_line[-2]
                font_size = int(tmp_split_line[-1])

                self.__write_to_plot_data_dict(key=identifier, update=True, value=[tmp_type, text_alignment,
                                                                                   x_coordinates, y_coordinates,
                                                                                   font_size])

    def __plot_ellipse(self, coordinates, linestyle, verbose=False):
        # TODO: Add linestyle support
        """ Function to plot an ellipse

        :parameter coordinates: x- and y-coordinates of the ellipse
        :type coordinates: int list
        :parameter linestyle: Line style of the ellipse
        :type linestyle: str
        :parameter verbose: Verbose of the ellipse
        :type verbose: Bool
        """
        # This function was only possible with the support of my dear friends ribbley (https://github.com/ribbley),
        # Ramin and David. Thanks a lot guys!

        # First two points define the x and y radius of the ellipse
        points_x = coordinates[0]
        points_y = coordinates[1]

        dx = np.max(points_x) - np.min(points_x)
        dy = np.max(points_y) - np.min(points_y)
        center_x = np.mean(points_x[:2])
        center_y = np.mean(points_y[:2])

        ra = dx / 2
        rb = dy / 2

        if verbose:
            print('+++++++++')
            print('plot_ellipse(): Coordinates: ' + str(points_x) + '; ' + str(points_y))
            print('plot_ellipse(): dx; dy: ' + str(dx) + '; ' + str(dy))
            print('plot_ellipse(): Center: ' + str(center_x) + '; ' + str(center_y))
            print('plot_ellipse(): ra; rb: ' + str(ra) + '; ' + str(rb))

        resolution_per_pi = 1000

        if len(points_x) > 2:
            # Start phase is defined by the third point
            tmp_x = points_x[2] - center_x
            tmp_y = points_y[2] - center_y
            start_phase = np.arctan2(tmp_y, tmp_x)

            # End phase is defined by fourth point
            tmp_x = points_x[3] - center_x
            tmp_y = points_y[3] - center_y
            end_phase = np.arctan2(tmp_y, tmp_x)

            if verbose:
                print('Start phase before correction: ' + str(np.rad2deg(start_phase)) + '(' + str(start_phase) + ')')
                print('End phase before correction: ' + str(np.rad2deg(end_phase)) + '(' + str(end_phase) + ')')

            # Correct plot direction
            if self.symbol_rotation.find('R') >= 0:
                # if both points are in the same half plane, no correction is necessary
                if not (0 > start_phase > end_phase and end_phase < 0):
                    if start_phase < 0:
                        start_phase += 2 * np.pi
                    if end_phase > start_phase:
                        end_phase -= 2 * np.pi
            elif self.symbol_rotation.find('M') >= 0:
                if not (0 < start_phase < end_phase and end_phase > 0):
                    if start_phase > 0:
                        start_phase -= 2 * np.pi
                    if end_phase < start_phase:
                        end_phase += 2 * np.pi

            plot_phase = np.linspace(start_phase, end_phase,
                                     int(resolution_per_pi / (np.abs(end_phase - start_phase))))
        else:
            start_phase = 0
            end_phase = 2 * np.pi
            plot_phase = np.linspace(start_phase, end_phase, 1000)

        if verbose:
            print('Start phase: ' + str(np.rad2deg(start_phase)))
            print('End phase: ' + str(np.rad2deg(end_phase)))

        x = center_x + ra * np.cos(plot_phase)
        y = center_y + rb * np.sin(plot_phase)

        plt.plot(x, y, '-', color='tab:blue')

        if verbose:
            self.__plot_arc_points(coordinates)

    def __plot_arc_points(self, coordinates, print_coord=False):
        """ Debug function to plot the ellipse points

        :param coordinates: x- and y-coordinates
        :type coordinates: int list
        :param print_coord: Boolean whether to add a legend with the coordinates or not
        :type print_coord: Bool, optional
        :return: void
        """
        x = coordinates[0]
        y = coordinates[1]

        # plot points
        counter = 0
        color = ['tab:blue', 'tab:orange', 'tab:green', 'tab:red']
        for x_str, y_str, color in zip(x, y, color):
            plt.plot(x_str, y_str, '*', markersize=10, color=color,
                     label='p' + str(counter + 1) + ': (' + str(x_str) + ',' + str(y_str) + ')')
            if print_coord:
                print('p' + str(counter + 1) + ': (' + str(x_str) + ',' + str(y_str) + ')')
            counter += 1

        # plot lines
        plt.plot(x[:2], y[:2], '--')

        if len(coordinates) > 4:
            x_center = np.mean(x[:2])
            y_center = np.mean(y[:2])
            plt.plot(x_center, y_center, '*', markersize=10, color='tab:purple')

            plt.plot([x_center, x[2]], [y_center, y[2]], ':', label='start phase')
            plt.plot([x_center, x[3]], [y_center, y[3]], ':', label='end phase')

    def __plot_rectangle(self, coordinates):
        """Function to plot a rectangle

        :param coordinates: x- and y-coordinates of the rectangle
        :type coordinates: int list
        :return: void
        """
        lines = [[coordinates[0][0], coordinates[0][0]], [coordinates[1][0], coordinates[1][1]],
                 [coordinates[0][1], coordinates[0][1]], [coordinates[1][0], coordinates[1][1]],
                 [coordinates[0][0], coordinates[0][1]], [coordinates[1][0], coordinates[1][0]],
                 [coordinates[0][0], coordinates[0][1]], [coordinates[1][1], coordinates[1][1]]
                 ]

        for i in range(int(len(lines) / 2)):
            plt.plot(lines[2 * i], lines[2 * i + 1], color='tab:blue')

    def plot_symbol(self, verbose=False):
        """ Function to plot the symbol

        :param verbose: Verbose output of the function
        :type verbose: Bool
        """
        for key in self.__defs.get_define('PLOT_KEYS'):
            try:
                if key == 'LINE':
                    for coordinates in self.plot_data[key]:
                        plt.plot(coordinates[0], coordinates[1],
                                 self.__defs.get_define('DEFAULT_LINE_STYLES')[coordinates[2]], color='tab:blue')
                elif key == 'CIRCLE':
                    for coordinates in self.plot_data[key]:
                        self.__plot_ellipse(coordinates, linestyle='-', verbose=verbose)
                elif key == 'RECTANGLE':
                    for coordinates in self.plot_data[key]:
                        self.__plot_rectangle(coordinates)
                elif key == 'ARC':
                    for coordinates in self.plot_data[key]:
                        try:
                            self.__plot_ellipse(coordinates[:2],
                                                linestyle=self.__defs.get_define('DEFAULT_LINE_STYLES')[
                                                    coordinates[-1]],
                                                verbose=verbose)
                        except ValueError as error:
                            print(err)
                elif key == 'WINDOW':
                    for coordinates in self.plot_data[key]:
                        if self.symbol_labels[coordinates[0]]:
                            label = self.symbol_labels[coordinates[0]]
                            text_alignment = coordinates[1]
                            fontsize = coordinates[-1]

                            plot_text(x_y_coordinates=[coordinates[2], coordinates[3]],
                                      label=label,
                                      text_alignment=text_alignment,
                                      font_size=fontsize,
                                      symbol_rotation=self.symbol_rotation,
                                      text_scaling_factor=self.text_scaling_factor,
                                      defines=self.__defs,
                                      verbose=verbose)
                elif key == 'TEXT' or key == 'PIN':
                    for coordinates in self.plot_data[key]:
                        label = coordinates[0]
                        text_alignment = coordinates[1]
                        fontsize = coordinates[-1]
                        # print('###')
                        # print('plot key: ' + key)
                        # print('label: ' + label)
                        # print('text al: ' + text_alignment)
                        # print('fontsize: ' + str(fontsize))
                        plot_text(x_y_coordinates=[coordinates[2], coordinates[3]],
                                  label=label,
                                  text_alignment=text_alignment,
                                  font_size=fontsize,
                                  symbol_rotation=self.symbol_rotation,
                                  text_scaling_factor=self.text_scaling_factor,
                                  defines=self.__defs,
                                  verbose=verbose)

            except KeyError as err:
                # print("Key error: {0}".format(err))
                pass

    def __get_coordinates(self, line):
        """Function to extract the coordinates

        :param line: Line of the coordinates to be extracted
        :type line: str
        :return: list of coordinates
        :rtype: int list
        """
        try:
            return [int(s) for s in re.findall('-?\d+\.?\d*', line)]
        except ValueError as err:
            if self.verbose:
                print('Error in get_coordinates: ' + line)
                print(err)
            # This should catch some value errors where the value at the end of the line is not used for the coordinates
            return [int(float(s)) for s in re.findall('-?\d+\.?\d*', line)]
            pass

    def __write_to_plot_data_dict(self, key, value, update=False):
        """Function to write the symbol plot data to a dict

        :param key: Key of the value
        :type key: str
        :param value: Value of the key
        :type value: str
        :param update: Boolean whether to update or overwrite a dict. Default: False
        :type update: Bool, optional
        :return: void
        """
        if update:
            # print('*******************')
            # print('Update: ' + str(self.plot_data[key]))
            # print('Length: ' + str(len(self.plot_data[key])))
            # print('New value: ' + str(value))

            updated = False
            # Loops trough existing window descriptions and overwrites them
            for i in range(len(self.plot_data[key])):
                if self.plot_data[key][i][0] == value[0]:
                    self.plot_data[key][i] = value
                    updated = True

            if not updated:
                self.plot_data[key].append(value)
            # print('Updated: ' + str(self.plot_data[key]))
        else:
            try:
                self.plot_data[key].append(value)
            except KeyError:
                self.plot_data[key] = [value]

    def __get_symbol_type(self):
        """ Function to determine the symbol type

        :param: None
        :return: Void
        """
        for line in self.raw_symbol:
            if line.find('SymbolType') >= 0:
                self.symbol_type = '-'.join(line.split(' ')[1:])

    def __read_symbol(self):
        """Function to read the symbol file

        :param: None
        :return: void
        """
        try:
            fid = open(self.path_to_symbol, 'r')
            if self.verbose:
                print('Symbol: ' + self.symbol_model + ' encoding: default')
            tmp_symbol = fid.readlines()
        except:
            fid = open(self.path_to_symbol, 'r', encoding='Latin9')
            if (self.verbose):
                print('Symbol encoding: Latin9')
            tmp_symbol = fid.readlines()
        # replace end of line
        tmp_symbol = [w.replace('\n', '') for w in tmp_symbol]
        # replace empty lines
        tmp_symbol = [string for string in tmp_symbol if string != ""]
        self.raw_symbol = tmp_symbol
