import os
import time
import typer
import subprocess
from banyan.api import BanyanApiClient

app = typer.Typer()

# Constants for API URLs
API_URLS = {
    "net": "https://net.banyanops.com",
    "release": "https://release.bnntest.com",
    "preview": "https://preview.console.banyanops.com",
}


# Function to generate a folder name or use the provided one
def get_folder_name(folder):
    folder_name = folder
    if not folder:
        folder_name = str(int(time.time()))
    os.makedirs("%s" % folder_name, exist_ok=True)
    return folder_name


# Function to get the API URL based on the console choice
def get_api_url(console):
    return API_URLS.get(console.lower(), console.lower())


# Function to initialize the Banyan API client
def initialize_api(api_key, api_url):
    return BanyanApiClient(api_url=api_url, api_key=api_key)


# Function to import resources and execute Terraform plan
def import_and_plan(api, resource, resource_type, folder_name, separate_files):
    resources = get_resources(api, resource, resource_type)
    if len(resources) <= 0:
        print(f"No {resource.capitalize()} found.")
        return

    print(f"Importing {resource.capitalize()}....")

    if separate_files:
        # separate files for each resource
        for item in resources:
            import_statement = f'import {{ \n to = banyan_{resource}_{resource_type}.{str(item.name).replace(".", "-").lower()}\n id = "{item.id}" \n}}\n'
            create_import_file([import_statement], folder_name, "import.tf")
            execute_terraform_plan(folder=folder_name, file_name=f"{str(item.name).replace('.', '-').lower()}.tf")
    else:
        # single file for all resources
        # Create a list to hold import statements
        import_statements = []

        for item in resources:
            import_statements.append(f'import {{ \n to = banyan_{resource}_{resource_type}.{str(item.name).replace(".", "-").lower()}\n id = "{item.id}" \n}}\n')

        # Write all import statements to a single import.tf file
        create_import_file(import_statements, folder_name, "import.tf")

        # Call execute_terraform_plan once with fixed file name generated.tf
        execute_terraform_plan(folder=folder_name, file_name="generated.tf")

    print("Done")


def get_resources(api, resource, resource_type):
    valid_resource_types = get_valid_resource_type(api)
    valid_types = valid_resource_types.get(resource.lower())
    if valid_types is None:
        raise Exception("Invalid input for resource")
    api_function = valid_types.get(resource_type.lower())
    if api_function is None:
        raise Exception(f"Invalid input resource_type for resource {resource}")
    resources = api_function()
    return resources


def get_valid_resource_type(api):
    valid_resource_types = {
        "service": {
            "web": api.services_web.list,
            "db": api.services_infra.list,
            "k8s": api.services_infra.list,
            "rdp": api.services_infra.list,
            "ssh": api.services_infra.list,
            "tcp": api.services_infra.list,
            "tunnel": api.service_tunnels.list,
        },
        "policy": {
            "infra": api.policies.list,
            "tunnel": api.policies.list,
            "web": api.policies.list,
        },
        "role": {
            "": api.roles.list,
        },
    }
    return valid_resource_types


# Function to execute Terraform plan
def execute_terraform_plan(folder, file_name):
    terraform_command = f"terraform -chdir={folder} plan -generate-config-out={file_name}"
    try:
        subprocess.run(terraform_command, shell=True, check=True)
        print("Terraform command executed successfully.")
    except subprocess.CalledProcessError as e:
        raise Exception(f"Error executing Terraform command: {e}")


# Function to execute Terraform initialization
def execute_terraform_init(host, api_key, folder):
    terraform_template = f'''
terraform {{
  required_providers {{
    banyan = {{
      source = "banyansecurity/banyan"
      version = "1.2.5"
    }}
  }}
}}

provider "banyan" {{
  host    = "{host}"
  api_key = "{api_key}"
}}
'''
    formatted_content = terraform_template
    if not os.path.exists(f"{folder}/main.tf"):
        with open(f"{folder}/main.tf", "w") as file:
            file.write(formatted_content)
            file.write("\n")
    terraform_command = f"terraform -chdir={folder} init"
    try:
        subprocess.run(terraform_command, shell=True, check=True)
        print("Terraform command executed successfully.")
    except subprocess.CalledProcessError as e:
        raise Exception(f"Error executing Terraform command: {e}")


# Function to create an import file
def create_import_file(import_statements, folder, file_name):
    content_template = '\n'.join(import_statements)
    with open(f"{folder}/{file_name}", "w") as file:
        file.write(content_template)
        file.write("\n")


@app.command()
def main(api_key: str, resource="service", resource_type="", console="net", folder="", separate_files: bool = False):
    folder_name = get_folder_name(folder)
    api_url = get_api_url(console)
    api = initialize_api(api_key, api_url)
    execute_terraform_init(host=api_url, api_key=api_key, folder=folder_name)
    import_and_plan(api, resource, resource_type, folder_name, separate_files)


if __name__ == "__main__":
    app()