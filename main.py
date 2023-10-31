import json
import os
import typer
import subprocess
import glob
from banyan.api import BanyanApiClient

app = typer.Typer()

# Constants for API URLs
API_URLS = {
    "net": "https://net.banyanops.com",
    "release": "https://release.bnntest.com",
    "preview": "https://preview.console.banyanops.com",
}


def get_log_file(folder_prefix):
    return f"{folder_prefix}/terraform_command.logs"


# Function to generate a folder name or use the provided one
def get_folder_name(folder):
    folder_name = folder
    if not folder:
        folder_name = "default"
    os.makedirs("%s" % folder_name, exist_ok=True)
    return folder_name


def concat_files(names: list, folder: str):
    for name in names:
        read_files = glob.glob(f"{folder}/{name}_*.tf")
        with open(f"{folder}/{name}.tf", "wb") as outfile:
            for f in read_files:
                with open(f, "rb") as infile:
                    outfile.write(infile.read())
                os.remove(f)


# Function to get the API URL based on the console choice
def get_api_url(console):
    return API_URLS.get(console.lower(), console.lower())


# Function to initialize the Banyan API client
def initialize_api(api_key, api_url):
    return BanyanApiClient(api_url=api_url, api_key=api_key)


# Function to import resources and execute Terraform plan
def import_and_plan(api, resource, resource_type, folder_name, module:bool = False):
    resources = get_resources(api, resource, resource_type)
    if len(resources) <= 0:
        print(f"No resource {resource.upper()} of type {resource_type.upper()} found.")
        return
    print(f"Found {len(resources)} {resource.upper()} of type {resource_type.upper()}")
    print(f"Importing {resource.upper()} of type {resource_type.upper()}....")

    # collect all passed import statements into a list
    import_statements = []
    # separate files for each resource
    os.makedirs(f"{folder_name}/separate_resources", exist_ok=True)
    my_resource_import = f'{resource}_{resource_type}'
    if resource == "role":
        my_resource_import = "role"

    for item in resources:
        resource_name = get_resource_name(item.name)
        import_statement = f'import {{ \n to = banyan_{my_resource_import}.{resource_name}\n id = "{item.id}" \n}}\n'
        create_import_file([import_statement], f"{folder_name}", "import.tf")
        try:
            execute_terraform_plan(folder=f"{folder_name}", file_name=f"{resource_name}.tf")
            import_statements.append(import_statement)
            os.replace(f"{folder_name}/{resource_name}.tf", f"{folder_name}/separate_resources/{resource_name}.tf")
        except Exception as e:
            # write errors exports to file
            with open(f"{folder_name}/failed_imports.txt", "a") as file:
                content = f"Failed {resource_name} with error: {e}\n"
                file.write(content)
            print(
                f".....[WARN] Error exporting resource {resource_name} error: {e}. REFER: {folder_name}/failed_imports.txt and {folder_name}/terraform_command.logs for reasons.")
    # delete import.tf file which could have last entry
    os.remove(f"{folder_name}/import.tf")
    # Write all import statements to a single import.tf file
    create_import_file(import_statements, folder_name, f"import_{my_resource_import}.tf")
    # Call execute_terraform_plan once with fixed file name generated.tf
    execute_terraform_plan(folder=folder_name, file_name=f"generated_{my_resource_import}.tf")

    create_import_file(import_statements, folder_name, f"import_{my_resource_import}.tf", module=module)

    print(
        f"---------------Finished importing {len(resources)} {resource.upper()} of type {resource_type.upper()}--------------------")


def get_resource_name(name):
    resource_name = (str(name).replace(".", "-").replace(" ", "-").
                     replace("/", "-").replace(":", "-").lower())
    return resource_name


def get_filtered_infra_services(resources, resource_type):
    return [service for service in resources if
            str(service.service_spec.metadata.tags.service_app_type).lower() == resource_type.lower()]


