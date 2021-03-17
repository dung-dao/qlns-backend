# Build development with cài đặt theo gói

**Cài đặt thư viện cần thiết bằng lệnh:**
pip install -r requirements.txt

**Chạy migrate database:**
python manage.py migrate

**Chạy lệnh tạo admin user:**
python manage.py createsuperuser

**Chạy compilemessages nếu có:**
python manage.py compilemessages

**Chạy lệnh gom file static về thu mục static:**
python manage.py collectstatic


# Build development with docker.

Pull source code from gitlab

Rename file setting.example.py thành setting.py

Vào thư mục gốc của dự án đã clone về.
**Chạy lệnh bên dưới:**
docker-compose up --build -d 

**Sau đó chạy lênh migrate dữ liệu:**
docker-compose run web python manage.py migrate

**Chạy lệnh tạo user admin:**
docker-compose run web python manage.py createsuperuser

**Vào trình duyệt để kiểm tra:**
localhost:8000


