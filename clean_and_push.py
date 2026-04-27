import subprocess
import os
import shutil

def run(cmd, cwd=r"D:\cursoc代码库\api"):
    print(f">>> {cmd}")
    result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True, encoding='utf-8', errors='ignore')
    print(result.stdout)
    if result.stderr:
        print(f"ERR: {result.stderr}")
    return result

# 1. 删除非项目文件
files_to_remove = ["fix_repo.py", "git_helper.py", "README.md"]
for f in files_to_remove:
    if os.path.exists(f):
        os.remove(f)
        print(f"Removed: {f}")

# 2. 删除typo-capsule（如果存在）
if os.path.exists("typo-capsule"):
    shutil.rmtree("typo-capsule")
    print("Removed: typo-capsule/")

# 3. 确保iqiyi-automation文件夹存在
if not os.path.exists("iqiyi-automation"):
    print("ERROR: iqiyi-automation folder not found!")
    exit(1)

# 4. 检查本地文件
print("\n=== 当前文件 ===")
for item in os.listdir("."):
    print(f"  {item}")

# 5. 提交并推送
print("\n=== Git操作 ===")
run("git add -A")
run('git commit -m "chore: 清理分支，只保留iqiyi-automation项目"')
run("git push -f origin master:creative")

print("\n✅ 完成！creative分支现在只包含iqiyi-automation项目")
print("你可以去恢复原有文件了")
