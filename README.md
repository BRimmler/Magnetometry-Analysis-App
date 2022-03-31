# Magnetometry-Analysis-App
 
Analysis code for M vs. H and M vs. T data acquired with QuantumDesign MPMS3 SQUID-VSM or Lakeshore VSM. Originally developed by me at MPI Halle. Feel free to contribute to the project or let me know if you need additional modules. 

## How to use
All input parameters are documented in the main files. Generally, it is required that one data file corresponds to a single measurement, i.e. one M vs. H loop or one M vs. T scan. For MH loops at different T use the fileSplitter module, as indicated below.

### Module mhFileSplitter.py
Splits MH curves taken at different temperatures saved in a single file into separate files. 

### mhmtAnalyzer.py
General analysis module. Main purposes:
- Unit conversion to emu/cm3 and muB/f.u. Requires sample to be specified and corresponding sample parameters stored in sample parameter database (not an actual database, just a .csv file, see below).
- Interpolation of high field data to extract diamagnetic substrate contribtion and substract to get only the film contribution.
- For M vs. H hysteresis loops: Extraction of important parameters (saturation, remanence, coercivity, offset-field) 
- Plotting: Plots and plot data are saved in separate files, so re-plotting with other programs is possible.

Have fun!
