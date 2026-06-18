# Hướng Dẫn Triển Khai Telegram GitHub Invitation Bot

Tài liệu này hướng dẫn chạy bot trên máy local. Bot nhận tin nhắn Telegram theo các format:

**Format cơ bản (mặc định role guest / pull):**

```text
github_username - owner/repo
```

**Format nhiều username cùng lúc:**

```text
user1,user2,user3 - owner/repo
```

**Format có chỉ định role:**

```text
github_username - owner/repo - role
user1,user2 - owner/repo - role
```

**Format có Telegram handle (ghi nhận ai yêu cầu mời):**

```text
@telegram_handle github_username - owner/repo
@telegram_handle user1,user2 - owner/repo - role
```

Ví dụ:

```text
octocat - tungnt/my-repo
octocat,hubot,defunkt - tungnt/my-repo
octocat - tungnt/my-repo - push
@johndoe octocat,hubot - tungnt/my-repo - push
```

### Bảng Role

| Role | Mô tả |
|------|--------|
| `pull` | Chỉ đọc (mặc định / guest) |
| `triage` | Quản lý issues và pull requests (chỉ org repo) |
| `push` | Đọc và ghi |
| `maintain` | Bảo trì repository (chỉ org repo) |
| `admin` | Toàn quyền admin |

Lưu ý: `triage` và `maintain` chỉ hoạt động trên repository thuộc **Organization**. Repo cá nhân chỉ hỗ trợ `pull`, `push`, `admin`.

Nếu không chỉ định role, mặc định là `pull` (guest / read-only). Nếu chỉ định role cụ thể, bot sẽ dùng role đó.

Bot dùng GitHub username để gọi GitHub REST API và mời user đó vào repository. GitHub cá nhân không hỗ trợ invite collaborator trực tiếp bằng email qua REST API, nên tool này không còn dùng email hoặc file mapping email.

## 1. Yêu Cầu Trước Khi Cài Đặt

Cần có:

- Python 3.12 hoặc mới hơn.
- Telegram bot token.
- Telegram group chat ID của group được phép dùng bot.
- GitHub fine-grained personal access token.
- Quyền admin trên repository GitHub cần mời collaborator.

## 2. Tạo Telegram Bot Token

1. Mở Telegram và tìm `@BotFather`.
2. Gửi lệnh:

```text
/newbot
```

3. Đặt tên bot và username cho bot theo hướng dẫn của BotFather.
4. Copy token BotFather trả về.
5. Gán token này vào biến `TELEGRAM_BOT_TOKEN` trong file `.env`.

Không commit token này lên git.

## 3. Lấy Telegram Group Chat ID

Bot chỉ nhận lệnh từ group/chat ID nằm trong `ALLOWED_TELEGRAM_CHAT_IDS`.

Các bước lấy group chat ID:

1. Thêm bot vào group Telegram.
2. Gửi một tin nhắn bất kỳ trong group.
3. Mở URL sau trên trình duyệt, thay `<TELEGRAM_BOT_TOKEN>` bằng token thật:

```text
https://api.telegram.org/bot<TELEGRAM_BOT_TOKEN>/getUpdates
```

4. Tìm trường `chat.id` trong response.
5. Group ID thường có dạng số âm, ví dụ `-1001234567890`.
6. Gán vào `.env`:

```env
ALLOWED_TELEGRAM_CHAT_IDS=-1001234567890
```

Nếu có nhiều group được phép dùng bot, cách nhau bằng dấu phẩy:

```env
ALLOWED_TELEGRAM_CHAT_IDS=-1001234567890,-1009876543210
```

Lưu ý: khi một group được allow, bất kỳ thành viên nào trong group đó cũng có thể gửi lệnh invite cho bot. Bot không nhận lệnh từ tin nhắn trực tiếp của user.

## 4. Tạo GitHub Token

Nên dùng fine-grained personal access token.

1. Vào GitHub Settings.
2. Mở Developer settings.
3. Chọn Personal access tokens.
4. Chọn Fine-grained tokens.
5. Tạo token mới.
6. Chọn repository mà bot được phép mời collaborator.
7. Cấp quyền repository:

```text
Administration: Read and write
```

8. Copy token và gán vào `.env`:

```env
GITHUB_TOKEN=github_pat_xxx
```

Không commit token này lên git.

## 5. Tạo Virtual Environment Và Cài Dependencies

Trong thư mục project:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Nếu dùng PowerShell và muốn activate venv:

