# if subfolder (not file) name in A folder and B folder, remove it from B folder
# generate code

import os
import shutil
from natsort import os_sorted


# def check_data(A:str, B:str) -> None:
#     for subfolder in os_sorted(os.listdir(A))[:66]:
#         subfolder += '_merged'
#         if os.path.isdir(os.path.join(B, subfolder)):
#             shutil.rmtree(os.path.join(B, subfolder))

# check_data('input/batch0723','input/batch0813')

def check_data(A:str, B:str) -> None:
    for subfolder in os_sorted(os.listdir(A))[:]:
        subfolder = subfolder.replace('_merged','') 
        if os.path.isdir(os.path.join(B, subfolder)):
            shutil.rmtree(os.path.join(B, subfolder))

check_data('input/batch0813','input/batch0723')