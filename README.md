# 4221_CTU_Sim
Simple model implemented in Simpy of the clinical trials process. Completed as part of the 2020 Sem1 ENGN4221 Clinical Trials Project.

ClinTrialSim does the heavy lifting, running each of the flow diagram processes using the simpy event simulator. 
OverViewSim works with the actual data provided to us to perform time based simulations and return the total process time.
TimeLoader imports the time data and generates a distribution which describes the event's time characteristics, as described in the following jupyter notebook.
The StatDistExp looks at the statistical distibrution used, originally used for experimenting with the scipy distributions but now is useful for understanding how they are implemented.