```powershell
.\.venv\Scripts\Activate.ps1
```

Sau khi activate, có thể chạy:

```powershell
python -m pip install -r requirements.txt
```

## 6. Tạo File Cấu Hình `.env`

Copy file mẫu:

```powershell
copy .env.example .env
```

Nội dung `.env` cần có:

```env
TELEGRAM_BOT_TOKEN=your-telegram-token
GITHUB_TOKEN=your-github-token
ALLOWED_TELEGRAM_CHAT_IDS=-1001234567890
ALLOWED_TELEGRAM_USER_IDS=
DEFAULT_PERMISSION=pull
GITHUB_API_VERSION=2022-11-28
LOG_LEVEL=INFO
LOG_BACKUP_COUNT=30
LOG_ROTATION_INTERVAL_DAYS=1
```

Giải thích:

- `TELEGRAM_BOT_TOKEN`: token từ BotFather.
- `GITHUB_TOKEN`: GitHub personal access token.
- `ALLOWED_TELEGRAM_CHAT_IDS`: danh sách Telegram group/chat ID được phép dùng bot.
- `ALLOWED_TELEGRAM_USER_IDS`: danh sách Telegram user ID được phép dùng bot.
- `DEFAULT_PERMISSION`: quyền collaborator mặc định khi không chỉ định role trong tin nhắn. Giá trị mặc định là `pull` (guest / read-only).
- `GITHUB_API_VERSION`: version GitHub REST API.
- `LOG_LEVEL`: mức log, mặc định `INFO`.
- `LOG_BACKUP_COUNT`: Số lượng file log cũ muốn giữ lại (mặc định 30). Đặt 0 nếu không muốn xoá.
- `LOG_ROTATION_INTERVAL_DAYS`: Chu kỳ xoay file log và dọn dẹp tính bằng ngày (mặc định 1).

Giá trị hợp lệ cho `DEFAULT_PERMISSION`:

```text
pull, triage, push, maintain, admin
```

> **Lưu ý:** Việc chỉ định role cụ thể chỉ áp dụng cho các kho lưu trữ (repository) thuộc tổ chức hoặc doanh nghiệp (Organization/Enterprise). Đối với các dự án cá nhân (dù là public hay private), GitHub không hỗ trợ phân chia role mà chỉ có duy nhất một mức quyền Collaborator chung. Khi làm việc với dự án cá nhân, việc truyền role có thể bị bỏ qua hoặc gây ra lỗi từ phía API.

Khuyến nghị giữ `pull` (guest) nếu không có nhu cầu khác. Khi gửi tin nhắn mời mà không kèm role, bot sẽ dùng giá trị `DEFAULT_PERMISSION` trong `.env`.

## 7. Chạy Test

Chạy test trước khi start bot:

```powershell
.\.venv\Scripts\python.exe -m pytest -v -p no:cacheprovider
```

## 8. Chạy Bot Local

Chạy lệnh:

```powershell
.\.venv\Scripts\python.exe -m src.bot
```

Bot sẽ bắt đầu polling Telegram. Trong group đã cấu hình, nhắn:

```text
/start
```

Bot sẽ trả về hướng dẫn format.

### 8.1. Mời 1 Collaborator Với Role Mặc Định (guest / pull)

Gửi tin nhắn:

```text
octocat - owner/repository-name
```

Bot sẽ mời `octocat` vào repo `owner/repository-name` với quyền `pull` (guest / read-only).

### 8.2. Mời Nhiều Collaborator Cùng Lúc

Liệt kê nhiều username cách nhau bằng dấu phẩy:

```text
octocat,hubot,defunkt - owner/repository-name
```

Bot sẽ mời từng user và trả về kết quả cho từng người:

```text
Ket qua moi vao repo owner/repository-name voi role pull:
✅ octocat: Da gui loi moi
✅ hubot: Da gui loi moi
❌ defunkt: Khong tim thay repo/user hoac GitHub token khong co quyen truy cap repo nay.
```

Nếu một user bị lỗi, các user khác vẫn được mời bình thường. Lỗi sẽ được ghi vào file log.

### 8.3. Mời Với Role Cụ Thể

Thêm role vào cuối tin nhắn:

```text
octocat - owner/repository-name - push
octocat,hubot - owner/repository-name - push
```

Bot sẽ mời với quyền `push` (read & write) thay vì `pull` mặc định.

Các role hợp lệ: `pull`, `triage`, `push`, `maintain`, `admin`.

