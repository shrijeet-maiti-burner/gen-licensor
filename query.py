import requests
import pandas as pd
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

def get_access_token(api_key):
    authenticator = IAMAuthenticator(api_key)
    return authenticator.token_manager.get_token()

def query_ai(software_name, query, token):
    url = "https://us-south.ml.cloud.ibm.com/ml/v1/text/generation?version=2023-05-29"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    prompt = f"answer the questions exactly and to the point. do not repeat the question, do not output anything extra. only the direct short answer.\n\nInput: {software_name} {query}\nOutput:"
    body = {
        "input": prompt,
        "parameters": {
            "decoding_method": "greedy",
            "max_new_tokens": 50,
            "repetition_penalty": 1.2
        },
        "model_id": "ibm/granite-13b-instruct-v2",
        "project_id": "60f05b68-e3a2-448b-944a-f8a7d765111e"
    }
    response = requests.post(url, headers=headers, json=body)
    if response.status_code == 200:
        return response.json()['results'][0]['generated_text']
    else:
        raise Exception(f"Failed to get a response: {response.status_code} - {response.text}")

def update_csv_with_ai_responses(file_path, ai_responses):
    df = pd.read_csv(file_path, dtype=str)
    for response in ai_responses:
        software_name = response['software_name']
        df.loc[df['Name'].str.lower() == software_name.lower(), 'License Type'] = response['license_type']
        df.loc[df['Name'].str.lower() == software_name.lower(), 'License Name'] = response['license_name']
        df.loc[df['Name'].str.lower() == software_name.lower(), 'Is Safe'] = response['is_safe']
        df.loc[df['Name'].str.lower() == software_name.lower(), 'Software Type'] = response['software_type']
    df.to_csv(file_path, index=False)
    print("CSV updated with AI responses.")

def main():
    api_key = 'API_KEY'
    token = get_access_token(api_key)
    file_path = 'installed_software.csv'
    software_df = pd.read_csv(file_path, dtype=str)

    ai_responses = []
    queries = ['license type', 'license name', 'is safe', 'software type']
    for index, row in software_df.iterrows():
        software_name = row['Name']
        responses = {}
        for query in queries:
            responses[query] = query_ai(software_name, query, token)
        
        ai_responses.append({
            'software_name': software_name,
            'license_type': responses['license type'],
            'license_name': responses['license name'],
            'is_safe': responses['is safe'],
            'software_type': responses['software type']
        })

    update_csv_with_ai_responses(file_path, ai_responses)

if __name__ == '__main__':
    main()