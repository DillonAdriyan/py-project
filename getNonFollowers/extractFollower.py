import json

def extract_usernames(input_file, output_file):
    """
    Ekstrak username dari file JSON dan simpan ke file JSON baru.
    
    Parameters:
    input_file (str): Path ke file input JSON.
    output_file (str): Path ke file output JSON yang akan disimpan.
    """
    try:
        # Membaca file JSON input
        with open(input_file, 'r') as file:
            data = json.load(file)
        
        # Mengambil username dari 'value' di 'string_list_data'
        usernames = [entry['value'] for group in data for entry in group['string_list_data']]
        
        # Menyimpan username ke file JSON baru
        with open(output_file, 'w') as file:
            json.dump(usernames, file, indent=4)
        
        print(f"Username berhasil diekstrak dan disimpan di {output_file}.")
    except Exception as e:
        print(f"Terjadi kesalahan: {e}")

if __name__ == "__main__":
    # Ganti 'followers_1.json' dengan nama file JSON input dan 'output_usernames.json' sebagai file output.
    input_file = 'followersMentah.json'
    output_file = 'usernameFollower.json'
    
    extract_usernames(input_file, output_file)
    