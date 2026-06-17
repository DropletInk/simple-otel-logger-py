import os


def get_project_name():

    project_path = os.path.dirname(os.path.abspath(__file__))

    project_name = os.path.basename(project_path)

    return project_name
