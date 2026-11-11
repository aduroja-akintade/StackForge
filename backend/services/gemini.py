import os
import json
import asyncio
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from the root .env file
load_dotenv(os.path.join(os.path.dirname(__file__), '../../.env'))

# Configure Gemini API
api_key = os.getenv("GOOGLE_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
else:
    print("Warning: GOOGLE_API_KEY not found in environment.")

class GeminiService:
    def __init__(self):
        self.model_name = os.getenv("GEMINI_MODEL", "gemini-flash-lite-latest")
        self.model = genai.GenerativeModel(self.model_name)

    def _parse_ai_json(self, raw_text: str):
        """
        Cleans and parses JSON from AI response, removing markdown code blocks if present.
        """
        cleaned_text = raw_text.strip()
        if cleaned_text.startswith("```"):
            # Remove start block (e.g., ```json)
            lines = cleaned_text.split("\n")
            if lines[0].startswith("```"):
                lines = lines[1:]
            # Remove end block (```)
            if lines[-1].strip() == "```":
                lines = lines[:-1]
            cleaned_text = "\n".join(lines).strip()
        
        try:
            value = json.loads(cleaned_text)
            return value if isinstance(value, dict) else {"error": "Unexpected AI response format"}
        except json.JSONDecodeError as jde:
            print("GeminiService: Invalid JSON response from provider")
            return {"error": "Invalid structured AI response"}

    async def analyse_job_description(self, jd_text: str):
        """
        Analyses a cloud/DevOps job description to extract:
        - Required skills
        - Preferred skills
        - Tools and technologies
        - Recommended projects
        """
        print(f"GeminiService: Starting analysis for JD (length: {len(jd_text)})")
        
        prompt = f"""
        You are an expert Cloud and DevOps Platform Engineer and technical recruiter.
        Analyse the following job description and break it down into four specific categories:
        1. Required Skills: Fundamental skills mentioned as mandatory.
        2. Preferred Skills: Nice-to-have skills or advanced qualifications.
        3. Tools & Technologies: Specific software, cloud providers, and platforms mentioned.
        4. Recommended Projects: Based on this JD, suggest 3-5 high-impact projects a candidate should build to prove their competence. 
           For each project, provide a title, a one-sentence 'why it matches', the tech stack it covers, estimated build time, and difficulty level.

        Format the output as a JSON object with these keys: 
        "required_skills", "preferred_skills", "tools_technologies", "recommended_projects".
        Each value should be a list of strings, except "recommended_projects" which should be a list of objects.

        Job Description:
        {jd_text}
        """
        
        try:
            print(f"GeminiService: Sending request to model {self.model_name}")
            response = await asyncio.to_thread(self.model.generate_content,
                prompt,
                generation_config={"response_mime_type": "application/json"}
            )
            print("GeminiService: Response received successfully")
            return self._parse_ai_json(response.text)
        except Exception as e:
            print(f"GeminiService: General Error: {str(e)}")
            return {"error": str(e)}

    async def recommend_projects(self, jd_text: str, current_skills: list = None):
        """
        Based on the job description and user's current skills, recommends 3-5
        specific projects, ranked by impact.
        """
        skills_context = f"The user already knows: {', '.join(current_skills)}." if current_skills else "No prior skills provided."
        
        prompt = f"""
        You are an expert Cloud and DevOps Platform Engineer and technical recruiter.
        Based on the job description below, recommend 3-5 specific projects that will have the highest impact on an employer.
        
        Context: {skills_context}

        Rank these projects from highest to lowest impact.
        Format the output as a JSON object with one key "recommendations", containing an array of 3-5 objects.
        Each object MUST use exactly these fields: "title", "impact", "stack", "time", and "difficulty".
        All values must be concise strings, without markdown fences.

        Job Description:
        {jd_text}
        """
        
        try:
            response = await asyncio.to_thread(self.model.generate_content,
                prompt,
                generation_config={"response_mime_type": "application/json"}
            )
            return self._parse_ai_json(response.text)
        except Exception as e:
            return {"error": str(e)}

    async def generate_implementation_plan(self, project_title: str, project_description: str = None, tech_stack: str = None):
        """
        Generates an ELITE, hyper-detailed step-by-step implementation plan for a given project.
        """
        prompt = f"""
        You are an Elite Staff Platform Engineer at a Tier-1 tech company (Google/AWS/Meta). 
        Your task is to provide a 'Gold-Standard' implementation plan that a Cloud Engineer can follow to build a production-grade portfolio project.

        PROJECT DETAILS:
        - Project Title: {project_title}
        - Context/Goal: {project_description if project_description else 'Standard production-grade deployment.'}
        - Tech Stack: {tech_stack if tech_stack else 'Modern DevOps tools (Terraform, Kubernetes, Docker, CI/CD).'}

        REQUIREMENTS FOR YOUR RESPONSE:
        1. Architecture: Describe the high-level system design, including networking, security, and data flow.
        2. File Structure: Provide a complete, nested directory and file structure for the entire project repository.
        3. Implementation Steps: Provide 5-8 detailed steps. Each step MUST include:
           - A clear objective.
           - Specific CLI commands (e.g., terraform init, docker build, kubectl apply).
           - Key configuration snippets or logic explanations (e.g., 'Ensure the S3 bucket has versioning enabled via HCL').
        4. Verification: Provide exact commands or tests to verify that each stage is working correctly.

        FORMAT: Return ONLY a valid JSON object with these keys: 
        "architecture_overview", "detailed_file_structure", "step_by_step_plan", "verification_checklist".
        step_by_step_plan MUST be an array of objects with "phase", "action", "command", and "logic_explanation".
        verification_checklist MUST be an array of strings.
        """
        
        try:
            response = await asyncio.to_thread(self.model.generate_content,
                prompt,
                generation_config={"response_mime_type": "application/json"}
            )
            return self._parse_ai_json(response.text)
        except Exception as e:
            return {"error": str(e)}

    async def generate_upgrade_advice(self, project_description: str, current_tech_stack: str = None):
        """
        Analyses an existing project and explains how to upgrade it to production grade.
        """
        prompt = f"""
        You are a Senior Staff Platform Engineer. 
        Analyze the following project and explain exactly how to upgrade it from a 'student/tutorial grade' to a 'production-grade' system.

        PROJECT TO UPGRADE:
        - Description: {project_description}
        - Tech Stack: {current_tech_stack if current_tech_stack else 'Standard stack.'}

        YOUR ANALYSIS MUST COVER:
        1. Security: (IAM, Secrets Management, Encryption, Network Policies).
        2. Reliability & HA: (Multi-AZ, Load Balancing, Auto-scaling).
        3. Observability: (Prometheus/Grafana, ELK, SLOs/SLIs).
        4. Performance & Scalability: (Caching, CDN, Database indexing).

        FORMAT: Return a JSON object with:
        "analysis": ["gap 1", "gap 2"],
        "senior_additions": ["specific improvement 1", "specific improvement 2"],
        "upgrade_steps": ["ordered step 1", "ordered step 2"].
        All three fields MUST contain arrays of strings.
        """
        
        try:
            response = await asyncio.to_thread(self.model.generate_content,
                prompt,
                generation_config={"response_mime_type": "application/json"}
            )
            return self._parse_ai_json(response.text)
        except Exception as e:
            return {"error": str(e)}

# Singleton instance
gemini_service = GeminiService()
