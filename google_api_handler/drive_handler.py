import os
from dataclasses import dataclass

from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive

default_permission_dict = {
    "type": "user",
    "value": "nagendrar@rideriver.com",
    "role": "reader",
}


@dataclass
class GooDriver:
    # GAuth

    gauth = GoogleAuth()

    creds = gauth.LoadCredentialsFile("mycreds.txt")

    if gauth.credentials is None:
        # 2. Authenticate if they don't exist (this opens the browser the first time)
        gauth.LocalWebserverAuth()
    elif gauth.access_token_expired:
        # 3. Refresh them if they are expired
        gauth.Refresh()
    else:
        # 4. Initialize the saved credentials
        gauth.Authorize()

    # 5. Save the current credentials to a file for the next run
    if not creds:
        gauth.SaveCredentialsFile("mycreds.txt")

    drive = GoogleDrive(gauth)

    def __prepare_metadata(self, name: str, drive_folder_id: str) -> dict:
        return {
            "title": name,
            "parents": [{"kind": "drive#fileLink", "id": drive_folder_id}],
        }

    def __upload(
        self,
        path: str,
        name: str,
        metadata: dict,
        permission: dict = default_permission_dict,
    ) -> None:
        fh = self.drive.CreateFile(metadata)
        fh.SetContentFile(os.path.join(path, name))
        fh.Upload()
        # Set file permission
        fh.InsertPermission(permission)
        current_permissions = fh.GetPermissions()
        # Cleaning instance
        fh = None

    def upload_files(
        self,
        file_path: str,
        file_name: list,
        file_permission: dict = default_permission_dict,
    ) -> None:
        for file in file_name:
            if os.path.exists(os.path.join(file_path, file)):
                metadata = {"title": file}
                self.__upload(file_path, file, metadata, file_permission)
            else:
                raise FileNotFoundError(
                    f"The following file: {file} does not exist in the following path: {file_path}"
                )

    def upload_folder(
        self,
        file_path: str,
        folder_name: str,
        file_permission: dict = default_permission_dict,
    ) -> None:
        if os.path.exists(file_path):
            folder_data = {
                "title": folder_name,
                "mimeType": "application/vnd.google-apps.folder",
            }
            folder = self.drive.CreateFile(folder_data)
            folder.Upload()
            for file in os.listdir(file_path):
                metadata = self.__prepare_metadata(file, folder["id"])
                self.__upload(file_path, file, metadata, file_permission)
        else:
            raise FileNotFoundError(f"The following path does not exist: {file_path}")

    def list_all_files(self, query: str) -> list:
        return self.drive.ListFile({"q": query}).GetList()


if __name__ == "__main__":
    permission_dict = {
        "type": "user",
        "value": "vehicle_software@rideriver.com",
        "role": "writer",
    }
    a = GooDriver()

    # Scan for a certain folder name
    query = "title = 'Gen 2.5 CYCLING DATA'and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
    a.list_all_files(query)
    # a.upload_files(r"C:\Users\Nagendra R\Documents\river_dev\Reporter\goobe", ["rare_file.txt", "rare_file2.py"])
    # a.upload_folder(r"C:\Users\Nagendra R\Documents\river_dev\Reporter\goobe", 'maha_goobe')
