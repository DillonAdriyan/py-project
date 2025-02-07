import json
from transformers import T5Tokenizer, T5ForConditionalGeneration, Seq2SeqTrainer, Seq2SeqTrainingArguments, DataCollatorForSeq2Seq
from datasets import Dataset

def main():
    # 1. Muat dataset Q&A dari file JSON
    data_file = "product_qa.json"
    with open(data_file, "r") as f:
        data = json.load(f)
    
    # Ubah list of dict ke Hugging Face Dataset
    dataset = Dataset.from_list(data)
    split_dataset = dataset.train_test_split(test_size=0.1)
    
    # 2. Inisialisasi tokenizer dan model T5
    model_name = "t5-small"  # Anda dapat mengganti dengan "t5-base" jika perangkat mendukung
    tokenizer = T5Tokenizer.from_pretrained(model_name)
    model = T5ForConditionalGeneration.from_pretrained(model_name)
    
    # 3. Fungsi preprocess untuk mempersiapkan data
    def preprocess_function(examples):
        # Membuat input berupa gabungan pertanyaan dan konteks
        inputs = [f"Pertanyaan: {q} Konteks: {c}" for q, c in zip(examples["question"], examples["context"])]
        model_inputs = tokenizer(inputs, max_length=512, truncation=True)
        
        # Tokenisasi target (jawaban)
        with tokenizer.as_target_tokenizer():
            labels = tokenizer(examples["answer"], max_length=128, truncation=True)
        model_inputs["labels"] = labels["input_ids"]
        return model_inputs
    
    tokenized_train = split_dataset["train"].map(preprocess_function, batched=True)
    tokenized_val = split_dataset["test"].map(preprocess_function, batched=True)
    
    # 4. Tentukan argumen pelatihan
    training_args = Seq2SeqTrainingArguments(
        output_dir="t5_finetuned_product_qa",
        evaluation_strategy="epoch",
        learning_rate=5e-5,
        per_device_train_batch_size=4,
        per_device_eval_batch_size=4,
        weight_decay=0.01,
        save_total_limit=3,
        num_train_epochs=3,
        predict_with_generate=True,
        logging_dir='./logs',
    )
    
    data_collator = DataCollatorForSeq2Seq(tokenizer, model=model)
    
    # 5. Inisialisasi Trainer
    trainer = Seq2SeqTrainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_train,
        eval_dataset=tokenized_val,
        data_collator=data_collator,
        tokenizer=tokenizer,
    )
    
    # 6. Mulai pelatihan
    trainer.train()
    trainer.save_model("t5_finetuned_product_qa")
    print("Pelatihan T5 untuk Q&A selesai dan model tersimpan di 't5_finetuned_product_qa'.")

if __name__ == "__main__":
    main()
