# 🧾 Bill Extraction System - User Guide (Hinglish)

Ye tool aapke hath se likhe hue bills (invoices) ki photos padh kar unka data automatic Excel sheet mein daal deta hai.

## ⚙️ Step 1: Ek baar ka Setup

1. **Python Install Karein:**
   - [python.org/downloads](https://www.python.org/downloads/) par jayein.
   - Python download karke install karein.
   - **⚠️ BAHUT ZAROORI:** Install karte time **"Add python.exe to PATH"** wale box par tick zaroor lagayein.

2. **Required Tools Install Karein:**
   - Apne computer mein **Command Prompt (cmd)** open karein.
   - Ye command type karein aur Enter dabayein:
     `pip install -r requirements.txt`
     *(Ya phir type karein: `pip install google-generativeai pandas openpyxl`)*

3. **Gemini API Key Banayein (Free):**
   - [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey) par jayein.
   - Google ID se login karein.
   - **"Create API Key"** par click karein aur chaabi (key) copy kar lein.

4. **API Key Code Mein Dalein:**
   - `main.py` file ko Notepad mein open karein.
   - Line number 11 par jahan `API_KEY = "YAHAN_APNI_API_KEY_PASTE_KAREIN"` likha hai, wahan apni asli key paste karein. (Quote `""` mat hatayein).
   - File save kar dein (`Ctrl + S`).

## 🚀 Step 2: System ko Kaise Chalayein (Roz ka kaam)

1. **Photos Dalein:**
   - Is folder ke andar ek `bills` naam ka folder hai. (Agar nahi hai toh bas ek baar script run karein, ye khud ban jayega).
   - Apni saari bill ki photos (`.jpg`, `.jpeg`, `.png`) us `bills` folder ke andar copy karke daal dein.

2. **Code Run Karein:**
   - Apne folder mein upar address bar mein click karein, `cmd` type karein aur Enter dabayein.
   - Command prompt khulne par type karein:
     `python main.py`
   - Enter dabayein.

3. **Result Dekhein:**
   - Ab computer ek-ek photo padhega. Aapko screen par dikhega ki konsi photo process ho rahi hai.
   - Pura hone ke baad, usi folder mein `Extracted_Bills_Data.xlsx` naam ki file ban jayegi.
   - Use double-click karke open karein, aapka saara data wahan tayyar milega! 🎉

## ❓ Troubleshoot (Agar koi dikkat aaye)
- **Error: "ModuleNotFoundError: No module named..."** -> Iska matlab tools theek se install nahi hue. CMD mein `pip install google-generativeai pandas openpyxl` phir se run karein.
- **Error: API key not valid** -> Dhyan dein ki aapne key bilkul sahi copy ki hai aur `""` ke andar rakhi hai.
- **Error: Rate limit exceeded** -> Google API free version mein ek baar mein bahut tezi se request nahi le sakta, isliye code mein 4 second ka gap diya gaya hai. Agar fir bhi error aaye, toh code mein `time.sleep(4)` ko badhakar `time.sleep(6)` kar dein.
