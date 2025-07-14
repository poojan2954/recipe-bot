import pandas as pd
import os
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain.schema import Document
from dotenv import load_dotenv

load_dotenv()

def build_vectorstore():
    # Load the recipe dataset
    df = pd.read_csv("archive/RAW_recipes.csv")

    # Keep only relevant columns and limit rows for faster processing
    df = df[['name', 'ingredients', 'steps']].dropna().head(1000)

    # Convert list-like strings to comma-separated strings
    df['ingredients'] = df['ingredients'].apply(lambda x: ', '.join(eval(x)))
    df['steps'] = df['steps'].apply(lambda x: '. '.join(eval(x)))

    # Prepare LangChain documents
    docs = []
    for _, row in df.iterrows():
        docs.append(Document(
            page_content=row['ingredients'],
            metadata={
                "name": row['name'],
                "ingredients": row['ingredients'],
                "instructions": row['steps'],
                "meal_type": "Any"  # Used for compatibility if needed
            }
        ))

    # Load the embedding model
    embedding = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

    # Build the FAISS vector store and save
    db = FAISS.from_documents(docs, embedding)
    db.save_local("recipes_index")
    print("✅ Vectorstore built and saved!")

if __name__ == "__main__":
    build_vectorstore()
