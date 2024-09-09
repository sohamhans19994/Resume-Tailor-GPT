from tex_writers import education_builder,experience_builder,projects_builder,skills_builder
from selector import Selector
import pyoverleaf
import os
import yaml

if __name__ == "__main__":
    show_cost = True
    api = pyoverleaf.Api()
    api.login_from_browser()
    format = 0

    with open('settings.yaml', 'r') as file:
        config = yaml.safe_load(file)

    # Delete all files in selected_data directory
    directory_path = config['SELECTED_DATA_FOLDER']
    os.makedirs(directory_path, exist_ok=True)
    for filename in os.listdir(directory_path):
        file_path = os.path.join(directory_path, filename)
        # Check if it is a file and not a directory
        if os.path.isfile(file_path):
            os.remove(file_path)
            print(f"Deleted file: {file_path}")

    with open(config["JOB_DESCRIPTION_FILE"],"r") as f:
        job_description = f.read()

    llm_select = Selector(job_description)
    format = llm_select.extract_data()

    io = pyoverleaf.ProjectIO(api, config["RESUME_PROJECT_ID"])

    education_tex = education_builder(os.path.join(config["DATA_FOLDER"],"education.json"),config['INCLUDE_RELEVANT_COURSEWORK'])
    with io.open("src/education.tex", "w+") as f:
        f.write(education_tex)
    
    
    experience_tex = experience_builder(os.path.join(config["SELECTED_DATA_FOLDER"],"experiences1.json"),"Relevant Experience")
    with io.open("src/experience1.tex", "w+") as f:
        f.write(experience_tex)
    
    if format == 0:
        project_tex = projects_builder(os.path.join(config["SELECTED_DATA_FOLDER"],"projects1.json"),"Key Projects")
        with io.open("src/projects1.tex", "w+") as f:
            f.write(project_tex)
    else:
        with io.open("src/projects1.tex", "w") as f:
            pass
    
    experience_tex2 = experience_builder(os.path.join(config["SELECTED_DATA_FOLDER"],"experiences2.json"),"Supplemental Experience")
    with io.open("src/experience2.tex", "w") as f:
        f.write(experience_tex2)
    
    project2_title = "Other Academic Projects"
    if format == 1:
        project2_title = "Academic Projects"
    project_tex = projects_builder(os.path.join(config["SELECTED_DATA_FOLDER"],"projects2.json"),project2_title)
    with io.open("src/projects2.tex", "w") as f:
            f.write(project_tex)

    skills_tex = skills_builder(os.path.join(config["SELECTED_DATA_FOLDER"],"skills.json"))
    with io.open("src/skills.tex", "w") as f:
        f.write(skills_tex)
    
    print("Done! Open Overleaf in browser to view and download pdf.")
    if show_cost:
        print(f"Total cost for tailoring this resume in USD: ${llm_select.cost}")


    



