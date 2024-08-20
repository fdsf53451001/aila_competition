import json
import tqdm
import os
import shutil
from natsort import os_sorted

from prompt_aila import generate_compliant_report, summery_report, modify_document


def save_to_file(data:str, output_folder:str , filename:str):
    with open(os.path.join(output_folder, filename), 'w') as f:
        f.write(data)

def modify_document_by_report(all_doc:str, summary_report:str, task_name:str, output_dir:str) -> None:
    try:
        summary_report_dict = json.loads(summary_report)
        summary_report_non_compliants = summary_report_dict['non_compliant']
        summary_report_non_compliants = json.dumps(summary_report_non_compliants)

    except (json.decoder.JSONDecodeError, KeyError):
        print(f'Error in task summary {task_name}.json')
        return

    modified_document = modify_document(all_doc, summary_report_non_compliants)
    if not modified_document:
        print(f'Error in generate modified document {task_name}')

    save_to_file(modified_document, output_dir, 'modified_document.txt')


def generate_report_for_company(path:str, output_base:str='output'):
    output_dir = os.path.join(output_base, os.path.basename(path))
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir)

    docs = []
    for file in os_sorted(os.listdir(path)):
        if file.endswith('.txt'):
            with open(os.path.join(path, file), 'r') as f:
                docs.append(f.read())

    compliants = []
    non_compliants = []
    success_request_amount = 0
    for i, doc in enumerate(tqdm.tqdm(docs,desc=f'task {path}')):
        report = generate_compliant_report(doc)
        if not report:
            continue

        try:
            report_dict = json.loads(report)
            compliants.extend(report_dict['compliant'])
            non_compliants.extend(report_dict['non_compliant'])

            success_request_amount += 1
            save_to_file(report, output_dir, f'report_{i}.json')

        except (json.decoder.JSONDecodeError, KeyError):
            print(f'Error in task report{i}.json')

    print(f'{success_request_amount}/{len(docs)} reports generated')

    all_report = {'compliant': compliants, 'non_compliant': non_compliants}
    all_report = json.dumps(all_report)
    save_to_file(all_report, output_dir, 'all_report.json')

    all_doc = ''.join(docs)
    summary_report = summery_report(all_doc, all_report)
    if not summary_report:
        print(f'No summary report generated : {path}')
        return
    save_to_file(summary_report, output_dir, 'summary_report.json')

    modify_document_by_report(all_doc, summary_report, path, output_dir)

def generate_report_for_companies(input_base:str='input', output_base:str='output', s_index:int=0):
    subfolders = [ f.path for f in os.scandir(input_base) if f.is_dir() ]
    subfolders = os_sorted(subfolders)

    for i, subfolder in enumerate(subfolders[s_index:]):
        print(f'company {i+s_index}: {subfolder}')
        generate_report_for_company(subfolder, output_base)
    
    
if __name__ == '__main__':
    generate_report_for_companies(input_base='input/batch0723', output_base='output/batch0723', s_index=0)
    # generate_report_for_company('input/zapier_chunks')
