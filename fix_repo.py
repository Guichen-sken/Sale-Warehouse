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

# 从main分支获取原有文件
print("=== 从main分支获取 README.md ===")
result = run("git show main:README.md")
if result.returncode == 0:
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(result.stdout)
    print("✅ README.md 已恢复")

print("\n=== 从main分支获取 typo-capsule ===")
# 先检查main分支是否有这个文件夹
result = run("git ls-tree -r main --name-only | findstr typo-capsule")
if result.stdout.strip():
    # 恢复整个文件夹
    run("git checkout main -- typo-capsule")
    print("✅ typo-capsule/ 已恢复")
else:
    print("❌ main分支没有typo-capsule文件夹")

print("\n=== 检查恢复后的文件 ===")
for item in os.listdir("."):
    print(f"  {item}")

print("\n=== 提交恢复的文件 ===")
run("git add -A")
run('git commit -m "fix: 恢复README.md和typo-capsule文件夹"')
run("git push origin master:creative")

print("\n✅ 完成！")
