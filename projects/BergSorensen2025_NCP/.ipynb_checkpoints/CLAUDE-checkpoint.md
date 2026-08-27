# BergSorensen2025_NCP — Research Project

## Project overview
The project develops a CGE model with the purpose of studying the economic and welfare consequences of alternative time paths towards net zero CO2 emissions. The model is a multi-sector dynamic CGE model of an open economy with heterogeneity in abatement costs across sectors and firms and installation costs in the adoption of new abatement technologies and investments more broadly.

## Structure
The project is not self-contained in the current repository. The project is one of several that implements CGE models using a combination of Python and GAMS. The main Github repository is `CGE_Generator`:
- `CGE_Generator/py/` - contains the Python implementation of projects.
- `CGE_Generator/work_folder/`- repository for temporary GAMS files created during simulations.
- `CGE_Generator/projects/` - contains all projects.  
- `CGE_Generator/projects/BergSorensen2025_NCP` - current project implementation. 

Structure under current project repo `CGE_Generator/projects/BergSorensen2025_NCP`: 
- Various implementations in ipynb notebooks. Main implementation for instance, goes through `Main_x` with x∈{1,2,3,4}. 
- `data/` - raw and processed data (not results).
- `py/` - python files relevant for the current project only.
- `results` - output tables, figures, and model instances and solution databases.
- `notes` - use this for smaller tasks and working notes. 

The final output from the project is a research paper in Overleaf that can be accessed here: https://da.overleaf.com/project/6847da83a33f87fb1c52de52.   

## Current status
The final model is up and running, and we have a working paper version here: https://www.ifo.de/cesifo/482. We are revising the paper based on various feedback. 

## Key conventions
- Language: Python / GAMS (whichever applies)
- Always commit working changes before major edits
- After each working session, append a short entry to `RESEARCH_LOG.md` summarizing what we did and what's next.
