from sentence_transformers import SentenceTransformer
import numpy as np
import pandas as pd
import sys # Import the sys module

# --- THIS IS THE FIX ---
try:
    # Load the pre-trained model. This will be downloaded from Hugging Face.
    print("Loading S-BioBert model... (This may take a few minutes on first run)")
    model = SentenceTransformer('pritamdeka/S-BioBert-snli-multinli-stsb')
    print("Model loaded successfully.")
except Exception as e:
    # If the download fails for any reason (network, etc.), stop the program.
    print(f"FATAL: Could not download or load the SentenceTransformer model.")
    print(f"Error: {e}")
    print("Please check your internet connection and try again.")
    # Exit the program with an error code
    sys.exit(1)
# -------------------------


def get_text_embeddings(text_series: pd.Series) -> pd.DataFrame:
    """
    Takes a pandas Series of text descriptions and returns a DataFrame of embeddings.
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