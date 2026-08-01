# IT Security Guide

## Accounts and passwords

Use the company password manager (1Password) for every work account. Passwords
must be at least 16 characters and unique per service — let the password
manager generate them. Two-factor authentication is mandatory on email, GitHub,
the VPN, and the HR portal. Hardware keys are available from IT on request and
are required for admins.

Never share credentials, not even with IT. IT will never ask for your password
in email or chat.

## Devices

Company laptops come with full-disk encryption and remote wipe enabled — do
not disable either. Set your screen to lock after at most 5 minutes of
inactivity. Install OS security updates within 7 days of release; the MDM
system will nag you after that and force-install after 14 days.

Personal devices may be used for email and Slack only, and only after
enrolling in mobile device management. Customer data must never be stored on
personal devices.

## Network

When working from the office network nothing special is needed. On any public
or shared Wi-Fi (cafes, airports, co-working spaces) the company VPN must be
connected before you access internal systems. The VPN client auto-connects on
untrusted networks; do not override it.

## Data handling

Customer data lives in approved systems only: the production database, the
support desk, and the analytics warehouse. Exporting customer data to
spreadsheets or personal storage (Dropbox, personal Google Drive, USB drives)
is prohibited. Anonymized samples for testing must go through the data team.

Classify documents when you create them: public, internal, or confidential.
Confidential documents are shared on a need-to-know basis and never posted in
public Slack channels.

## Phishing and incidents

Report suspicious emails with the "Report phishing" button in the mail client,
or forward them to security@company.test. If you clicked a suspicious link or
entered credentials somewhere you shouldn't have: change the password
immediately, then report it. See the Incident Response How-To for what happens
next — reporting fast is always better than staying quiet, and honest mistakes
are never punished.
