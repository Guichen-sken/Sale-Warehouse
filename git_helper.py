import subprocess
import os
import shutil

def run(cmd, cwd=r"D:\cursoc代码库\api"):
    print(f">>> {cmd}")
    result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print(f"ERR: {result.stderr}")
    return result.returncode == 0

# 1. 创建iqiyi-automation子文件夹
os.makedirs("iqiyi-automation", exist_ok=True)
os.makedirs("iqiyi-automation/screenshots", exist_ok=True)
os.makedirs("iqiyi-automation/videos", exist_ok=True)

# 2. 移动自动化相关文件到子文件夹
files_to_move = [
    "iqiyi_master_automation.py",
    "report_master.html",
    ".gitignore"
]

for f in files_to_move:
    if os.path.exists(f):
        shutil.move(f, f"iqiyi-automation/{f}")
        print(f"Moved: {f}")

# 3. 移动截图和视频
if os.path.exists("screenshots"):
    for f in os.listdir("screenshots"):
        shutil.move(f"screenshots/{f}", f"iqiyi-automation/screenshots/{f}")
    os.rmdir("screenshots")

if os.path.exists("videos"):
    for f in os.listdir("videos"):
        shutil.move(f"videos/{f}", f"iqiyi-automation/videos/{f}")
    os.rmdir("videos")

# 4. 从远程creative分支恢复原有文件
run("git fetch origin creative")
run("git checkout origin/creative -- typo-capsule README.md")

# 5. 添加所有更改
run("git add -A")

# 6. 提交
run('git commit -m "feat: 添加爱奇艺自动化测试到iqiyi-automation子文件夹\n\n- 恢复typo-capsule和README.md\n- 将自动化代码放入iqiyi-automation/子文件夹\n- 保留原有项目结构"')

# 7. 强制推送到creative分支
run("git push -f -u origin master:creative")

print("\n✅ 完成！")
