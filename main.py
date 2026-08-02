import warnings
warnings.filterwarnings('ignore')
import google.generativeai as genai
import pandas as pd
import os
import json
import time
import sys
from PIL import Image, ImageEnhance
from dotenv import load_dotenv

load_dotenv()

# ==============================================================================
# ⚙️ SETTINGS
# ==============================================================================
# API key is now loaded from .env file
API_KEY = os.getenv("GEMINI_API_KEY") 


# Folder jahan bills ki photos rakhi jayengi
BILLS_FOLDER = "bills" 

# Output Excel file ka naam jo banegi
OUTPUT_FILE = "Extracted_Bills_Data.xlsx"
# ==============================================================================

# Configure API
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-3.5-flash')

def setup_folder():
    """Ensure the bills folder exists"""
    if not os.path.exists(BILLS_FOLDER):
        os.makedirs(BILLS_FOLDER)
        print(f"[!] '{BILLS_FOLDER}' naam ka folder nahi mila tha, isliye naya folder bana diya gaya hai.")
        print(f"[!] Kripya apni saari bill ki photos '{BILLS_FOLDER}' folder ke andar dalein aur script dobara chalayein.")
        sys.exit()

def preprocess_image(image_path):
    """Enhances the image to make text clearer for OCR"""
    try:
        img = Image.open(image_path)
        
        # Increase contrast to make text pop out
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.8)
        
        # Increase sharpness for blurry text
        sharpness = ImageEnhance.Sharpness(img)
        img = sharpness.enhance(2.0)
        
        temp_path = "temp_processed.jpg"
        img.save(temp_path)
        
        # Ye line process hui image ko automatic screen par open kar degi
        img.show()
        
        return temp_path
    except Exception as e:
        print(f"[!] Image preprocess fail hui, original use kar rahe hain. Error: {e}")
        return image_path

def extract_data_from_image(image_path, retries=3):
    """Uploads the image and extracts data using Gemini AI"""
    for attempt in range(retries):
        try:
            # Image ko pehle saaf (preprocess) karo
            processed_path = preprocess_image(image_path)
            
            sample_file = genai.upload_file(path=processed_path)
            
            # AI ko instructions detail mein diye gaye hain
            prompt = """
            You are an advanced OCR and data extraction AI with expert reasoning capabilities.
            Analyze this handwritten invoice image carefully. The image might be blurry, rough, or have poor handwriting in Hindi and English.
            
            Your goal is to extract the following details. If a word is blurry or slightly cut off, use context clues to deduce the most likely names, numbers, or items.
            Return the result EXACTLY in this JSON format, and do not include any other text or explanation:
            {
                "Invoice_Number": "",
                "Date": "",
                "Customer_Name": "",
                "Mobile_Number": "",
                "Address": "",
                "Items_Purchased": "",
                "Total_Amount": "",
                "Salesman_Signature": ""
            }
            
            Instructions:
            - Invoice_Number is usually near 'क्रम सं०' or 'No.'.
            - If a field is missing, try very hard to find it anywhere on the page. Only output "Not Readable" if it is impossible to guess.
            - For 'Items_Purchased', combine all item names, IMEI numbers, and details into a single readable string.
            - Pay close attention to messy handwriting. Differentiate between similar looking numbers (e.g., 1 & 7, 0 & 8, 5 & 6) by using context like the Total Amount calculation.
            - For 'Salesman_Signature', check if there is a signature or name at the bottom of the bill. Output "Present", "Not Present", or the readable name of the salesman if visible.
            """
            
            response = model.generate_content([sample_file, prompt])
            
            # Temp file ko delete karo agar wo bani thi
            if processed_path == "temp_processed.jpg" and os.path.exists(processed_path):
                os.remove(processed_path)
            
            # Clean response to parse JSON safely
            raw_text = response.text.strip()
            if raw_text.startswith("```json"):
                raw_text = raw_text[7:]
            if raw_text.endswith("```"):
                raw_text = raw_text[:-3]
                
            data = json.loads(raw_text.strip())
            return data
            
        except Exception as e:
            if attempt < retries - 1:
                print(f"[!] '{os.path.basename(image_path)}' par error aaya. 10 seconds mein retry kar raha hai... (Attempt {attempt+1}/{retries})")
                time.sleep(10)
            else:
                print(f"[ERROR] '{os.path.basename(image_path)}' ko read karne mein dikkat aayi: {e}")
                return None

