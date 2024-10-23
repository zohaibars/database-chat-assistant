REDMINE_DATABASE = {
    "projects": {
        "description": """The core unit of organization in Redmine. Each project can have multiple issues, members, and associated trackers.""",
        "important_columns": [
            {"name": "id", "description": "Unique identifier for each project."},
            {"name": "name", "description": "Name of the project."},
            {"name": "description", "description": "Description of the project."},
            {"name": "identifier", "description": "Short name used in URLs for the project."}
        ],
        "relationships": [
            {"related_table": "issues", "relation": "One-to-Many", "key": "id", "related_key": "project_id"},
            {"related_table": "members", "relation": "One-to-Many", "key": "id", "related_key": "project_id"},
            {"related_table": "projects_trackers", "relation": "One-to-Many", "key": "id", "related_key": "project_id"}
        ]
    },
    "issues": {
        "description": """Represent tasks, bugs, or features within a project. Each issue is linked to a specific project and tracker and has an associated status to indicate its progress.""",
        "important_columns": [
            {"name": "id", "description": "Unique identifier for each issue."},
            {"name": "project_id", "description": "ID of the project the issue belongs to."},
            {"name": "tracker_id", "description": "ID of the category the project is tracked by."},
            {"name": "subject", "description": "Subject or title of the issue."},
            {"name": "description", "description": "Description of the issue."},
            {"name": "status_id", "description": "ID of the status of the issue."},
            {"name": "assigned_to_id", "description": "ID of the user assigned to the issue."}
        ],
        "relationships": [
            {"related_table": "projects", "relation": "Many-to-One", "key": "project_id", "related_key": "id"},
            {"related_table": "time_entries", "relation": "One-to-Many", "key": "id", "related_key": "issue_id"},
            {"related_table": "users", "relation": "Many-to-One", "key": "assigned_to_id", "related_key": "id"}
        ]
    },
    "users": {
        "description": " Stores information about users in Redmine, including their login names, email addresses, and other user-related settings.",
        "important_columns": [
            {"name": "id", "description": "Unique identifier for each user."},
            {"name": "login", "description": "User's email address."},
            {"name": "firstname", "description": "User's first name."},
            {"name": "lastname", "description": "User's last name."}
        ],
        "relationships": [
            {"related_table": "issues", "relation": "One-to-Many", "key": "id", "related_key": "assigned_to_id"},
            {"related_table": "time_entries", "relation": "One-to-Many", "key": "id", "related_key": "user_id"},
            {"related_table": "members", "relation": "One-to-Many", "key": "id", "related_key": "user_id"}
        ]
    },
    "roles": {
        "description": "Defines roles with specific permissions that can be assigned to users within projects.",
        "important_columns": [
            {"name": "id", "description": "Unique identifier for each role."},
            {"name": "name", "description": "Name of the role."},
            {"name": "permissions", "description": "Permissions assigned to the role."},
            {"name": "assignable", "description": "Indicates if the role is assignable."}
        ],
        "relationships": [
            {"related_table": "member_roles", "relation": "One-to-Many", "key": "id", "related_key": "role_id"}
        ]
    },
    "members": {
        "description": "Associates users with projects and roles by storing membership information.",
        "important_columns": [
            {"name": "id", "description": "Unique identifier for each membership."},
            {"name": "user_id", "description": "ID of the user."},
            {"name": "project_id", "description": "ID of the project."},
            {"name": "role_id", "description": "ID of the role within the project."}
        ],
        "relationships": [
            {"related_table": "projects", "relation": "Many-to-One", "key": "project_id", "related_key": "id"},
            {"related_table": "users", "relation": "Many-to-One", "key": "user_id", "related_key": "id"},
            {"related_table": "member_roles", "relation": "One-to-Many", "key": "id", "related_key": "member_id"}
        ]
    },
    "trackers": {
        "description": "Define different types of issues (e.g., bug, feature, support) that can be used in projects. Projects specify which trackers they use through the projects_trackers table.",
        "important_columns": [
            {"name": "id", "description": "Unique identifier for each tracker."},
            {"name": "name", "description": "Name of the tracker."},
            {"name": "is_in_chlog", "description": "Indicates if the tracker should be shown in the changelog."}
        ],
        "relationships": [
            {"related_table": "projects_trackers", "relation": "One-to-Many", "key": "id", "related_key": "tracker_id"},
            {"related_table": "issues", "relation": "One-to-Many", "key": "id", "related_key": "tracker_id"}
        ]
    },
    "issue_statuses": {
        "description": "Defines the possible statuses that issues can have, such as 'New', 'In Progress', 'Resolved', etc.",
        "important_columns": [
            {"name": "id", "description": "Unique identifier for each status."},
            {"name": "name", "description": "Name of the status."},
            {"name": "is_closed", "description": "Indicates if the status represents a closed state."}
        ],
        "relationships": [
            {"related_table": "issues", "relation": "One-to-Many", "key": "id", "related_key": "status_id"}
        ]
    },
    "custom_fields": {
        "description": "Stores information about custom fields that can be added to projects or issues, including their names, types, and configurations.",
        "important_columns": [
            {"name": "id", "description": "Unique identifier for each custom field."},
            {"name": "name", "description": "Name of the custom field."},
            {"name": "field_format", "description": "Format of the custom field."},
            {"name": "is_required", "description": "Indicates if the custom field is required."}
        ],
        "relationships": [
            {"related_table": "custom_values", "relation": "One-to-Many", "key": "id", "related_key": "custom_field_id"}
        ]
    },
    "time_entries": {
        "description": "Records time entries for work done on issues, tracking the amount of time spent by users on specific tasks",
        "important_columns": [
            {"name": "id", "description": "Unique identifier for each time entry."},
            {"name": "user_id", "description": "ID of the user who logged the time entry."},
            {"name": "issue_id", "description": "ID of the issue the time entry is related to."},
            {"name": "hours", "description": "Amount of time spent on the issue (in hours)."},
            {"name": "activity_id", "description": "ID of the activity associated with the time entry."},
            {"name": "spent_on", "description": "Date when the time was logged."},
            {"name": "comments", "description": "Additional comments or description for the time entry."}
        ],
        "relationships": [
            {"related_table": "issues", "relation": "Many-to-One", "key": "issue_id", "related_key": "id"},
            {"related_table": "users", "relation": "Many-to-One", "key": "user_id", "related_key": "id"}
        ]
    },
    # "attachments": {
    #     "description": "Stores file attachments associated with issues or other entities in Redmine, such as documents, images, or screenshots.",
    #     "important_columns": [
    #         {"name": "id", "description": "Unique identifier for each attachment."},
    #         {"name": "container_id", "description": "ID of the entity the attachment belongs to."},
    #         {"name": "container_type", "description": "Type of the entity the attachment belongs to."},
    #         {"name": "filename", "description": "Name of the attached file."},
    #         {"name": "disk_filename", "description": "Name of the file on disk."},
    #         {"name": "filesize", "description": "Size of the attached file."}
    #     ],
    #     "relationships": [
    #         {"related_table": "issues", "relation": "Many-to-One", "key": "container_id", "related_key": "id", "condition": "container_type='Issue'"}
    #     ]
    # },
    "enumerations": {
        "description": "Contains various enumerations used throughout Redmine, such as priorities, time entry activities, and custom field formats.",
        "important_columns": [
            {"name": "id", "description": "Unique identifier for each enumeration."},
            {"name": "name", "description": "Name of the enumeration."},
            {"name": "position", "description": "Position of the enumeration."},
            {"name": "is_default", "description": "Indicates if the enumeration is a default option."}
        ],
        "relationships": [
            {"related_table": "time_entries", "relation": "One-to-Many", "key": "id", "related_key": "activity_id", "condition": "type='TimeEntryActivity'"}
        ]
    },
    "member_roles": {
        "description": "Associates roles with members (users) within projects, defining the roles each member holds in a project.",
        "important_columns": [
            {"name": "id", "description": "Unique identifier for each member role."},
            {"name": "member_id", "description": "ID of the member associated with the role."},
            {"name": "role_id", "description": "ID of the role assigned to the member."},
            {"name": "inherited_from", "description": "Indicates if the role is inherited from a parent project."}
        ],
        "relationships": [
            {"related_table": "members", "relation": "Many-to-One", "key": "member_id", "related_key": "id"},
            {"related_table": "roles", "relation": "Many-to-One", "key": "role_id", "related_key": "id"}
        ]
    },
    "projects_trackers": {
        "description": "Defines which trackers are available for each project, specifying which types of issues can be created within a project.",
        "important_columns": [
            {"name": "id", "description": "Unique identifier for each project-tracker association."},
            {"name": "project_id", "description": "ID of the project."},
            {"name": "tracker_id", "description": "ID of the tracker associated with the project."}
        ],
        "relationships": [
            {"related_table": "projects", "relation": "Many-to-One", "key": "project_id", "related_key": "id"},
            {"related_table": "trackers", "relation": "Many-to-One", "key": "tracker_id", "related_key": "id"}
        ]
    }
}

