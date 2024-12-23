import requests

# URL của tệp SQL
url = "https://raw.githubusercontent.com/lerocha/chinook-database/master/ChinookDatabase/DataSources/Chinook_Sqlite.sql"

# Tên tệp muốn lưu
output_file = "Chinook_Sqlite.sql"

# Tải tệp
response = requests.get(url)
if response.status_code == 200:
    with open(output_file, "wb") as file:
        file.write(response.content)
    print(f"Tệp đã được tải xuống thành công: {output_file}")
else:
    print(f"Lỗi khi tải tệp. Mã trạng thái: {response.status_code}")