import subprocess
import os

def run(cmd, cwd=r"D:\cursoc代码库\api"):
    print(f">>> {cmd}")
    result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True, encoding='utf-8', errors='ignore')
    print(result.stdout)
    if result.stderr:
        print(f"ERR: {result.stderr}")
    return result

# 获取远程所有分支的commit
print("=== 获取远程分支信息 ===")
run("git fetch origin")

print("\n=== 检查所有远程分支 ===")
run("git branch -r")

print("\n=== 尝试从其他分支恢复文件 ===")
# 尝试从 sold/for-sale/main 分支获取
branches = ["origin/main", "origin/sold", "origin/for-sale"]
for branch in branches:
    print(f"\n--- 检查 {branch} ---")
    result = run(f"git ls-tree -r {branch} --name-only 2>nul | findstr -i \"readme typo\" ")
    if result.stdout.strip():
        print(f"✅ 在 {branch} 找到文件！")
        # 恢复README.md
        run(f"git show {branch}:README.md > README.md 2>nul")
        # 恢复typo-capsule
        run(f"git checkout {branch} -- typo-capsule 2>nul")
        break

print("\n=== 检查本地文件 ===")
for item in os.listdir("."):
    print(f"  {item}")

print("\n=== 提交并推送 ===")
run("git add -A")
run('git commit -m "fix: 从其他分支恢复README.md和typo-capsule"')
run("git push origin master:creative")

print("\n✅ 完成！")
