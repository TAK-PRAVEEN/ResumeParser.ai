import pandas as pd
import csv
import os
import docx2txt
import PyPDF2
import json
import re
from nltk.tokenize import blankline_tokenize
import json

class ResumeParser:
    def __init__(self, file):
        self.SECTION_KEYWORDS = {
            "personal_info": [
                "Personal Information", "Contact Information", "Contact Details", "Profile", "About Me", "Bio"
            ],
            "objective": [
                "Objective", "Career Objective", "Professional Summary", "Summary", "Profile Summary", "Career Summary", "Personal Statement", "Executive Summary"
            ],
            "skills": [
                "Skills", "Key Skills", "Technical Skills", "Core Competencies", "Competencies", "Areas of Expertise", "Technical Proficiencies"
            ],
            "experience": [
                "Work Experience", "Professional Experience", "Employment History", "Experience", "Relevant Experience", "Work History", "Career History"
            ],
            "education": [
                "Education", "Educational Qualifications", "Academic Background", "Academic History", "Academic Qualifications", "Educational Background"
            ],
            "certifications": [
                "Certifications", "Certificates", "Professional Certifications", "Licenses", "Training"
            ],
            "projects": [
                "Projects", "Key Projects", "Project Experience", "Significant Projects", "Relevant Projects"
            ],
            "achievements": [
                "Achievements", "Accomplishments", "Key Achievements", "Awards and Honors", "Honors", "Recognitions"
            ],
            "languages": [
                "Languages", "Language Proficiency", "Language Skills"
            ],
            "interests": [
                "Interests", "Hobbies", "Personal Interests", "Extra-Curricular Activities"
            ],
            "references": [
                "References", "Referees"
            ],
            "publications": [
                "Publications", "Research Publications", "Papers", "Articles"
            ],
            "volunteer": [
                "Volunteer Experience", "Volunteering", "Community Involvement", "Social Service"
            ],
            "additional": [
                "Additional Information", "Other Information", "Miscellaneous"
            ],
            "development": [
                "Professional Development", "Continuing Education", "Workshops", "Seminars", "Conferences"
            ]
        }

        self.file = file

    def data_ingestion(self):
        # Check the file extension to determine how to read the file
        _, file_extension = os.path.splitext(self.file)

        if file_extension == '.txt':
            with open(self.file, "r", encoding="utf-8") as file:
                content = file.read()
        
        elif file_extension == '.docx':
            content = docx2txt.process(self.file)
        
        elif file_extension == '.pdf':
            content = ""
            with open(self.file, "rb") as file:
                reader = PyPDF2.PdfReader(file)
                for page in reader.pages:
                    content += page.extract_text() + "\n"
        
        else:
            raise ValueError("Unsupported file format: {}".format(file_extension))

        return content



    def preprocess(self):
        content = self.data_ingestion()
        tokenized = blankline_tokenize(content)
        return tokenized

    def extract_resume_info(self):
       text = self.preprocess()
       # Join the tokenized content into a single string
       text = "\n".join(text)
       lines = [line.strip() for line in text.splitlines() if line.strip()]
       
       # ---------- 1. Extract Phone (10-digit, Indian style) ----------
       phone = re.findall(r'\b[6-9]\d{9}\b', text)
       phone = phone[0] if phone else None

       # ---------- 2. Extract Email ----------
       email = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)
       email = email[0] if email else None

       # ---------- 3. Extract Links ----------
       raw_urls = re.findall(r'https?://[^\s)>\]]+', text)
       markdown_urls = re.findall(r'\[.*?\]\((https?://[^\s)]+)\)', text)
       html_urls = re.findall(r'href="(https?://[^\s"]+)"', text)
       links = list(set(raw_urls + markdown_urls + html_urls))

       # ---------- 4. Extract Name ----------
       # Assume name is first non-empty line and contains no @ or digits
       name = None
       for line in lines[:5]:
           if not any(char.isdigit() for char in line) and '@' not in line and len(line.split()) <= 5:
               name = line
               break

       return {
           "name": name,
           "phone": phone,
           "email": email,
           "links": links,
       }
   

    def section_identification(self):
        document = self.data_ingestion()
        tokenized = self.preprocess()

        sections = {}
        sections_list = []
        sections_index = {}
        previous_section = None

        resume_info = self.extract_resume_info()
        sections.update(resume_info)
            
        for num in range(len(tokenized)):
            section_name = tokenized[num].split("\n")[0].title()
            element = tokenized[num].split("\n")[0].strip().title()
            sections_list.append(element)
            for section, keywords in self.SECTION_KEYWORDS.items():
                if any(keyword in section_name for keyword in keywords):
                    section_name = section_name.strip()
                    sections_index[section_name] = sections_list.index(section_name)
                    current_section = section
                    sections[current_section] = []
                    if previous_section:
                        sections[ps] = (tokenized[sections_index[previous_section]:sections_index[section_name]])
                        previous_section = section_name
                        ps = current_section
                    else:
                        previous_section = section_name
                        ps = current_section

            # for section, details in sections.items():
            #     sections[section] = str("".join(details))   

        return sections


    def csv_format(self):
        json_data = self.section_identification()
        
        # Convert JSON data to a dictionary if it's a JSON string
        if isinstance(json_data, str):
            json_data = json.loads(json_data)

        # Define the uploads directory
        uploads_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'uploads'))
        os.makedirs(uploads_dir, exist_ok=True)  # Create the directory if it doesn't exist

        # Define the CSV file path
        csv_file_path = os.path.join(uploads_dir, "resume_data.csv")
        
        # Open the CSV file for writing
        with open(csv_file_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            
            # Write the header
            writer.writerow(["Section", "Content"])

            # Iterate through the JSON data and write to CSV
            for section, content in json_data.items():
                if isinstance(content, list):
                    for item in content:
                        writer.writerow([section, item])
                else:
                    writer.writerow([section, str(content)])

        return "resume_data.csv"
        # Simulate file download (in a real application, you would return the file)
        # For example, in a Flask app, you would use send_file(csv_file_path)

        # After the file is downloaded, delete it
        # os.remove(csv_file_path)


    def json_format(self):
        raw_text = self.section_identification()
        
        # Define the uploads directory
        uploads_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'uploads'))
        os.makedirs(uploads_dir, exist_ok=True)  # Create the directory if it doesn't exist

        # Define the CSV file path
        json_file_path = os.path.join(uploads_dir, "resume_data.json")
        
        # Write the JSON data to the file
        with open(json_file_path, "w", encoding="utf-8") as f:
            json.dump(raw_text, f, indent=4, ensure_ascii=False)

        # Read the JSON data back from the file
        with open(json_file_path, "r", encoding="utf-8") as f:
            content = json.load(f)

        return "resume_data.json"


    def excel_format(self):
        raw_text = self.section_identification()
        rows = []
        
        # Prepare the data for the DataFrame
        for section, items in raw_text.items():
            if isinstance(items, list):
                for item in items:
                    rows.append({"Section": section, "Content": item})
            else:
                rows.append({"Section": section, "Content": str(items)})

        uploads_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'uploads'))
        os.makedirs(uploads_dir, exist_ok=True)  # Create the directory if it doesn't exist

        # Define the Excel file path
        excel_file_path = os.path.join(uploads_dir, "resume_data.xlsx")
        
        # Create a DataFrame and save it to an Excel file
        df = pd.DataFrame(rows)
        df.to_excel(excel_file_path, index=False)

        # Read the Excel file back (if needed)
        # You can use pd.read_excel() if you want to read it back into a DataFrame
        # df_read = pd.read_excel(excel_file_path)


        return "resume_data.xlsx"  # Return the DataFrame if needed

