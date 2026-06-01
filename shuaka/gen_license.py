"""授权码生成工具（开发者持有，不随软件分发）"""
import sys
from auth_manager import generate_license, get_machine_code

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法:")
        print("  python gen_license.py <机器码> <月数>")
        print("  python gen_license.py <机器码>          (默认12个月)")
        print("  python gen_license.py --self <月数>     (本机)")
        print()
        print("月数: 1 / 6 / 12")
        sys.exit(1)

    months = 12
    if sys.argv[1] == "--self":
        mc = get_machine_code()
        if len(sys.argv) >= 3:
            months = int(sys.argv[2])
    else:
        mc = sys.argv[1].strip()
        if len(sys.argv) >= 3:
            months = int(sys.argv[2])

    lic, expiry = generate_license(mc, months)
    full_code = f"{lic}-{expiry}"
    print(f"机器码:   {mc}")
    print(f"有效期:   {expiry[:4]}-{expiry[4:6]}-{expiry[6:8]} ({months}个月)")
    print(f"授权码:   {full_code}")
