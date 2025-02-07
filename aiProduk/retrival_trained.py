import json
import os
import torch
import numpy as np
from sentence_transformers import SentenceTransformer, InputExample, losses
from torch.utils.data import DataLoader

def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def main():
    # 1. Cek device (GPU jika tersedia, jika tidak gunakan CPU)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print("Menggunakan device:", device)

    # 2. Pastikan file data produk tersedia
    json_file_path = 'product_data.json'
    if not os.path.exists(json_file_path):
        print(f"File {json_file_path} tidak ditemukan. Pastikan file tersebut ada.")
        return

    with open(json_file_path, 'r') as f:
        product_data = json.load(f)

    # 3. Membuat contoh data pelatihan (training examples)
    # Kita iterasi setiap kategori dan tiap produk untuk membuat pasangan (pertanyaan, deskripsi)
    train_examples = []
    for category in product_data['products']:
        for item in category['items']:
            description = item.get('description', item.get('desc', ''))
            query = f"Apa keunggulan {item['name']}?"
            train_examples.append(InputExample(texts=[query, description], label=1.0))
    
    # Membuat beberapa contoh negatif dengan memasangkan query dari satu produk dengan deskripsi produk lain
    n = len(train_examples)
    negative_examples = []
    if n > 1:
        for i in range(n):
            j = (i + 1) % n  # ambil produk berikutnya (melingkar)
            query = train_examples[i].texts[0]
            wrong_description = train_examples[j].texts[1]
            negative_examples.append(InputExample(texts=[query, wrong_description], label=0.0))
    train_examples.extend(negative_examples)
    print("Jumlah contoh pelatihan:", len(train_examples))

    # 4. Inisialisasi model retrieval menggunakan model yang ringan: "all-MiniLM-L6-v2"
    model_name = "all-MiniLM-L6-v2"
    model = SentenceTransformer(model_name, device=device)
    print(f"Model {model_name} berhasil diinisialisasi pada {device}.")

    # 5. Membuat DataLoader untuk training
    batch_size = 2
    train_dataloader = DataLoader(train_examples, shuffle=True, batch_size=batch_size)

    # 6. Gunakan CosineSimilarityLoss untuk melatih model
    train_loss = losses.CosineSimilarityLoss(model)

    # 7. Atur parameter pelatihan
    num_epochs = 3
    warmup_steps = int(len(train_dataloader) * num_epochs * 0.1)
    print("Mulai pelatihan model...")

    model.fit(
        train_objectives=[(train_dataloader, train_loss)],
        epochs=num_epochs,
        warmup_steps=warmup_steps,
        show_progress_bar=True,
        output_path='fine_tuned_product_model'
    )
    print("Pelatihan selesai. Model telah tersimpan di folder 'fine_tuned_product_model'.")

if __name__ == '__main__':
    main()
    