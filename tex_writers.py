import json
import re

def escape_latex(text):
    pattern = re.compile(r'([#$%^&_{|}~\\])')
    return pattern.sub(lambda m: '\\' + m.group(1), text)

def education_builder(education_path, relevant_coursework = False):
    with open(education_path, 'r') as file:
        edu_data = json.load(file)
    edu_tex ="\section{Education}\n\\resumeSubHeadingListStart"
    for edu_item in edu_data:
        edu_tex += "\n\\resumeSubheading\n"
        
        univ_name = edu_item['University Name']
        edu_tex += f"{{{univ_name}}}"
        
        dates = edu_item['Dates']
        edu_tex += f"{{{dates}}}"
        
        edu_tex += "\n"

        degree = edu_item['Degree']
        edu_tex += f"{{{degree}}}"

        gpa = edu_item['GPA']
        edu_tex += f"{{GPA: {gpa}}}"

        edu_tex += "\n"

        if relevant_coursework:
            relevant_coursework = edu_item['Relevant Coursework']
            if len(relevant_coursework) > 0:
                edu_tex += "\\resumeItemListStart\n"
                edu_tex += "\\resumeItem{\\textbf{Relevant Coursework:}"
                coursework = ", ".join(relevant_coursework)
                edu_tex += f"{escape_latex(coursework)}"
                edu_tex += "\n\\resumeItemListEnd"
        
    edu_tex += "\n\\resumeSubHeadingListEnd"
    return edu_tex

def experience_builder(experience_path,title):
    with open(experience_path, 'r') as file:
        exp_data = json.load(file)
    exp_tex =f"\section{{{title}}}\n\\resumeSubHeadingListStart"
    for exp_item in exp_data:
        exp_tex += "\n\\resumeSubheading\n"
        
        company_name = exp_item['Company Name']
        exp_tex += f"{{{company_name}}}"
        
        dates = exp_item['Dates']
        exp_tex += f"{{{dates}}}"
        
        exp_tex += "\n"

        role = exp_item['Role Title']
        exp_tex += f"{{{role}}}"

        location = exp_item['Location']
        exp_tex += f"{{{location}}}"

        exp_tex += "\n"

        points = exp_item['Selected Points']
        if len(points) > 0:
            exp_tex += "\\resumeItemListStart\n"
            for point in points:
                exp_tex += f"\\resumeItem{{{escape_latex(point)}}}\n"
            exp_tex += "\n\\resumeItemListEnd"
        else:
            print("ERRORRR NO POINTSSSSS")
        
    exp_tex += "\n\\resumeSubHeadingListEnd"
    return exp_tex

def projects_builder(projects_path,title):
    with open(projects_path, 'r') as file:
        project_data = json.load(file)
    project_tex =f"\section{{{title}}}\n\\resumeSubHeadingListStart"
    for project_item in project_data:
        project_tex += "\n\\resumeProjectHeading\n"
        
        project_name = project_item['Project Name']
        project_tex += f"{{\\textbf{{{project_name}}}"
        
        
        
        # project_tex += "$|$ \emph"
        # tools_list = project_item['Tools List']
        # tools = ", ".join(tools_list)
        # project_tex += f"{{{escape_latex(tools)}}}"

        project_tex += "}  {}"

        # if 'Dates' in project_item:
        #     dates = project_item['Dates']
        #     project_tex += f"{{{dates}}}"

        project_tex += "\n"

        points = project_item['Selected Points']
        if len(points) > 0:
            project_tex += "\\resumeItemListStart\n"
            for point in points:
                project_tex += f"\\resumeItem{{{escape_latex(point)}}}\n"
            project_tex += "\n\\resumeItemListEnd"
        else:
            print("ERRORRR NO POINTSSSSS")
        
    project_tex += "\n\\resumeSubHeadingListEnd"
    return project_tex

def skills_builder(skills_path):
    with open(skills_path, 'r') as file:
        skills_data = json.load(file)
    skills_tex ="\section{Technical Skills}\n\\begin{itemize}[leftmargin=0.15in, label={}]"
    skills_tex += "\n\small{\item{"

    languages = skills_data['Languages']
    languages = ", ".join(languages)
    skills_tex += f"\n\\textbf{{Languages}}{{: {escape_latex(languages)}}} \\\\"

    technologies = skills_data['Technologies']
    technologies = ", ".join(technologies)
    skills_tex += f"\n\\textbf{{Technologies}}{{: {escape_latex(technologies)}}} \\\\"

    concepts = skills_data['Concepts']
    concepts = ", ".join(concepts)
    skills_tex += f"\n\\textbf{{Concepts}}{{: {escape_latex(concepts)}}}"

    skills_tex += "\n}}"

    skills_tex += "\n\end{itemize}"

    return skills_tex