### 8.4. Ghi Nhận Telegram Handle Của Người Mời

Thêm `@telegram_handle` vào đầu tin nhắn để bot ghi nhận ai yêu cầu mời:

```text
@johndoe octocat - owner/repository-name
@johndoe octocat,hubot - owner/repository-name - push
```

Bot sẽ hiển thị thông tin Telegram handle trong phản hồi.

Telegram handle là tuỳ chọn, không bắt buộc.

## 9. File Log Lỗi

Bot tự động ghi log lỗi vào file `logs/bot.log` trong thư mục project. File log ghi nhận:

- Thời gian lỗi
- Username bị lỗi
- Repository
- Role đang dùng
- Telegram handle (nếu có)
- Nội dung lỗi chi tiết

Ví dụ nội dung file log:

```text
2026-06-18 10:30:15,123 ERROR src.bot: Invite FAILED | user=defunkt | repo=owner/repo | role=pull | tele=johndoe | error=Khong tim thay repo/user hoac GitHub token khong co quyen truy cap repo nay.
```

Vị trí file log:

- **Local**: `logs/bot.log` (tương đối từ thư mục project)
- **Docker**: xem log bằng `docker compose logs -f github-invite-bot`, hoặc mount volume cho thư mục `logs/` nếu muốn giữ file log bên ngoài container

Để mount volume log khi dùng Docker, thêm vào `docker-compose.yml`:

```yaml
services:
  github-invite-bot:
    volumes:
      - ./logs:/app/logs
```

## 10. Triển Khai Bằng Docker Trên VPS

### 10.1. Cài Docker Trên VPS

Trên Ubuntu/Debian, cài Docker theo tài liệu chính thức của Docker hoặc dùng package manager của hệ điều hành. Sau khi cài, kiểm tra:

```bash
docker --version
docker compose version
```

### 10.2. Đưa Source Code Lên VPS

Copy project lên VPS bằng `git clone`, `scp`, hoặc công cụ deploy bạn đang dùng. Ví dụ:

```bash
git clone <repo-url>
cd tools_auto_accept_email_github
```

Nếu chưa dùng git, có thể upload toàn bộ thư mục project lên VPS, nhưng không upload `.env` qua nơi không an toàn.

### 10.3. Tạo File `.env` Trên VPS

Trên VPS, tạo `.env` từ file mẫu:

```bash
cp .env.example .env
nano .env
```

Nội dung cần có:

```env
TELEGRAM_BOT_TOKEN=your-telegram-token
GITHUB_TOKEN=your-github-token
ALLOWED_TELEGRAM_CHAT_IDS=-1001234567890
ALLOWED_TELEGRAM_USER_IDS=
DEFAULT_PERMISSION=pull
GITHUB_API_VERSION=2022-11-28
LOG_LEVEL=INFO
LOG_BACKUP_COUNT=30
LOG_ROTATION_INTERVAL_DAYS=1
```

Không commit `.env` và không copy token vào Dockerfile hoặc `docker-compose.yml`.

### 10.4. Build Và Chạy Container

Chạy:

```bash
docker compose up -d --build
```

Kiểm tra container:

```bash
docker compose ps
```

Xem log:

```bash
docker compose logs -f github-invite-bot
```

Không paste output của `docker compose config` lên chat hoặc ticket public, vì lệnh đó có thể in ra toàn bộ biến môi trường trong `.env`, bao gồm Telegram token và GitHub token.

Nếu bot chạy đúng, vào group Telegram đã cấu hình và nhắn:

```text
/start
```

Sau đó gửi lệnh invite:

```text
octocat - owner/repository-name
octocat,hubot - owner/repository-name - push
@johndoe octocat,hubot - owner/repository-name
```

### 10.5. Restart, Stop, Update

Restart bot:

```bash
docker compose restart github-invite-bot
```

Dừng bot:

```bash
docker compose down
```

Sau khi cập nhật code:

```bash
docker compose up -d --build
```

### 10.6. Lưu Ý Khi Chạy Docker

- Bot dùng Telegram polling nên không cần mở port inbound trên VPS.
- VPS chỉ cần outbound internet để gọi Telegram API và GitHub API.
- Container chạy bằng user non-root.
- Container đọc `.env` lúc start; sửa `.env` xong cần restart container.
- `restart: unless-stopped` giúp bot tự chạy lại sau reboot hoặc crash.
- Mount thư mục `logs/` ra ngoài container nếu cần xem file log lỗi.

