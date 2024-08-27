from gemini_api import GeminiAPIRotate
from gpt_api import GPTAPI
from utils.gdpr_chroma import search_gdpr_formatted
from utils.twpdp_chroma import search_twpdp_formatted
## tools

# gemini_r = GeminiAPIRotate()
gpt4o_mini = GPTAPI()
act_name = 'GDPR'

def set_act_name(name:str):
    global act_name
    act_name = name

def chat_llm(prompt: str, mode: str, temp:float=0) -> str:
    # return gemini_r.chat_gemini(prompt, mode, temp)
    return gpt4o_mini.chat_gpt4o_mini(prompt, mode, temp)

def generate_compliant_report(doc:str) -> str:
    # 這份隱私政策，哪些部分符合GDPR？哪些部分不符合GDPR？
    # 請將政策與條文對應，引據條號及法律條文：
    prompt_generate_report = f"""    
    Which parts of this privacy policy comply with {act_name}? Which parts are not {act_name} compliant?
    Please match the policy with the provisions, citing article numbers and legal provisions:
    
    """+"""
    for example json:
    {
        "compliant": [
            {
            "section": "...",
            "article numbers": "...",
            "legal provisions": "..."
            }
        ],
        "non_compliant": [
            {
            "section": "...",
            "article numbers": "...",
            "legal provisions": "...",
            "amend": "..."
            }
        ]
    }
    """
    prompt = doc + prompt_generate_report
    response = chat_llm(prompt, mode='json')
    return response

def generate_compliant_report_rag(doc:str) -> dict:
    '''
    return {"legal_documents":legal_documents, "report":response}
    '''
    # 這份隱私政策，哪些部分符合GDPR？哪些部分不符合GDPR？
    # 請將政策與條文對應，引據條號及法律條文：
    if act_name == 'GDPR':
        legal_documents = search_gdpr_formatted(doc)
    elif act_name == 'TWPDP':
        legal_documents = search_twpdp_formatted(doc)
    else:
        legal_documents = ""

    prompt_generate_report = f"""    
    Which parts of this privacy policy comply with {act_name}? Which parts are not {act_name} compliant?
    Please refer to the following legal provisions:
    {legal_documents}
    
    Please match the policy with the provisions, citing article numbers and legal provisions:
    """+"""
    for example json:
    {
        "compliant": [
            {
            "section": "...",
            "article numbers": "..."
            }
        ],
        "non_compliant": [
            {
            "section": "...",
            "article numbers": "...",
            "amend": "..."
            }
        ]
    }
    """
    prompt = doc + prompt_generate_report
    response = chat_llm(prompt, mode='json')
    return {"legal_documents":legal_documents, "report":response}

def summery_report(docs:str, reports:str) -> str:
    # 請將以下隱私政策進行整合，歸納出符合GDPR的部分及不符合GDPR的部分，並提出建議修正方案：
    prompt = f"""
    Please integrate the following privacy policies, summarize the parts that are compliant with {act_name} and the parts that are not compliant with {act_name}, and provide suggestions for amendments:
    Please remove duplicate and unnecessary parts
    
    privacy policies :
    {docs}
    reports :
    {reports}
    """+"""
    for example json:
    {
        "compliant": [
            {
            "section": "...",
            "legal article numbers": "...",
            "legal provisions": "..."
            }
        ],
        "non_compliant": [
            {
            "section": "...",
            "legal article numbers": "...",
            "legal provisions": "...",
            "amend": "..."
            }
        ]
    }
    """

    response = chat_llm(prompt, mode='json')
    return response

def modify_document(document:str, report:str) -> str:
    # 請根據報告中的建議，修改隱私政策：
    prompt = f"""
    Please make only necessary and minimal changes to the privacy policy document based on the amend in the report:
    report :
    {report}
    document :
    {document}    

    """+"""
    Please reply the modified document. Don't add extra content and descriptions. Don't modify the original format.
    """
    response = chat_llm(prompt, mode='text')
    return response

