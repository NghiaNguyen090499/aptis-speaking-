# Aptis Speaking Practice Platform

Hệ thống luyện thi Aptis Speaking với xác thực người dùng và lưu trữ dữ liệu trên Firebase.

## Yêu cầu hệ thống

- Python 3.7+
- Firebase account
- AWS account (để deploy)

## Cài đặt

1. Clone repository:
```bash
git clone <repository-url>
cd aptis-speaking
```

2. Tạo môi trường ảo và cài đặt dependencies:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

3. Tạo file `.env` và cấu hình các biến môi trường:
```
SECRET_KEY=your-secret-key-here
FLASK_ENV=development
FLASK_APP=app.py
```

4. Tạo project trên Firebase Console và tải file credentials:
- Truy cập Firebase Console
- Tạo project mới
- Vào Project Settings > Service Accounts
- Tải file credentials JSON
- Đổi tên file thành `firebase-credentials.json` và đặt trong thư mục gốc của project

## Chạy ứng dụng

1. Chạy server phát triển:
```bash
flask run
```

2. Truy cập ứng dụng tại `http://localhost:5000`

## Deploy lên AWS

1. Tạo EC2 instance:
- Chọn Amazon Linux 2 AMI
- Cấu hình Security Group để mở port 80 và 443
- Tạo key pair để SSH

2. Cài đặt dependencies trên EC2:
```bash
sudo yum update -y
sudo yum install python3 python3-pip git -y
```

3. Clone và cài đặt ứng dụng:
```bash
git clone <repository-url>
cd aptis-speaking
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

4. Cấu hình Gunicorn:
```bash
pip install gunicorn
```

5. Tạo service file:
```bash
sudo nano /etc/systemd/system/aptis-speaking.service
```

Thêm nội dung:
```ini
[Unit]
Description=Gunicorn instance to serve aptis speaking
After=network.target

[Service]
User=ec2-user
Group=ec2-user
WorkingDirectory=/home/ec2-user/aptis-speaking
Environment="PATH=/home/ec2-user/aptis-speaking/venv/bin"
ExecStart=/home/ec2-user/aptis-speaking/venv/bin/gunicorn --workers 3 --bind 0.0.0.0:8000 app:app

[Install]
WantedBy=multi-user.target
```

6. Khởi động service:
```bash
sudo systemctl start aptis-speaking
sudo systemctl enable aptis-speaking
```

7. Cấu hình Nginx:
```bash
sudo yum install nginx -y
sudo nano /etc/nginx/conf.d/aptis-speaking.conf
```

Thêm nội dung:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

8. Khởi động Nginx:
```bash
sudo systemctl start nginx
sudo systemctl enable nginx
```

## Tính năng

- Đăng ký và đăng nhập người dùng
- Lưu trữ câu trả lời trên Firebase
- Giao diện responsive
- Dark mode
- Text-to-speech cho các bài mẫu
- Export/Import câu trả lời

## Bảo mật

- Mật khẩu được mã hóa trước khi lưu trữ
- Sử dụng HTTPS
- Xác thực người dùng với Flask-Login
- Bảo vệ các route với @login_required

## Đóng góp

Mọi đóng góp đều được hoan nghênh! Vui lòng tạo issue hoặc pull request để đóng góp.
