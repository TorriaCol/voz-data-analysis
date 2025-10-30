### Change mypath to return whatever relative path your data is in. This is the only place you will need to define it.
def raw_2023data_path():
    return r"../reference_files/2023rawdata/"

def raw_2025data_path():
    return r"../reference_files/2025rawdata/"

def local_image_folder(sensor):
    return rf"../../PMCalibrations{sensor}/"