REDMINE_EXAMPLES = [
    {
        "query": "what are the time logged by talha. With comments, date, and for which project?",
        "passage": """
        SELECT 
            te.spent_on, 
            te.comments, 
            te.hours, 
            p.name AS project_name
        FROM 
            time_entries te
        JOIN 
            users u ON te.user_id = u.id
        JOIN 
            projects p ON te.project_id = p.id
        WHERE 
            u.firstname sounds like 'Talha'
        ORDER BY 
            te.spent_on DESC
        LIMIT 50;"""
    },
    {
        "query": "Count all the projects worked on last month",
        "passage": """
        SELECT 
            p.name AS project_name, 
            COUNT(te.id) AS total_hours
        FROM 
            time_entries te
        JOIN 
            issues i ON te.issue_id = i.id
        JOIN 
            projects p ON i.project_id = p.id
        WHERE 
            te.spent_on >= DATE_SUB(CURDATE(), INTERVAL 1 MONTH)
        GROUP BY 
            p.name"""
    },
    {
        "query": "Count all the projects being worked on.",
        "passage": """
        SELECT 
            COUNT(DISTINCT p.id) AS project_count
        FROM 
            projects p
        JOIN 
            issues i ON p.id = i.project_id
        JOIN 
            time_entries te ON i.id = te.issue_id;"""
    },
    {
        "query": "Drop The table projects.",
        "passage": "Select no;"
    },
    {
        "query": "create The table new project with id, title, description columns.",
        "passage": "Select no;"
    },
    {
        "query": "what tasks are in ChatBot project",
        "passage": """
        SELECT 
            i.subject AS task_name
        FROM 
            issues i
        JOIN 
            projects p ON i.project_id = p.id
        WHERE 
            p.name  LIKE '%ChatBot%'"""
    },
    {
        "query": "Number of tasks assigned to Zohaib that are in progress by developer:",
        "passage": """
        SELECT COUNT(*) AS in_progress_tasks FROM issues 
        JOIN users ON issues.assigned_to_id = users.id 
        JOIN issue_statuses ON issues.status_id = issue_statuses.id 
        WHERE users.firstname Sounds LIKE '%Zohaib%' AND issue_statuses.name LIKE '%In Progress(Dev)%'
        """
    },
    {
        "query": "What is the current backlog size for Project Chat Food App?",
        "passage": """
        "SELECT COUNT(*) AS backlog_size 
        FROM issues i 
        INNER JOIN projects p ON i.project_id = p.id 
        INNER JOIN issue_statuses s ON i.status_id = s.id 
        WHERE p.name like '%Chat Food App%' AND s.is_closed = 0
        """

    },
    {
        "query": "How many tasks are assigned to talha muhammad and what is there status?",
        "passage": """
        SELECT i.id, i.subject, iss.name AS status
        FROM issues i
        JOIN issue_statuses iss ON i.status_id = iss.id
        JOIN users u ON i.assigned_to_id = u.id
        WHERE u.firstname SOUNDS LIKE '%talha%' and u.lastname SOUNDS LIKE '%muhammad%'"""
    },
    {
        "query": "How many tasks were opened this month compared to last month?",
        "passage": """
        SELECT
            SUM(CASE WHEN DATE_FORMAT(created_on, '%Y-%m') = DATE_FORMAT(CURRENT_DATE, '%Y-%m') THEN 1 ELSE 0 END) AS this_month,
            SUM(CASE WHEN DATE_FORMAT(created_on, '%Y-%m') = DATE_FORMAT(CURRENT_DATE - INTERVAL 1 MONTH, '%Y-%m') THEN 1 ELSE 0 END) AS last_month
        FROM issues"""
    },
    {
        "query": "How many bugs were reported in the last quarter?",
        "passage": """ 
        SELECT COUNT(*) AS reported_bugs
        FROM issues
        WHERE tracker_id = (SELECT id FROM trackers WHERE name like '%Bug%')
        AND created_on >= DATE_SUB(DATE_FORMAT(CURRENT_DATE, '%Y-%m-01'), INTERVAL QUARTER(CURRENT_DATE) - 1 QUARTER);"""
    },
    {
        "query": "The number of tasks assigned to Zarar that are in progress",
        "passage": """
        SELECT COUNT(*) AS in_progress_tasks
        FROM issues
        JOIN users ON issues.assigned_to_id = users.id
        JOIN issue_statuses ON issues.status_id = issue_statuses.id
        WHERE users.firstname SOUNDS LIKE '%Zarar%' AND issue_statuses.name like '%In Progress%';"""
    },
    {
        "query": "Tasks closed by QA team that were assigned to Muhammad Usama.",
        "passage": """
        SELECT 
            issues.subject, 
            issue_statuses.name as status
        FROM issues 
        JOIN users ON issues.assigned_to_id = users.id
        JOIN issue_statuses ON issues.status_id = issue_statuses.id
        WHERE 
            users.firstname SOUNDS LIKE '%Muhammad%' 
            AND users.lastname SOUNDS LIKE '%Usama%' 
            AND issue_statuses.name like '%Closed(QA)%';"""
    },
    {
        "query": "list all Bugs that require urgent attention in nimar projects.",
        "passage": """
        SELECT 
            i.subject,
            i.description,
            i.due_date,
            p.name AS project_name
        FROM 
            issues AS i
        JOIN 
            projects AS p ON i.project_id = p.id
        WHERE 
            i.tracker_id IN (SELECT id FROM trackers WHERE name = 'Bug')
            AND i.priority_id IN (SELECT id FROM enumerations WHERE name LIKE '%Urgent%')
            AND i.project_id IN (SELECT id FROM projects WHERE name LIKE '%nimar%')
        Limit 50;"""
    },
    {
        "query": "List bugs reported between a date range of 5/22/2024 to 5/29/2024.",
        "passage": """
        SELECT * FROM issues 
        WHERE tracker_id = (SELECT id FROM trackers WHERE name like '%Bug%') 
        AND created_on BETWEEN '2024-05-22' AND '2024-05-29';
        """
    },
    {
        "query": "What are tasks typically handled by individuals who are not developers",
        "passage": """
        SELECT 
            u.firstname as assigned_to,
            i.subject as title,
            i.description as details,
            i.due_date,
            s.name as status,
            r.name as role
        FROM 
            issues AS i
        JOIN 
            users AS u ON i.assigned_to_id = u.id
        JOIN 
            issue_statuses AS s ON i.status_id = s.id
        LEFT JOIN 
            members AS m ON m.user_id = u.id
        LEFT JOIN 
            member_roles AS mr ON mr.member_id = m.id
        LEFT JOIN 
            roles AS r ON mr.role_id = r.id
        WHERE 
            s.name like '%In Progress%'
            AND (r.name IS NULL OR r.name not like '%Developer%')
        limit 50;"""
    },
    {
        "query": "How many tasks are currently in progress by individuals who are not developers?",
        "passage": """
        SELECT 
            count(*)
        FROM 
            issues AS i
        JOIN 
            users AS u ON i.assigned_to_id = u.id
        JOIN 
            issue_statuses AS s ON i.status_id = s.id
        LEFT JOIN 
            members AS m ON m.user_id = u.id
        LEFT JOIN 
            member_roles AS mr ON mr.member_id = m.id
        LEFT JOIN 
            roles AS r ON mr.role_id = r.id
        WHERE 
            s.name like '%In Progress%'
            AND (r.name IS NULL OR r.name not like '%Developer%')"""
    },
    {
        "query": "What tasks are involved in the AI-NIMAR project and their category?",
        "passage": """
        SELECT 
            i.subject AS task_name,
            t.name AS tracker_name
        FROM 
            issues AS i
        JOIN 
            projects AS p ON i.project_id = p.id
        JOIN 
            trackers AS t ON i.tracker_id = t.id
        WHERE 
            p.name LIKE '%ai-nimar%'
        LIMIT 50;"""
    },
    {
        "query": "Which projects is NLP a part of?",
        "passage": """
        SELECT 
            p.name AS parent_project_name
        FROM 
            projects p
        JOIN 
            projects AS child_p ON p.id = child_p.parent_id
        WHERE 
            child_p.name like '%NLP%'"""
    },
    {
        "query": "what projects saud is working on.",
        "passage": """
        SELECT 
            DISTINCT p.name AS project_name
        FROM 
            projects p
        JOIN 
            issues i ON p.id = i.project_id
        JOIN 
            users u ON i.assigned_to_id = u.id
        WHERE 
            u.firstname Sounds like '%Saud%'"""
    },
    {
        "query": "Find developers that are working on Computer vision projects.",
        "passage": """
        SELECT 
            DISTINCT u.firstname, 
            u.lastname,
            p.name AS project_name,
            r.name AS role_name
        FROM 
            projects AS p
        JOIN 
            members AS m ON p.id = m.project_id
        JOIN 
            member_roles AS mr ON m.id = mr.member_id
        JOIN 
            roles AS r ON mr.role_id = r.id
        JOIN 
            users AS u ON m.user_id = u.id
        WHERE 
            p.name LIKE '%Computer Vision%'
            AND r.name Sounds LIKE '%Developer%'
        ORDER BY 
            u.firstname,u.lastname;"""
    },
    {
        "query": "What bugs reported by Wajeeh are still unresolved?",
        "passage": """
        SELECT 
            author.firstname AS author_firstname,
            author.lastname AS author_lastname,
            assignee.firstname AS assigned_firstname,
            assignee.lastname AS assigned_lastname,
            i.subject AS bug_subject,
            i.description AS bug_description,
            i.created_on AS reported_date,
            s.name AS status
        FROM 
            issues AS i
        JOIN 
            users AS author ON i.author_id = author.id
        JOIN 
            users AS assignee ON i.assigned_to_id = assignee.id
        JOIN 
            trackers AS t ON i.tracker_id = t.id
        JOIN 
            issue_statuses AS s ON i.status_id = s.id
        WHERE 
            author.firstname Sounds LIKE '%Wajeeh%'
            AND t.name LIKE '%Bug%'
            AND s.is_closed = 0
        ORDER BY 
            i.created_on DESC
        LIMIT 25;"""
    },
    {
        "query": "Child/sub projects in computer vision project",
        "passage": """
        SELECT 
            p2.name AS sub_project_name,
            p2.description AS sub_project_description
        FROM 
            projects AS p1
        JOIN 
            projects AS p2 ON p1.id = p2.parent_id
        WHERE 
            p1.name LIKE '%Computer Vision%'
        ORDER BY 
            p2.name;"""
    },
    #     {
    #     "query": "Drop The table projects.",
    #     "passage": """Select no;"""
    # },
]

