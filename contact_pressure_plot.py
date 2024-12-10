import os
import pandas as pd
import plotly.express as px
from PIL import Image

class MechPlotter():
    def __init__(self, name):
        self.name = name
        if name == "ContactPressurePlot":
            files = self.file_check()
            if files is not None:
                ids = self.get_contact_pair_ids(files[0])
                clean_data = self.prep_contact_pressure_df(ids, files[1])
                self.generate_plots(ids, clean_data)
                self.combine_plots()

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
        data = {"contact_id": [], "max_contact_pressure": [], "step": [], "iteration": []}
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
                iteration = int(iteration)
                step += 1

            if "<" not in line:
                entry_data = line.split()
                pair_id = int(entry_data[id_col_num])
                if pair_id in id_array:
                    data["contact_id"].append(pair_id)
                    pressure = float(entry_data[pres_col_num])
                    data["max_contact_pressure"].append(pressure)
                    data["step"].append(step)
                    data["iteration"].append(iteration)
        df = pd.DataFrame(data)
        return df
    
    def filter_by_id(self, df, contact_id):
        filtered_df = df[df["contact_id"] == contact_id].reset_index(drop=True)
        prev_row = None
        indices_to_drop = []
        for idx, row in filtered_df.iterrows():
            if idx > 0:
                if (row["iteration"] != 0) and (prev_row["iteration"] == 0):
                    indices_to_drop.append(idx-1)
            prev_row = row

        filtered_df = filtered_df.drop(indices_to_drop).reset_index(drop=True)
        filtered_df["step"]= filtered_df.index + 1
        return filtered_df
    
    def generate_plots(self, id_array, cleaned_data):
        for id in id_array:
            id_subset = self.filter_by_id(cleaned_data, id)
            fig = px.line(id_subset, x="step", y="max_contact_pressure", color="contact_id")
            fig.update_layout(xaxis_title="Iteration",
                              yaxis_title="Max Contact Pressure",
                              legend={"title": f"Contact ID"},
                              title=f"Pair {id} Contact Pressure Plot")
            fig.write_image(f"pair_{id}_contact_pressure_plot.png")

    def combine_plots(self):
        files = os.listdir(".")
        png_files = [x for x in files if "pair" in x]
        images = [Image.open(path) for path in png_files]
        min_img_width = min(i.width for i in images)
        total_height = 0
        for i, img in enumerate(images):
            if img.width > min_img_width:
                images[i] = img.resize((min_img_width, 
                                        int(img.height/img.width * min_img_width)), 
                                        Image.ANTIALIAS)
            total_height += images[i].height
        img_merge = Image.new(images[0].mode, (min_img_width, total_height))
        y = 0
        for img in images:
            img_merge.paste(img, (0,y))
            y += img.height
        img_merge.save("ContactPressures.png")
        # Delete original images once the merged one has been created
        for file in png_files:
            os.remove(file)
if __name__ == "__main__":
    MechPlotter("ContactPressurePlot")
