from tex_writers import education_builder,experience_builder,projects_builder,skills_builder
from selector import Selector
import pyoverleaf
import os
import yaml
import argparse


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Process some arguments.')
    script_path = os.path.dirname(os.path.abspath(__file__))
    # Add the "use_selected" argument as a flag
    parser.add_argument(
        '--use_selected',
        action='store_true',
        default=False,  # Default value is False
        help='Use selected option'
    )

    # Parse the arguments
    args = parser.parse_args()

    
    format = 0

    with open(os.path.join(script_path,'settings.yaml'), 'r') as file:
        config = yaml.safe_load(file)

    # Delete all files in selected_data directory

    if not args.use_selected:
        directory_path = config['SELECTED_DATA_FOLDER']
        os.makedirs(directory_path, exist_ok=True)
        for filename in os.listdir(directory_path):
            file_path = os.path.join(directory_path, filename)
            # Check if it is a file and not a directory
            if os.path.isfile(file_path):
                os.remove(file_path)
                print(f"Deleted file: {file_path}")

        with open(os.path.join(script_path,"job_description.txt"),"r") as f:
            job_description = f.read()

        llm_select = Selector(job_description)
        format = llm_select.extract_data()
    
    else:
        format = 0
        if not os.path.isfile(os.path.join(config['SELECTED_DATA_FOLDER'],"projects1.json")):
            format = 1

    education_tex = education_builder(os.path.join(config["DATA_FOLDER"],"education.json"),config['INCLUDE_RELEVANT_COURSEWORK'])
    with open(os.path.join(script_path,"tex_files/src/education.tex"),"w+") as f:
        f.write(education_tex)

    
    experience_tex = experience_builder(os.path.join(config["SELECTED_DATA_FOLDER"],"experiences1.json"),"Relevant Experience")
    with open(os.path.join(script_path,"tex_files/src/experience1.tex"),"w+") as f:
        f.write(experience_tex)

    if format == 0:
        project_tex = projects_builder(os.path.join(config["SELECTED_DATA_FOLDER"],"projects1.json"),"Key Projects")
        with open(os.path.join(script_path,"tex_files/src/projects1.tex"),"w+") as f:
            f.write(project_tex)
    else:
        with open(os.path.join(script_path,"tex_files/src/projects1.tex"),"w") as f:
            pass
    
    experience_tex2 = experience_builder(os.path.join(config["SELECTED_DATA_FOLDER"],"experiences2.json"),"Supplemental Experience")
    with open(os.path.join(script_path,"tex_files/src/experience2.tex"),"w+") as f:
        f.write(experience_tex2)
    
    project2_title = "Other Academic Projects"
    if format == 1:
        project2_title = "Academic Projects"
    project_tex2 = projects_builder(os.path.join(config["SELECTED_DATA_FOLDER"],"projects2.json"),project2_title)
    with open(os.path.join(script_path,"tex_files/src/projects2.tex"),"w+") as f:
        f.write(project_tex2)

    skills_tex = skills_builder(os.path.join(config["SELECTED_DATA_FOLDER"],"skills.json"))
    with open(os.path.join(script_path,"tex_files/src/skills.tex"),"w+") as f:
        f.write(skills_tex)
    
    print("Done! Convert tex_files to PDF to view")
    if config['SHOW_API_COST']:
        print(f"Total cost for tailoring this resume in USD: ${llm_select.cost}")


    



