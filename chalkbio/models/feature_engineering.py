from sentence_transformers import SentenceTransformer
import numpy as np
import pandas as pd

# Load the pre-trained model. This will be downloaded from Hugging Face the first time it's run.
# We choose a model specifically fine-tuned for biomedical sentence similarity.
model = SentenceTransformer('pritamdeka/S-BioBert-snli-multinli-stsb')

def get_text_embeddings(text_series: pd.Series) -> pd.DataFrame:
    """
    Takes a pandas Series of text descriptions and returns a DataFrame of embeddings.
    
    Each row in the output DataFrame corresponds to a text description, and the columns
    are the dimensions of the embedding vector (768 for BioBert).
    """
    print("Generating text embeddings...")
    # The model.encode method converts a list of sentences into a list of vectors (numpy arrays)
    embeddings = model.encode(text_series.tolist(), show_progress_bar=True)
    
    # Create column names for the embedding features
    embedding_cols = [f'embed_{i}' for i in range(embeddings.shape[1])]
    
    # Create a DataFrame from the embeddings
    embeddings_df = pd.DataFrame(embeddings, index=text_series.index, columns=embedding_cols)
    print("Embeddings generated successfully.")
    return embeddings_df