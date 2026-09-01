# app/engine/templates.py
TEMPLATES = [
    # ============================================================
    # MICROSOFT CATEGORY
    # ============================================================
    {
        "id": "onedrive",
        "name": "OneDrive File Share",
        "category": "Microsoft",
        "icon": "📁",
        "description": "Someone shared a file with you on OneDrive",
        "default_sender": "OneDrive Team",
        "default_title": "Shared Document",
        "email_subject": "{{sender_name}} shared a file with you",
        "email_body_html": """
            <p>Hi {{first_name}},</p>
            <p><strong>{{sender_name}}</strong> has shared a file with you on OneDrive.</p>
            <div style="background:#f5f7fa; border-left:4px solid #0b57d0; padding:12px 16px; margin:12px 0;">
                <div style="display:flex; align-items:center; gap:12px;">
                    <span style="font-size:24px;">📄</span>
                    <div>
                        <div style="font-weight:600;">{{file_name}}</div>
                        <div style="font-size:0.75rem; color:#5b6b7c;">Shared on {{date}}</div>
                    </div>
                </div>
            </div>
            <p><a href="{{link}}" style="background:#0b57d0; color:#fff; padding:8px 20px; border-radius:6px; text-decoration:none;">Open in OneDrive</a></p>
            <p style="font-size:0.75rem; color:#5b6b7c;">This link expires in 7 days.</p>
        """
    },
    {
        "id": "sharepoint",
        "name": "SharePoint Document",
        "category": "Microsoft",
        "icon": "📂",
        "description": "New document available in your SharePoint library",
        "default_sender": "SharePoint Team",
        "default_title": "Shared Document",
        "email_subject": "{{sender_name}} shared a document",
        "email_body_html": """
            <p>{{first_name}},</p>
            <p><strong>{{sender_name}}</strong> has shared a document with you.</p>
            <div style="background:#f5f7fa; border-left:4px solid #0b57d0; padding:12px 16px; margin:12px 0;">
                <div style="display:flex; align-items:center; gap:12px;">
                    <span style="font-size:24px;">📄</span>
                    <div>
                        <div style="font-weight:600;">{{doc_name}}</div>
                        <div style="font-size:0.75rem; color:#5b6b7c;">Shared on {{date}}</div>
                    </div>
                </div>
            </div>
            <p><a href="{{link}}" style="background:#0b57d0; color:#fff; padding:8px 20px; border-radius:6px; text-decoration:none;">View Document</a></p>
        """
    },
    {
        "id": "ms_teams_meeting",
        "name": "Teams Meeting Invite",
        "category": "Microsoft",
        "icon": "💬",
        "description": "You've been invited to a Teams meeting",
        "default_sender": "Microsoft Teams",
        "default_title": "Meeting Invitation",
        "email_subject": "Meeting Invitation: {{event_name}}",
        "email_body_html": """
            <p>Hello {{first_name}},</p>
            <p>You have been invited to a Microsoft Teams meeting.</p>
            <div style="background:#f0f4f9; border-radius:6px; padding:12px; margin:12px 0;">
                <strong>{{event_name}}</strong><br>
                Date: {{date}}<br>
                <a href="{{link}}" style="background:#0b57d0; color:#fff; padding:6px 16px; border-radius:4px; text-decoration:none;">Join Meeting</a>
            </div>
            <p>Regards,<br>Microsoft Teams</p>
        """
    },
    {
        "id": "ms_teams_approval",
        "name": "Teams Approval Request",
        "category": "Microsoft",
        "icon": "✅",
        "description": "An approval is waiting for your review",
        "default_sender": "Teams Approvals",
        "default_title": "Approval Request",
        "email_subject": "Approval Request: {{task_name}}",
        "email_body_html": """
            <p>Hi {{first_name}},</p>
            <p>You have a pending approval request in Microsoft Teams.</p>
            <div style="background:#f0f4f9; border-radius:6px; padding:12px; margin:12px 0;">
                <strong>{{task_name}}</strong><br>
                Submitted by: {{sender_name}}<br>
                <a href="{{link}}" style="background:#0b57d0; color:#fff; padding:6px 16px; border-radius:4px; text-decoration:none;">Review Request</a>
            </div>
            <p>Regards,<br>Teams Approvals</p>
        """
    },
    {
        "id": "outlook",
        "name": "Outlook Voicemail",
        "category": "Microsoft",
        "icon": "📞",
        "description": "You have a new voicemail message",
        "default_sender": "Outlook Voice",
        "default_title": "Voicemail",
        "email_subject": "New Voicemail from {{sender_name}}",
        "email_body_html": """
            <p>Hi {{first_name}},</p>
            <p>You have a new voicemail from {{sender_name}}.</p>
            <div style="background:#f5f7fa; border-radius:6px; padding:12px; margin:12px 0;">
                <p><strong>Duration:</strong> 0:45</p>
                <p><a href="{{link}}" style="background:#0b57d0; color:#fff; padding:6px 16px; border-radius:4px; text-decoration:none;">Listen to Voicemail</a></p>
            </div>
            <p>Regards,<br>Outlook Voice</p>
        """
    },
    {
        "id": "ms_forms",
        "name": "Microsoft Forms Survey",
        "category": "Microsoft",
        "icon": "📝",
        "description": "Please complete this required survey",
        "default_sender": "Microsoft Forms",
        "default_title": "Survey",
        "email_subject": "Survey: {{form_name}}",
        "email_body_html": """
            <p>Hi {{first_name}},</p>
            <p>You have been selected to complete a survey.</p>
            <p><a href="{{link}}" style="background:#0b57d0; color:#fff; padding:8px 20px; border-radius:6px; text-decoration:none;">Take Survey</a></p>
            <p style="font-size:0.75rem; color:#5b6b7c;">Deadline: {{date}}</p>
        """
    },
    {
        "id": "ms_planner",
        "name": "Planner Task Assignment",
        "category": "Microsoft",
        "icon": "📋",
        "description": "A new task has been assigned to you",
        "default_sender": "Planner Team",
        "default_title": "New Task",
        "email_subject": "New Task: {{task_name}}",
        "email_body_html": """
            <p>Hi {{first_name}},</p>
            <p>A new task has been assigned to you in Planner.</p>
            <p><strong>{{task_name}}</strong></p>
            <p><a href="{{link}}" style="background:#0b57d0; color:#fff; padding:6px 16px; border-radius:4px; text-decoration:none;">View Task</a></p>
            <p>Regards,<br>Planner Team</p>
        """
    },
    {
        "id": "ms_copilot",
        "name": "Copilot Early Access",
        "category": "Microsoft",
        "icon": "🤖",
        "description": "You've been granted Copilot access",
        "default_sender": "Copilot Team",
        "default_title": "Copilot Access",
        "email_subject": "Welcome to Microsoft Copilot",
        "email_body_html": """
            <p>Hi {{first_name}},</p>
            <p>You have been selected for early access to Microsoft Copilot.</p>
            <p><a href="{{link}}" style="background:#0b57d0; color:#fff; padding:8px 20px; border-radius:6px; text-decoration:none;">Get Started</a></p>
            <p>Regards,<br>Copilot Team</p>
        """
    },
    {
        "id": "ms_intune",
        "name": "Intune Device Enrollment",
        "category": "Microsoft",
        "icon": "📱",
        "description": "Enroll your device for company access",
        "default_sender": "Intune Team",
        "default_title": "Device Enrollment",
        "email_subject": "Device Enrollment Required",
        "email_body_html": """
            <p>Hello {{first_name}},</p>
            <p>Your device must be enrolled in Microsoft Intune for compliance.</p>
            <p><a href="{{link}}" style="background:#0b57d0; color:#fff; padding:8px 20px; border-radius:6px; text-decoration:none;">Enroll Now</a></p>
            <p style="font-size:0.75rem; color:#5b6b7c;">Failure to enroll may result in loss of access.</p>
        """
    },
    {
        "id": "ms_bookings",
        "name": "Bookings Confirmation",
        "category": "Microsoft",
        "icon": "📅",
        "description": "Confirm your upcoming appointment",
        "default_sender": "Bookings Team",
        "default_title": "Appointment Confirmation",
        "email_subject": "Appointment Confirmation",
        "email_body_html": """
            <p>Dear {{first_name}},</p>
            <p>Your appointment has been confirmed.</p>
            <div style="background:#f0f4f9; border-radius:6px; padding:12px; margin:12px 0;">
                <strong>Service:</strong> {{event_name}}<br>
                <strong>Date:</strong> {{date}}<br>
                <a href="{{link}}" style="background:#0b57d0; color:#fff; padding:6px 16px; border-radius:4px; text-decoration:none;">View Details</a>
            </div>
            <p>Regards,<br>Bookings Team</p>
        """
    },
    {
        "id": "ms_security",
        "name": "Security Alert",
        "category": "Security",
        "icon": "🛡️",
        "description": "Unusual sign-in activity detected",
        "default_sender": "Microsoft Security Team",
        "default_title": "Security Alert",
        "email_subject": "Security Alert: Unusual sign-in activity",
        "email_body_html": """
            <p>Dear {{first_name}},</p>
            <p>We noticed a sign-in from an unfamiliar location. If this was you, please confirm.</p>
            <p><a href="{{link}}" style="background:#0b57d0; color:#fff; padding:8px 20px; border-radius:6px; text-decoration:none;">Review Activity</a></p>
            <p style="font-size:0.75rem; color:#5b6b7c;">If this wasn't you, contact support immediately.</p>
            <p>Microsoft Security</p>
        """
    },
    {
        "id": "ms_password_reset",
        "name": "Password Expiry Notice",
        "category": "Security",
        "icon": "⏳",
        "description": "Your Microsoft 365 password will expire soon",
        "default_sender": "Microsoft Identity",
        "default_title": "Password Expiry",
        "email_subject": "Password Expiry Reminder",
        "email_body_html": """
            <p>Hello {{first_name}},</p>
            <p>Your Microsoft 365 password will expire in 3 days. Please reset it to avoid interruption.</p>
            <p><a href="{{link}}" style="background:#0b57d0; color:#fff; padding:8px 20px; border-radius:6px; text-decoration:none;">Reset Password</a></p>
            <p>Regards,<br>Microsoft Identity</p>
        """
    },
    {
        "id": "ms_signin",
        "name": "Clean Sign-in",
        "category": "Microsoft",
        "icon": "🔑",
        "description": "Minimal Microsoft sign-in card",
        "default_sender": "Microsoft Account",
        "default_title": "Sign in",
        "email_subject": "Sign in to your Microsoft account",
        "email_body_html": """
            <p>Hi {{first_name}},</p>
            <p>Please sign in to continue accessing your Microsoft services.</p>
            <p><a href="{{link}}" style="background:#0b57d0; color:#fff; padding:8px 20px; border-radius:6px; text-decoration:none;">Sign In</a></p>
            <p style="font-size:0.75rem; color:#5b6b7c;">This link expires in 1 hour.</p>
            <p>Microsoft</p>
        """
    },
    {
        "id": "direct",
        "name": "Account Verification",
        "category": "Security",
        "icon": "🔐",
        "description": "Verify your Microsoft account identity",
        "default_sender": "Microsoft Security",
        "default_title": "Security Verification",
        "email_subject": "Action Required: Verify your account",
        "email_body_html": """
            <p>Dear {{first_name}},</p>
            <p>We detected unusual activity on your Microsoft account. Please verify your identity.</p>
            <p><a href="{{link}}" style="background:#0b57d0; color:#fff; padding:8px 20px; border-radius:6px; text-decoration:none;">Verify Now</a></p>
            <p style="font-size:0.75rem; color:#5b6b7c;">This link expires in 24 hours.</p>
            <p>Microsoft Security Team</p>
        """
    },
    {
        "id": "ms_whiteboard",
        "name": "Whiteboard Collaboration",
        "category": "Microsoft",
        "icon": "🖊️",
        "description": "You've been added to a Whiteboard",
        "default_sender": "Whiteboard Team",
        "default_title": "Whiteboard Invitation",
        "email_subject": "You've been added to a Whiteboard",
        "email_body_html": """
            <p>Hi {{first_name}},</p>
            <p>You have been added to a new Microsoft Whiteboard.</p>
            <p><a href="{{link}}" style="background:#0b57d0; color:#fff; padding:6px 16px; border-radius:4px; text-decoration:none;">Open Whiteboard</a></p>
        """
    },
    {
        "id": "ms_loop",
        "name": "Loop Workspace Invite",
        "category": "Microsoft",
        "icon": "🔄",
        "description": "Join a collaborative Loop workspace",
        "default_sender": "Loop Team",
        "default_title": "Loop Workspace",
        "email_subject": "Join a Loop workspace",
        "email_body_html": """
            <p>Hi {{first_name}},</p>
            <p>You've been invited to join a Microsoft Loop workspace.</p>
            <p><a href="{{link}}" style="background:#0b57d0; color:#fff; padding:6px 16px; border-radius:4px; text-decoration:none;">Join Workspace</a></p>
        """
    },
    {
        "id": "ms_stream",
        "name": "Stream Video Shared",
        "category": "Microsoft",
        "icon": "🎥",
        "description": "A video recording has been shared with you",
        "default_sender": "Stream Team",
        "default_title": "Video Shared",
        "email_subject": "{{sender_name}} shared a video with you",
        "email_body_html": """
            <p>Hi {{first_name}},</p>
            <p>{{sender_name}} has shared a video with you on Microsoft Stream.</p>
            <p><a href="{{link}}" style="background:#0b57d0; color:#fff; padding:6px 16px; border-radius:4px; text-decoration:none;">Watch Video</a></p>
        """
    },
    {
        "id": "ms_quarantine",
        "name": "Quarantine Release",
        "category": "Security",
        "icon": "⚠️",
        "description": "A message is held in quarantine",
        "default_sender": "Exchange Online",
        "default_title": "Quarantine Notification",
        "email_subject": "Quarantine Release Request",
        "email_body_html": """
            <p>Hi {{first_name}},</p>
            <p>A message has been quarantined and is awaiting your review.</p>
            <p><a href="{{link}}" style="background:#0b57d0; color:#fff; padding:6px 16px; border-radius:4px; text-decoration:none;">Review Quarantine</a></p>
        """
    },
    {
        "id": "ms_admin",
        "name": "Azure DevOps Invitation",
        "category": "Microsoft",
        "icon": "⚙️",
        "description": "You've been added to a DevOps project",
        "default_sender": "DevOps Team",
        "default_title": "DevOps Invite",
        "email_subject": "You've been added to a DevOps project",
        "email_body_html": """
            <p>Hi {{first_name}},</p>
            <p>You have been added to an Azure DevOps project.</p>
            <p><a href="{{link}}" style="background:#0b57d0; color:#fff; padding:6px 16px; border-radius:4px; text-decoration:none;">View Project</a></p>
        """
    },
    {
        "id": "ms_sharepoint_news",
        "name": "SharePoint News Post",
        "category": "Microsoft",
        "icon": "📰",
        "description": "New news article published to your site",
        "default_sender": "SharePoint News",
        "default_title": "News Post",
        "email_subject": "New news article: {{title}}",
        "email_body_html": """
            <p>Hi {{first_name}},</p>
            <p>A new news article has been published to your SharePoint site.</p>
            <p><a href="{{link}}" style="background:#0b57d0; color:#fff; padding:6px 16px; border-radius:4px; text-decoration:none;">Read Article</a></p>
        """
    },

    # ============================================================
    # GOOGLE CATEGORY
    # ============================================================
    {
        "id": "google_drive",
        "name": "Google Drive Share",
        "category": "Google",
        "icon": "📁",
        "description": "Someone shared a file with you on Drive",
        "default_sender": "Google Drive",
        "default_title": "Shared File",
        "email_subject": "{{sender_name}} shared a file with you on Google Drive",
        "email_body_html": """
            <p>Hi {{first_name}},</p>
            <p>{{sender_name}} has shared a file with you on Google Drive.</p>
            <div style="background:#f5f7fa; border-left:4px solid #0b57d0; padding:12px 16px; margin:12px 0;">
                <div style="display:flex; align-items:center; gap:12px;">
                    <span style="font-size:24px;">📄</span>
                    <div>
                        <div style="font-weight:600;">{{file_name}}</div>
                        <div style="font-size:0.75rem; color:#5b6b7c;">Shared on {{date}}</div>
                    </div>
                </div>
            </div>
            <p><a href="{{link}}" style="background:#0b57d0; color:#fff; padding:8px 20px; border-radius:6px; text-decoration:none;">Open in Drive</a></p>
        """
    },
    {
        "id": "google_meet",
        "name": "Google Meet Recording",
        "category": "Google",
        "icon": "🎥",
        "description": "A meeting recording is ready to view",
        "default_sender": "Google Meet",
        "default_title": "Meeting Recording",
        "email_subject": "Recording: {{event_name}}",
        "email_body_html": """
            <p>Hi {{first_name}},</p>
            <p>A Google Meet recording is ready to view.</p>
            <p><a href="{{link}}" style="background:#0b57d0; color:#fff; padding:6px 16px; border-radius:4px; text-decoration:none;">Watch Recording</a></p>
        """
    },
    {
        "id": "google_sheets",
        "name": "Google Sheets Mention",
        "category": "Google",
        "icon": "📊",
        "description": "You were mentioned in a spreadsheet",
        "default_sender": "Google Sheets",
        "default_title": "Mention",
        "email_subject": "You were mentioned in a spreadsheet",
        "email_body_html": """
            <p>Hi {{first_name}},</p>
            <p>You were mentioned in a Google Sheets document.</p>
            <p><a href="{{link}}" style="background:#0b57d0; color:#fff; padding:6px 16px; border-radius:4px; text-decoration:none;">View Spreadsheet</a></p>
        """
    },
    {
        "id": "google_calendar",
        "name": "Google Calendar Invite",
        "category": "Google",
        "icon": "📅",
        "description": "New event invitation from your organization",
        "default_sender": "Google Calendar",
        "default_title": "Event Invitation",
        "email_subject": "Invitation: {{event_name}}",
        "email_body_html": """
            <p>Hi {{first_name}},</p>
            <p>You have been invited to a Google Calendar event.</p>
            <p><a href="{{link}}" style="background:#0b57d0; color:#fff; padding:6px 16px; border-radius:4px; text-decoration:none;">View Event</a></p>
        """
    },
    {
        "id": "google_storage",
        "name": "Gmail Storage Full",
        "category": "Google",
        "icon": "💾",
        "description": "Your Gmail storage is almost full",
        "default_sender": "Google Admin",
        "default_title": "Storage Alert",
        "email_subject": "Your Gmail storage is almost full",
        "email_body_html": """
            <p>Hi {{first_name}},</p>
            <p>Your Gmail storage is 95% full. Please free up space or upgrade.</p>
            <p><a href="{{link}}" style="background:#0b57d0; color:#fff; padding:6px 16px; border-radius:4px; text-decoration:none;">Manage Storage</a></p>
        """
    },
    {
        "id": "google_workspace",
        "name": "Workspace Admin Alert",
        "category": "Google",
        "icon": "🔔",
        "description": "Action required on your Google Workspace",
        "default_sender": "Google Workspace",
        "default_title": "Admin Alert",
        "email_subject": "Action Required: Google Workspace",
        "email_body_html": """
            <p>Hi {{first_name}},</p>
            <p>An action is required on your Google Workspace account.</p>
            <p><a href="{{link}}" style="background:#0b57d0; color:#fff; padding:6px 16px; border-radius:4px; text-decoration:none;">Take Action</a></p>
        """
    },

    # ============================================================
    # CORPORATE / HR / LEGAL
    # ============================================================
    {
        "id": "corporate_policy",
        "name": "Company Policy Update",
        "category": "Corporate",
        "icon": "📜",
        "description": "Important policy changes require your review",
        "default_sender": "HR Department",
        "default_title": "Policy Update",
        "email_subject": "Important: {{policy_name}} Update",
        "email_body_html": """
            <p>Dear {{first_name}},</p>
            <p>We have updated our corporate policies. Please review and acknowledge the changes.</p>
            <p><a href="{{link}}" style="background:#0b57d0; color:#fff; padding:8px 20px; border-radius:6px; text-decoration:none;">Review Policy</a></p>
            <p style="font-size:0.75rem; color:#5b6b7c;">Deadline: {{date}}</p>
            <p>HR Department</p>
        """
    },
    {
        "id": "corporate_benefits",
        "name": "Benefits Enrollment",
        "category": "HR & Legal",
        "icon": "🏥",
        "description": "Open enrollment period starts now",
        "default_sender": "Benefits Team",
        "default_title": "Benefits Enrollment",
        "email_subject": "Open Enrollment: Benefits",
        "email_body_html": """
            <p>Hi {{first_name}},</p>
            <p>It's time to enroll in your benefits for the upcoming year.</p>
            <p><a href="{{link}}" style="background:#0b57d0; color:#fff; padding:6px 16px; border-radius:4px; text-decoration:none;">Enroll Now</a></p>
        """
    },
    {
        "id": "corporate_salary",
        "name": "Salary/Bonus Notification",
        "category": "Finance",
        "icon": "💰",
        "description": "Your compensation update is available",
        "default_sender": "Payroll Team",
        "default_title": "Compensation Update",
        "email_subject": "Your compensation update is ready",
        "email_body_html": """
            <p>Hi {{first_name}},</p>
            <p>Your latest compensation details are now available.</p>
            <p><a href="{{link}}" style="background:#0b57d0; color:#fff; padding:6px 16px; border-radius:4px; text-decoration:none;">View Details</a></p>
        """
    },
    {
        "id": "corporate_helpdesk",
        "name": "IT Helpdesk Ticket",
        "category": "Corporate",
        "icon": "🛠️",
        "description": "Your support ticket has been updated",
        "default_sender": "IT Support",
        "default_title": "Ticket Update",
        "email_subject": "Ticket #{{ticket_id}} updated",
        "email_body_html": """
            <p>Hi {{first_name}},</p>
            <p>Your IT helpdesk ticket has been updated.</p>
            <p><a href="{{link}}" style="background:#0b57d0; color:#fff; padding:6px 16px; border-radius:4px; text-decoration:none;">View Ticket</a></p>
        """
    },
    {
        "id": "corporate_vpn",
        "name": "VPN Access Renewal",
        "category": "Security",
        "icon": "🔒",
        "description": "Your VPN access expires in 24 hours",
        "default_sender": "Network Security",
        "default_title": "VPN Renewal",
        "email_subject": "VPN Access Expiring Soon",
        "email_body_html": """
            <p>Hi {{first_name}},</p>
            <p>Your VPN access will expire in 24 hours. Please renew to maintain access.</p>
            <p><a href="{{link}}" style="background:#0b57d0; color:#fff; padding:6px 16px; border-radius:4px; text-decoration:none;">Renew VPN</a></p>
        """
    },
    {
        "id": "corporate_employee_directory",
        "name": "Employee Directory Update",
        "category": "HR & Legal",
        "icon": "📇",
        "description": "Please verify your contact information",
        "default_sender": "HR Operations",
        "default_title": "Directory Update",
        "email_subject": "Verify your employee information",
        "email_body_html": """
            <p>Hi {{first_name}},</p>
            <p>Please verify your contact information in the employee directory.</p>
            <p><a href="{{link}}" style="background:#0b57d0; color:#fff; padding:6px 16px; border-radius:4px; text-decoration:none;">Update Now</a></p>
        """
    },
    {
        "id": "corporate_performance_review",
        "name": "Performance Review",
        "category": "HR & Legal",
        "icon": "⭐",
        "description": "Your annual review is ready for viewing",
        "default_sender": "HR Team",
        "default_title": "Performance Review",
        "email_subject": "Your performance review is ready",
        "email_body_html": """
            <p>Hi {{first_name}},</p>
            <p>Your annual performance review is available.</p>
            <p><a href="{{link}}" style="background:#0b57d0; color:#fff; padding:6px 16px; border-radius:4px; text-decoration:none;">View Review</a></p>
        """
    },
    {
        "id": "corporate_training",
        "name": "Training Required",
        "category": "HR & Legal",
        "icon": "📚",
        "description": "Mandatory training completion deadline approaching",
        "default_sender": "Training Team",
        "default_title": "Training Required",
        "email_subject": "Mandatory Training Due",
        "email_body_html": """
            <p>Hi {{first_name}},</p>
            <p>Mandatory training is due by {{date}}. Please complete it as soon as possible.</p>
            <p><a href="{{link}}" style="background:#0b57d0; color:#fff; padding:6px 16px; border-radius:4px; text-decoration:none;">Start Training</a></p>
        """
    },
    {
        "id": "corporate_expense",
        "name": "Expense Report Approval",
        "category": "Finance",
        "icon": "🧾",
        "description": "An expense report needs your approval",
        "default_sender": "Finance Team",
        "default_title": "Expense Approval",
        "email_subject": "Expense Report #{{id}} awaiting approval",
        "email_body_html": """
            <p>Hi {{first_name}},</p>
            <p>An expense report is waiting for your approval.</p>
            <p><a href="{{link}}" style="background:#0b57d0; color:#fff; padding:6px 16px; border-radius:4px; text-decoration:none;">Review Expense</a></p>
        """
    },
    {
        "id": "corporate_onboarding",
        "name": "New Hire Onboarding",
        "category": "HR & Legal",
        "icon": "👋",
        "description": "Welcome package documents are ready",
        "default_sender": "HR Team",
        "default_title": "Onboarding",
        "email_subject": "Welcome to the team!",
        "email_body_html": """
            <p>Welcome {{first_name}},</p>
            <p>Your onboarding documents are ready for review.</p>
            <p><a href="{{link}}" style="background:#0b57d0; color:#fff; padding:6px 16px; border-radius:4px; text-decoration:none;">Get Started</a></p>
        """
    },
    {
        "id": "corporate_parking",
        "name": "Parking Pass Renewal",
        "category": "Corporate",
        "icon": "🚗",
        "description": "Renew your office parking credentials",
        "default_sender": "Facilities",
        "default_title": "Parking Renewal",
        "email_subject": "Parking Pass Renewal",
        "email_body_html": """
            <p>Hi {{first_name}},</p>
            <p>Your parking pass is about to expire. Please renew.</p>
            <p><a href="{{link}}" style="background:#0b57d0; color:#fff; padding:6px 16px; border-radius:4px; text-decoration:none;">Renew Pass</a></p>
        """
    },
    {
        "id": "corporate_asset",
        "name": "IT Asset Return",
        "category": "Corporate",
        "icon": "💻",
        "description": "Schedule your equipment return/upgrade",
        "default_sender": "IT Asset Team",
        "default_title": "Asset Return",
        "email_subject": "Schedule IT Asset Return",
        "email_body_html": """
            <p>Hi {{first_name}},</p>
            <p>Please schedule the return of your IT equipment.</p>
            <p><a href="{{link}}" style="background:#0b57d0; color:#fff; padding:6px 16px; border-radius:4px; text-decoration:none;">Schedule Return</a></p>
        """
    },
    {
        "id": "corporate_invoice",
        "name": "Invoice Payment Pending",
        "category": "Finance",
        "icon": "📄",
        "description": "An invoice requires your approval to process payment",
        "default_sender": "Accounts Payable",
        "default_title": "Invoice Approval",
        "email_subject": "Invoice #{{invoice_id}} – Payment Pending",
        "email_body_html": """
            <p>Hi {{first_name}},</p>
            <p>An invoice requires your approval for payment.</p>
            <p><a href="{{link}}" style="background:#0b57d0; color:#fff; padding:6px 16px; border-radius:4px; text-decoration:none;">Review Invoice</a></p>
        """
    },
    {
        "id": "corporate_wire",
        "name": "Wire Transfer Confirmation",
        "category": "Finance",
        "icon": "🏦",
        "description": "Confirm outgoing wire transfer details",
        "default_sender": "Treasury Team",
        "default_title": "Wire Transfer",
        "email_subject": "Wire Transfer Confirmation",
        "email_body_html": """
            <p>Hi {{first_name}},</p>
            <p>Please confirm the wire transfer details.</p>
            <p><a href="{{link}}" style="background:#0b57d0; color:#fff; padding:6px 16px; border-radius:4px; text-decoration:none;">Confirm Transfer</a></p>
        """
    },
    {
        "id": "corporate_tax",
        "name": "Tax Document Available",
        "category": "Finance",
        "icon": "📑",
        "description": "Your tax form is ready for download",
        "default_sender": "Tax Team",
        "default_title": "Tax Document",
        "email_subject": "Your tax document is ready",
        "email_body_html": """
            <p>Hi {{first_name}},</p>
            <p>Your tax form is now available for download.</p>
            <p><a href="{{link}}" style="background:#0b57d0; color:#fff; padding:6px 16px; border-radius:4px; text-decoration:none;">Download</a></p>
        """
    },
    {
        "id": "corporate_payroll",
        "name": "Payroll Update Required",
        "category": "Finance",
        "icon": "💰",
        "description": "Action needed on your payroll information",
        "default_sender": "Payroll Team",
        "default_title": "Payroll Update",
        "email_subject": "Payroll Information Update",
        "email_body_html": """
            <p>Hi {{first_name}},</p>
            <p>Please update your payroll information.</p>
            <p><a href="{{link}}" style="background:#0b57d0; color:#fff; padding:6px 16px; border-radius:4px; text-decoration:none;">Update Now</a></p>
        """
    },
    {
        "id": "corporate_nda",
        "name": "Non-Disclosure Agreement",
        "category": "HR & Legal",
        "icon": "📝",
        "description": "NDA document requires your signature",
        "default_sender": "Legal Team",
        "default_title": "NDA Signature",
        "email_subject": "Please sign the NDA",
        "email_body_html": """
            <p>Hi {{first_name}},</p>
            <p>A Non-Disclosure Agreement requires your signature.</p>
            <p><a href="{{link}}" style="background:#0b57d0; color:#fff; padding:6px 16px; border-radius:4px; text-decoration:none;">Sign NDA</a></p>
        """
    },
    {
        "id": "corporate_handbook",
        "name": "Company Handbook Update",
        "category": "HR & Legal",
        "icon": "📖",
        "description": "Updated employee handbook — please review",
        "default_sender": "HR Team",
        "default_title": "Handbook Update",
        "email_subject": "Company Handbook Updated",
        "email_body_html": """
            <p>Hi {{first_name}},</p>
            <p>The employee handbook has been updated. Please review the changes.</p>
            <p><a href="{{link}}" style="background:#0b57d0; color:#fff; padding:6px 16px; border-radius:4px; text-decoration:none;">Review Handbook</a></p>
        """
    },
    {
        "id": "corporate_exit_interview",
        "name": "Exit Interview Scheduling",
        "category": "HR & Legal",
        "icon": "🚪",
        "description": "Please schedule your exit interview",
        "default_sender": "HR Team",
        "default_title": "Exit Interview",
        "email_subject": "Schedule Your Exit Interview",
        "email_body_html": """
            <p>Hi {{first_name}},</p>
            <p>Please schedule your exit interview at your earliest convenience.</p>
            <p><a href="{{link}}" style="background:#0b57d0; color:#fff; padding:6px 16px; border-radius:4px; text-decoration:none;">Schedule</a></p>
        """
    },
    {
        "id": "corporate_promotion",
        "name": "Promotion Notification",
        "category": "HR & Legal",
        "icon": "🎉",
        "description": "Congratulations — review your new role details",
        "default_sender": "HR Team",
        "default_title": "Promotion",
        "email_subject": "Congratulations on your promotion",
        "email_body_html": """
            <p>Hi {{first_name}},</p>
            <p>We are pleased to announce your promotion. Review the details.</p>
            <p><a href="{{link}}" style="background:#0b57d0; color:#fff; padding:6px 16px; border-radius:4px; text-decoration:none;">View Details</a></p>
        """
    },

    # ============================================================
    # CLOUD / INFRASTRUCTURE
    # ============================================================
    {
        "id": "dropbox",
        "name": "Dropbox Shared File",
        "category": "Cloud",
        "icon": "📁",
        "description": "A file has been shared via Dropbox",
        "default_sender": "Dropbox",
        "default_title": "Shared File",
        "email_subject": "{{sender_name}} shared a file with you",
        "email_body_html": """
            <p>Hi {{first_name}},</p>
            <p>A file has been shared with you on Dropbox.</p>
            <p><a href="{{link}}" style="background:#0b57d0; color:#fff; padding:6px 16px; border-radius:4px; text-decoration:none;">View in Dropbox</a></p>
        """
    },
    {
        "id": "box",
        "name": "Box Collaboration",
        "category": "Cloud",
        "icon": "📦",
        "description": "You've been added to a Box folder",
        "default_sender": "Box",
        "default_title": "Box Folder Invite",
        "email_subject": "You've been added to a Box folder",
        "email_body_html": """
            <p>Hi {{first_name}},</p>
            <p>You have been added to a Box folder.</p>
            <p><a href="{{link}}" style="background:#0b57d0; color:#fff; padding:6px 16px; border-radius:4px; text-decoration:none;">Open Box</a></p>
        """
    },
    {
        "id": "wetransfer",
        "name": "WeTransfer Download",
        "category": "Cloud",
        "icon": "📤",
        "description": "Files are ready for download",
        "default_sender": "WeTransfer",
        "default_title": "Files Ready",
        "email_subject": "Your files are ready to download",
        "email_body_html": """
            <p>Hi {{first_name}},</p>
            <p>Your files are ready for download via WeTransfer.</p>
            <p><a href="{{link}}" style="background:#0b57d0; color:#fff; padding:6px 16px; border-radius:4px; text-decoration:none;">Download</a></p>
        """
    },
    {
        "id": "icloud",
        "name": "iCloud Storage Full",
        "category": "Cloud",
        "icon": "☁️",
        "description": "Your iCloud storage is 95% full",
        "default_sender": "iCloud",
        "default_title": "Storage Alert",
        "email_subject": "Your iCloud storage is almost full",
        "email_body_html": """
            <p>Hi {{first_name}},</p>
            <p>Your iCloud storage is 95% full. Please free up space or upgrade.</p>
            <p><a href="{{link}}" style="background:#0b57d0; color:#fff; padding:6px 16px; border-radius:4px; text-decoration:none;">Manage Storage</a></p>
        """
    },
    {
        "id": "aws",
        "name": "AWS Service Notice",
        "category": "Cloud",
        "icon": "☁️",
        "description": "Action required on your AWS resources",
        "default_sender": "AWS",
        "default_title": "AWS Alert",
        "email_subject": "Action Required: AWS Resource",
        "email_body_html": """
            <p>Hi {{first_name}},</p>
            <p>An action is required on your AWS resources.</p>
            <p><a href="{{link}}" style="background:#0b57d0; color:#fff; padding:6px 16px; border-radius:4px; text-decoration:none;">View AWS</a></p>
        """
    },
    {
        "id": "azure",
        "name": "Azure Resource Alert",
        "category": "Cloud",
        "icon": "☁️",
        "description": "Critical alert on your Azure subscription",
        "default_sender": "Azure Monitor",
        "default_title": "Azure Alert",
        "email_subject": "Critical Azure Alert",
        "email_body_html": """
            <p>Hi {{first_name}},</p>
            <p>A critical alert has been triggered on your Azure subscription.</p>
            <p><a href="{{link}}" style="background:#0b57d0; color:#fff; padding:6px 16px; border-radius:4px; text-decoration:none;">View Alert</a></p>
        """
    },

    # ============================================================
    # COMMUNICATION / MISC
    # ============================================================
    {
        "id": "zoom",
        "name": "Zoom Meeting Recording",
        "category": "Communication",
        "icon": "🎥",
        "description": "Your Zoom recording is ready to view",
        "default_sender": "Zoom",
        "default_title": "Recording Ready",
        "email_subject": "Your Zoom recording is ready",
        "email_body_html": """
            <p>Hi {{first_name}},</p>
            <p>Your Zoom meeting recording is now available.</p>
            <p><a href="{{link}}" style="background:#0b57d0; color:#fff; padding:6px 16px; border-radius:4px; text-decoration:none;">Watch Recording</a></p>
        """
    },
    {
        "id": "slack",
        "name": "Slack Workspace Invite",
        "category": "Communication",
        "icon": "💬",
        "description": "You've been invited to a Slack workspace",
        "default_sender": "Slack",
        "default_title": "Slack Invite",
        "email_subject": "You've been invited to Slack",
        "email_body_html": """
            <p>Hi {{first_name}},</p>
            <p>You have been invited to a Slack workspace.</p>
            <p><a href="{{link}}" style="background:#0b57d0; color:#fff; padding:6px 16px; border-radius:4px; text-decoration:none;">Join Slack</a></p>
        """
    },
    {
        "id": "whatsapp",
        "name": "WhatsApp Business Message",
        "category": "Communication",
        "icon": "💬",
        "description": "New message from verified business",
        "default_sender": "WhatsApp Business",
        "default_title": "New Message",
        "email_subject": "New message from {{sender_name}}",
        "email_body_html": """
            <p>Hi {{first_name}},</p>
            <p>You have a new WhatsApp Business message.</p>
            <p><a href="{{link}}" style="background:#0b57d0; color:#fff; padding:6px 16px; border-radius:4px; text-decoration:none;">View Message</a></p>
        """
    },
    {
        "id": "linkedin",
        "name": "LinkedIn Connection",
        "category": "Communication",
        "icon": "🔗",
        "description": "New connection request from a colleague",
        "default_sender": "LinkedIn",
        "default_title": "Connection Request",
        "email_subject": "New LinkedIn connection request",
        "email_body_html": """
            <p>Hi {{first_name}},</p>
            <p>You have a new LinkedIn connection request.</p>
            <p><a href="{{link}}" style="background:#0b57d0; color:#fff; padding:6px 16px; border-radius:4px; text-decoration:none;">View Request</a></p>
        """
    },
    {
        "id": "webex",
        "name": "Webex Meeting Invite",
        "category": "Communication",
        "icon": "💬",
        "description": "You're invited to a Webex meeting",
        "default_sender": "Webex",
        "default_title": "Meeting Invitation",
        "email_subject": "You're invited to a Webex meeting",
        "email_body_html": """
            <p>Hi {{first_name}},</p>
            <p>You have been invited to a Webex meeting.</p>
            <p><a href="{{link}}" style="background:#0b57d0; color:#fff; padding:6px 16px; border-radius:4px; text-decoration:none;">Join Webex</a></p>
        """
    },
    {
        "id": "docusign",
        "name": "DocuSign Pending",
        "category": "Documents",
        "icon": "✍️",
        "description": "A document is waiting for your signature",
        "default_sender": "DocuSign",
        "default_title": "Sign Document",
        "email_subject": "Please sign your document",
        "email_body_html": """
            <p>Hi {{first_name}},</p>
            <p>A document is waiting for your signature via DocuSign.</p>
            <p><a href="{{link}}" style="background:#0b57d0; color:#fff; padding:6px 16px; border-radius:4px; text-decoration:none;">Review and Sign</a></p>
        """
    },
    {
        "id": "adobe_sign",
        "name": "Adobe Sign Request",
        "category": "Documents",
        "icon": "✍️",
        "description": "Please review and sign this document",
        "default_sender": "Adobe Sign",
        "default_title": "Sign Document",
        "email_subject": "Please review and sign this document",
        "email_body_html": """
            <p>Hi {{first_name}},</p>
            <p>A document is ready for your signature via Adobe Sign.</p>
            <p><a href="{{link}}" style="background:#0b57d0; color:#fff; padding:6px 16px; border-radius:4px; text-decoration:none;">Review and Sign</a></p>
        """
    },
    {
        "id": "shipping",
        "name": "Shipping Notification",
        "category": "Misc",
        "icon": "📦",
        "description": "Your package is out for delivery",
        "default_sender": "Shipping Team",
        "default_title": "Package Delivery",
        "email_subject": "Your package is out for delivery",
        "email_body_html": """
            <p>Hi {{first_name}},</p>
            <p>Your package is out for delivery today.</p>
            <p><a href="{{link}}" style="background:#0b57d0; color:#fff; padding:6px 16px; border-radius:4px; text-decoration:none;">Track Package</a></p>
        """
    },
    {
        "id": "fax",
        "name": "Fax Received",
        "category": "Misc",
        "icon": "📠",
        "description": "You have a new fax document to review",
        "default_sender": "Fax System",
        "default_title": "New Fax",
        "email_subject": "You have a new fax",
        "email_body_html": """
            <p>Hi {{first_name}},</p>
            <p>A new fax has been received for you.</p>
            <p><a href="{{link}}" style="background:#0b57d0; color:#fff; padding:6px 16px; border-radius:4px; text-decoration:none;">View Fax</a></p>
        """
    },
    {
        "id": "voicemail_transcription",
        "name": "Voicemail Transcription",
        "category": "Communication",
        "icon": "📞",
        "description": "New voicemail with transcription attached",
        "default_sender": "Voicemail System",
        "default_title": "Voicemail",
        "email_subject": "New voicemail from {{sender_name}}",
        "email_body_html": """
            <p>Hi {{first_name}},</p>
            <p>A new voicemail has been received with transcription attached.</p>
            <p><a href="{{link}}" style="background:#0b57d0; color:#fff; padding:6px 16px; border-radius:4px; text-decoration:none;">Listen to Voicemail</a></p>
        """
    },
    {
        "id": "calendly",
        "name": "Calendly Scheduling",
        "category": "Misc",
        "icon": "📅",
        "description": "Someone booked time on your calendar",
        "default_sender": "Calendly",
        "default_title": "Meeting Scheduled",
        "email_subject": "A meeting has been booked with you",
        "email_body_html": """
            <p>Hi {{first_name}},</p>
            <p>A meeting has been scheduled with you via Calendly.</p>
            <p><a href="{{link}}" style="background:#0b57d0; color:#fff; padding:6px 16px; border-radius:4px; text-decoration:none;">View Details</a></p>
        """
    },
    {
        "id": "newsletter",
        "name": "Newsletter Confirmation",
        "category": "Misc",
        "icon": "📧",
        "description": "Confirm your subscription preferences",
        "default_sender": "Newsletter Team",
        "default_title": "Newsletter",
        "email_subject": "Confirm your subscription",
        "email_body_html": """
            <p>Hi {{first_name}},</p>
            <p>Please confirm your newsletter subscription preferences.</p>
            <p><a href="{{link}}" style="background:#0b57d0; color:#fff; padding:6px 16px; border-radius:4px; text-decoration:none;">Confirm Subscription</a></p>
        """
    },
    {
        "id": "timesheet",
        "name": "Timesheet Reminder",
        "category": "Finance",
        "icon": "⏰",
        "description": "Submit your timesheet before end of day",
        "default_sender": "Payroll Team",
        "default_title": "Timesheet Reminder",
        "email_subject": "Reminder: Submit your timesheet",
        "email_body_html": """
            <p>Hi {{first_name}},</p>
            <p>Please submit your timesheet before end of day.</p>
            <p><a href="{{link}}" style="background:#0b57d0; color:#fff; padding:6px 16px; border-radius:4px; text-decoration:none;">Submit Timesheet</a></p>
        """
    }
]

def get_template(template_id):
    for t in TEMPLATES:
        if t['id'] == template_id:
            return t
    return None

def get_categories():
    return sorted({t['category'] for t in TEMPLATES})

def get_template_names():
    return [(t['id'], t['name']) for t in TEMPLATES]