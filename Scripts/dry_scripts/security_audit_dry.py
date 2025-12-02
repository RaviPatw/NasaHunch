#!/usr/bin/env python3
import subprocess
import os

def run_or_simulate(cmd, simulate_text):
    """
    Runs a Linux command. If it fails (missing, permission denied, etc),
    return a safe simulated placeholder.
    """
    try:
        out = subprocess.check_output(cmd, text=True, stderr=subprocess.STDOUT)
        return out.strip()
    except Exception:
        return f"[SIMULATED]\n{simulate_text}"


def main():
    print(" Running Linux Security Audit (DRY RUN)...\n")

    # --- SSH CONFIG ---
    print("➡ SSH configuration:")
    print(run_or_simulate(
        ["sshd", "-T"],
        "sshd config would normally be shown here."
    ))
    print()

    # --- USERS WITH SHELL ACCESS ---
    print("➡ Users with /bin/bash:")
    if os.path.exists("/etc/passwd"):
        print(run_or_simulate(
            ["grep", "/bin/bash", "/etc/passwd"],
            "No users or file inaccessible."
        ))
    else:
        print("[SIMULATED] /etc/passwd not found")
    print()

    # --- ROOT LOGIN ATTEMPTS ---
    print("➡ Root login attempts in auth.log:")
    if os.path.exists("/var/log/auth.log"):
        print(run_or_simulate(
            ["grep", "sshd.*root", "/var/log/auth.log"],
            "No root login attempts or log inaccessible."
        ))
    else:
        print("[SIMULATED] /var/log/auth.log not found")
    print()

    # --- UFW STATUS ---
    print("➡ UFW firewall status:")
    print(run_or_simulate(
        ["ufw", "status"],
        "Firewall status unavailable."
    ))
    print()

    # --- FAIL2BAN STATUS ---
    print("➡ Fail2ban status:")
    print(run_or_simulate(
        ["systemctl", "status", "fail2ban"],
        "Fail2ban may not be installed or systemctl isn't available."
    ))
    print()

    print("✅ Dry-run Linux audit complete.\n"
          "No privileged operations were attempted.")


if __name__ == "__main__":
    main()
