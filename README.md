# Magnetometry-Analysis-App
 
Analysis code for M vs. H and M vs. T data acquired with QuantumDesign MPMS3 SQUID-VSM or Lakeshore VSM. Originally developed at Max Planck Institute for Microstructure Physics, Halle, Germany. Feel free to contribute to the project!

## How to use
All input parameters are documented in the main files. Generally, it is required that one data file corresponds to a single measurement, i.e. one M vs. H loop or one M vs. T scan. For MH loops at different T use the fileSplitter module, as indicated below.

### Module mhFileSplitter.py
Splits MH curves taken at different temperatures saved in a single file into separate files. 

### Module mhmtAnalyzer.py
General analysis module. Main purposes:
- Unit conversion to emu/cm3 and muB/f.u. Requires sample to be specified and corresponding sample parameters stored in sample parameter database (not an actual database, just a .csv file, see below).
- Interpolation of high field data to extract diamagnetic substrate contribtion and substract to get only the film contribution.
- For M vs. H hysteresis loops: Extraction of important parameters (saturation, remanence, coercivity, offset-field) 
- Plotting: Plots and plot data are saved in separate files, so re-plotting with other programs is possible.

### Sample parameter database
Here all information concerning the samples are stored.

In order to calculate the magnetization from the magnetic moment, the volume of the sample is required. For thin films, the code assumes that the volume of the magnetic layer can be 
calculated from the film area * layer thickness. The area can be given in two ways:
- If the sample is rectangular: A = L1*L2, both given in mm (this is important!). 
- If the sample has an irregular shape, you can calculate the area yourself and give it directly in units of mm2. 

The magnetic layer thickness t must be given in nm. 

In this way the magnetization in emu/cm3 can be calculated. Furthermore, to convert it into units of muB/f.u. (Bohr magneton per formular unit), the volume of the unit cell Vuc (nm3/f.u.), the material density rho (g/cm3) and the molar mass M_uc (g/mol) must be given. 

To see how the unit conversion is performed, see file subs/mhUnitConversion.py

For the code to work please consider:
- Not to use commas in any column
- Not change the column headers
- Reference the sample in the code with the exact same ID as given in the .csv file.

Have fun!
