import modules

modules.auditd.setup_security_auditing()
modules.fail2ban.setup_bruteforce_protection()
modules.fail2ban.integrations.setup_pam_audit_protection()
modules.fail2ban.integrations.setup_ufw_rule()
