import json
import tqdm
import os
import shutil
from natsort import os_sorted

from prompt_aila import set_act_name
from prompt_aila import generate_compliant_report, generate_compliant_report_rag
from prompt_aila import summery_report, modify_document

set_act_name('TWPDP')

def save_to_file(data:str, output_folder:str , filename:str):
    with open(os.path.join(output_folder, filename), 'w') as f:
        f.write(data)

def generate_report_for_company(path:str, output_base:str='output', rag=False):
    # folder preprocess
    output_dir = os.path.join(output_base, os.path.basename(path))
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir)

    # generate individual report
    docs, compliants, non_compliants, success_request_amount = _generate_report_for_company(path, output_dir, rag)
    print(f'{success_request_amount}/{len(docs)} reports generated')

    # generate all report and summary report
    all_report = {'compliant': compliants, 'non_compliant': non_compliants}
    all_report = json.dumps(all_report)
    save_to_file(all_report, output_dir, 'all_report.json')

    all_doc = '\n'.join(docs)
    summary_report = summery_report(all_doc, all_report)
    if not summary_report:
        print(f'No summary report generated : {path}')
        return
    save_to_file(summary_report, output_dir, 'summary_report.json')
    modify_document_by_report(all_doc, summary_report, path, output_dir)

def _generate_report_for_company(path:str, output_dir:str, rag:bool) -> tuple:
    docs = []
    for file in os_sorted(os.listdir(path)):
        if file.endswith('.txt'):
            with open(os.path.join(path, file), 'r') as f:
                docs.append(f.read())

    compliants = []
    non_compliants = []
    success_request_amount = 0
    for i, doc in enumerate(tqdm.tqdm(docs,desc=f'task {path}')):
        if rag:
            report = generate_compliant_report_rag(doc)
            rag_doc = report['legal_documents']
            report = report['report']

            if rag_doc:
                save_to_file(rag_doc, output_dir, f'rag_{i}.json')
        else:
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
    return (docs, compliants, non_compliants, success_request_amount)

def generate_report_for_companies(input_base:str='input', output_base:str='output', s_index:int=0):
    subfolders = [ f.path for f in os.scandir(input_base) if f.is_dir() ]
    subfolders = os_sorted(subfolders)

    for i, subfolder in enumerate(subfolders[s_index:]):
        print(f'company {i+s_index}: {subfolder}')
        generate_report_for_company(subfolder, output_base)
    
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


if __name__ == '__main__':
    generate_report_for_companies(input_base='data/input/batch0813', output_base='data/output/batch0813_rag_twpdp', s_index=0)
    # generate_report_for_company('data/input/batch0822/fubon_manual',output_base='data/output/batch0822_rag_twpdp', rag=True)
