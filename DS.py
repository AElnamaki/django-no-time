import os
import subprocess
import shutil
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s', filename='setup_log.log', filemode='w')

class StructureAgent:
    def __init__(self):
        self.project_name = None
        self.apps = []

    def prompt_user(self, message, default=None):
        """Prompt user for input with optional default value."""
        if default:
            response = input(f"{message} (default: {default}): ")
        else:
            response = input(f"{message}: ")
        logging.info(f"Prompt: {message} | Response: {response}")
        return response.strip() or default

    def validate_non_empty(self, input_value, error_message):
        """Validate input to ensure it is not empty."""
        while not input_value.strip():
            logging.warning(f"Empty input received. Prompting again with message: {error_message}")
            print(error_message)
            input_value = self.prompt_user(error_message)
        return input_value.strip()

    def print_confirmation(self, message):
        """Print confirmation message."""
        print(f"✅ {message}")

    def create_directory(self, dir_path):
        """Create a directory if it doesn't exist."""
        try:
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
                logging.info(f"Directory '{dir_path}' created.")
                self.print_confirmation(f"Directory '{dir_path}' created.")
            else:
                logging.info(f"Directory '{dir_path}' already exists.")
        except OSError as e:
            logging.error(f"Error creating directory '{dir_path}': {e}")
            raise RuntimeError(f"Error creating directory '{dir_path}': {e}")

    def validate_project_structure(self):
        """Validate the project structure to ensure it adheres to Django's recommended layout."""
        expected_dirs = ['static', 'templates']
        for dir_name in expected_dirs:
            dir_path = os.path.join(self.project_name, dir_name)
            self.create_directory(dir_path)

    def check_virtualenv(self):
        """Check if virtual environment is activated."""
        if not os.environ.get('VIRTUAL_ENV'):
            raise EnvironmentError("Virtual environment is not activated. Please activate the virtual environment and run the script again.")

    def create_django_project(self):
        """Create a new Django project."""
        try:
            subprocess.run(['django-admin', 'startproject', self.project_name, '.'], check=True)
            logging.info(f"Django project '{self.project_name}' created.")
            self.print_confirmation(f"Django project '{self.project_name}' created.")
        except subprocess.CalledProcessError as e:
            logging.error(f"Error creating Django project: {e}")
            raise RuntimeError(f"Error creating Django project: {e}")

    def create_django_app(self, app_name):
        """Create a new Django app."""
        try:
            subprocess.run(['python', 'manage.py', 'startapp', app_name], check=True)
            self.apps.append(app_name)
            logging.info(f"Django app '{app_name}' created.")
            self.print_confirmation(f"Django app '{app_name}' created.")
        except subprocess.CalledProcessError as e:
            logging.error(f"Error creating Django app '{app_name}': {e}")
            raise RuntimeError(f"Error creating Django app '{app_name}': {e}")

    def create_template_file(self, template_name, app_name):
        """Create a new template file for a Django app."""
        try:
            template_dir = os.path.join(app_name, 'templates', app_name)
            self.create_directory(template_dir)
            template_path = os.path.join(template_dir, f"{template_name}.html")
            if not os.path.isfile(template_path):
                with open(template_path, 'w') as f:
                    f.write(f"<!-- Template for {template_name} -->\n")
                logging.info(f"Template file '{template_path}' created.")
                self.print_confirmation(f"Template file '{template_path}' created.")
        except IOError as e:
            logging.error(f"Error creating template file '{template_name}.html' for app '{app_name}': {e}")
            raise RuntimeError(f"Error creating template file '{template_name}.html' for app '{app_name}': {e}")

    def create_static_file(self, file_name, app_name, file_type):
        """Create a new static file (CSS or JS) for a Django app."""
        try:
            static_dir = os.path.join(app_name, 'static', app_name, file_type)
            self.create_directory(static_dir)
            file_path = os.path.join(static_dir, f"{file_name}.{file_type}")
            if not os.path.isfile(file_path):
                with open(file_path, 'w') as f:
                    if file_type == 'css':
                        f.write(f"/* CSS file for {file_name} */\n")
                    elif file_type == 'js':
                        f.write(f"// JavaScript file for {file_name}\n")
                logging.info(f"{file_type.upper()} file '{file_path}' created.")
                self.print_confirmation(f"{file_type.upper()} file '{file_path}' created.")
        except IOError as e:
            logging.error(f"Error creating {file_type} file '{file_name}.{file_type}' for app '{app_name}': {e}")
            raise RuntimeError(f"Error creating {file_type} file '{file_name}.{file_type}' for app '{app_name}': {e}")

    def create_media_folder(self, app_name):
        """Create a media folder with subdirectories (photos, audio, video) for a Django app."""
        try:
            media_folder = os.path.join(self.project_name, app_name, 'media')
            self.create_directory(media_folder)
            for folder in ['photos', 'audio', 'video']:
                folder_path = os.path.join(media_folder, folder)
                self.create_directory(folder_path)
            logging.info(f"Media folder 'media/' with subdirectories 'photos/', 'audio/', 'video/' created for app '{app_name}'.")
            self.print_confirmation(f"Media folder 'media/' with subdirectories 'photos/', 'audio/', 'video/' created for app '{app_name}'.")
        except Exception as e:
            logging.error(f"Error creating media folder for app '{app_name}': {e}")
            raise RuntimeError(f"Error creating media folder for app '{app_name}': {e}")

    def setup_project(self):
        """Set up a Django project."""
        try:
            # Check if virtual environment is activated
            self.check_virtualenv()

            # Prompt user for project name with default value suggestion
            default_project_name = "my_project"
            self.project_name = self.prompt_user(f"Enter the Django project name", default=default_project_name)
            self.project_name = self.validate_non_empty(self.project_name, "Project name cannot be empty. Please enter the Django project name: ")

            # Create project directory
            self.create_directory(self.project_name)
            os.chdir(self.project_name)

            # Create Django project
            logging.info("Setting up Django project...")
            self.create_django_project()

            # Validate project structure
            self.validate_project_structure()

            # Create initial app
            self.setup_app()

            # Ask user if they want to create more apps
            while True:
                create_app = self.prompt_user("\nDo you want to create a new Django app? (yes/no): ").lower()
                if create_app != 'yes' and create_app != 'y':
                    break
                self.setup_app()

            logging.info(f"Django project '{self.project_name}' has been created.")
            if self.apps:
                logging.info(f"The following apps have been created: {', '.join(self.apps)}.")

        except Exception as e:
            logging.error(f"An error occurred during setup: {e}")
            print("Rolling back changes...")
            if os.path.exists(self.project_name):
                shutil.rmtree(self.project_name, ignore_errors=True)
                logging.info(f"Rolled back changes by deleting directory '{self.project_name}'.")
            print("Setup aborted.")

    def setup_app(self):
        """Set up a Django app."""
        try:
            # Prompt user for app name with default value suggestion
            default_app_name = "my_app"
            app_name = self.prompt_user("Enter the Django app name", default=default_app_name)
            app_name = self.validate_non_empty(app_name, "App name cannot be empty. Please enter the Django app name: ")
            self.create_django_app(app_name)

            # Ask user if they want to create a templates folder
            create_templates = self.prompt_user(f"Do you want to create a templates folder for app '{app_name}'? (yes/no): ").lower()
            if create_templates == 'yes' or create_templates == 'y':
                # Ask user for page names
                page_names = self.prompt_user(f"Enter the page names for templates in app '{app_name}' (comma-separated): ")
                if page_names.strip():
                    pages = [page.strip() for page in page_names.split(',')]
                    for page_name in pages:
                        self.create_template_file(page_name, app_name)

            # Ask user if they want to create a static folder
            create_static = self.prompt_user(f"Do you want to create a static folder for app '{app_name}'? (yes/no): ").lower()
            if create_static == 'yes' or create_static == 'y':
                # Ask user for CSS file
                create_css = self.prompt_user(f"Do you want to create a CSS file for app '{app_name}'? (yes/no): ").lower()
                if create_css == 'yes' or create_css == 'y':
                    css_file_name = self.prompt_user(f"Enter the CSS file name for app '{app_name}': ")
                    css_file_name = self.validate_non_empty(css_file_name, "CSS file name cannot be empty. Please enter the CSS file name: ")
                    self.create_static_file(css_file_name, app_name, 'css')

                # Ask user for JavaScript file
                create_js = self.prompt_user(f"Do you want to create a JavaScript file for app '{app_name}'? (yes/no): ").lower()
                if create_js == 'yes' or create_js == 'y':
                    js_file_name = self.prompt_user(f"Enter the JavaScript file name for app '{app_name}': ")
                    js_file_name = self.validate_non_empty(js_file_name, "JavaScript file name cannot be empty. Please enter the JavaScript file name: ")
                    self.create_static_file(js_file_name, app_name, 'js')

                # Ask user if they want to create a media folder
                create_media = self.prompt_user(f"Do you want to create a media folder for app '{app_name}'? (yes/no): ").lower()
                if create_media == 'yes' or create_media == 'y':
                    self.create_media_folder(app_name)
                else:
                    print(f"No media folder created for app '{app_name}'.")

        except Exception as e:
            logging.error(f"An error occurred while setting up the app '{app_name}': {e}")
            raise

# Example usage:
if __name__ == "__main__":
    agent = StructureAgent()
    agent.setup_project()

# ship the path for statics modification modification 
