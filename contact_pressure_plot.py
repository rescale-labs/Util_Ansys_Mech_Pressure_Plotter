import os
import pandas as pd
import plotly.express as px

class MechPlotter():
    def __init__(self, name):
        self.name = name
        if name == "ContactPressurePlot":
            files = self.file_check()
            if files is not None:
                ids = self.get_contact_pair_ids(files[0])
                clean_data = self.prep_contact_pressure_df(ids, files[1])
                self.generate_plots(ids, clean_data)

    def get_cnd_file(self):
        cnd_file = None
        for filename in os.listdir("."):
            if filename.endswith(".cnd"):
                cnd_file = filename
        return cnd_file

    def get_nlh_file(self):
        nlh_file = None
        for filename in os.listdir("."):
            if filename.endswith(".nlh"):
                nlh_file = filename
        return nlh_file
    
    def file_check(self):
        cnd = self.get_cnd_file()
        nlh = self.get_nlh_file()
        if (cnd or nlh) is None:
            print(f"INFO: No cnd or nlh file found (cnd file: {cnd} nlh file: {nlh}). Has the Mechanical solver started yet?")
            return None
        return (nlh, cnd)
    
    def get_contact_pair_ids(self, file):
        contact_pair_array = []
        with open(file, "r") as f:
            file_lines = f.readlines()
        for line in file_lines:
            try:
                if "CONTACT_PAIR" in line:
                    line_data = line.split()
                    contact_pair_id = int(line_data[line_data.index("CONTACT_PAIR=\"") + 1].strip("\""))
                    contact_pair_array.append(contact_pair_id)
            except (IndexError, ValueError):
                pass
        return contact_pair_array
    
    def prep_contact_pressure_df(self, id_array, file):
        # First, lets check for the nlh file to get the user defined contact pair ids
        with open(file, "r") as f:
            file_lines = f.readlines()
        data = {"contact_id": [], "max_contact_pressure": [], "step": []}
        iteration = 0
        step = 0
        for line in file_lines:
            if "Contact Pair ID" in line:
                id_col_num = int(line.split(">Contact")[0].split()[-1].strip("\""))
                id_col_num -= 1
            if "Max. Contact Pressure" in line:
                pres_col_num = int(line.split(">Max. Contact Pressure")[0].split()[-1].strip("\""))
                pres_col_num -= 1
            if "COLDATA " in line:
                iteration_data = line.split()
                iteration = iteration_data[iteration_data.index("ITERATION=\"") + 1].replace("\"","")
                if int(iteration) != 0:
                    step += 1

            if "<" not in line and int(iteration) != 0:
                entry_data = line.split()
                pair_id = int(entry_data[id_col_num])
                if pair_id in id_array:
                    data["contact_id"].append(pair_id)
                    pressure = float(entry_data[pres_col_num])
                    data["max_contact_pressure"].append(pressure)
                    data["step"].append(step)
        df = pd.DataFrame(data)
        return df

    def generate_plots(self, id_array, cleaned_data):
        for id in id_array:
            id_subset = cleaned_data[cleaned_data["contact_id"] == id]
            fig = px.line(id_subset, x="step", y="max_contact_pressure", color="contact_id")
            fig.update_layout(xaxis_title="Iteration",
                              yaxis_title="Max Contact Pressure",
                              title=f"Pair {id} Contact Pressure Plot")
            fig.write_image(f"pair_{id}_contact_pressure_plot.png")


if __name__ == "__main__":
    MechPlotter("ContactPressurePlot")