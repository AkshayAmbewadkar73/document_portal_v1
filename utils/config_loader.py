# import yaml

# def load_config(config_path:str="C:\document_portal_v1\config\config.yaml")->dict:
#     with open(config_path,"r") as file:
#         config=yaml.safe_load(file)
#         print(config)

#     return config   

# load_config("C:\document_portal_v1\config\config.yaml") 


import yaml

def load_config(config_path:str="C:\document_portal_v1\config\config.yaml")->dict:
    with open(config_path,"r") as file:
        config=yaml.safe_load(file)
        print(config)
    return config    

load_config("C:\document_portal_v1\config\config.yaml")