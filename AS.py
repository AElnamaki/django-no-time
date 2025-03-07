import os
import subprocess
import shutil
import logging
import argparse

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s', filename='setup_log.log', filemode='w')

class StructureAgent:
    def __init__(self):
        self.project_name = None
        self.apps = []
        self.auto_confirm = False  # Flag to control auto confirmation

    def prompt_user(self, message, default=None):
        """Prompt user for input with optional default value."""
        if self.auto_confirm:
            return default
        response = input(f"{message} (default: {default}): ") if default else input(f"{message}: ")
        logging.info(f"Prompt: {message} | Response: {response}")
        return response.strip() or default

    def validate_non_empty(self, input_value, error_message):
        """Validate input to ensure it is not empty."""
        while not input_value.strip():
            logging.warning(f"Empty input received. Prompting again with message: {error_message}")
            print(error_message)
            input_value = self.prompt_user(error_message)
        return input_value.strip()
    
    def confirm_user_input(self, input_value, expected_type):
        """Confirm user input and allow re-entry or termination if incorrect."""
        while True:
            confirmation = self.prompt_user(f"Is '{input_value}' correct for {expected_type}? (yes to confirm, no to re-enter, terminate to exit): ", "yes").lower()
            if confirmation in ['yes', 'y']:
                return input_value
            elif confirmation in ['no', 'n']:
                input_value = self.prompt_user(f"Re-enter the {expected_type}: ")
            elif confirmation == 'terminate':
                raise RuntimeError("Process terminated by the user.")
            else:
                print("Invalid response. Please type 'yes', 'no', or 'terminate'.")

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

    def setup_project(self, project_name, app_data):
        """Set up a Django project."""
        try:
            # Check if virtual environment is activated
            self.check_virtualenv()

            # Set project name
            self.project_name = project_name

            # Create project directory
            self.create_directory(self.project_name)
            os.chdir(self.project_name)

            # Create Django project
            logging.info("Setting up Django project...")
            self.create_django_project()

            # Validate project structure
            self.validate_project_structure()

            # Set up apps
            for app_name, page_names in app_data:
                self.setup_app(app_name, page_names)

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

    def setup_app(self, app_name, page_names):
        """Set up a Django app."""
        try:
            # Create the Django app
            self.create_django_app(app_name)

            # Create templates
            create_templates = self.prompt_user(f"Do you want to create a templates folder for app '{app_name}'? (yes/no): ", "yes").lower()
            if create_templates in ['yes', 'y']:
                pages = [page.strip() for page in page_names.split(',')]
                for page_name in pages:
                    self.create_template_file(page_name, app_name)

            # Create static files
            create_static = self.prompt_user(f"Do you want to create a static folder for app '{app_name}'? (yes/no): ", "yes").lower()
            if create_static in ['yes', 'y']:
                # Create CSS file
                create_css = self.prompt_user(f"Do you want to create a CSS file for app '{app_name}'? (yes/no): ", "yes").lower()
                if create_css in ['yes', 'y']:
                    css_file_name = self.prompt_user(f"Enter the CSS file name for app '{app_name}': ", "style")
                    self.create_static_file(css_file_name, app_name, 'css')

                # Create JS file
                create_js = self.prompt_user(f"Do you want to create a JS file for app '{app_name}'? (yes/no): ", "yes").lower()
                if create_js in ['yes', 'y']:
                    js_file_name = self.prompt_user(f"Enter the JS file name for app '{app_name}': ", "script")
                    self.create_static_file(js_file_name, app_name, 'js')

            # Create media folder
            create_media = self.prompt_user(f"Do you want to create a media folder for app '{app_name}'? (yes/no): ", "yes").lower()
            if create_media in ['yes', 'y']:
                self.create_media_folder(app_name)

        except Exception as e:
            logging.error(f"Error setting up app '{app_name}': {e}")
            raise RuntimeError(f"Error setting up app '{app_name}': {e}")

def main():
    parser = argparse.ArgumentParser(description="Set up a Django project with apps, templates, and static files.")
    parser.add_argument("--project-name", required=True, help="Name of the Django project.")
    parser.add_argument("--app-name", required=True, nargs='+', help="Names of the Django apps.")
    parser.add_argument("--page-names", required=True, nargs='+', help="Comma-separated list of template page names for each app.")
    parser.add_argument("-y", "--yes", action="store_true", help="Auto confirm all prompts.")
    args = parser.parse_args()

    if len(args.app_name) != len(args.page_names):
        parser.error("The number of app names must match the number of sets of page names.")

    # Prepare app data
    app_data = list(zip(args.app_name, args.page_names))

    agent = StructureAgent()
    agent.auto_confirm = args.yes
    agent.setup_project(args.project_name, app_data)

if __name__ == "__main__":
    main()

