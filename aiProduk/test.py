import json
import numpy as np
from sentence_transformers import SentenceTransformer
from transformers import T5Tokenizer, T5ForConditionalGeneration
from numpy import dot
from numpy.linalg import norm

def cosine_similarity(a, b):
    return dot(a, b) / (norm(a) * norm(b))

def load_contexts(product_data):
    """
    Mengubah data produk menjadi daftar string konteks untuk tiap produk.
    """
    contexts = []
    # Iterasi setiap kategori
    for category in product_data["products"]:
        cat = category["category"]
        for item in category["items"]:
            # Gabungkan informasi produk yang relevan
            context = (
                f"Produk: {item.get('name', '')}\n"
                f"Kategori: {cat}\n"
                f"Harga: {item.get('price', '')}\n"
                f"Deskripsi: {item.get('description', item.get('desc', ''))}\n"
                f"Kemasan: {item.get('packaging', '')}\n"
                f"Opsi tambahan: {', '.join(item.get('extras', []))}\n"
                f"Toko: {product_data.get('store_info', {}).get('location', '')}\n"
                f"Waktu pembuatan: {product_data.get('store_info', {}).get('processing_time', '')}"
            )
            contexts.append(context)
    return contexts

def retrieve_best_context(query, contexts, retrieval_model):
    """
    Mengambil konteks terbaik dari daftar konteks berdasarkan query.
    """
    query_emb = retrieval_model.encode([query])[0]
    context_embs = retrieval_model.encode(contexts)
    similarities = [cosine_similarity(query_emb, emb) for emb in context_embs]
    best_idx = np.argmax(similarities)
    return contexts[best_idx], similarities[best_idx]

def generate_answer(query, context, t5_model, t5_tokenizer):
    """
    Menghasilkan jawaban menggunakan model T5 berdasarkan query dan konteks.
    """
    prompt = f"Pertanyaan: {query}\nInformasi produk: {context}\nJawaban:"
    input_ids = t5_tokenizer.encode(prompt, return_tensors="pt")
    output_ids = t5_model.generate(input_ids, max_length=100, num_beams=4, early_stopping=True)
    answer = t5_tokenizer.decode(output_ids[0], skip_special_tokens=True)
    return answer

def main():
    # Muat data produk dari file JSON
    with open("product_data.json", "r") as f:
        product_data = json.load(f)
    contexts = load_contexts(product_data)
    
    # Inisialisasi model retrieval (SentenceTransformer fine-tuned)
    retrieval_model = SentenceTransformer("fine_tuned_product_model")
    
    # Inisialisasi model generatif T5 yang telah difine-tune untuk Q&A
    t5_model = T5ForConditionalGeneration.from_pretrained("t5_finetuned_product_qa")
    t5_tokenizer = T5Tokenizer.from_pretrained("t5_finetuned_product_qa")
    
    print("AI Assistant siap menjawab pertanyaan produk. Ketik 'exit' atau 'quit' untuk berhenti.")
    while True:
        query = input("Question: ")
        if query.lower() in ["exit", "quit"]:
            break
        # Ambil konteks terbaik berdasarkan query
        best_context, sim = retrieve_best_context(query, contexts, retrieval_model)
        # Hasilkan jawaban dari model T5
        answer = generate_answer(query, best_context, t5_model, t5_tokenizer)
        print("Jawaban:", answer)
        print()

if __name__ == "__main__":
    main()
