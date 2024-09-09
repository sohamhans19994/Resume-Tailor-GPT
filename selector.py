import os
import sys
import copy
from pydantic import BaseModel, Field, conint, field_validator
from typing import List
import json
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_community.llms import LlamaCpp
from langchain_core.callbacks import CallbackManager, StreamingStdOutCallbackHandler
import yaml
from langchain_community.callbacks import get_openai_callback


with open('settings.yaml', 'r') as file:
    config = yaml.safe_load(file)

os.environ['OPENAI_API_KEY'] = config['OPENAI_API_KEY']


class JobDescriptionKeywords(BaseModel):
    experience_keywords: List[str]
    skills_keywords: List[str]
    publication_required: bool

class ResumeObject(BaseModel):
    title: str
    keywords_to_align: List[str]
    relevancy_score: str
    points: List[str] = Field(min_items=2, max_items=3)


class SkillsObject(BaseModel):
    languages: List[str] = Field(min_items=8,max_items=18)
    technologies: List[str] = Field(min_items=8,max_items=18)
    concepts: List[str] = Field(min_items=8,max_items=18)

class Selector:
    def __init__(self,job_description):
        self.job_desc = job_description
        # Callbacks support token-wise streaming
        callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])
        if config['USE_LLAMA']:
            self.llama_llm = LlamaCpp(
                model_path=config['LLAMA_MODEL_PATH'],
                n_gpu_layers=60,
                n_batch=1024,
                callback_manager=callback_manager,
                verbose=True,  # Verbose is required to pass to the callback manager
            )
        self.gpt_llm = ChatOpenAI(model="gpt-4o-mini")
        self.cost = 0

    
    def extract_keywords(self):
        jd_keywords_query = f"""
            Given the job description \n
            {self.job_desc}
            \nAssume that you are tailoring your resume for this role. Come up with 2 lists, one for experience related keywords, and another list for skills keywords.\n
            Lastly, based on the description answer in True/False whether the description specifically requests research publications.
            Adhere to the output template strictly, do not add any extra elements like comments.
            """
        parser = JsonOutputParser(pydantic_object=JobDescriptionKeywords)

        prompt = PromptTemplate(
            template="Answer the user query.\n{format_instructions}\n{query}\n",
            input_variables=["query"],
            partial_variables={"format_instructions": parser.get_format_instructions()},
        )

        chain = prompt | self.gpt_llm | parser
        with get_openai_callback() as cb:
            out = chain.invoke({"query": jd_keywords_query})
            self.cost += cb.total_cost
        return out

    def write_resume_points(self,jd_keywords_str, experience_description, example_resume_points, isProject = False, points_range = [1,3]):
        point_type = "experience"
        if isProject:
            point_type = "project"
        generate_experience_bullet_template = f"""
            You identified that the keywords in the job description as follows \n
            {jd_keywords_str}
            Given that your resume has an {point_type} described below:\n
            {experience_description}
            Your task will finally be to write resume style short bullet points to help align this experience to a few of the key phrases identified above in a natural sounding manner.\n
            Note: Take great care to ensure the essence of the description is not changed in any way and none of the factual elements are modified.\n
            The process is described as follows. \n
            First, think of a few keywords that this {point_type} can be aligned to. \n 
            Based on how well the keywords can be aligned, give the {point_type} a relevance score between 1 to 10 with respect to the job description keywords. This score will be used to rank the items in your resume, and all of the experiences are in the AI and SWE space, so be stringent in giving a score to ensure that finally the scores are approximately in a bell curve centered at 5\n
            Finally, write down {points_range[0]} to {points_range[1]} resume style points that are tailored to the job such that they use most of the keywords you chose to align. Make sure to use any quantitative results given in the description and examples that may align align to each point\n 
            Here are some example points shown, the example may not be tailored to the keywords found\n
            {example_resume_points}
            Adhere to the output template strictly, do not add any extra elements like comments.
            """
        parser = JsonOutputParser(pydantic_object=ResumeObject)

        prompt = PromptTemplate(
            template="{format_instructions}\n{query}\n",
            input_variables=["query"],
            partial_variables={"format_instructions": parser.get_format_instructions()},
        )

        chain = prompt | self.gpt_llm | parser

        with get_openai_callback() as cb:
            out = chain.invoke({"query": generate_experience_bullet_template})
            self.cost += cb.total_cost
        return out
        

    def extract_skills(self,jd_skills_keywords,available_skills_json):
        generate_skills_template = f"""
            You identified that keywords in the job description as follows \n
            {jd_skills_keywords}
            \nDivide the skills keywords into 3 sections: Languages, Technologies, Concepts. \n

            Given that your resume has skills divided into 3 sections as described below:\n
            Languages: {available_skills_json['Languages']} \n
            Technologies: {available_skills_json['Technologies']} \n
            Concepts: {available_skills_json['Concepts']}\n

            Based on the required skills in the job description, find matching skills in your resume and list them into the 3 sections. Even if a skill from the job description isn't directly present in the resume, if it's closely enough related to other resume listed skills include it. \n
            Also Identify skills in your resume that are closely related to some of the experience keywords, but aren't directly mentioned in the skills keywords, and make sure to include them with lower priority.
            Finally populate each section list with approximately 10 - 15 elements first with exact matching skills, then with job description skills that are close to ones in your resume, and last with other resume skills which are related to the job description skills even if not exactly listed.\n
            Adhere to the output template strictly, do not add any extra elements like comments.
            """
        parser = JsonOutputParser(pydantic_object=SkillsObject)

        prompt = PromptTemplate(
            template="{format_instructions}\n{query}\n",
            input_variables=["query"],
            partial_variables={"format_instructions": parser.get_format_instructions()},
        )

        chain = prompt | self.gpt_llm | parser

        with get_openai_callback() as cb:
            out = chain.invoke({"query": generate_skills_template})
            self.cost += cb.total_cost
        return out
        


    def extract_data(self):
        with open('data/experiences.json') as f:
            experiences = json.load(f)
        
        with open('data/projects.json') as f:
            projects = json.load(f)
        
        with open('data/skills.json') as f:
            skills = json.load(f)
        
        keywords_output = self.extract_keywords()
        experience_str = "\n".join(keywords_output['experience_keywords'])
        skills_str = "\n".join(keywords_output['skills_keywords'])
        keywords_str = (
            "Experience Keywords:\n"
            f"{experience_str}\n\n"
            "Skills Keywords:\n"
            f"{skills_str}\n"
        )

        selected_exps = []
        for exp in experiences:
            resume_points_obj = self.write_resume_points(keywords_str,exp['Experience Description'],exp['Example Points'],isProject=False,points_range=exp["Points Range"])
            new_exp = copy.deepcopy(exp)
            new_exp['Selected Points'] = resume_points_obj['points']
            new_exp['Relevance Score'] = float(resume_points_obj['relevancy_score'])
            new_exp['type'] = 'Experience'
            selected_exps.append(new_exp)
            
        
        for proj in projects:
            resume_points_obj = self.write_resume_points(keywords_str,proj['Project Description'],proj['Example Points'],isProject=True,points_range=exp["Points Range"])
            new_proj = copy.deepcopy(proj)
            new_proj['Selected Points'] = resume_points_obj['points']
            new_proj['Relevance Score'] = float(resume_points_obj['relevancy_score'])
            new_proj['type'] = 'Project'
            selected_exps.append(new_proj)
        
        selected_exps.sort(key=lambda x: x['Relevance Score'], reverse=True)
        
        p1_exps = []
        p1_projs = []
        p2_exps = []
        p2_projs = []
        format = 0
        
        for selection in selected_exps:
            if selection['type'] == 'Experience':
                if len(p1_exps) < 3:
                    p1_exps.append(selection)
                else:
                    p2_exps.append(selection)
            elif selection['type'] == 'Project':
                if len(p1_projs) < 2:
                    p1_projs.append(selection)
                else:
                    p2_projs.append(selection)
            
        if len(p1_projs) == 1:
            exp_score = p2_exps[0]['Relevance Score'] + p2_exps[1]['Relevance Score']
            projs_score = p1_projs[0]['Relevance Score'] + p2_projs[0]['Relevance Score']
            if projs_score >= exp_score:
                p1_projs.append(p2_projs[0])
                p2_projs.pop(0)
            
            else:
                p1_exps.append(p2_exps[0])
                p1_exps.append(p2_exps[1])
                p2_exps.pop(0)
                p2_exps.pop(0)
                p2_projs.insert(0,p1_projs[0])

        if len(p1_projs) == 0:
            format = 1
        
        with open('selected_data/experiences1.json', 'w') as f:
            json.dump(sorted(p1_exps, key=lambda x: x["Order"], reverse=True),f,indent=4)
        
        with open('selected_data/experiences2.json', 'w') as f:
            json.dump(sorted(p2_exps, key=lambda x: x["Order"], reverse=True),f,indent=4)
        
        if format == 0:
            with open('selected_data/projects1.json', 'w') as f:
                json.dump(sorted(p1_projs, key=lambda x: x["Order"], reverse=True),f,indent=4)
            
        with open('selected_data/projects2.json', 'w') as f:
            json.dump(sorted(p2_projs, key=lambda x: x["Order"], reverse=True),f,indent=4)
        
        skills_obj = self.extract_skills(skills_str,skills)
        skills_dict = {
            "Languages":skills_obj['languages'],
            "Technologies":skills_obj['technologies'],
            "Concepts":skills_obj['concepts']
        }
        with open('selected_data/skills.json', 'w') as f:
            json.dump(skills_dict,f,indent=4)
        
        return format        