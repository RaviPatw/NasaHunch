#!/usr/bin/env python3
import subprocess

def run(cmd):
    try:
        out = subprocess.check_output(cmd, text=True, stderr=subprocess.STDOUT)
        return out.strip()
    except subprocess.CalledProcessError as e:
        return e.output.strip()

def main():
    print("🔒 Running Security Audit...\n")
    print("Checking SSH configuration...")
    print(run(["sshd", "-T"]))

    print("\nListing active users with shell access:")
    print(run(["grep", "/bin/bash", "/etc/passwd"]))

    print("\nChecking for root login attempts:")
    print(run(["grep", "sshd.*root", "/var/log/auth.log"]))

    print("\nChecking firewall status:")
    print(run(["ufw", "status"]))

    print("\nFail2ban status (if installed):")
    print(run(["systemctl", "status", "fail2ban"]))

if __name__ == "__main__":
    main()