def main():
    print("="*60)
    print(" BILL EXTRACTION SYSTEM (Powered by Gemini AI) ")
    print("="*60)
    print("\n")
    
    if not API_KEY or API_KEY.startswith("YOUR_API_KEY"):
        print("[ERROR] Aapne API key nahi daali hai!")
        print("Kripya 'main.py' file ko Notepad mein open karein aur apni API key dalein.")
        sys.exit()

    setup_folder()
    
    # Folder se saari images dhoondhna
    image_files = [f for f in os.listdir(BILLS_FOLDER) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    
    if not image_files:
        print(f"[!] '{BILLS_FOLDER}' folder khali hai. Kripya isme bill ki photos dalein.")
        sys.exit()

    # Pehle se process ho chuki files check karna
    processed_files = set()
    if os.path.exists(OUTPUT_FILE):
        try:
            df_existing = pd.read_excel(OUTPUT_FILE)
            if 'Filename' in df_existing.columns:
                processed_files = set(df_existing['Filename'].tolist())
        except Exception as e:
            print(f"[!] Pehle wali Excel file read karne mein dikkat: {e}")

    new_image_files = [f for f in image_files if f not in processed_files]
    
    if not new_image_files:
        print(f"[*] Saari {len(image_files)} photos pehle hi process ho chuki hain. Nayi koi photo nahi mili.")
        sys.exit()

    if len(processed_files) > 0:
        print(f"[*] Total {len(image_files)} bills the. Jisme se {len(processed_files)} pehle ho chuke hain.")
        print(f"[*] Ab bachi hui {len(new_image_files)} naye bills ko process kar raha hai...\n")
    else:
        print(f"[*] Total {len(new_image_files)} bills mile hain processing ke liye.\n")
    
    image_files = new_image_files
    
    all_data = []
    
    # Har photo par ek-ek karke loop chalana
    for count, filename in enumerate(image_files, 1):
        print(f"--- Process kar raha hai ({count}/{len(image_files)}): {filename} ---")
        image_path = os.path.join(BILLS_FOLDER, filename)
        
        extracted_info = extract_data_from_image(image_path)
        
        if extracted_info:
            extracted_info['Filename'] = filename
            all_data.append(extracted_info)
            name = extracted_info.get('Customer_Name', 'N/A')
            amt = extracted_info.get('Total_Amount', 'N/A')
            print(f"[SUCCESS] Data mil gaya -> Name: {name} | Amount: {amt}")
        else:
            print(f"[FAILED] '{filename}' se data nikalne mein fail hua.")
            
        # API limit se bachne ke liye 5 second ka tharav (delay)
        if count < len(image_files):
            print("[*] 5 seconds ka wait kar raha hai (API limit se bachne ke liye)...\n")
            time.sleep(5)
            
    # Data ko Excel mein save karna
    if all_data:
        print("\n[*] Data Excel mein save kiya jaa raha hai...")
        df_new = pd.DataFrame(all_data)
        
        # Purana data mila kar save karna
        if os.path.exists(OUTPUT_FILE):
            try:
                df_existing = pd.read_excel(OUTPUT_FILE)
                df_final = pd.concat([df_existing, df_new], ignore_index=True)
            except Exception as e:
                print(f"[!] Excel append fail hua: {e}. Nayi sheet ban rahi hai.")
                df_final = df_new
        else:
            df_final = df_new
        
        # Columns ko proper order mein lagana
        cols = ['Filename', 'Invoice_Number', 'Date', 'Customer_Name', 'Mobile_Number', 'Address', 'Items_Purchased', 'Total_Amount', 'Salesman_Signature']
        # Agar koi extra column AI ne de diya ho, usko bhi add kar lenge
        existing_cols = [c for c in cols if c in df_final.columns]
        other_cols = [c for c in df_final.columns if c not in cols]
        df_final = df_final[existing_cols + other_cols]
        
        try:
            df_final.to_excel(OUTPUT_FILE, index=False)
            print("\n" + "="*60)
            print(f" BADHAI HO! Saara data '{OUTPUT_FILE}' mein save ho gaya hai. ")
            print("="*60)
        except PermissionError:
            backup_file = OUTPUT_FILE.replace(".xlsx", "_backup.xlsx")
            df_final.to_excel(backup_file, index=False)
            print("\n" + "="*60)
            print(f" [WARNING] '{OUTPUT_FILE}' pehle se khuli hui thi!")
            print(f" Isliye saara data '{backup_file}' naam ki nayi file mein save kar diya gaya hai.")
            print(" Aapka koi data waste nahi hua! 🎉")
            print("="*60)
    else:
        print("\n[!] Koi naya data extract nahi ho paya.")

if __name__ == "__main__":
    main()
