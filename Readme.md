# PyLTSpice_macOS beta v1.0

Are you using an Apple device and are you frustrated that LTSpice is great for running simulations, but the GUI output of it still looks like it's from the last century?  
Are you sad that someone has already written a great toolchain for LTSpice interactions, but only for Windows? (Highly recommended for Windows users though: [PyLTSpice](https://github.com/nunobrum/PyLTSpice))  

Well, weep no more, because this is a Python toolchain for interacting with LTSpice for Apple devices.  

## Installation

Clone this git and either use locally or add to your path.

## Usage
### Features
- Run simulations in LTSpice and read out the results
- Plot the results with the debug function or do it on your own
- Plot the .asc circuit

### Examples
You can find the complete documentation at [readthedocs.io](https://pyltspice-macos.readthedocs.io/en/latest/index.html)  
Refer to the example below or check out the [Example folder](https://github.com/simongapp/PyLTSpice_macOS/tree/main/Examples) 
```python
import PyLTSpice_macOS as LTC
import DebugHelpers as debug

example_circuit = LTC('example_circuit.asc')
# Plot schematic
example_circuit.schematic.plot_schematic()

# Read out data
data_vin = example_circuit.get_trace_data('V(vin)')
data_vout = example_circuit.get_trace_data('V(vout)')
# time is sometimes not read out correctly but this can be fixed by using the absolute value
time = np.abs(example_circuit.get_trace_data('time'))

# Plot schematic and simulation results
debug.show_results(example_circuit, 'vin', 'vout')

# Change component in schematic and rerun simulation
example_circuit.change_component('R1', '1k')
example_circuit.update()
```
## Known issues
The toolchain has been validated on a MacBook Pro with macOS 10.15.7 and LTSpice Build Mar 3 2021 Version:17.0.23.0  
Since this is a beta release there are still a lot of issues. Please refer to the issues of this repository to learn more.
      

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.