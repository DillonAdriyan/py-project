import json

def extract_usernames_followers(input_file, output_file):
    """
    Ekstrak username dari file followers JSON dan simpan ke file JSON baru.
    """
    try:
        # Membaca file JSON input
        with open(input_file, 'r') as file:
            data = json.load(file)
        
        # Mengambil username dari 'value' di 'string_list_data' (langsung, tanpa key tambahan)
        usernames = [entry['value'] for group in data for entry in group['string_list_data']]
        
        # Menyimpan username ke file JSON baru
        with open(output_file, 'w') as file:
            json.dump(usernames, file, indent=4)
        
        print(f"Username followers berhasil diekstrak dan disimpan di {output_file}.")
    except Exception as e:
        print(f"Terjadi kesalahan pada followers: {e}")

def extract_usernames_following(input_file, output_file):
    """
    Ekstrak username dari file following JSON dan simpan ke file JSON baru.
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
            
            print(f"Username following berhasil diekstrak dan disimpan di {output_file}.")
        else:
            print("Kunci 'relationships_following' tidak ditemukan dalam file JSON.")
    
    except Exception as e:
        print(f"Terjadi kesalahan pada following: {e}")

def check_non_followers(following_file, followers_file, output_file):
    """
    Membandingkan username following dan followers untuk menemukan akun yang tidak mengikuti balik.
    """
    try:
        # Membaca file JSON following dan followers
        with open(following_file, 'r') as file:
            following = json.load(file)
        
        with open(followers_file, 'r') as file:
            followers = json.load(file)
        
        # Mencari akun yang tidak mengikuti balik
        non_followers = [user for user in following if user not in followers]
        
        # Menyimpan daftar akun yang tidak mengikuti balik ke file JSON baru
        with open(output_file, 'w') as file:
            json.dump(non_followers, file, indent=4)
        
        print(f"Akun yang tidak mengikuti balik telah disimpan di {output_file}.")
    except Exception as e:
        print(f"Terjadi kesalahan saat memeriksa non-followers: {e}")

if __name__ == "__main__":
    # File input dan output untuk followers dan following
    
    # sesuaikan nama file json dari Instagram biasanya adalah followers_1.json
    followers_input = 'followersMentah.json'
    
    # sesuaikan nama file json dari Instagram biasanya adalah following.json
    following_input = 'followingMentah.json'
    
    # output file nantinya
    followers_output = 'usernameFollower.json'
    following_output = 'usernameFollowing.json'
    non_followers_output = 'nonFollowers.json'
    
    # Langkah 1: Ekstrak username followers
    extract_usernames_followers(followers_input, followers_output)
    
    # Langkah 2: Ekstrak username following
    extract_usernames_following(following_input, following_output)
    
    # Langkah 3: Cek akun yang tidak mengikuti balik
    check_non_followers(following_output, followers_output, non_followers_output)
    