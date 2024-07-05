import os
import logging
import argparse

class Identifier:
    def __init__(self, project_path):
        self.project_path = self.validate_project_path(project_path)
        self.apps = self.get_apps()

    def print_confirmation(self, message):
        """Print confirmation message with ✅."""
        print(f"✅ {message}")

    def print_alert(self, message):
        """Print alert message with 🔴."""
        print(f"🔴 {message}")

    def validate_project_path(self, project_path):
        assert os.path.exists(project_path), f"Project path '{project_path}' does not exist."
        return project_path

    def get_apps(self):
        apps = []
        try:
            for item in os.listdir(self.project_path):
                item_path = os.path.join(self.project_path, item)
                if os.path.isdir(item_path) and item not in ['__pycache__', os.path.basename(self.project_path)]:
                    if os.path.exists(os.path.join(item_path, 'apps.py')):
                        apps.append(item)
        except Exception as e:
            logging.error(f"Error while getting apps: {e}")
        return apps

    def get_directories(self, app):
        try:
            app_path = os.path.join(self.project_path, app)
            static_path = os.path.join(app_path, 'static', app)
            templates_path = os.path.join(app_path, 'templates', app)
            media_path = os.path.join(app_path, 'media')

            css_dir = os.path.join(static_path, 'css')
            js_dir = os.path.join(static_path, 'js')

            directories = {
                'static': static_path,
                'templates': templates_path,
                'css': css_dir,
                'js': js_dir,
                'media': media_path
            }

            return directories
        except Exception as e:
            logging.error(f"Error while getting directories for app {app}: {e}")
            return {}

    def identify_static_files(self):
        static_files = []
        for app in self.apps:
            static_dir = os.path.join(self.project_path, app, 'static', app)
            if os.path.exists(static_dir):
                for root, _, files in os.walk(static_dir):
                    for file in files:
                        if file.endswith('.css') or file.endswith('.js'):
                            file_path = os.path.join(root, file)
                            static_files.append(file_path)
                            self.print_confirmation(f"Found static file: {file_path}")
            else:
                self.print_alert(f"Static directory missing for app '{app}'")
        return static_files

    def identify_urls_file(self):
        urls_files = []
        for app in self.apps:
            urls_file_path = os.path.join(self.project_path, app, 'urls.py')
            if os.path.exists(urls_file_path):
                urls_files.append(urls_file_path)
                self.print_confirmation(f"Found URLs file: {urls_file_path}")
            else:
                self.print_alert(f"URLs file 'urls.py' missing for app '{app}'")
        return urls_files

    def identify_settings_file(self):
        settings_files = []
        settings_file_path = os.path.join(self.project_path, 'settings.py')
        if os.path.exists(settings_file_path):
            settings_files.append(settings_file_path)
            self.print_confirmation(f"Found Settings file: {settings_file_path}")
        else:
            self.print_alert("Settings file 'settings.py' missing in project root.")
        return settings_files

    def organize_apps(self):
        apps_data = []
        for app in self.apps:
            app_data = {
                'app_name': app,
                'pages': self.get_pages(app),
                # Add more components as needed
            }
            apps_data.append(app_data)
        return apps_data

    def get_pages(self, app):
        try:
            app_path = os.path.join(self.project_path, app)
            templates_path = os.path.join(app_path, 'templates', app)

            pages = []
            if os.path.exists(templates_path):
                for root, _, files in os.walk(templates_path):
                    for file in files:
                        if file.endswith('.html'):
                            page_name = os.path.splitext(file)[0]
                            pages.append(page_name)
                            self.print_confirmation(f"Found HTML page: {os.path.join(root, file)}")
            return pages
        except Exception as e:
            logging.error(f"Error while getting pages for app {app}: {e}")
            return []

def main():
    parser = argparse.ArgumentParser(description="Identify Django project apps and components.")
    parser.add_argument('project_path', metavar='PATH', type=str, nargs='?', help='Path to the Django project')
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    if args.project_path:
        project_path = args.project_path
    else:
        project_path = input("Enter the path to your Django project: ")

    if not os.path.exists(project_path):
        logging.error("The provided path does not exist.")
        return

    identifier = Identifier(project_path)

    logging.info(f"Project Path: {identifier.project_path}")
    logging.info(f"Apps: {identifier.apps}")

    # Organize apps data
    apps_data = identifier.organize_apps()
    logging.info(f"\nOrganized Apps Data:")
    for app_data in apps_data:
        logging.info(f"App Name: {app_data['app_name']}")
        logging.info(f"Pages: {app_data['pages']}")
        # Add more logging or processing for other components

    # Identify static files
    static_files = identifier.identify_static_files()
    logging.info(f"\nIdentified Static Files:")
    for file_path in static_files:
        logging.info(file_path)

    # Identify URLs files
    urls_files = identifier.identify_urls_file()
    logging.info(f"\nIdentified URLs Files:")
    for file_path in urls_files:
        logging.info(file_path)

    # Identify settings files
    settings_files = identifier.identify_settings_file()
    logging.info(f"\nIdentified Settings Files:")
    for file_path in settings_files:
        logging.info(file_path)

    # Alert for missing files
    for app in identifier.apps:
        missing_files = []
        directories = identifier.get_directories(app)
        expected_files = ['static', 'templates', 'media']
        for file_type in expected_files:
            if not os.path.exists(directories.get(file_type, '')):
                missing_files.append(file_type)
        
        if missing_files:
            logging.warning(f"Missing directories/files in app '{app}': {', '.join(missing_files)}")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")

# /home/elnamaki/Desktop/WorkingAgents/AS_args.py --project-name MyProject --app-name App1 App2 --page-names "home,about" "dashboard,profile" -y
