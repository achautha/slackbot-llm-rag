from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings, StorageContext, load_index_from_storage
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.ollama import Ollama
from llama_index.readers.remote import RemoteReader
from llama_index.llms.huggingface import HuggingFaceInferenceAPI
import logging
import sys
import os.path
import requests


logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

def download_dataset(url, save_folder="datasets", file_name=None):
    # Create the save folder if it doesn't exist
    os.makedirs(save_folder, exist_ok=True)
    
    # Get the file content
    response = requests.get(url)
    
    # Check if the request was successful
    if response.status_code == 200:
        if not file_name:
            file_name = url.split("/")[-1]  # Use the last part of the URL as the file name
            
        file_path = os.path.join(save_folder, file_name)
        
        # Write the file content to the file
        with open(file_path, 'wb') as file:
            file.write(response.content)
        
        exists = os.path.exists(file_path)
        logging.info('Exists' + str(exists))
        return f"Dataset downloaded and saved to {file_path}"
    else:
        return f"Failed to download dataset. Status code: {response.status_code}"
    
def display_prompt_dict(prompts_dict):
    for k, p in prompts_dict.items():
        text_md = f"**Prompt Key**: {k}<br>" f"**Text:** <br>"
        print(p.get_template())

# bge-base embedding model
Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-base-en-v1.5")

# ollama
# Settings.llm = Ollama(model="llama3", request_timeout=360.0)
Settings.llm = HuggingFaceInferenceAPI(model_name="HuggingFaceH4/zephyr-7b-beta")

# documents = SimpleDirectoryReader("data").load_data()
# documents = RemoteReader().load_data(url='https://www.sci.gov.in/wp-admin/admin-ajax.php?action=get_court_pdf&diary_no=272882023&type=o&order_date=2024-06-11&from=latest_judgements_order')
# llmsherpa_api_url = 'https://readers.llmsherpa.com/api/document/developer/parseDocument?renderFormat=all'
# pdf_url = 'https://www.sci.gov.in/wp-admin/admin-ajax.php?action=get_court_pdf&diary_no=272882023&type=o&order_date=2024-06-11&from=latest_judgements_order'

download_dataset(url='https://www.sci.gov.in/wp-admin/admin-ajax.php?action=get_court_pdf&diary_no=272882023&type=o&order_date=2024-06-11&from=latest_judgements_order', file_name='dataset.pdf')

documents = SimpleDirectoryReader("datasets").load_data()
index = VectorStoreIndex.from_documents(
    documents,
)

# chat_engine = index.as_chat_engine(
#     chat_mode="context",
#     #memory=memory,
#     system_prompt=(
#         "You are a helpful assistant for a law firm in india who can interpret court judgements"
#     ),
# )

# response = chat_engine.chat("Summarise judgement in the context in 2-3 sentences for layman to understand")

query_engine = index.as_query_engine()

print(query_engine.query("Intepret the judegement and convert it into a NEWS story format. It should include information about petitioner, respondent and quick sumary or order passed. ")
)
