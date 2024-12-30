# ANSYS Mechanical Contact Pair Pressure Plots

<img width="748" alt="Screenshot 2024-11-21 at 2 29 45 PM" src="https://github.com/user-attachments/assets/141c3e4d-152d-42cf-bcea-839ec0390fd1">


When running a non-linear ANSYS Mechanical simulation with contact pairs defined. The solver generates a value for the maximum pressure at each step of the simulation. This tool can be used during batch simulations to generate plots of the max pressure per iteration as PNG files, which can then be easily viewed during the course of the simulation to effectively monitor the status of the analysis.

# Working
This script uses the Python libraries pandas, plotly, and kaleido to generate the contact pressure plots during runtime.
1. It reads the file.nlh to determine which contact pair IDs we care about.
2. It reads the file.cnd to extract iteration number and max contact pressure for each contact pair ID then saves it into a pandas dataframe
3. The max contact pressure plots are then generated inside of the working directory.
Users can then search for the "png" extension from the Rescale livetailing menu to review the graphs while the job is running
# Usage
1. Create a template:
For the automated Force-Convergence generation approach, it is advisable to create and save a template with the specified settings. This ensures that the template can be reused without manual command editing for each run.
2. Software Commands:
After selecting the desired ANSYS Mechanical version, prepend the following commands to downlaod the Python file from this Rescale Labs Github Repository and then install and configure the Python virtual environment with the required libraries.
```
	wget https://raw.githubusercontent.com/rescale-labs/Util_Ansys_Mech_Pressure_Plotter/main/contact_pressure_plot.py
	pip3 install --user virtualenv
	python3 -m virtualenv $HOME/ansys
	source $HOME/ansys/bin/activate
	pip install pandas==1.1.5 Pillow==8.4.0 kaleido==0.2.1 plotly==5.18.0
```
Setting up the Python virtual environment typically takes under a minute which minimizes impact on solution time.

At the end of the default ANSYS Mechanical solve command, we will append "&" to background the solver and then repeatedly invoke the contact pressure plotting script every few minutes. We capture the Linux process ID of the ANSYS solver and continue to rerun the plotting script as long as the ANSYS solver is still alive.

```
	export LICENSE_FEATURE=ansys
	#export LICENSE_FEATURE=meba
	#export LICENSE_FEATURE=mech_1
	#export LICENSE_FEATURE=mech_2
	ansys${ANSYSMECH_VERSION/./} -dis -b -mpi $ANS_MPI_VERS -np $RESCALE_CORES_PER_SLOT -machines $MACHINES -i *.dat -p $LICENSE_FEATURE &
	pid=$!
	while ps -p $pid &>/dev/null; do
	python contact_pressure_plot.py
	sleep 300
	done
	deactivate
```