## 11. Kết Quả Mong Đợi

### Mời 1 user thành công:

```text
Ket qua moi vao repo owner/repository-name voi role pull:
✅ octocat: Da gui loi moi
```

### Mời nhiều user, có lỗi:

```text
Ket qua moi vao repo owner/repository-name voi role push: (Telegram: @johndoe)
✅ octocat: Da gui loi moi
✅ hubot: Da co quyen hoac quyen da duoc cap nhat
❌ defunkt: Khong tim thay repo/user hoac GitHub token khong co quyen truy cap repo nay.
```

### User đã có quyền:

```text
Ket qua moi vao repo owner/repository-name voi role pull:
✅ octocat: Da co quyen hoac quyen da duoc cap nhat
```

### Role không hợp lệ:

```text
Role khong hop le. Gia tri hop le: pull, triage, push, maintain, admin.
```

### Token thiếu quyền:

```text
Ket qua moi vao repo owner/repository-name voi role pull:
❌ octocat: Khong the gui loi moi. GitHub token co the thieu quyen admin/write cho repo hoac policy cua repo/org dang chan invite.
```

## 12. Lỗi Thường Gặp

### Sai format tin nhắn

Dùng một trong các format sau:

```text
github_username - owner/repo
user1,user2 - owner/repo
github_username - owner/repo - role
@telegram_handle user1,user2 - owner/repo - role
```

Ví dụ:

```text
octocat - tungnt/my-repo
octocat,hubot - tungnt/my-repo - push
@johndoe octocat - tungnt/my-repo
```

Không dùng URL GitHub:

```text
octocat - https://github.com/tungnt/my-repo
```

### Role không hợp lệ

Chỉ dùng các role: `pull`, `triage`, `push`, `maintain`, `admin`.

Lưu ý: `triage` và `maintain` chỉ hoạt động trên repo thuộc Organization. Repo cá nhân chỉ hỗ trợ `pull`, `push`, `admin`.

### Một số user mời thất bại trong danh sách

Khi mời nhiều user cùng lúc, nếu một user bị lỗi, các user khác vẫn được xử lý bình thường. Kiểm tra:

- Username có đúng chính tả không
- User đó có tồn tại trên GitHub không
- Xem file `logs/bot.log` để biết chi tiết lỗi

### GitHub username không đúng

Kiểm tra username bằng cách mở profile:

```text
https://github.com/octocat
```

Nếu profile không tồn tại hoặc username sai, GitHub API sẽ từ chối request.

### GitHub token không mời được collaborator

Kiểm tra:

- Token còn hạn hay không.
- Token có access đúng repository hay không.
- Token có `Administration: Read and write` hay không.
- Bạn có quyền admin trên repo hay không.
- Repository owner/repo có đúng chính tả hay không.

### Telegram group bị từ chối

Kiểm tra Telegram group chat ID có nằm trong `.env` hay không:

```env
ALLOWED_TELEGRAM_CHAT_IDS=-1001234567890
```

### Container chạy nhưng bot không phản hồi

Kiểm tra:

- `.env` có đúng `TELEGRAM_BOT_TOKEN` không.
- Bot đã được thêm vào đúng group chưa.
- `ALLOWED_TELEGRAM_CHAT_IDS` có đúng group chat ID chưa.
- VPS có outbound internet không.
- Log container có lỗi gì không:

```bash
docker compose logs -f github-invite-bot
```

## 13. Lưu Ý Bảo Mật

- Không commit `.env`.
- Không gửi token qua chat.
- Không log token.
- Không đưa token vào Dockerfile hoặc image.
- Không chia sẻ output của `docker compose config` nếu compose đang đọc `.env` thật.
- Chỉ thêm Telegram group thật sự được phép sử dụng bot.
- Khi allow group, mọi thành viên trong group đó đều có thể gửi lệnh cho bot.
- Bot không nhận lệnh từ tin nhắn trực tiếp của user.
- Nên để `DEFAULT_PERMISSION=pull` (guest / read-only) nếu chỉ cần mời collaborator đọc repo.
- Nếu nghi token bị lộ, revoke token trên GitHub và BotFather, sau đó tạo token mới.
- Khi chỉ định role `admin` hoặc `maintain`, hãy cẩn thận vì user được mời sẽ có quyền cao trên repo.
- File log (`logs/bot.log`) không ghi token, chỉ ghi thông tin lỗi invite.
