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
        
        # Pastikan data berada di dalam 'relationships_following'
        if 'relationships_following' in data:
            relationships = data['relationships_following']
            
            # Mengambil username dari 'value' di 'string_list_data'
            usernames = []
            for group in relationships:
                if 'string_list_data' in group:
                    for entry in group['string_list_data']:
                        usernames.append(entry.get('value'))  # Mendapatkan value dari setiap entry
            
            # Menyimpan username ke file JSON baru
            with open(output_file, 'w') as file:
                json.dump(usernames, file, indent=4)
            
            print(f"Username berhasil diekstrak dan disimpan di {output_file}.")
        else:
            print("Kunci 'relationships_following' tidak ditemukan dalam file JSON.")
    
    except Exception as e:
        print(f"Terjadi kesalahan: {e}")

if __name__ == "__main__":
    # Ganti 'followingMentah.json' dengan nama file JSON input dan 'usernameFollowing.json' sebagai file output.
    input_file = 'followingMentah.json'
    output_file = 'usernameFollowing.json'
    
    extract_usernames(input_file, output_file)
