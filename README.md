# Resume Tailor GPT
This is a Large-Langage-Model (GPT) based tool to help automatically tailor your resume to job descriptions by extracting important keywords and integrating them within your resume naturally. It works by extracting information from your data and updating a latex resume template using Overleaf. 

## Installation

Clone the repository.
Install the required packages

```bash
pip install -r requirements.txt
```

## Usage

First populate the files within the `data/` folder with your information.

Next, login to [Overleaf](https://www.overleaf.com/). Use the following [resume template](https://www.overleaf.com/latex/templates/swe-resume-template/bznbzdprjfyy) by Audric Serador and select the `Open as Template` button to create a project based on this template. Here, add details such as your name in `src/heading.tex`. Finally, go back to the [Overleaf Home](https://www.overleaf.com/project) to ensure the project is added.

You will now need to retrieve the Project ID for the newly added project. This can be done by running the following code snippet (It assumes the resume template is your most recent project).


```python
import pyoverleaf

api = pyoverleaf.Api()
api.login_from_browser()
projects = api.get_projects()

# prints project ID
print(projects[0].id)
```

Populate the necessary elements in `settings.yaml`, including the retrieved project id from the previous step, as well as an `OPENAI_API_KEY`.

To generate a tailored resume, paste the job description in the `job_description.txt` file. Then run
```bash
python3 main.py
```

## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.

## License

[MIT](https://choosealicense.com/licenses/mit/)
