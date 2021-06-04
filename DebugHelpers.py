#!/usr/bin/env python
# ---------------------------------------------------------------------------------------------------
# Name:        DebugHelpers.py
# Purpose:     Collection of functions that make it easier to debug the three classes of PyLTSpice_macOS separately
#
# Author:      Simon Gapp
#
# Created:     31.05.2018
# Licence:
# ---------------------------------------------------------------------------------------------------
"""Collection of functions that make it easier to debug the three classes of PyLTSpice_macOS separately
"""

import PyLTSpice_macOS as LTC
import numpy as np
import matplotlib.pyplot as plt


def find_nearest(array, max_vals, min_vals):
    """Finds nearest value in an array

    :param array: Array that will be searched
    :type array: list
    :param max_vals: Maximum value to be searched
    :type max_vals: double
    :param min_vals: Minimum value to be searched
    :type min_vals: double
    """
    array = np.asarray(array)
    difference = np.abs(np.array(max_vals) - np.array(np.abs(min_vals)))
    idx = np.abs(difference).argmin()
    # print(idx)
    # return array[idx]
    return idx


def get_raw_asc_data(filename, encoding='utf-16-le'):
    """Reads in a raw asc file. Helpful for debugging the Schematic class

    :param filename: Absolute path to filename
    :type filename: str
    :param encoding: Encoding. Default is ``utf-16-le`` if this fails try ``latin9``
    :type encoding: str, optional
    :return: data
    :rtype: str list
    """
    try:
        fid = open('test/' + filename, 'r', encoding=encoding)
    except FileNotFoundError:
        fid = open(filename, 'r', encoding=encoding)
    data = fid.readlines()
    fid.close()

    return data


def write_asc_file(filename, data):
    """Writes raw data to an asc file.

    :param filename: Name of the file to be written
    :type filename: str
    :param data: Data to be written into the file
    :type data: str list
    :return: void
    """
    fid = open('test/' + filename, 'w', encoding='utf-16-le')
    fid.writelines(data)
    fid.close()


def show_results(ltcobject, voltage_input_name, voltage_output_name,
                 plot_schematic=True, schematic_figure_size=(20, 10),
                 plot_graph=True, graph_figure_size=(20, 10), subplot=False):
    """Quick plot helper for ``.tran`` commands. Based on the assumption that the input and output of the simulation are labeled

    :param ltcobject: LTC object
    :type ltcobject: LTC
    :param voltage_input_name: Name of the input label
    :type voltage_input_name: str
    :param voltage_output_name: Name of the output label
    :type voltage_output_name: str
    :param plot_schematic: Boolean whether the schematic shall be plotted
    :type plot_schematic: Bool, optional
    :param schematic_figure_size: Defines the figuresize of the schematic. Default: ``(20,10)``
    :type schematic_figure_size: Tuple, optional
    :param plot_graph: Boolean whether the graph shall be plotted
    :type plot_graph: Bool, optional
    :param graph_figure_size: Defines the figuresize of the graph. Default: ``(20,10)``
    :type graph_figure_size: Tuple, optional
    :param subplot: Boolean whether the input and output label are plotted in separate graphs or in in graph. Default: False
    :type subplot: Bool, optional
    :return: void
    """
    if plot_schematic:
        ltcobject.schematic.plot_schematic(figsize=schematic_figure_size)
    if ltcobject.simulate_data:
        if plot_graph:
            time = ltcobject.get_trace_data(0)
            v_in_string = 'V(' + str(voltage_input_name) + ')'
            v_in = ltcobject.get_trace_data(v_in_string)
            v_out_string = 'V(' + str(voltage_output_name) + ')'
            v_out = ltcobject.get_trace_data(v_out_string)

            plt.figure(figsize=graph_figure_size)
            if subplot:
                plt.subplot(2, 1, 1)
                plt.plot(np.abs(time), v_in, label='Input')
                plt.legend()
                plt.grid(True, which='both')

                plt.subplot(2, 1, 2)
                plt.plot(np.abs(time), v_out, label='Output')
                plt.legend()
                plt.grid(True, which='both')
            else:
                plt.plot(np.abs(time), v_in, label='Input')
                plt.plot(np.abs(time), v_out, label='Output')
                plt.legend()
                plt.grid(True, which='both')
            plt.show()