def get_filtered_policies(resources, resource_type):
    filtered_resources = []

    for policy in resources:
        my_policy_spec = json.loads(policy.spec)
        access = (my_policy_spec["spec"])["access"]
        options = {}
        l7_protocol = ""
        disable_tls_client_authentication = False

        if "options" in dict(my_policy_spec["spec"]).keys():
            options = (my_policy_spec["spec"])["options"]
            l7_protocol = str(options["l7_protocol"]).lower()
            disable_tls_client_authentication = bool(options["disable_tls_client_authentication"])

        if resource_type.lower() == "web" and disable_tls_client_authentication and l7_protocol == "http":
            filtered_resources.append(policy)
        elif resource_type.lower() == "infra" and len(
                options) > 1 and not disable_tls_client_authentication and l7_protocol == "":
            appended = False
            for access_item in access:
                if ("l4_access" not in dict(access_item["rules"]).keys()
                        and "l7_access" in dict(access_item["rules"]).keys() and not appended):
                    filtered_resources.append(policy)
                    appended = True
        elif resource_type.lower() == "tunnel" and len(options) == 0:
            appended = False
            for access_item in access:
                if "options" not in dict(my_policy_spec["spec"]).keys() and "l4_access" in dict(
                        access_item["rules"]) and "l7_access" not in dict(access_item["rules"]).keys() and not appended:
                    filtered_resources.append(policy)
                    appended = True

    return filtered_resources


def get_resources(api, resource, resource_type):
    valid_resource_types = get_valid_resource_type(api)
    valid_types = valid_resource_types.get(resource.lower())
    if valid_types is None:
        raise Exception("Invalid input for resource")
    api_function = valid_types.get(resource_type.lower())
    if api_function is None:
        raise Exception(f"Invalid input resource_type for resource {resource}")
    resources = api_function()
    if resource.lower() == "service" and resource_type.lower() != "web" and resource_type.lower() != "tunnel":
        resources = get_filtered_infra_services(resources, resource_type)
    elif resource.lower() == "policy":
        resources = get_filtered_policies(resources, resource_type)

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
            # "tunnel": api.service_tunnels.list,
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
        with open(get_log_file(folder), 'a') as file:
            subprocess.run(terraform_command, encoding='utf-8', stdout=file, stderr=file, shell=True, check=True)
        if "generated_" not in file_name:
            print(f".....Terraform command executed successfully for {str(file_name).replace('.tf', '')}.")
    except subprocess.CalledProcessError as e:
        raise Exception(f".....Error executing Terraform command: {e}")


# Function to execute Terraform initialization
def execute_terraform_init(host, api_key, folder):
    terraform_template = f'''
terraform {{
  required_providers {{
    banyan = {{
      source = "banyansecurity/banyan"
      version = "1.2.6"
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
        with open(get_log_file(folder), 'w') as file:
            subprocess.run(terraform_command, encoding='utf-8', stdout=file, stderr=file, shell=True, check=True)
        print(f"Terraform init executed successfully.")
    except subprocess.CalledProcessError as e:
        raise Exception(f".....Error executing Terraform command: {e}")


# Function to create an import file
def create_import_file(import_statements: list, folder, file_name, module: bool = False):
    if module is True:
        new_import_statements = []
        for each_import in import_statements:
            each_import = each_import.replace("to = banyan_", f"to = module.{folder}.banyan_")
            new_import_statements.append(each_import)
        import_statements = new_import_statements
    content_template = '\n'.join(import_statements)
    with open(f"{folder}/{file_name}", "w") as file:
        file.write(content_template)
        file.write("\n")


@app.command()
def main(api_key: str, resource="service", resource_type="", console="net", folder="", module: bool = False):
    folder_name = get_folder_name(folder)
    api_url = get_api_url(console)
    api = initialize_api(api_key, api_url)
    execute_terraform_init(host=api_url, api_key=api_key, folder=folder_name)
    if resource == "all":
        for my_resource in ["service", "policy", "role"]:
            if my_resource == "service":
                for my_resource_type in ["web", "db", "k8s", "rdp", "ssh", "tcp"]:
                    import_and_plan(api, "service", my_resource_type, folder_name, module)
            if my_resource == "policy":
                for my_resource_type in ["infra", "tunnel", "web"]:
                    import_and_plan(api, "policy", my_resource_type, folder_name, module)
            if my_resource == "role":
                import_and_plan(api, "role", "", folder_name, module)
    elif resource == "service" and resource_type == "all":
        for my_resource_type in ["web", "db", "k8s", "rdp", "ssh", "tcp"]:
            import_and_plan(api, "service", my_resource_type, folder_name, module)
    elif resource == "policy" and resource_type == "all":
        for my_resource_type in ["infra", "tunnel", "web"]:
            import_and_plan(api, "policy", my_resource_type, folder_name, module)
    elif resource == "role" and resource_type == "all":
        import_and_plan(api, "role", "", folder_name, module)
    else:
        import_and_plan(api, resource, resource_type, folder_name, module)

    # combine seperated resource files into a single file
    concat_files(["generated", "import"], folder_name)


if __name__ == "__main__":
    app()