if __name__ == '__main__':
    doc = """
    1. Introduction
    This privacy policy (the “Policy”) applies to Midjourney, Inc., the Midjourney.com website, and the Midjourney image generation platform (the “Services”) . Midjourney, Inc. (“Midjourney”) is a communications technology incubator that provides image generation services to augment human creativity and foster social connection.

    As used in this Policy, “personal data” means any information that relates to, describes, could be used to identify an individual, directly or indirectly.

    Applicability: This Policy applies to personal data that Midjourney collects, uses, and discloses and which may include: (i) data collected through the Services, (ii) data collected through the process of training Midjourney machine learning algorithms, (iii) data collected through Midjourney websites, and (iv) data collected from third party sources. Third party sources may include, but not be limited to: public databases, commercial data sources, and the public internet. When you make purchases, we use third-party payment processors to collect credit card or other financial information. Midjourney does not store the credit card or payment information you provide, only confirmation that payment was made.

    This Policy does not apply to the following information:

    Personal Data about Midjourney employees and candidates, and certain contractors and agents acting in similar roles.
    Changes: We may update this Policy from time-to-time to reflect changes in legal, regulatory, operational requirements, our practices, and other factors. Please check this Policy periodically for updates. If any of the changes are unacceptable to you, you should cease interacting with us. When required under applicable law, we will notify you of any changes to this Policy.

    Definitions: Through this Policy, You, or Your means the individual accessing or using the Service, or the company, or other legal entity on behalf of which such individual is accessing or using the Service, as applicable. Company (referred to as either "the Company", "We", "Us" or "Our" in this Agreement) refers to Midjourney LLC. Usage Data refers to data collected automatically, either generated by the use of the Service or from the Service infrastructure itself (for example, the duration of a page visit).
    """    
    response = generate_compliant_report_rag(doc)
    # report = """
    # {
    #     "compliant": [
    #         {
    #             "section": "This privacy policy (the “Policy”) applies to Midjourney, Inc., the Midjourney.com website, and the Midjourney image generation platform (the “Services”).",
    #             "legal article numbers": "Article 13, 14",
    #             "legal provisions": "Transparency and information to be provided"
    #         },
    #         {
    #             "section": "As used in this Policy, “personal data” means any information that relates to, describes, could be used to identify an individual, directly or indirectly.",
    #             "legal article numbers": "Article 4(1)",
    #             "legal provisions": "Definition of personal data"
    #         },
    #         {
    #             "section": "Applicability: This Policy applies to personal data that Midjourney collects, uses, and discloses and which may include: (i) data collected through the Services, (ii) data collected through the process of training Midjourney machine learning algorithms, (iii) data collected through Midjourney websites, and (iv) data collected from third party sources.",
    #             "legal article numbers": "Article 13, 14",
    #             "legal provisions": "Information about the data processing activities"
    #         },
    #         {
    #             "section": "When you make purchases, we use third-party payment processors to collect credit card or other financial information. Midjourney does not store the credit card or payment information you provide, only confirmation that payment was made.",
    #             "legal article numbers": "Article 5(1)(c), Article 25",
    #             "legal provisions": "Data minimisation and data protection by design and default"
    #         },
    #         {
    #             "section": "Changes: We may update this Policy from time-to-time to reflect changes in legal, regulatory, operational requirements, our practices, and other factors.",
    #             "legal article numbers": "Article 13(2), 14(2)",
    #             "legal provisions": "Information to be provided where personal data are collected"
    #         }
    #     ],
    #     "non_compliant": [
    #         {
    #             "section": "This Policy does not apply to the following information: Personal Data about Midjourney employees and candidates, and certain contractors and agents acting in similar roles.",
    #             "legal article numbers": "Article 2(2), Article 3",
    #             "legal provisions": "Territorial scope and material scope of the GDPR",
    #             "amend": "The GDPR still applies to personal data of employees and candidates. This section should be removed or amended to clarify that the GDPR applies to all personal data processed by Midjourney."
    #         },
    #         {
    #             "section": "If any of the changes are unacceptable to you, you should cease interacting with us.",
    #             "legal article numbers": "Article 7(3), Article 21",
    #             "legal provisions": "Conditions for consent, Right to object",
    #             "amend": "Users have the right to withdraw consent and object to processing. Simply ceasing interaction may not be sufficient. The policy should explain the process for withdrawing consent and objecting to processing."
    #         },
    #         {
    #             "section": "When required under applicable law, we will notify you of any changes to this Policy.",
    #             "legal article numbers": "Article 13(3), 14(4)",
    #             "legal provisions": "Notification of changes",
    #             "amend": "The GDPR requires notification of changes to the privacy policy regardless of whether it is required by other applicable laws. This section should be amended to reflect that."
    #         },
    #         {
    #             "section": "The entire policy lacks information about:",
    #             "legal article numbers": "Articles 12-23, 32-34",
    #             "legal provisions": "Rights of data subjects, Security of processing, Data breach notification",
    #             "amend": "The policy needs to include information about data subject rights (access, rectification, erasure, etc.), data security measures, and data breach notification procedures."
    #         }
    #     ]
    # }
    # """
    # response = modify_document(doc, report)
    print(response)